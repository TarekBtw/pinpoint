type Item = { price: number; qty: number; promo?: { code: string; pct: number } };

function applyPromo(promo: { pct: number }, total: number): number {
  return total * (1 - promo.pct);
}

function lineTotal(item: Item): number {
  const base = item.price * item.qty;
  return applyPromo(item.promo!, base);
}

const cart: Item[] = [
  { price: 10, qty: 2, promo: { code: "SAVE10", pct: 0.1 } },
  { price: 5, qty: 1 },
];

console.log(cart.reduce((sum, i) => sum + lineTotal(i), 0));
