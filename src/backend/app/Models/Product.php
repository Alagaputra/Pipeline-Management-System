<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Product extends Model
{
    protected $fillable = ['code', 'name', 'measure', 'is_active'];
    protected function casts(): array { return ['is_active' => 'boolean']; }
    public function divisions() { return $this->belongsToMany(Division::class, 'division_products'); }
}
