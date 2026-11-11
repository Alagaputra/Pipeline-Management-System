<?php

namespace App\Http\Controllers;

use App\Models\Division;
use App\Models\Product;
use App\Models\User;
use Illuminate\Http\Request;

class LookupController extends Controller
{
    public function divisions(Request $request)
    {
        return $request->user()->isHead() ? Division::orderBy('name')->get() : Division::whereKey($request->user()->division_id)->get();
    }

    public function products(Request $request)
    {
        $query = Product::query()->where('is_active', true)->with('divisions:id,code,name');
        if (!$request->user()->isHead()) $query->whereHas('divisions', fn ($q) => $q->whereKey($request->user()->division_id));
        return $query->orderBy('name')->get();
    }

    public function pics(Request $request)
    {
        $query = User::with('division:id,code,name')->where('role', 'pic')->where('is_active', true);
        if (!$request->user()->isHead()) $query->where('division_id', $request->user()->division_id);
        elseif ($request->filled('division_id')) $query->where('division_id', $request->integer('division_id'));
        return $query->orderBy('name')->get(['id', 'division_id', 'username', 'name', 'role']);
    }
}
