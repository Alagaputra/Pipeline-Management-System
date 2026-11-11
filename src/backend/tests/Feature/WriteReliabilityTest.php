<?php

namespace Tests\Feature;

use App\Models\AnnualTarget;
use App\Models\Opportunity;
use App\Models\Product;
use App\Models\User;
use Database\Seeders\DatabaseSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Str;
use Laravel\Sanctum\Sanctum;
use Tests\TestCase;

class WriteReliabilityTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(DatabaseSeeder::class);
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
    }

    private function opportunity(): array
    {
        $pic = User::where('username', 'suci')->firstOrFail();
        return [
            'division_id' => $pic->division_id, 'pic_id' => $pic->id,
            'product_id' => Product::where('code', 'tabungan')->value('id'),
            'customer_name' => 'PT Retry Aman', 'segment' => 'Mid', 'nominal' => 1000000000,
            'interest_status' => 'Hot', 'recorded_date' => today()->format('Y-m-d'),
            'follow_up_date' => today()->format('Y-m-d'), 'notes' => 'Catatan awal',
        ];
    }

    private function unitPayload(): array
    {
        return ['scope' => 'shared', 'year' => 2026, 'targets' => [[
            'product' => 'cms', 'target_value' => 120, 'version' => 0,
            'monthly' => array_map(fn ($month) => [
                'month' => $month, 'target_value' => 10, 'units' => $month === 1 ? 8 : 0, 'version' => 0,
            ], range(1, 12)),
        ]]];
    }

    public function test_create_retries_replay_success_without_duplicate_data_or_audit(): void
    {
        $headers = ['Idempotency-Key' => (string) Str::uuid()];
        $payload = $this->opportunity();
        $first = $this->postJson('/api/opportunities', $payload, $headers)->assertCreated();
        $this->postJson('/api/opportunities', $payload, $headers)->assertCreated()
            ->assertHeader('Idempotency-Replayed', 'true')->assertJsonPath('id', $first->json('id'));
        $this->postJson('/api/opportunities', [...$payload, 'customer_name' => 'Berbeda'], $headers)->assertConflict();
        $this->assertDatabaseCount('opportunities', 1);
        $this->assertDatabaseCount('opportunity_assignments', 1);
        $this->assertDatabaseCount('audit_events', 1);
        $this->assertDatabaseCount('request_receipts', 1);
    }

    public function test_closing_saves_notes_and_outcome_together_and_replays_without_extra_version(): void
    {
        $id = $this->postJson('/api/opportunities', $this->opportunity())->assertCreated()->json('id');
        $headers = ['Idempotency-Key' => (string) Str::uuid()];
        $payload = ['outcome' => 'Won', 'realization' => 700000000, 'closed_date' => today()->format('Y-m-d'),
            'notes' => 'Dana masuk sebagian', 'version' => 1];
        $this->postJson("/api/opportunities/{$id}/closing", [...$payload, 'realization' => 0], $headers)->assertUnprocessable();
        $this->assertDatabaseHas('opportunities', ['id' => $id, 'outcome' => 'Active', 'notes' => 'Catatan awal', 'version' => 1]);
        $this->assertDatabaseCount('request_receipts', 0);
        $this->postJson("/api/opportunities/{$id}/closing", $payload, $headers)->assertOk()->assertJsonPath('version', 2);
        $this->postJson("/api/opportunities/{$id}/closing", $payload, $headers)->assertOk()->assertHeader('Idempotency-Replayed', 'true');
        $this->assertDatabaseHas('opportunities', ['id' => $id, 'outcome' => 'Won', 'notes' => 'Dana masuk sebagian', 'version' => 2]);
        $this->assertDatabaseCount('audit_events', 2);
    }

    public function test_funding_batch_rolls_back_all_products_when_a_later_product_conflicts(): void
    {
        $this->putJson('/api/targets/komersil/tabungan/2026', ['target_value' => 100, 'version' => 0])->assertOk();
        $payload = ['scope' => 'komersil', 'year' => 2026, 'targets' => [
            ['product' => 'giro', 'target_value' => 200, 'version' => 0],
            ['product' => 'tabungan', 'target_value' => 300, 'version' => 0],
        ]];
        $this->postJson('/api/targets/batch', $payload, ['Idempotency-Key' => (string) Str::uuid()])->assertConflict();
        $this->assertDatabaseCount('annual_targets', 1);
        $this->assertDatabaseHas('annual_targets', ['target_value' => 100, 'version' => 1]);
        $this->assertDatabaseCount('audit_events', 1);
        $this->assertDatabaseCount('request_receipts', 0);
        $payload['targets'][1]['version'] = 1;
        $headers = ['Idempotency-Key' => (string) Str::uuid()];
        $this->postJson('/api/targets/batch', $payload, $headers)->assertOk()->assertJsonCount(2);
        $this->postJson('/api/targets/batch', $payload, $headers)->assertOk()->assertHeader('Idempotency-Replayed', 'true');
        $this->assertDatabaseCount('annual_targets', 2);
        $this->assertDatabaseCount('audit_events', 3);
    }

    public function test_unit_batch_rolls_back_annual_monthly_and_audit_changes_on_month_conflict(): void
    {
        $payload = $this->unitPayload();
        $headers = ['Idempotency-Key' => (string) Str::uuid()];
        $payload['targets'][0]['monthly'][11]['version'] = 1;
        $this->postJson('/api/targets/batch', $payload, $headers)->assertConflict();
        foreach (['annual_targets', 'monthly_targets', 'unit_realizations', 'audit_events', 'request_receipts'] as $table) {
            $this->assertDatabaseCount($table, 0);
        }
        $payload['targets'][0]['monthly'][11]['version'] = 0;
        $this->postJson('/api/targets/batch', $payload, $headers)->assertOk()->assertJsonPath('0.target_value', '120')
            ->assertJsonCount(12, '0.monthly_targets')->assertJsonCount(12, '0.unit_realizations');
        $this->postJson('/api/targets/batch', $payload, $headers)->assertOk()->assertHeader('Idempotency-Replayed', 'true');
        $this->assertDatabaseCount('audit_events', 13);
        $this->assertDatabaseCount('request_receipts', 1);

        $payload['targets'][0]['version'] = 1;
        $payload['targets'][0]['target_value'] = 999;
        foreach ($payload['targets'][0]['monthly'] as &$month) $month['version'] = 1;
        unset($month);
        $payload['targets'][0]['monthly'][11]['version'] = 0;
        $payload['targets'][0]['monthly'][0]['units'] = 9;
        $this->postJson('/api/targets/batch', $payload)->assertConflict();
        $this->assertDatabaseHas('annual_targets', ['target_value' => 120, 'version' => 1]);
        $this->assertDatabaseHas('unit_realizations', ['month' => 1, 'units' => 8, 'version' => 1]);
        $this->assertDatabaseCount('audit_events', 13);
        $payload['targets'][0]['monthly'][11]['version'] = 1;
        $this->postJson('/api/targets/batch', $payload)->assertOk();
        // Only the changed realization and annual target receive new audit events.
        $this->assertDatabaseCount('audit_events', 15);
    }

    public function test_batch_enforces_division_permissions_and_unique_months(): void
    {
        Sanctum::actingAs(User::where('username', 'nisa')->firstOrFail());
        $this->postJson('/api/targets/batch', ['scope' => 'komersil', 'year' => 2026, 'targets' => [
            ['product' => 'tabungan', 'target_value' => 100, 'version' => 0],
        ]])->assertForbidden();
        $this->postJson('/api/targets/batch', ['scope' => 'konsumer', 'year' => 2026, 'targets' => [
            ['product' => 'giro', 'target_value' => 100, 'version' => 0],
        ]])->assertUnprocessable();
        $payload = $this->unitPayload();
        $payload['targets'][0]['monthly'][11]['month'] = 1;
        $this->postJson('/api/targets/batch', $payload)->assertUnprocessable();
        $this->assertDatabaseCount('annual_targets', 0);
        $this->postJson('/api/targets/batch', $this->unitPayload())->assertOk();
        $this->assertSame('shared', AnnualTarget::sole()->scope_code);
    }

    public function test_legacy_small_records_remain_editable_without_accepting_new_small_records(): void
    {
        $payload = [...$this->opportunity(), 'segment' => 'Small'];
        $this->postJson('/api/opportunities', $payload)->assertUnprocessable();
        $legacy = Opportunity::create([...$payload, 'outcome' => 'Active', 'realization' => 0]);
        $this->patchJson("/api/opportunities/{$legacy->id}", [...$payload, 'version' => 1, 'notes' => 'Diperbarui'])
            ->assertOk()->assertJsonPath('segment', 'Small')->assertJsonPath('notes', 'Diperbarui');
    }
}
