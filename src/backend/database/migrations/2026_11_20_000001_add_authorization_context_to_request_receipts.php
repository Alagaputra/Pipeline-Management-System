<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('request_receipts', function (Blueprint $table) {
            $table->string('authorization_context', 64)->nullable();
        });
    }

    public function down(): void
    {
        Schema::table('request_receipts', fn (Blueprint $table) => $table->dropColumn('authorization_context'));
    }
};
