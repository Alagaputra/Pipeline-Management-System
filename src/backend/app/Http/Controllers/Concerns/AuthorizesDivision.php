<?php

namespace App\Http\Controllers\Concerns;

use App\Models\Division;
use App\Models\Opportunity;
use Illuminate\Http\Request;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

trait AuthorizesDivision
{
    // Batas akses selalu ditegakkan di backend; filter pilihan divisi UI bukan otorisasi.
    protected function divisionId(Request $request, ?int $requested = null): int
    {
        $user = $request->user();
        if (!$user->isHead()) return (int) $user->division_id;
        // Head harus memilih satu divisi saat menulis; pengguna lain memakai divisi akunnya.
        $id = $requested ?: (int) $request->input('division_id', $request->query('division_id'));
        abort_unless($id && Division::whereKey($id)->exists(), 422, 'Pilih satu divisi yang valid.');
        return $id;
    }

    protected function visibleOpportunity(Request $request, int $id, bool $lock = false): Opportunity
    {
        // Batasi pencarian sebelum findOrFail, sehingga data divisi lain tidak terungkap.
        // lock dipakai di dalam transaksi tulis untuk mencegah perubahan bersamaan.
        $query = Opportunity::query();
        if (!$request->user()->isHead()) $query->where('division_id', $request->user()->division_id);
        if ($lock) $query->lockForUpdate();
        return $query->findOrFail($id);
    }
}
