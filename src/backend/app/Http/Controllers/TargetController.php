<?php

namespace App\Http\Controllers;

use App\Models\AnnualTarget;
use App\Models\BranchTarget;
use App\Models\Division;
use App\Models\Product;
use App\Models\TargetScope;
use App\Models\UnitRealization;
use App\Support\WritesAudit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class TargetController extends Controller
{
    use WritesAudit;

    public function index(Request $request)
    {
        $request->validate(['year' => ['required', 'integer', 'between:2000,2100'], 'scope' => ['nullable', 'string']]);
        $scopes = $this->readableScopes($request);
        if ($request->filled('scope')) {
            abort_unless(in_array($request->scope, $scopes, true), 403);
            $scopes = [$request->scope];
        }
        return AnnualTarget::with(['product:id,code,name,measure', 'monthlyTargets', 'unitRealizations'])
            ->whereIn('scope_code', $scopes)->where('year', $request->integer('year'))->get();
    }

    public function batch(Request $request)
    {
        $data = $request->validate([
            'scope' => ['required', 'string'], 'year' => ['required', 'integer', 'between:2000,2100'],
            'targets' => ['required', 'array', 'min:1', 'max:10'],
            'targets.*.product' => ['required', 'string', 'distinct'],
            'targets.*.target_value' => ['required', 'integer', 'min:0'],
            'targets.*.version' => ['required', 'integer', 'min:0'],
            'targets.*.monthly' => ['sometimes', 'array', 'size:12'],
            'targets.*.monthly.*.month' => ['required', 'integer', 'between:1,12'],
            'targets.*.monthly.*.target_value' => ['required', 'integer', 'min:0'],
            'targets.*.monthly.*.units' => ['sometimes', 'integer', 'min:0'],
            'targets.*.monthly.*.version' => ['sometimes', 'integer', 'min:0'],
        ]);
        $entries = collect($data['targets'])->sortBy('product')->map(function ($entry) use ($request, $data) {
            $product = Product::where('code', $entry['product'])->where('is_active', true)->firstOrFail();
            $this->authorizeWrite($request, $data['scope'], $product);
            if (isset($entry['monthly'])) {
                abort_unless(count(array_unique(array_column($entry['monthly'], 'month'))) === 12, 422, 'Bulan tidak boleh berulang.');
                foreach ($entry['monthly'] as $month) {
                    if ($product->measure === 'UNIT') abort_unless(isset($month['units'], $month['version']), 422, 'Lengkapi realisasi setiap bulan.');
                    else abort_if(isset($month['units']), 422, 'Realisasi unit hanya untuk produk layanan.');
                }
            }
            return [$product, $entry];
        });
        return DB::transaction(function () use ($request, $data, $entries) {
            TargetScope::whereKey($data['scope'])->lockForUpdate()->firstOrFail();
            $saved = [];
            foreach ($entries as [$product, $entry]) {
                $target = AnnualTarget::where(['scope_code' => $data['scope'], 'product_id' => $product->id, 'year' => $data['year']])->lockForUpdate()->first();
                abort_if(($target ? (int) $target->version : 0) !== $entry['version'], 409, 'Target telah berubah. Muat data terbaru.');
                $before = $target?->load(['monthlyTargets', 'unitRealizations'])->toArray();
                $target ??= new AnnualTarget(['scope_code' => $data['scope'], 'product_id' => $product->id, 'year' => $data['year']]);
                $target->fill(['target_value' => $entry['target_value'], 'updated_by' => $request->user()->id, 'version' => $target->exists ? $target->version + 1 : 1])->save();
                foreach ($entry['monthly'] ?? [] as $month) {
                    $target->monthlyTargets()->updateOrCreate(['month' => $month['month']], ['target_value' => $month['target_value']]);
                    if ($product->measure !== 'UNIT') continue;
                    $actual = $target->unitRealizations()->where('month', $month['month'])->lockForUpdate()->first();
                    abort_if(($actual ? (int) $actual->version : 0) !== $month['version'], 409, 'Realisasi telah berubah. Muat data terbaru.');
                    if (!$actual || (int) $actual->units !== $month['units']) {
                        $old = $actual?->toArray();
                        $actual ??= new UnitRealization(['annual_target_id' => $target->id, 'month' => $month['month']]);
                        $actual->fill(['units' => $month['units'], 'updated_by' => $request->user()->id, 'version' => $actual->exists ? $actual->version + 1 : 1])->save();
                        $this->audit($request->user()->id, 'unit_realization', $actual->id, $old ? 'updated' : 'created', $old, $actual->toArray());
                    }
                }
                $after = $target->load(['product', 'monthlyTargets', 'unitRealizations']);
                $this->audit($request->user()->id, 'annual_target', $target->id, $before ? 'updated' : 'created', $before, $after->toArray());
                $saved[] = $after;
            }
            return response()->json($saved);
        });
    }

    public function upsert(Request $request, string $scope, string $product, int $year)
    {
        $productModel = Product::where('code', $product)->where('is_active', true)->firstOrFail();
        $this->authorizeWrite($request, $scope, $productModel);
        abort_unless($year >= 2000 && $year <= 2100, 422, 'Tahun tidak valid.');
        $data = $request->validate([
            'target_value' => ['required', 'integer', 'min:0'], 'version' => ['required', 'integer', 'min:0'],
            'monthly' => ['sometimes', 'array', 'size:12'], 'monthly.*.month' => ['required', 'integer', 'between:1,12', 'distinct'],
            'monthly.*.target_value' => ['required', 'integer', 'min:0'],
        ]);
        return DB::transaction(function () use ($request, $scope, $productModel, $year, $data) {
            TargetScope::whereKey($scope)->lockForUpdate()->firstOrFail();
            $target = AnnualTarget::where(['scope_code' => $scope, 'product_id' => $productModel->id, 'year' => $year])->lockForUpdate()->first();
            abort_if($target && $target->version !== $data['version'], 409, 'Target telah berubah. Muat ulang.');
            abort_if(!$target && $data['version'] !== 0, 409, 'Target belum ada; gunakan version 0.');
            $before = $target?->load('monthlyTargets')->toArray();
            $target ??= new AnnualTarget(['scope_code' => $scope, 'product_id' => $productModel->id, 'year' => $year]);
            $target->fill(['target_value' => $data['target_value'], 'updated_by' => $request->user()->id, 'version' => $target->exists ? $target->version + 1 : 1])->save();
            foreach ($data['monthly'] ?? [] as $month) $target->monthlyTargets()->updateOrCreate(['month' => $month['month']], ['target_value' => $month['target_value']]);
            $after = $target->load(['product', 'monthlyTargets', 'unitRealizations']);
            $this->audit($request->user()->id, 'annual_target', $target->id, $before ? 'updated' : 'created', $before, $after->toArray());
            return response()->json($after);
        });
    }

    public function realize(Request $request, string $scope, string $product, int $year, int $month)
    {
        $productModel = Product::where('code', $product)->where('measure', 'UNIT')->firstOrFail();
        $this->authorizeWrite($request, $scope, $productModel);
        abort_unless($year >= 2000 && $year <= 2100 && $month >= 1 && $month <= 12, 422, 'Tahun atau bulan tidak valid.');
        $data = $request->validate(['units' => ['required', 'integer', 'min:0'], 'version' => ['required', 'integer', 'min:0']]);
        return DB::transaction(function () use ($request, $scope, $productModel, $year, $month, $data) {
            TargetScope::whereKey($scope)->lockForUpdate()->firstOrFail();
            $target = AnnualTarget::firstOrCreate(['scope_code' => $scope, 'product_id' => $productModel->id, 'year' => $year], ['target_value' => 0, 'updated_by' => $request->user()->id]);
            $actual = UnitRealization::where(['annual_target_id' => $target->id, 'month' => $month])->lockForUpdate()->first();
            abort_if($actual && $actual->version !== $data['version'], 409, 'Realisasi telah berubah. Muat ulang.');
            abort_if(!$actual && $data['version'] !== 0, 409, 'Realisasi belum ada; gunakan version 0.');
            $before = $actual?->toArray();
            $actual ??= new UnitRealization(['annual_target_id' => $target->id, 'month' => $month]);
            $actual->fill(['units' => $data['units'], 'updated_by' => $request->user()->id, 'version' => $actual->exists ? $actual->version + 1 : 1])->save();
            $this->audit($request->user()->id, 'unit_realization', $actual->id, $before ? 'updated' : 'created', $before, $actual->toArray());
            return response()->json($actual);
        });
    }

    public function branches(Request $request)
    {
        $request->validate(['year' => ['required', 'integer', 'between:2000,2100'], 'division_id' => ['nullable', 'integer']]);
        $query = BranchTarget::with('division:id,code,name')->where('year', $request->integer('year'));
        if (!$request->user()->isHead()) $query->where('division_id', $request->user()->division_id);
        elseif ($request->filled('division_id')) $query->where('division_id', $request->integer('division_id'));
        return $query->get();
    }

    public function upsertBranch(Request $request, string $division, string $branch, int $year)
    {
        $divisionModel = Division::where('code', $division)->firstOrFail();
        abort_unless($request->user()->isHead() || $request->user()->division_id === $divisionModel->id, 403);
        abort_unless($year >= 2000 && $year <= 2100, 422, 'Tahun tidak valid.');
        $data = $request->validate(['target_value' => ['required', 'integer', 'min:0'], 'version' => ['required', 'integer', 'min:0']]);
        return DB::transaction(function () use ($request, $divisionModel, $branch, $year, $data) {
            Division::whereKey($divisionModel->id)->lockForUpdate()->firstOrFail();
            $target = BranchTarget::where(['division_id' => $divisionModel->id, 'branch_code' => strtolower($branch), 'year' => $year])->lockForUpdate()->first();
            abort_if($target && $target->version !== $data['version'], 409, 'Target cabang telah berubah. Muat ulang.');
            abort_if(!$target && $data['version'] !== 0, 409, 'Target cabang belum ada; gunakan version 0.');
            $before = $target?->toArray();
            $target ??= new BranchTarget(['division_id' => $divisionModel->id, 'branch_code' => strtolower($branch), 'year' => $year]);
            $target->fill(['target_value' => $data['target_value'], 'updated_by' => $request->user()->id, 'version' => $target->exists ? $target->version + 1 : 1])->save();
            $this->audit($request->user()->id, 'branch_target', $target->id, $before ? 'updated' : 'created', $before, $target->toArray());
            return response()->json($target->load('division'));
        });
    }

    private function readableScopes(Request $request): array
    {
        if ($request->user()->isHead()) return ['konsumer', 'komersil', 'shared'];
        return [$request->user()->division->code, 'shared'];
    }

    private function authorizeWrite(Request $request, string $scope, Product $product): void
    {
        abort_unless(TargetScope::whereKey($scope)->exists(), 404);
        if ($scope === 'shared') {
            abort_unless($product->code === 'cms', 422, 'Scope shared hanya untuk CMS.');
            return;
        }
        abort_if($product->code === 'cms', 422, 'CMS harus memakai scope shared.');
        $division = TargetScope::whereKey($scope)->value('division_id');
        abort_unless($request->user()->isHead() || $request->user()->division_id === $division, 403);
        abort_unless($product->divisions()->whereKey($division)->exists(), 422, 'Produk tidak tersedia untuk divisi ini.');
    }
}
