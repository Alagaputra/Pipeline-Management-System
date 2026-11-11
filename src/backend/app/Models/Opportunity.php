<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Opportunity extends Model
{
    protected $guarded = [];
    protected function casts(): array
    {
        return [
            'recorded_date' => 'date:Y-m-d', 'follow_up_date' => 'date:Y-m-d', 'closed_date' => 'date:Y-m-d',
            'follow_up_completed' => 'boolean', 'nominal' => 'string', 'realization' => 'string',
        ];
    }
    public function division() { return $this->belongsTo(Division::class); }
    public function pic() { return $this->belongsTo(User::class, 'pic_id'); }
    public function product() { return $this->belongsTo(Product::class); }
    public function assignments() { return $this->hasMany(OpportunityAssignment::class); }
}
