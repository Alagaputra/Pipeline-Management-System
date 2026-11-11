<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Division extends Model
{
    protected $fillable = ['code', 'name'];

    public function users() { return $this->hasMany(User::class); }
    public function products() { return $this->belongsToMany(Product::class, 'division_products'); }
}
