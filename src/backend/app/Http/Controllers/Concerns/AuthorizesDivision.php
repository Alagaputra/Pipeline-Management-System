<?php

namespace App\Http\Controllers\Concerns;

use App\Models\Division;
use App\Models\Opportunity;
use Illuminate\Http\Request;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;

trait AuthorizesDivision
{
    protected function divisionId(Request $request, ?int $requested = null): int
    {
        $user = $request->user();
        if (!$user->isHead()) return (int) $user->division_id;
        $id = $requested ?: (int) $request->input('division_id', $request->query('division_id'));
        abort_unless($id && Division::whereKey($id)->exists(), 422, 'Pilih satu divisi yang valid.');
        return $id;
    }

    protected function visibleOpportunity(Request $request, int $id, bool $lock = false): Opportunity
    {
        $query = Opportunity::query();
        if (!$request->user()->isHead()) $query->where('division_id', $request->user()->division_id);
        if ($lock) $query->lockForUpdate();
        return $query->findOrFail($id);
    }
}
