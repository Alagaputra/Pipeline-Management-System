<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{
    public function login(Request $request)
    {
        $data = $request->validate(['username' => ['required', 'string'], 'password' => ['required', 'string']]);
        $user = User::with('division')->where('username', strtolower($data['username']))->where('is_active', true)->first();
        if (!$user || !Hash::check($data['password'], $user->password)) {
            throw ValidationException::withMessages(['username' => ['Username atau password tidak sesuai.']]);
        }
        $user->tokens()->delete();
        return response()->json(['token' => $user->createToken('vue-app')->plainTextToken, 'user' => $user]);
    }

    public function me(Request $request) { return $request->user()->load('division'); }

    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()?->delete();
        return response()->noContent();
    }
}
