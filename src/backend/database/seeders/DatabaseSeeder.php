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
        $konsumer = Division::updateOrCreate(['code' => 'konsumer'], ['name' => 'Konsumer']);
        $komersil = Division::updateOrCreate(['code' => 'komersil'], ['name' => 'Komersil']);

        $products = collect([
            ['code' => 'tabungan', 'name' => 'Tabungan', 'measure' => 'IDR'],
            ['code' => 'giro', 'name' => 'Giro', 'measure' => 'IDR'],
            ['code' => 'deposito', 'name' => 'Deposito', 'measure' => 'IDR'],
            ['code' => 'bale-syariah', 'name' => 'Bale Syariah', 'measure' => 'UNIT'],
            ['code' => 'qris', 'name' => 'QRIS', 'measure' => 'UNIT'],
            ['code' => 'cms', 'name' => 'CMS', 'measure' => 'UNIT'],
        ])->mapWithKeys(fn ($row) => [$row['code'] => Product::updateOrCreate(['code' => $row['code']], [...$row, 'is_active' => true])]);

        $konsumer->products()->sync($products->only(['tabungan', 'deposito', 'bale-syariah', 'qris', 'cms'])->pluck('id'));
        $komersil->products()->sync($products->only(['tabungan', 'giro', 'deposito', 'cms'])->pluck('id'));

        TargetScope::updateOrCreate(['code' => 'konsumer'], ['division_id' => $konsumer->id, 'label' => 'Konsumer']);
        TargetScope::updateOrCreate(['code' => 'komersil'], ['division_id' => $komersil->id, 'label' => 'Komersil']);
        TargetScope::updateOrCreate(['code' => 'shared'], ['division_id' => null, 'label' => 'Bersama']);

        foreach ([
            ['suci', 'Suci', $komersil->id, 'pic'],
            ['cacan', 'Cacan', $komersil->id, 'pic'],
            ['dharma', 'Dharma', $komersil->id, 'pic'],
            ['nisa', 'Nisa', $konsumer->id, 'pic'],
            ['head', 'Head Funding', null, 'head'],
        ] as [$username, $name, $divisionId, $role]) {
            User::updateOrCreate(['username' => $username], [
                'name' => $name, 'division_id' => $divisionId, 'role' => $role,
                'password' => Hash::make('demo123'), 'is_active' => true,
            ]);
        }
    }
}
