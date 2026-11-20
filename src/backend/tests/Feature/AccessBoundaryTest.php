<?php

namespace Tests\Feature;

use App\Models\Division;
use App\Models\Opportunity;
use App\Models\Product;
use App\Models\User;
use Database\Seeders\DatabaseSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Laravel\Sanctum\Sanctum;
use Tests\TestCase;

class AccessBoundaryTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(DatabaseSeeder::class);
    }

    private function payload(array $replace = []): array
    {
        $pic = User::where('username', 'suci')->firstOrFail();
        return [...[
            'division_id' => $pic->division_id, 'pic_id' => $pic->id,
            'product_id' => Product::where('code', 'tabungan')->value('id'),
            'customer_name' => 'Private commercial customer', 'segment' => 'Mid', 'nominal' => 1000,
            'interest_status' => 'Hot', 'recorded_date' => today()->format('Y-m-d'),
            'follow_up_date' => today()->format('Y-m-d'), 'notes' => 'Private notes',
        ], ...$replace];
    }

    private function tokenRequest(string $token, string $method, string $url, array $payload = [], array $headers = [])
    {
        $this->app['auth']->forgetGuards();
        return $this->json($method, $url, $payload, ['Authorization' => 'Bearer '.$token, ...$headers]);
    }

    public function test_moved_pic_history_hides_opportunities_from_previous_division(): void
    {
        $suci = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($suci);
        $id = $this->postJson('/api/opportunities', $this->payload())->assertCreated()->json('id');
        $suci->update(['division_id' => Division::where('code', 'konsumer')->value('id')]);
        Opportunity::whereKey($id)->update(['notes' => 'New confidential commercial update after transfer']);
        Sanctum::actingAs(User::where('username', 'nisa')->firstOrFail());

        $this->getJson('/api/opportunities/'.$id)->assertNotFound();
        $this->getJson('/api/pics/'.$suci->id.'/opportunities')->assertOk()
            ->assertJsonCount(0, 'data');
    }

    public function test_receipt_replay_rejects_changed_division_even_with_new_token(): void
    {
        $suci = User::where('username', 'suci')->firstOrFail();
        $token = $suci->createToken('review')->plainTextToken;
        $payload = $this->payload();
        $headers = ['Idempotency-Key' => 'c3cd684c-c398-4b6b-9d37-4b7f26ab8c14'];
        $id = $this->tokenRequest($token, 'POST', '/api/opportunities', $payload)->assertCreated()->json('id');
        $payload['version'] = 1;
        $url = '/api/opportunities/'.$id;
        $this->tokenRequest($token, 'PATCH', $url, $payload, $headers)->assertOk()->assertJsonPath('version', 2);
        $suci->update(['division_id' => Division::where('code', 'konsumer')->value('id')]);
        $this->assertDatabaseCount('personal_access_tokens', 0);
        $this->tokenRequest($token, 'GET', '/api/me')->assertUnauthorized();
        $token = $suci->createToken('new-scope')->plainTextToken;

        $this->tokenRequest($token, 'GET', '/api/opportunities/'.$id)->assertNotFound();
        $this->tokenRequest($token, 'PATCH', $url, $payload, $headers)->assertConflict();
        $this->tokenRequest($token, 'PATCH', $url, $payload, [
            'Idempotency-Key' => '8a83ef25-0508-489f-b043-66e4c783c267',
        ])->assertNotFound();
        $this->assertDatabaseCount('opportunities', 1);
    }

    public function test_pic_without_division_cannot_login_or_access_dashboard(): void
    {
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
        $commercial = $this->postJson('/api/opportunities', $this->payload())->assertCreated()->json('id');
        $nisa = User::where('username', 'nisa')->firstOrFail();
        Sanctum::actingAs($nisa);
        $consumer = $this->postJson('/api/opportunities', $this->payload([
            'division_id' => $nisa->division_id, 'pic_id' => $nisa->id, 'customer_name' => 'Private consumer customer',
        ]))->assertCreated()->json('id');
        $pic = User::create(['username' => 'unassigned-pic', 'name' => 'Unassigned', 'role' => 'pic', 'password' => 'review-password', 'is_active' => true]);
        $this->postJson('/api/login', ['username' => $pic->username, 'password' => 'review-password'])->assertUnauthorized();
        $token = $pic->createToken('invalid-access')->plainTextToken;

        $this->tokenRequest($token, 'GET', '/api/dashboard?year='.today()->year)->assertUnauthorized();
        $this->assertDatabaseCount('personal_access_tokens', 0);
    }

    public function test_inactive_unit_product_rejects_realization_writes(): void
    {
        Sanctum::actingAs(User::where('username', 'nisa')->firstOrFail());
        Product::where('code', 'qris')->update(['is_active' => false]);
        $this->getJson('/api/products')->assertOk()->assertJsonMissing(['code' => 'qris']);
        $this->putJson('/api/targets/konsumer/qris/2026', ['target_value' => 10, 'version' => 0])->assertNotFound();
        $this->putJson('/api/unit-realizations/konsumer/qris/2026/1', ['units' => 9, 'version' => 0])
            ->assertNotFound();
        $this->assertDatabaseCount('unit_realizations', 0);
        $this->assertDatabaseCount('audit_events', 0);
    }

    public function test_oversized_integer_is_rejected_and_maximum_is_accepted(): void
    {
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
        $this->postJson('/api/opportunities', $this->payload(['nominal' => '9007199254740993']))
            ->assertUnprocessable()->assertJsonValidationErrors('nominal');
        $this->postJson('/api/opportunities', $this->payload(['nominal' => '9007199254740991']))
            ->assertCreated()->assertJsonPath('nominal', '9007199254740991');
    }

    public function test_target_batch_rejects_other_division_without_receipt(): void
    {
        Sanctum::actingAs(User::where('username', 'nisa')->firstOrFail());
        $this->postJson('/api/targets/batch', ['scope' => 'komersil', 'year' => 2026,
            'targets' => [['product' => 'tabungan', 'target_value' => 1, 'version' => 0]],
        ])->assertForbidden();
        $this->assertDatabaseCount('annual_targets', 0);
    }

    public function test_legacy_receipt_cannot_be_replayed_or_execute_again(): void
    {
        $user = User::where('username', 'suci')->firstOrFail();
        $token = $user->createToken('review')->plainTextToken;
        $headers = ['Idempotency-Key' => '0d0fa989-b218-4e0f-8408-2f3f7e137be4'];
        $payload = $this->payload();
        $this->tokenRequest($token, 'POST', '/api/opportunities', $payload, $headers)->assertCreated();
        \Illuminate\Support\Facades\DB::table('request_receipts')->update(['authorization_context' => null]);
        $this->tokenRequest($token, 'POST', '/api/opportunities', $payload, $headers)->assertConflict();
        $this->assertDatabaseCount('opportunities', 1);
        $this->assertDatabaseCount('audit_events', 1);
    }

    public function test_role_downgrade_revokes_tokens_and_rejects_old_receipts(): void
    {
        $head = User::where('username', 'head')->firstOrFail();
        $token = $head->createToken('head')->plainTextToken;
        $headers = ['Idempotency-Key' => 'ce6e9308-af1d-410c-9c5e-7dc54abb85f3'];
        $payload = $this->payload();
        $this->tokenRequest($token, 'POST', '/api/opportunities', $payload, $headers)->assertCreated();
        $head->update(['role' => 'pic', 'division_id' => Division::where('code', 'komersil')->value('id')]);
        $this->assertDatabaseCount('personal_access_tokens', 0);
        $this->tokenRequest($token, 'GET', '/api/me')->assertUnauthorized();
        $newToken = $head->createToken('pic')->plainTextToken;
        $this->tokenRequest($newToken, 'POST', '/api/opportunities', $payload, $headers)->assertConflict();
        $this->assertDatabaseCount('opportunities', 1);
    }

    public function test_unknown_role_is_rejected_on_login_and_protected_requests(): void
    {
        $user = User::where('username', 'suci')->firstOrFail();
        $user->update(['role' => 'unknown']);
        $token = $user->createToken('invalid-role')->plainTextToken;
        $this->tokenRequest($token, 'GET', '/api/dashboard')->assertUnauthorized();
        $this->postJson('/api/login', ['username' => 'suci', 'password' => 'demo123'])->assertUnauthorized();
        $this->assertDatabaseCount('personal_access_tokens', 0);
    }

    public function test_numeric_limits_cover_closing_targets_monthly_and_units(): void
    {
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
        $max = 9007199254740991;
        $id = $this->postJson('/api/opportunities', $this->payload())->assertCreated()->json('id');
        $closing = ['outcome' => 'Won', 'closed_date' => today()->format('Y-m-d'), 'version' => 1];
        $this->postJson('/api/opportunities/'.$id.'/closing', [...$closing, 'realization' => $max + 1])->assertUnprocessable();
        $this->postJson('/api/opportunities/'.$id.'/closing', [...$closing, 'realization' => $max])->assertOk();
        $this->putJson('/api/targets/komersil/tabungan/2026', ['target_value' => $max + 1, 'version' => 0])->assertUnprocessable();
        $this->putJson('/api/targets/komersil/tabungan/2026', ['target_value' => $max, 'version' => 0])->assertOk();
        $this->putJson('/api/branch-targets/komersil/bekasi/2026', ['target_value' => $max + 1, 'version' => 0])->assertUnprocessable();
        $this->putJson('/api/unit-realizations/shared/cms/2026/1', ['units' => $max + 1, 'version' => 0])->assertUnprocessable();
        $this->putJson('/api/unit-realizations/shared/cms/2026/1', ['units' => $max, 'version' => 0])->assertOk();
        $payload = ['scope' => 'shared', 'year' => 2026, 'targets' => [[
            'product' => 'cms', 'target_value' => $max, 'version' => 1,
            'monthly' => array_map(fn ($month) => ['month' => $month, 'target_value' => 0, 'units' => 0, 'version' => $month === 1 ? 1 : 0], range(1, 12)),
        ]]];
        foreach (['target_value', 'units'] as $field) {
            $invalid = $payload;
            $invalid['targets'][0]['monthly'][0][$field] = $max + 1;
            $this->postJson('/api/targets/batch', $invalid)->assertUnprocessable();
        }
        $this->postJson('/api/targets/batch', $payload)->assertOk();
    }
}
