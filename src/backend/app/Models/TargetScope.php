<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TargetScope extends Model
{
    protected $primaryKey = 'code';
    public $incrementing = false;
    protected $keyType = 'string';
    protected $guarded = [];
}
