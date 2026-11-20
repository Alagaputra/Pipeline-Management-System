<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class EnsureActiveUser
{
    public function handle(Request $request, Closure $next)
    {
        if (!$request->user()->is_active || !$request->user()->hasValidAccess()) {
            // Berlaku juga jika status diubah lewat query langsung tanpa event model.
            $request->user()->tokens()->delete();

            return response()->json(['message' => 'Akun tidak aktif atau akses belum valid. Silakan hubungi administrator.'], 401);
        }

        return $next($request);
    }
}
