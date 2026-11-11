<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class OpportunityAssignment extends Model
{
    protected $guarded = [];
    protected function casts(): array { return ['assigned_at' => 'datetime', 'unassigned_at' => 'datetime']; }
    public function opportunity() { return $this->belongsTo(Opportunity::class); }
    public function pic() { return $this->belongsTo(User::class, 'pic_id'); }
}
