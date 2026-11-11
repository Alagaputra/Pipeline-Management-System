<?php

namespace App\Services;

use App\Models\AnnualTarget;
use App\Models\Division;
use App\Models\Opportunity;
use App\Models\Product;

class DashboardReport
{
    public function build(int $year, ?int $divisionId): array
    {
        $query = Opportunity::query()->when($divisionId, fn ($q) => $q->where('division_id', $divisionId));
        $active = (clone $query)->where('outcome', 'Active');
        $won = (clone $query)->where('outcome', 'Won')->whereYear('closed_date', $year);
        $scopes = Division::query()->when($divisionId, fn ($q) => $q->whereKey($divisionId))->pluck('code');
        $targets = AnnualTarget::whereIn('scope_code', $scopes)->where('year', $year)
            ->selectRaw('product_id, SUM(target_value) as total')->groupBy('product_id')->pluck('total', 'product_id');
        $actuals = (clone $won)->selectRaw('product_id, SUM(realization) as total')->groupBy('product_id')->pluck('total', 'product_id');
        $summary = Product::where('measure', 'IDR')->where('is_active', true)
            ->when($divisionId, fn ($q) => $q->whereHas('divisions', fn ($d) => $d->whereKey($divisionId)))
            ->orderBy('id')->get()->map(function ($product) use ($targets, $actuals) {
                $target = (int) ($targets[$product->id] ?? 0);
                $realization = (int) ($actuals[$product->id] ?? 0);
                return ['product' => $product->name, 'target' => $target, 'realization' => $realization,
                    'percentage' => $target > 0 ? $realization / $target * 100 : null,
                    'remaining' => max(0, $target - $realization)];
            });
        $totalTarget = $summary->sum('target');
        $realization = (int) (clone $won)->sum('realization');
        $interest = (clone $active)->selectRaw('interest_status, COUNT(*) as total')->groupBy('interest_status')->pluck('total', 'interest_status');
        $due = (clone $active)->whereNotNull('follow_up_date')->where('follow_up_completed', false)
            ->whereDate('follow_up_date', '<=', today());
        // Group dates in PHP so the same report is testable on SQLite and PostgreSQL.
        $recorded = (clone $query)->whereYear('recorded_date', $year)->get(['recorded_date', 'nominal'])
            ->groupBy(fn ($row) => (int) $row->recorded_date->format('n'));
        $closed = (clone $won)->get(['closed_date', 'realization'])
            ->groupBy(fn ($row) => (int) $row->closed_date->format('n'));
        $trend = collect(range(1, 12))->map(function ($month) use ($year, $recorded, $closed) {
            $future = $year > now()->year || ($year === now()->year && $month > now()->month);
            return ['month' => $month,
                'recorded_nominal' => $future ? null : (int) ($recorded->get($month)?->sum('nominal') ?? 0),
                'realization' => $future ? null : (int) ($closed->get($month)?->sum('realization') ?? 0)];
        });
        return [
            'year' => $year, 'active_opportunities' => (clone $active)->count(),
            'active_nominal' => (int) (clone $active)->sum('nominal'),
            'hot_opportunities' => (clone $active)->where('interest_status', 'Hot')->count(),
            'hot_nominal' => (int) (clone $active)->where('interest_status', 'Hot')->sum('nominal'),
            'won' => (clone $won)->count(),
            'lost' => (clone $query)->where('outcome', 'Lost')->whereYear('closed_date', $year)->count(),
            'realization' => $realization, 'total_target' => $totalTarget,
            'percentage' => $totalTarget > 0 ? $realization / $totalTarget * 100 : null,
            'summary' => $summary, 'trend' => $trend,
            'interest' => collect(['Cold', 'Warm', 'Hot'])->mapWithKeys(fn ($status) => [$status => (int) ($interest[$status] ?? 0)]),
            'follow_up_count' => (clone $due)->count(),
            'follow_ups' => (clone $due)->with(['pic:id,name', 'product:id,name'])->orderBy('follow_up_date')->limit(5)->get(),
        ];
    }
}
