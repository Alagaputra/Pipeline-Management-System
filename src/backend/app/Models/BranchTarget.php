<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BranchTarget extends Model
{
    protected $guarded = [];
    protected function casts(): array { return ['target_value' => 'string']; }
    public function division() { return $this->belongsTo(Division::class); }
}
