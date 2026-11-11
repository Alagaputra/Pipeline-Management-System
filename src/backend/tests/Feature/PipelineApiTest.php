<?php

namespace Tests\Feature;

use App\Models\AuditEvent;
use App\Models\Division;
use App\Models\Opportunity;
use App\Models\Product;
use App\Models\User;
use Database\Seeders\DatabaseSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Laravel\Sanctum\Sanctum;
use Tests\TestCase;

class PipelineApiTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(DatabaseSeeder::class);
    }

    public function test_login_returns_token_and_user_scope(): void
    {
        $this->postJson('/api/login', ['username' => 'nisa', 'password' => 'demo123'])
            ->assertOk()->assertJsonPath('user.division.code', 'konsumer')->assertJsonStructure(['token']);

        $this->postJson('/api/login', ['username' => 'nisa', 'password' => 'salah'])->assertUnprocessable();
    }

    public function test_unauthenticated_api_request_returns_json_401(): void
    {
        $this->get('/api/divisions')
            ->assertUnauthorized()
            ->assertJson(['message' => 'Unauthenticated.']);
    }

    public function test_consumer_cannot_create_giro_or_use_commercial_pic(): void
    {
        $nisa = User::where('username', 'nisa')->firstOrFail();
        Sanctum::actingAs($nisa);
        $payload = $this->opportunityPayload([
            'pic_id' => User::where('username', 'suci')->value('id'),
            'product_id' => Product::where('code', 'giro')->value('id'),
        ]);
        $this->postJson('/api/opportunities', $payload)->assertUnprocessable();
        $this->assertDatabaseCount('opportunities', 0);
    }

    public function test_opportunity_can_be_created_closed_won_and_audited(): void
    {
        $suci = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($suci);
        $response = $this->postJson('/api/opportunities', $this->opportunityPayload([
            'pic_id' => $suci->id,
            'product_id' => Product::where('code', 'tabungan')->value('id'),
        ]))->assertCreated();
        $id = $response->json('id');
        $this->postJson("/api/opportunities/{$id}/closing", [
            'outcome' => 'Won', 'realization' => 700000000, 'closed_date' => now()->format('Y-m-d'), 'version' => 1,
        ])->assertOk()->assertJsonPath('outcome', 'Won')->assertJsonPath('version', 2);
        $this->assertDatabaseHas('opportunities', ['id' => $id, 'realization' => 700000000, 'outcome' => 'Won']);
        $this->assertDatabaseCount('audit_events', 2);
        $this->patchJson("/api/opportunities/{$id}", [...$this->opportunityPayload(), 'version' => 2])->assertConflict();
    }

    public function test_closing_won_above_potential_preserves_nominal_and_counts_full_realization(): void
    {
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
        $id = $this->postJson('/api/opportunities', $this->opportunityPayload())->assertCreated()->json('id');
        $this->postJson("/api/opportunities/{$id}/closing", [
            'outcome' => 'Won', 'realization' => 1200000000, 'closed_date' => today()->format('Y-m-d'), 'version' => 1,
        ])->assertOk()->assertJsonPath('outcome', 'Won')->assertJsonPath('version', 2);
        $this->assertDatabaseHas('opportunities', [
            'id' => $id, 'nominal' => 1000000000, 'realization' => 1200000000, 'outcome' => 'Won',
        ]);
        $this->getJson("/api/opportunities/{$id}")->assertOk()
            ->assertJsonPath('nominal', '1000000000')->assertJsonPath('realization', '1200000000');
        $closing = AuditEvent::where('resource_type', 'opportunity')->where('resource_id', (string) $id)
            ->where('action', 'closed_won')->firstOrFail();
        $this->assertSame('1000000000', $closing->before_data['nominal']);
        $this->assertSame('1000000000', $closing->after_data['nominal']);
        $this->assertSame('1200000000', $closing->after_data['realization']);
        $this->getJson('/api/dashboard?year='.today()->year)->assertOk()
            ->assertJsonPath('realization', 1200000000)->assertJsonPath('active_opportunities', 0);
    }

    public function test_closing_won_still_rejects_missing_zero_negative_fractional_and_non_numeric_realization(): void
    {
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
        $id = $this->postJson('/api/opportunities', $this->opportunityPayload())->assertCreated()->json('id');
        $payload = ['outcome' => 'Won', 'closed_date' => today()->format('Y-m-d'), 'version' => 1];
        $this->postJson("/api/opportunities/{$id}/closing", $payload)->assertUnprocessable();
        foreach ([null, 0, -1, 1.5, 'abc'] as $realization) {
            $this->postJson("/api/opportunities/{$id}/closing", [...$payload, 'realization' => $realization])->assertUnprocessable();
        }
        $this->assertDatabaseHas('opportunities', [
            'id' => $id, 'nominal' => 1000000000, 'realization' => 0, 'outcome' => 'Active', 'version' => 1,
        ]);
        $this->assertDatabaseCount('audit_events', 1);
    }

    public function test_shared_cms_target_is_one_record_for_both_divisions(): void
    {
        $monthly = collect(range(1, 12))->map(fn ($month) => ['month' => $month, 'target_value' => $month === 1 ? 10 : 0])->all();
        $suci = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($suci);
        $this->putJson('/api/targets/shared/cms/2026', ['target_value' => 120, 'monthly' => $monthly, 'version' => 0])->assertOk();
        $nisa = User::where('username', 'nisa')->firstOrFail();
        Sanctum::actingAs($nisa);
        $this->getJson('/api/targets?scope=shared&year=2026')->assertOk()->assertJsonCount(1)->assertJsonPath('0.target_value', '120');
        $this->putJson('/api/unit-realizations/shared/cms/2026/1', ['units' => 9, 'version' => 0])->assertOk()->assertJsonPath('units', 9);
        $this->assertDatabaseCount('annual_targets', 1);
    }

    public function test_dashboard_counts_only_scoped_won_by_closing_year_and_reports_monthly_values(): void
    {
        $this->travelTo(\Illuminate\Support\Carbon::parse('2026-10-13 12:00:00'));
        $suci = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($suci);
        $product = Product::where('code', 'tabungan')->firstOrFail();
        $this->putJson('/api/targets/komersil/tabungan/2026', ['target_value' => 1000000000, 'version' => 0])->assertOk();
        $base = [...$this->opportunityPayload(), 'division_id' => $suci->division_id];
        Opportunity::create([...$base, 'outcome' => 'Won', 'recorded_date' => '2025-12-01', 'closed_date' => '2026-02-01', 'realization' => 700000000]);
        Opportunity::create([...$base, 'outcome' => 'Lost', 'closed_date' => '2026-02-02', 'realization' => 0]);
        Opportunity::create([...$base, 'outcome' => 'Won', 'closed_date' => '2025-12-31', 'realization' => 300000000]);
        Opportunity::create([...$base, 'outcome' => 'Active', 'recorded_date' => '2026-03-01', 'follow_up_date' => '2026-10-12']);
        $nisa = User::where('username', 'nisa')->firstOrFail();
        Opportunity::create([...$base, 'division_id' => $nisa->division_id, 'pic_id' => $nisa->id,
            'outcome' => 'Won', 'closed_date' => '2026-02-01', 'realization' => 900000000]);
        $this->getJson('/api/dashboard?year=2026&division_id='.$nisa->division_id)->assertOk()
            ->assertJsonPath('realization', 700000000)->assertJsonPath('total_target', 1000000000)
            ->assertJsonPath('percentage', 70)->assertJsonPath('active_opportunities', 1)
            ->assertJsonPath('hot_opportunities', 1)->assertJsonPath('follow_up_count', 1)
            ->assertJsonPath('interest.Hot', 1)->assertJsonPath('interest.Cold', 0)
            ->assertJsonPath('trend.1.realization', 700000000)
            ->assertJsonPath('trend.2.recorded_nominal', 1000000000)
            ->assertJsonPath('trend.10.recorded_nominal', null)
            ->assertJsonPath('summary.0.remaining', 300000000);
        Sanctum::actingAs(User::where('username', 'head')->firstOrFail());
        $this->getJson('/api/dashboard?year=2026')->assertOk()->assertJsonPath('realization', 1600000000);
        $this->getJson('/api/dashboard?year=2026&division_id='.$nisa->division_id)->assertOk()
            ->assertJsonPath('realization', 900000000)->assertJsonCount(2, 'summary');
    }

    public function test_timeline_contains_actor_changes_and_closing_and_is_hidden_from_other_division(): void
    {
        $suci = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($suci);
        $id = $this->postJson('/api/opportunities', $this->opportunityPayload())->assertCreated()->json('id');
        $this->patchJson("/api/opportunities/{$id}", [...$this->opportunityPayload(), 'interest_status' => 'Warm', 'notes' => 'Nasabah meminta penawaran', 'version' => 1])->assertOk();
        $this->postJson("/api/opportunities/{$id}/closing", ['outcome' => 'Lost', 'closed_date' => today()->format('Y-m-d'), 'lost_reason' => 'Belum disetujui', 'version' => 2])->assertOk();
        $this->getJson("/api/opportunities/{$id}")->assertOk()->assertJsonCount(3, 'timeline')
            ->assertJsonPath('timeline.0.actor.name', 'Suci')
            ->assertJsonPath('timeline.1.before_data.interest_status', 'Hot')
            ->assertJsonPath('timeline.1.after_data.interest_status', 'Warm')
            ->assertJsonPath('timeline.2.action', 'closed_lost');
        Sanctum::actingAs(User::where('username', 'nisa')->firstOrFail());
        $this->getJson("/api/opportunities/{$id}")->assertNotFound();
    }

    public function test_new_follow_up_schedule_resets_completion_and_validates_dates(): void
    {
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
        $payload = $this->opportunityPayload();
        $id = $this->postJson('/api/opportunities', $payload)->assertCreated()->json('id');
        $this->postJson("/api/opportunities/{$id}/follow-up-completion", ['version' => 1])->assertOk();
        $this->patchJson("/api/opportunities/{$id}", [...$payload, 'follow_up_date' => today()->addDays(2)->format('Y-m-d'), 'version' => 2])
            ->assertOk()->assertJsonPath('follow_up_completed', false);
        $this->patchJson("/api/opportunities/{$id}", [...$payload, 'follow_up_date' => today()->subDays(5)->format('Y-m-d'), 'version' => 3])->assertUnprocessable();
    }

    public function test_annual_only_target_update_preserves_existing_monthly_records(): void
    {
        Sanctum::actingAs(User::where('username', 'suci')->firstOrFail());
        $monthly = collect(range(1, 12))->map(fn ($month) => ['month' => $month, 'target_value' => 100])->all();
        $this->putJson('/api/targets/komersil/tabungan/2026', ['target_value' => 1000, 'monthly' => $monthly, 'version' => 0])->assertOk();
        $this->putJson('/api/targets/komersil/tabungan/2026', ['target_value' => 2000, 'version' => 1])->assertOk()
            ->assertJsonPath('target_value', '2000')->assertJsonCount(12, 'monthly_targets');
        $this->assertDatabaseHas('monthly_targets', ['month' => 1, 'target_value' => 100]);
        $this->getJson('/api/dashboard?year=1999')->assertUnprocessable();
    }

    private function opportunityPayload(array $replace = []): array
    {
        $division = Division::where('code', 'komersil')->first();
        return array_replace([
            'division_id' => $division?->id,
            'pic_id' => User::where('username', 'suci')->value('id'),
            'product_id' => Product::where('code', 'tabungan')->value('id'),
            'customer_name' => 'PT Contoh', 'segment' => 'Mid', 'nominal' => 1000000000,
            'interest_status' => 'Hot', 'recorded_date' => now()->subDay()->format('Y-m-d'),
            'follow_up_date' => now()->addDay()->format('Y-m-d'), 'notes' => 'Uji API',
        ], $replace);
    }
}
