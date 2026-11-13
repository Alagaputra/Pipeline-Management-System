<?php

namespace App\Support;

use App\Models\AuditEvent;

trait WritesAudit
{
    // Snapshot sebelum/sesudah membentuk timeline perubahan. Controller memanggil
    // audit di dalam transaksi bisnis agar riwayat hanya tersimpan jika perubahan berhasil.
    protected function audit(?int $actorId, string $type, string|int $id, string $action, ?array $before, ?array $after): void
    {
        AuditEvent::create([
            'actor_id' => $actorId,
            'resource_type' => $type,
            'resource_id' => (string) $id,
            'action' => $action,
            'before_data' => $before,
            'after_data' => $after,
            'occurred_at' => now(),
            'source' => 'api',
        ]);
    }
}
