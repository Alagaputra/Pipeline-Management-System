<?php

namespace Tests\Feature;

use App\Models\User;
use Database\Seeders\DatabaseSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AuthenticationSecurityTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(DatabaseSeeder::class);
    }

    private function requestWithToken(string $token, string $method, string $url, array $data = [], array $headers = [])
    {
        // RequestGuard menyimpan pengguna selama satu request; simulasi request baru.
        $this->app['auth']->forgetGuards();

        return $this->json($method, $url, $data, ['Authorization' => 'Bearer '.$token, ...$headers]);
    }

    public function test_deactivation_immediately_revokes_all_tokens_and_reactivation_does_not_restore_them(): void
    {
        $user = User::where('username', 'suci')->firstOrFail();
        $token = $user->createToken('existing')->plainTextToken;
        $user->createToken('other-device');
        $this->requestWithToken($token, 'GET', '/api/me')->assertOk();

        $user->update(['is_active' => false]);
        $this->assertDatabaseCount('personal_access_tokens', 0);
        $this->requestWithToken($token, 'GET', '/api/me')->assertUnauthorized();
        $this->postJson('/api/login', ['username' => 'suci', 'password' => 'demo123'])->assertUnprocessable();

        $user->update(['is_active' => true]);
        $this->requestWithToken($token, 'GET', '/api/me')->assertUnauthorized();
    }

    public function test_direct_database_deactivation_blocks_reads_and_revokes_tokens(): void
    {
        $user = User::where('username', 'suci')->firstOrFail();
        $token = $user->createToken('existing')->plainTextToken;
        $user->createToken('other-device');
        User::whereKey($user->id)->update(['is_active' => false]);

        $this->requestWithToken($token, 'GET', '/api/me')->assertUnauthorized();
        $this->assertDatabaseCount('personal_access_tokens', 0);
    }

    public function test_inactive_account_cannot_replay_successful_writes(): void
    {
        $user = User::where('username', 'suci')->firstOrFail();
        $token = $user->createToken('existing')->plainTextToken;
        $headers = ['Idempotency-Key' => 'd177e937-8f5e-42d0-96ed-5fb77922d077'];
        $payload = ['target_value' => 100, 'version' => 0];
        $url = '/api/targets/komersil/tabungan/2026';
        $this->requestWithToken($token, 'PUT', $url, $payload, $headers)->assertOk();
        User::whereKey($user->id)->update(['is_active' => false]);

        $this->requestWithToken($token, 'PUT', $url, $payload, $headers)->assertUnauthorized();
        $this->assertDatabaseHas('annual_targets', ['target_value' => 100, 'version' => 1]);
        $this->assertDatabaseCount('audit_events', 1);
        $this->assertDatabaseCount('personal_access_tokens', 0);
    }

    public function test_login_issues_expiring_token_and_rejects_it_after_expiration(): void
    {
        $this->travelTo(now()->startOfSecond());
        $response = $this->postJson('/api/login', ['username' => 'suci', 'password' => 'demo123'])->assertOk();
        $token = $response->json('token');
        $expiresAt = now()->addMinutes(config('sanctum.expiration'));
        $this->assertSame($expiresAt->toIso8601String(), $response->json('expires_at'));
        $this->assertTrue(User::where('username', 'suci')->firstOrFail()->tokens()->firstOrFail()->expires_at->equalTo($expiresAt));
        $this->requestWithToken($token, 'GET', '/api/me')->assertOk();

        $this->travel(config('sanctum.expiration') + 1)->minutes();
        $this->requestWithToken($token, 'GET', '/api/me')->assertUnauthorized();
    }

    public function test_legacy_tokens_without_expires_at_are_also_limited_by_age(): void
    {
        $token = User::where('username', 'suci')->firstOrFail()->createToken('legacy')->plainTextToken;
        $this->requestWithToken($token, 'GET', '/api/me')->assertOk();
        $this->travel(config('sanctum.expiration') + 1)->minutes();
        $this->requestWithToken($token, 'GET', '/api/me')->assertUnauthorized();
    }

    public function test_new_login_and_logout_revoke_previous_tokens(): void
    {
        $credentials = ['username' => 'suci', 'password' => 'demo123'];
        $old = $this->postJson('/api/login', $credentials)->assertOk()->json('token');
        $new = $this->postJson('/api/login', $credentials)->assertOk()->json('token');
        $this->requestWithToken($old, 'GET', '/api/me')->assertUnauthorized();
        $this->requestWithToken($new, 'GET', '/api/me')->assertOk();
        $this->requestWithToken($new, 'POST', '/api/logout')->assertNoContent();
        $this->requestWithToken($new, 'GET', '/api/me')->assertUnauthorized();
    }
}
