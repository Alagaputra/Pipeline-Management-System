<?php

namespace App\Http\Middleware;

use Closure;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class IdempotentWrite
{
    // Idempotency-Key menghubungkan retry ke hasil simpan pertama untuk akun tersebut.
    // Jika key/payload sama, kembalikan respons tersimpan tanpa menjalankan controller lagi.
    public function handle(Request $request, Closure $next)
    {
        $key = $request->header('Idempotency-Key');
        if ($request->isMethodSafe() || !$key) return $next($request);
        abort_unless(Str::isUuid($key), 422, 'Identitas penyimpanan tidak valid.');
        $userId = $request->user()->id;
        $hash = hash('sha256', $request->method().' '.$request->getRequestUri().' '.$request->getContent());
        // Hash mengikat key ke method, endpoint, dan isi permintaan yang persis sama.

        return DB::transaction(function () use ($request, $next, $key, $userId, $hash) {
            // Kunci akun agar dua request bersamaan tidak sama-sama menganggap key baru.
            $user = User::whereKey($userId)->lockForUpdate()->firstOrFail();
            if (!$user->is_active || !$user->hasValidAccess()) {
                $user->tokens()->delete();
                return response()->json(['message' => 'Akses akun tidak valid.'], 401);
            }
            $authorizationContext = $user->authorizationContext();
            $user->withAccessToken($request->user()->currentAccessToken());
            $request->setUserResolver(fn () => $user);
            $receipt = DB::table('request_receipts')->where('user_id', $userId)->where('request_key', $key)->first();
            if ($receipt) {
                abort_unless($receipt->authorization_context && hash_equals($receipt->authorization_context, $authorizationContext), 409, 'Hak akses berubah atau hasil lama perlu diperiksa. Muat data terbaru sebelum menyimpan.');
                abort_unless(hash_equals($receipt->request_hash, $hash), 409, 'Permintaan sebelumnya sudah tersimpan. Muat data terbaru.');
                return response($receipt->response_body, $receipt->status_code)
                    ->header('Content-Type', 'application/json')->header('Idempotency-Replayed', 'true');
            }
            $response = $next($request);
            // Simpan receipt hanya untuk respons sukses, dalam transaksi yang sama
            // dengan perubahan bisnis sehingga data dan hasil retry tetap konsisten.
            if ($response->isSuccessful()) {
                DB::table('request_receipts')->insert([
                    'user_id' => $userId, 'request_key' => $key, 'request_hash' => $hash, 'authorization_context' => $authorizationContext,
                    'status_code' => $response->getStatusCode(), 'response_body' => $response->getContent(),
                    'created_at' => now(),
                ]);
            }
            return $response;
        });
    }
}
