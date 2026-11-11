<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->string('code', 40)->unique();
            $table->string('name', 80);
            $table->string('measure', 10);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
        });

        Schema::create('division_products', function (Blueprint $table) {
            $table->foreignId('division_id')->constrained()->cascadeOnDelete();
            $table->foreignId('product_id')->constrained()->cascadeOnDelete();
            $table->primary(['division_id', 'product_id']);
        });

        Schema::create('opportunities', function (Blueprint $table) {
            $table->id();
            $table->string('legacy_id')->nullable()->unique();
            $table->foreignId('division_id')->constrained()->restrictOnDelete();
            $table->foreignId('pic_id')->constrained('users')->restrictOnDelete();
            $table->foreignId('product_id')->constrained()->restrictOnDelete();
            $table->string('customer_name', 160);
            $table->string('segment', 20);
            $table->unsignedBigInteger('nominal');
            $table->string('interest_status', 10);
            $table->string('outcome', 10)->default('Active');
            $table->date('recorded_date');
            $table->date('follow_up_date')->nullable();
            $table->boolean('follow_up_completed')->default(false);
            $table->date('closed_date')->nullable();
            $table->unsignedBigInteger('realization')->default(0);
            $table->text('notes')->nullable();
            $table->text('lost_reason')->nullable();
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();
            $table->foreignId('updated_by')->nullable()->constrained('users')->nullOnDelete();
            $table->unsignedBigInteger('version')->default(1);
            $table->timestamps();
            $table->index(['division_id', 'outcome', 'updated_at']);
            $table->index(['pic_id', 'outcome', 'closed_date']);
        });

        Schema::create('opportunity_assignments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('opportunity_id')->constrained()->cascadeOnDelete();
            $table->foreignId('pic_id')->constrained('users')->restrictOnDelete();
            $table->dateTime('assigned_at')->nullable();
            $table->dateTime('unassigned_at')->nullable();
            $table->foreignId('changed_by')->nullable()->constrained('users')->nullOnDelete();
            $table->string('source', 20)->default('app');
            $table->timestamps();
        });

        Schema::create('target_scopes', function (Blueprint $table) {
            $table->string('code', 30)->primary();
            $table->foreignId('division_id')->nullable()->constrained()->restrictOnDelete();
            $table->string('label', 80);
            $table->timestamps();
        });

        Schema::create('annual_targets', function (Blueprint $table) {
            $table->id();
            $table->string('scope_code', 30);
            $table->foreign('scope_code')->references('code')->on('target_scopes')->restrictOnDelete();
            $table->foreignId('product_id')->constrained()->restrictOnDelete();
            $table->unsignedSmallInteger('year');
            $table->unsignedBigInteger('target_value')->default(0);
            $table->foreignId('updated_by')->nullable()->constrained('users')->nullOnDelete();
            $table->unsignedBigInteger('version')->default(1);
            $table->timestamps();
            $table->unique(['scope_code', 'product_id', 'year']);
        });

        Schema::create('monthly_targets', function (Blueprint $table) {
            $table->id();
            $table->foreignId('annual_target_id')->constrained()->cascadeOnDelete();
            $table->unsignedTinyInteger('month');
            $table->unsignedBigInteger('target_value')->default(0);
            $table->timestamps();
            $table->unique(['annual_target_id', 'month']);
        });

        Schema::create('unit_realizations', function (Blueprint $table) {
            $table->id();
            $table->foreignId('annual_target_id')->constrained()->cascadeOnDelete();
            $table->unsignedTinyInteger('month');
            $table->unsignedBigInteger('units')->default(0);
            $table->foreignId('updated_by')->nullable()->constrained('users')->nullOnDelete();
            $table->unsignedBigInteger('version')->default(1);
            $table->timestamps();
            $table->unique(['annual_target_id', 'month']);
        });

        Schema::create('branch_targets', function (Blueprint $table) {
            $table->id();
            $table->foreignId('division_id')->constrained()->restrictOnDelete();
            $table->string('branch_code', 40);
            $table->unsignedSmallInteger('year');
            $table->unsignedBigInteger('target_value')->default(0);
            $table->foreignId('updated_by')->nullable()->constrained('users')->nullOnDelete();
            $table->unsignedBigInteger('version')->default(1);
            $table->timestamps();
            $table->unique(['division_id', 'branch_code', 'year']);
        });

        Schema::create('audit_events', function (Blueprint $table) {
            $table->id();
            $table->foreignId('actor_id')->nullable()->constrained('users')->nullOnDelete();
            $table->string('resource_type', 80);
            $table->string('resource_id', 80);
            $table->string('action', 60);
            $table->json('before_data')->nullable();
            $table->json('after_data')->nullable();
            $table->dateTime('occurred_at');
            $table->string('source', 20)->default('api');
            $table->index(['resource_type', 'resource_id']);
        });
    }

    public function down(): void
    {
        foreach (['audit_events', 'branch_targets', 'unit_realizations', 'monthly_targets', 'annual_targets', 'target_scopes', 'opportunity_assignments', 'opportunities', 'division_products', 'products'] as $table) {
            Schema::dropIfExists($table);
        }
    }
};
