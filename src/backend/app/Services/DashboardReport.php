<?php

namespace App\Services;

use App\Models\AnnualTarget;
use App\Support\ExactAmount;
use App\Models\Division;
use App\Models\Opportunity;
use App\Models\Product;

class DashboardReport
{
    public function build(int $year, ?int $divisionId): array
    {
        // Pipeline aktif mencakup seluruh periode; Won/Lost dan realisasi tahunan
        // mengikuti tahun closed_date. divisionId null berarti seluruh divisi.
        $query = Opportunity::query()->when($divisionId, fn ($q) => $q->where('division_id', $divisionId));
        $active = (clone $query)->where('outcome', 'Active');
        // Clone query dasar agar filter satu metrik tidak terbawa ke metrik lainnya.
        $won = (clone $query)->where('outcome', 'Won')->whereYear('closed_date', $year);
        $funding = fn ($q) => $q->whereHas('product', fn ($product) => $product->where('measure', 'IDR'));
        $fundingWon = $funding(clone $won);
        $scopes = Division::query()->when($divisionId, fn ($q) => $q->whereKey($divisionId))->pluck('code');
        $targets = AnnualTarget::whereIn('scope_code', $scopes)->where('year', $year)
            ->get(['product_id', 'target_value'])->groupBy('product_id')->map(fn ($rows) => ExactAmount::sum($rows->pluck('target_value')));
        $actuals = (clone $fundingWon)->get(['product_id', 'realization'])->groupBy('product_id')->map(fn ($rows) => ExactAmount::sum($rows->pluck('realization')));
        $monthlyActuals = (clone $fundingWon)->get(['product_id', 'closed_date', 'realization'])
            ->groupBy('product_id')
            ->map(fn ($rows) => $rows->groupBy(fn ($row) => (int) $row->closed_date->format('n'))
                ->map(fn ($monthRows) => ExactAmount::sum($monthRows->pluck('realization'))));
        $summary = Product::where('measure', 'IDR')->where('is_active', true)
            ->when($divisionId, fn ($q) => $q->whereHas('divisions', fn ($d) => $d->whereKey($divisionId)))
            ->orderBy('id')->get()->map(function ($product) use ($targets, $actuals, $monthlyActuals) {
                $target = ($targets[$product->id] ?? 0);
                $realization = ($actuals[$product->id] ?? 0);
                // Target nol menghasilkan persentase null (belum ada target), bukan 0%.
                return ['product' => $product->name, 'target' => $target, 'realization' => $realization,
                    'percentage' => $target > 0 ? $realization / $target * 100 : null,
                    'remaining' => ExactAmount::remaining($target, $realization),
                    'monthly_realizations' => $monthlyActuals->get($product->id, collect())];
            });
        $totalTarget = ExactAmount::sum($summary->pluck('target'));
        $realization = ExactAmount::sum((clone $fundingWon)->pluck('realization'));
        $interest = (clone $active)->selectRaw('interest_status, COUNT(*) as total')->groupBy('interest_status')->pluck('total', 'interest_status');
        $due = (clone $active)->whereNotNull('follow_up_date')->where('follow_up_completed', false)
            ->whereDate('follow_up_date', '<=', today());
        // Kelompokkan tanggal di PHP agar logika laporan sama pada SQLite dan PostgreSQL.
        $recordedRows = $funding(clone $query)->whereYear('recorded_date', $year)->get(['recorded_date', 'nominal']);
        $closedRows = (clone $fundingWon)->get(['closed_date', 'realization']);
        $serviceWon = Opportunity::with('product:id,code,name')->where('outcome', 'Won')
            ->whereYear('closed_date', $year)
            ->whereHas('product', fn ($product) => $product->whereIn('code', ['cms', 'bale-syariah', 'qris']))
            ->where(function ($q) use ($divisionId) {
                $q->whereHas('product', fn ($product) => $product->where('code', 'cms'))
                    ->orWhere(fn ($other) => $other->whereHas('product', fn ($product) => $product->whereIn('code', ['bale-syariah', 'qris']))
                        ->when($divisionId, fn ($scope) => $scope->where('division_id', $divisionId)));
            })->get(['product_id', 'division_id', 'closed_date']);
        $unitClosings = $divisionId ? $serviceWon->where('division_id', $divisionId) : $serviceWon;
        $unitsByDate = $unitClosings->countBy(fn ($row) => $row->closed_date->format('Y-m-d'));
        $serviceRealizations = $serviceWon->groupBy(fn ($row) => $row->product->name)
            ->map(fn ($rows) => $rows->countBy(fn ($row) => (int) $row->closed_date->format('n')));
        $recorded = $recordedRows->groupBy(fn ($row) => (int) $row->recorded_date->format('n'));
        $closed = $closedRows->groupBy(fn ($row) => (int) $row->closed_date->format('n'));
        $trend = collect(range(1, 12))->map(function ($month) use ($year, $recorded, $closed) {
            // Bulan mendatang memakai null agar grafik tidak menampilkan realisasi nol semu.
            $future = $year > now()->year || ($year === now()->year && $month > now()->month);
            return ['month' => $month,
                'recorded_nominal' => $future ? null : ExactAmount::sum($recorded->get($month)?->pluck('nominal') ?? []),
                'realization' => $future ? null : ExactAmount::sum($closed->get($month)?->pluck('realization') ?? [])];
        });
        $recordedByDate = $recordedRows->groupBy(fn ($row) => $row->recorded_date->format('Y-m-d'));
        $closedByDate = $closedRows->groupBy(fn ($row) => $row->closed_date->format('Y-m-d'));
        $date = \Carbon\CarbonImmutable::create($year, 1, 1)->startOfDay();
        $today = now()->toDateString();
        $daily = [];
        while ($date->year === $year) {
            $dateKey = $date->toDateString();
            $future = $dateKey > $today;
            $daily[] = [
                'date' => $dateKey,
                'realized_units' => $future ? null : $unitsByDate->get($dateKey, 0),
                'recorded_nominal' => $future ? null : ExactAmount::sum($recordedByDate->get($dateKey)?->pluck('nominal') ?? []),
                'realization' => $future ? null : ExactAmount::sum($closedByDate->get($dateKey)?->pluck('realization') ?? []),
            ];
            $date = $date->addDay();
        }
        return [
            'year' => $year, 'active_opportunities' => (clone $active)->count(),
            'active_nominal' => ExactAmount::sum($funding(clone $active)->pluck('nominal')),
            'hot_opportunities' => (clone $active)->where('interest_status', 'Hot')->count(),
            'hot_nominal' => ExactAmount::sum($funding(clone $active)->where('interest_status', 'Hot')->pluck('nominal')),
            'won' => (clone $won)->count(),
            'realized_units' => $unitClosings->count(),
            'lost' => (clone $query)->where('outcome', 'Lost')->whereYear('closed_date', $year)->count(),
            'realization' => $realization, 'total_target' => $totalTarget,
            'percentage' => $totalTarget > 0 ? $realization / $totalTarget * 100 : null,
            'summary' => $summary, 'trend' => $trend, 'daily' => $daily, 'service_realizations' => $serviceRealizations,
            'interest' => collect(['Cold', 'Warm', 'Hot'])->mapWithKeys(fn ($status) => [$status => (int) ($interest[$status] ?? 0)]),
            'follow_up_count' => (clone $due)->count(),
            'follow_ups' => (clone $due)->with(['pic:id,name', 'product:id,name'])->orderBy('follow_up_date')->limit(5)->get(),
        ];
    }
}
