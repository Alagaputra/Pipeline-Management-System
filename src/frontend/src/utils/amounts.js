// Nilai kecil tetap number untuk kompatibilitas; total besar menjadi string desimal.
export function exactAmount(value) {
  const integer = BigInt(value ?? 0)
  return integer <= BigInt(Number.MAX_SAFE_INTEGER) && integer >= BigInt(Number.MIN_SAFE_INTEGER)
    ? Number(integer)
    : integer.toString()
}
export const sumAmounts = (values) =>
  exactAmount(values.reduce((total, value) => total + BigInt(value ?? 0), 0n))
export const remainingAmount = (target, actual) =>
  exactAmount(
    BigInt(target ?? 0) > BigInt(actual ?? 0) ? BigInt(target ?? 0) - BigInt(actual ?? 0) : 0n,
  )
export const compareAmounts = (a, b) => (BigInt(a) < BigInt(b) ? -1 : BigInt(a) > BigInt(b) ? 1 : 0)
export const formatInteger = (value) => new Intl.NumberFormat('id-ID').format(BigInt(value ?? 0))
