<?php

namespace Database\Seeders;

use App\Models\Division;
use App\Models\Product;
use App\Models\TargetScope;
use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $konsumer = Division::firstOrCreate(['code' => 'konsumer'], ['name' => 'Konsumer']);
        $komersil = Division::firstOrCreate(['code' => 'komersil'], ['name' => 'Komersil']);

        $products = collect([
            ['code' => 'tabungan', 'name' => 'Tabungan', 'measure' => 'IDR'],
            ['code' => 'giro', 'name' => 'Giro', 'measure' => 'IDR'],
            ['code' => 'deposito', 'name' => 'Deposito', 'measure' => 'IDR'],
            ['code' => 'bale-syariah', 'name' => 'Bale Syariah', 'measure' => 'UNIT'],
            ['code' => 'qris', 'name' => 'QRIS', 'measure' => 'UNIT'],
            ['code' => 'cms', 'name' => 'CMS', 'measure' => 'UNIT'],
        ])->mapWithKeys(fn ($row) => [$row['code'] => Product::firstOrCreate(['code' => $row['code']], [...$row, 'is_active' => true])]);

        // Relasi bawaan hanya untuk divisi baru; pengaturan administrator tetap utuh.
        if ($konsumer->wasRecentlyCreated) $konsumer->products()->sync($products->only(['tabungan', 'deposito', 'bale-syariah', 'qris', 'cms'])->pluck('id'));
        if ($komersil->wasRecentlyCreated) $komersil->products()->sync($products->only(['tabungan', 'giro', 'deposito', 'cms'])->pluck('id'));

        TargetScope::firstOrCreate(['code' => 'konsumer'], ['division_id' => $konsumer->id, 'label' => 'Konsumer']);
        TargetScope::firstOrCreate(['code' => 'komersil'], ['division_id' => $komersil->id, 'label' => 'Komersil']);
        TargetScope::firstOrCreate(['code' => 'shared'], ['division_id' => null, 'label' => 'Bersama']);

        // Akun dengan kredensial demo hanya boleh dibuat di pengembangan/pengujian.
        if (!app()->environment(['local', 'testing'])) {
            return;
        }

        foreach ([
            ['suci', 'Suci', $komersil->id, 'pic'],
            ['cacan', 'Cacan', $komersil->id, 'pic'],
            ['dharma', 'Dharma', $komersil->id, 'pic'],
            ['nisa', 'Nisa', $konsumer->id, 'pic'],
            ['head', 'Head Funding', null, 'head'],
        ] as [$username, $name, $divisionId, $role]) {
            User::firstOrCreate(['username' => $username], [
                'name' => $name, 'division_id' => $divisionId, 'role' => $role,
                'password' => Hash::make('demo123'), 'is_active' => true,
            ]);
        }
    }
}
