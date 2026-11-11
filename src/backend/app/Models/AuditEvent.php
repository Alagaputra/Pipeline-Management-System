<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class AuditEvent extends Model
{
    public $timestamps = false;
    protected $guarded = [];
    public function actor() { return $this->belongsTo(User::class, 'actor_id'); }
    protected function casts(): array { return ['before_data' => 'array', 'after_data' => 'array', 'occurred_at' => 'datetime']; }
}
