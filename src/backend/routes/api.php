<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\LookupController;
use App\Http\Controllers\OpportunityController;
use App\Http\Controllers\ReportController;
use App\Http\Controllers\TargetController;
use Illuminate\Support\Facades\Route;

Route::post('/login', [AuthController::class, 'login'])->middleware('throttle:10,1');

Route::middleware(['auth:sanctum', \App\Http\Middleware\IdempotentWrite::class])->group(function () {
    Route::get('/me', [AuthController::class, 'me']);
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::get('/divisions', [LookupController::class, 'divisions']);
    Route::get('/products', [LookupController::class, 'products']);
    Route::get('/pics', [LookupController::class, 'pics']);
    Route::get('/opportunities', [OpportunityController::class, 'index']);
    Route::post('/opportunities', [OpportunityController::class, 'store']);
    Route::get('/opportunities/{id}', [OpportunityController::class, 'show']);
    Route::patch('/opportunities/{id}', [OpportunityController::class, 'update']);
    Route::post('/opportunities/{id}/follow-up-completion', [OpportunityController::class, 'completeFollowUp']);
    Route::post('/opportunities/{id}/closing', [OpportunityController::class, 'close']);
    Route::get('/targets', [TargetController::class, 'index']);
    Route::post('/targets/batch', [TargetController::class, 'batch']);
    Route::put('/targets/{scope}/{product}/{year}', [TargetController::class, 'upsert']);
    Route::put('/unit-realizations/{scope}/{product}/{year}/{month}', [TargetController::class, 'realize']);
    Route::get('/branch-targets', [TargetController::class, 'branches']);
    Route::put('/branch-targets/{division}/{branch}/{year}', [TargetController::class, 'upsertBranch']);
    Route::get('/dashboard', [ReportController::class, 'dashboard']);
    Route::get('/team', [ReportController::class, 'team']);
    Route::get('/pics/{id}/opportunities', [ReportController::class, 'picOpportunities']);
});
