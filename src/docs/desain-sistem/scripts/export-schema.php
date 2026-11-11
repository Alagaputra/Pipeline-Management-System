<?php

// Read metadata only; never export application rows or connection credentials.
require dirname(__DIR__, 3).'/backend/vendor/autoload.php';
$app = require dirname(__DIR__, 3).'/backend/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
if (Illuminate\Support\Facades\DB::connection()->getDriverName() !== 'pgsql') {
    throw new RuntimeException('Dokumentasi fisik ini membutuhkan PostgreSQL.');
}
$schema = [
    'captured_on' => '2026-10-19',
    'engine' => 'PostgreSQL',
    'tables' => Illuminate\Support\Facades\DB::select("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"),
    'columns' => Illuminate\Support\Facades\DB::select("SELECT table_name, column_name, ordinal_position, data_type, udt_name, character_maximum_length, is_nullable, column_default FROM information_schema.columns WHERE table_schema = 'public' ORDER BY table_name, ordinal_position"),
    'constraints' => Illuminate\Support\Facades\DB::select("SELECT r.relname AS table_name, c.conname AS name, c.contype AS type, pg_get_constraintdef(c.oid, true) AS definition FROM pg_constraint c JOIN pg_class r ON r.oid = c.conrelid JOIN pg_namespace n ON n.oid = r.relnamespace WHERE n.nspname = 'public' AND c.contype IN ('p','f','u','c') ORDER BY r.relname, c.conname"),
    'indexes' => Illuminate\Support\Facades\DB::select("SELECT tablename AS table_name, indexname AS name, indexdef AS definition FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname"),
];
file_put_contents(dirname(__DIR__).'/schema.json', json_encode($schema, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES).PHP_EOL);
echo count($schema['tables']).' tabel, '.count($schema['columns']).' kolom, '.count($schema['constraints']).' constraint diekspor (metadata saja).'.PHP_EOL;
