<?php

namespace Tests\Feature;

use App\Models\User;
use App\Models\Product;
use Database\Seeders\DatabaseSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Laravel\Sanctum\Sanctum;
use Tests\TestCase;

class ReportReliabilityTest extends TestCase
{
    use RefreshDatabase;

    public function test_team_totals_do_not_include_previous_division_after_pic_transfer(): void
    {
        $this->seed(DatabaseSeeder::class);
        $suci = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($suci);
        $this->postJson('/api/opportunities', [
            'pic_id' => $suci->id, 'product_id' => Product::where('code', 'tabungan')->value('id'),
            'customer_name' => 'Private commercial', 'segment' => 'Mid', 'nominal' => 1000,
            'interest_status' => 'Hot', 'recorded_date' => today()->format('Y-m-d'),
        ])->assertCreated();
        $nisa = User::where('username', 'nisa')->firstOrFail();
        $suci->update(['division_id' => $nisa->division_id]);
        Sanctum::actingAs($nisa);
        $row = collect($this->getJson('/api/team')->assertOk()->json())->firstWhere('id', $suci->id);
        $this->assertSame(0, $row['total_pipeline']);
        $this->assertSame(0, $row['active_pipeline']);
        $this->assertSame(0, $row['active_nominal']);
        Sanctum::actingAs(User::where('username', 'head')->firstOrFail());
        $row = collect($this->getJson('/api/team')->assertOk()->json())->firstWhere('id', $suci->id);
        $this->assertSame(1, $row['total_pipeline']);
        $this->assertSame(1000, $row['active_nominal']);
    }

    public function test_exact_amounts_can_exceed_php_int64_without_overflow(): void
    {
        $this->assertSame('9223372036854775809', \App\Support\ExactAmount::sum(['9223372036854775807', '2']));
        $this->assertSame(9007199254740991, \App\Support\ExactAmount::remaining('9007199254740993', 2));
    }

    public function test_closing_target_and_trend_aggregates_keep_exact_values(): void
    {
        $this->seed(DatabaseSeeder::class);
        $user = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($user);
        foreach ([9007199254740991, 2] as $nominal) {
            $id = $this->postJson('/api/opportunities', [
                'pic_id' => $user->id, 'product_id' => Product::where('code', 'tabungan')->value('id'),
                'customer_name' => 'Exact total', 'segment' => 'Mid', 'nominal' => $nominal,
                'interest_status' => 'Hot', 'recorded_date' => today()->format('Y-m-d'),
            ])->assertCreated()->json('id');
            $this->postJson('/api/opportunities/'.$id.'/closing', ['version' => 1, 'outcome' => 'Won', 'closed_date' => today()->format('Y-m-d'), 'realization' => $nominal])->assertOk();
        }
        Sanctum::actingAs(User::where('username', 'head')->firstOrFail());
        foreach (['komersil' => 9007199254740991, 'konsumer' => 2] as $scope => $amount) {
            $this->putJson('/api/targets/'.$scope.'/tabungan/'.today()->year, ['version' => 0, 'target_value' => $amount])->assertOk();
        }
        $this->getJson('/api/dashboard?year='.today()->year)->assertOk()
            ->assertJsonPath('realization', '9007199254740993')->assertJsonPath('total_target', '9007199254740993')
            ->assertJsonPath('summary.0.target', '9007199254740993')->assertJsonPath('summary.0.remaining', 0)
            ->assertJsonPath('trend.'.(today()->month - 1).'.realization', '9007199254740993')
            ->assertJsonPath('trend.'.(today()->month - 1).'.recorded_nominal', '9007199254740993');
    }

    public function test_large_aggregates_are_serialized_as_exact_decimal_strings(): void
    {
        $this->seed(DatabaseSeeder::class);
        $user = User::where('username', 'suci')->firstOrFail();
        Sanctum::actingAs($user);
        foreach ([9007199254740991, 2] as $nominal) {
            $this->postJson('/api/opportunities', [
                'pic_id' => $user->id, 'product_id' => Product::where('code', 'tabungan')->value('id'),
                'customer_name' => 'Audit', 'segment' => 'Mid', 'nominal' => $nominal,
                'interest_status' => 'Hot', 'recorded_date' => today()->format('Y-m-d'),
            ])->assertCreated()->assertJsonPath('version', 1);
        }
        $response = $this->getJson('/api/dashboard?year='.today()->year)->assertOk();
        $this->assertSame('9007199254740993', $response->json('active_nominal'));
        $this->getJson('/api/team')->assertOk()->assertJsonPath('0.active_nominal', '9007199254740993');
        $this->assertStringContainsString('"active_nominal":"9007199254740993"', $response->getContent());
    }

    public function test_daily_report_uses_recorded_and_closing_dates_and_respects_division(): void
    {
        $this->seed(DatabaseSeeder::class);
        $suci = User::where('username', 'suci')->firstOrFail();
        $nisa = User::where('username', 'nisa')->firstOrFail();
        $product = Product::where('code', 'tabungan')->value('id');
        foreach ([[$suci, 120], [$nisa, 500]] as [$user, $amount]) {
            Sanctum::actingAs($user);
            $id = $this->postJson('/api/opportunities', [
                'pic_id' => $user->id, 'product_id' => $product,
                'customer_name' => 'Daily report', 'segment' => 'Mid', 'nominal' => $amount,
                'interest_status' => 'Hot', 'recorded_date' => '2024-02-28',
            ])->assertCreated()->json('id');
            $this->postJson('/api/opportunities/'.$id.'/closing', [
                'version' => 1, 'outcome' => 'Won', 'closed_date' => '2024-02-29', 'realization' => $amount,
            ])->assertOk();
        }
        Sanctum::actingAs($suci);
        $response = $this->getJson('/api/dashboard?year=2024')->assertOk()->assertJsonCount(366, 'daily');
        $response->assertJsonPath('daily.58.date', '2024-02-28')
            ->assertJsonPath('daily.58.recorded_nominal', 120)
            ->assertJsonPath('daily.58.realization', 0)
            ->assertJsonPath('daily.59.date', '2024-02-29')
            ->assertJsonPath('daily.59.recorded_nominal', 0)
            ->assertJsonPath('daily.59.realization', 120);
    }

    public function test_production_reseed_preserves_disabled_products_and_custom_relations(): void
    {
        $this->seed(DatabaseSeeder::class);
        Product::where('code', 'qris')->update(['is_active' => false]);
        \App\Models\Division::where('code', 'konsumer')->firstOrFail()->products()->detach(Product::where('code', 'qris')->value('id'));
        $this->app['env'] = 'production';
        $this->artisan('db:seed', ['--class' => DatabaseSeeder::class, '--force' => true])->assertSuccessful();
        $this->assertDatabaseHas('products', ['code' => 'qris', 'is_active' => false]);
        $this->assertFalse(\App\Models\Division::where('code', 'konsumer')->firstOrFail()->products()->where('code', 'qris')->exists());
    }
}
