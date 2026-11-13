<?php

namespace App\Http\Controllers;

use App\Models\Opportunity;
use App\Models\User;
use Illuminate\Http\Request;

class ReportController extends Controller
{
    public function dashboard(Request $request)
    {
        // Head dapat membaca semua/satu divisi; role lain selalu dibatasi divisi akun.
        $request->validate(['year' => ['nullable', 'integer', 'between:2000,2100'],
            'division_id' => ['nullable', 'integer', 'exists:divisions,id']]);
        $divisionId = $request->user()->isHead()
            ? ($request->filled('division_id') ? $request->integer('division_id') : null)
            : $request->user()->division_id;
        return app(\App\Services\DashboardReport::class)->build($request->integer('year', now()->year), $divisionId);
    }

    public function team(Request $request)
    {
        // Ringkasan endpoint tim ini memakai seluruh periode, tanpa filter tahun closing.
        $query = User::where('role', 'pic')->where('is_active', true)->with('division:id,code,name');
        if (!$request->user()->isHead()) $query->where('division_id', $request->user()->division_id);
        elseif ($request->filled('division_id')) $query->where('division_id', $request->integer('division_id'));
        return $query->withCount([
            'opportunities as total_pipeline',
            'opportunities as active_pipeline' => fn ($q) => $q->where('outcome', 'Active'),
            'opportunities as won' => fn ($q) => $q->where('outcome', 'Won'),
            'opportunities as lost' => fn ($q) => $q->where('outcome', 'Lost'),
        ])->withSum(['opportunities as active_nominal' => fn ($q) => $q->where('outcome', 'Active')], 'nominal')->get();
    }

    public function picOpportunities(Request $request, int $id)
    {
        // Tampilkan juga peluang yang pernah ditangani PIC melalui riwayat penugasan.
        $pic = User::where('role', 'pic')->findOrFail($id);
        abort_unless($request->user()->isHead() || $request->user()->division_id === $pic->division_id, 404);
        return Opportunity::with(['product', 'division'])->where(function ($q) use ($id) {
            $q->where('pic_id', $id)->orWhereHas('assignments', fn ($a) => $a->where('pic_id', $id));
        })->latest('updated_at')->paginate(20);
    }

    private function scope(Request $request, $query): void
    {
        if (!$request->user()->isHead()) $query->where('division_id', $request->user()->division_id);
        elseif ($request->filled('division_id')) $query->where('division_id', $request->integer('division_id'));
    }
}
