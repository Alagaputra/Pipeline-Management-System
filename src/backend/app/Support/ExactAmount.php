<?php

namespace App\Support;

use Brick\Math\BigInteger;

final class ExactAmount
{
    public static function encode(BigInteger $value): int|string
    {
        return $value->abs()->isLessThanOrEqualTo('9007199254740991') ? $value->toInt() : (string) $value;
    }

    public static function sum(iterable $values): int|string
    {
        $total = BigInteger::zero();
        foreach ($values as $value) $total = $total->plus((string) ($value ?? 0));
        return self::encode($total);
    }

    public static function remaining(int|string $target, int|string $realization): int|string
    {
        $difference = BigInteger::of($target)->minus($realization);
        return $difference->isNegative() ? 0 : self::encode($difference);
    }
}
