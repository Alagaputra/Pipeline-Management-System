<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class ImportLegacyMySql extends Command
{
    protected $signature = 'pipeline:import-mysql {--database=pipeline_funding} {--host=127.0.0.1} {--port=3306} {--username=root}';
    protected $description = 'Copy existing MySQL pipeline data into an empty PostgreSQL database without changing the source';

    public function handle(): int
    {
        if (DB::connection()->getDriverName() !== 'pgsql') {
            $this->error('The destination must be PostgreSQL.');
            return self::FAILURE;
        }
        $tables = ['divisions', 'users', 'products', 'division_products', 'target_scopes',
            'opportunities', 'opportunity_assignments', 'annual_targets', 'monthly_targets',
            'unit_realizations', 'branch_targets', 'audit_events'];
        foreach ($tables as $table) {
            if (DB::table($table)->exists()) {
                $this->error('Destination is not empty; no data was copied.');
                return self::FAILURE;
            }
        }
        config(['database.connections.legacy_mysql' => [
            'driver' => 'mysql', 'host' => $this->option('host'), 'port' => $this->option('port'),
            'database' => $this->option('database'), 'username' => $this->option('username'),
            'password' => env('LEGACY_MYSQL_PASSWORD', ''), 'charset' => 'utf8mb4',
            'collation' => 'utf8mb4_unicode_ci', 'prefix' => '', 'strict' => true,
        ]]);
        $source = DB::connection('legacy_mysql');
        // One source snapshot, one destination transaction. Preserve IDs and foreign keys.
        $source->transaction(function () use ($source, $tables) {
            DB::transaction(function () use ($source, $tables) {
                $booleans = ['users' => ['is_active'], 'products' => ['is_active'], 'opportunities' => ['follow_up_completed']];
                foreach ($tables as $table) {
                    $rows = $source->table($table)->get()->map(function ($row) use ($booleans, $table) {
                        $data = (array) $row;
                        foreach ($booleans[$table] ?? [] as $field) $data[$field] = (bool) $data[$field];
                        return $data;
                    });
                    foreach ($rows->chunk(100) as $chunk) DB::table($table)->insert($chunk->all());
                    if (!in_array($table, ['division_products', 'target_scopes'], true)) {
                        DB::select("SELECT setval(pg_get_serial_sequence(?, 'id'), COALESCE(MAX(id), 1), COUNT(*) > 0) FROM {$table}", [$table]);
                    }
                    $this->line($table.': '.$rows->count().' records');
                }
            });
        });
        $this->info('Import completed. MySQL source was not modified; login again on PostgreSQL.');
        return self::SUCCESS;
    }
}
