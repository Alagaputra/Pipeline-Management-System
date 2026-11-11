<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AnnualTarget extends Model
{
    protected $guarded = [];
    protected function casts(): array { return ['target_value' => 'string']; }
    public function product() { return $this->belongsTo(Product::class); }
    public function monthlyTargets() { return $this->hasMany(MonthlyTarget::class); }
    public function unitRealizations() { return $this->hasMany(UnitRealization::class); }
}
