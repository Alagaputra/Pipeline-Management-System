<?php

namespace Tests\Feature;

use App\Models\User;
use Database\Seeders\DatabaseSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class SeederSecurityTest extends TestCase
{
    use RefreshDatabase;

    public function test_reseeding_preserves_existing_credentials_status_and_profile(): void
    {
        $this->seed(DatabaseSeeder::class);
        foreach (User::all() as $user) {
            $user->update(['password' => 'changed-password', 'is_active' => false, 'name' => 'Updated '.$user->username, 'role' => 'pic']);
        }
        $before = User::orderBy('id')->get()->map->getAttributes()->all();

        $this->seed(DatabaseSeeder::class);

        $this->assertSame($before, User::orderBy('id')->get()->map->getAttributes()->all());
        $this->assertDatabaseCount('users', 5);
        foreach (User::all() as $user) {
            $this->assertTrue(Hash::check('changed-password', $user->password));
            $this->assertFalse(Hash::check('demo123', $user->password));
        }
    }

    public function test_production_and_staging_seed_master_data_without_demo_accounts(): void
    {
        foreach (['production', 'staging'] as $environment) {
            $this->app['env'] = $environment;
            $this->artisan('db:seed', ['--class' => DatabaseSeeder::class, '--force' => true])->assertSuccessful();
            $this->assertDatabaseCount('users', 0);
            $this->assertDatabaseCount('divisions', 2);
            $this->assertDatabaseCount('products', 6);
            $this->assertDatabaseCount('target_scopes', 3);
        }
    }

    public function test_production_seed_preserves_existing_head_account(): void
    {
        $head = User::create(['username' => 'head', 'name' => 'Real Head', 'role' => 'head', 'password' => 'production-password', 'is_active' => false]);
        $before = $head->refresh()->getAttributes();
        $this->app['env'] = 'production';

        $this->artisan('db:seed', ['--class' => DatabaseSeeder::class, '--force' => true])->assertSuccessful();

        $this->assertSame($before, $head->fresh()->getAttributes());
        $this->assertDatabaseCount('users', 1);
    }
}
