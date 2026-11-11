<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class IdempotentWrite
{
    public function handle(Request $request, Closure $next)
    {
        $key = $request->header('Idempotency-Key');
        if ($request->isMethodSafe() || !$key) return $next($request);
        abort_unless(Str::isUuid($key), 422, 'Identitas penyimpanan tidak valid.');
        $userId = $request->user()->id;
        $hash = hash('sha256', $request->method().' '.$request->path().' '.$request->getContent());

        return DB::transaction(function () use ($request, $next, $key, $userId, $hash) {
            // Serialize writes for this account, including the first use of a request key.
            DB::table('users')->where('id', $userId)->lockForUpdate()->first();
            $receipt = DB::table('request_receipts')->where('user_id', $userId)->where('request_key', $key)->first();
            if ($receipt) {
                abort_unless(hash_equals($receipt->request_hash, $hash), 409, 'Permintaan sebelumnya sudah tersimpan. Muat data terbaru.');
                return response($receipt->response_body, $receipt->status_code)
                    ->header('Content-Type', 'application/json')->header('Idempotency-Replayed', 'true');
            }
            $response = $next($request);
            if ($response->isSuccessful()) {
                DB::table('request_receipts')->insert([
                    'user_id' => $userId, 'request_key' => $key, 'request_hash' => $hash,
                    'status_code' => $response->getStatusCode(), 'response_body' => $response->getContent(),
                    'created_at' => now(),
                ]);
            }
            return $response;
        });
    }
}
