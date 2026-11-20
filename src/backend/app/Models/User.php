<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    /** @use HasFactory<\Database\Factories\UserFactory> */
    use HasApiTokens, HasFactory, Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var list<string>
     */
    protected $fillable = [
        'name',
        'username',
        'email',
        'password',
        'division_id',
        'role',
        'is_active',
    ];

    /**
     * The attributes that should be hidden for serialization.
     *
     * @var list<string>
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
            'is_active' => 'boolean',
        ];
    }

    protected static function booted(): void
    {
        static::updated(function (User $user) {
            if (($user->wasChanged('is_active') && !$user->is_active) || $user->wasChanged(['role', 'division_id'])) {
                $user->tokens()->delete();
            }
        });
    }

    public function division()
    {
        return $this->belongsTo(Division::class);
    }

    public function opportunities()
    {
        return $this->hasMany(Opportunity::class, 'pic_id');
    }

    public function isHead(): bool
    {
        return $this->role === 'head';
    }

    public function hasValidAccess(): bool
    {
        return $this->isHead() || ($this->role === 'pic' && $this->division()->exists());
    }

    public function authorizationContext(): string
    {
        return hash('sha256', json_encode([$this->role, $this->division_id]));
    }
}
