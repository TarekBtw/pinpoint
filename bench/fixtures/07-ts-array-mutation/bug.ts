function topN<T>(items: T[], n: number, key: (x: T) => number): T[] {
  return items.sort((a, b) => key(b) - key(a)).slice(0, n);
}

const scores = [{ name: "a", v: 3 }, { name: "b", v: 1 }, { name: "c", v: 2 }];
console.log(topN(scores, 2, (x) => x.v));
console.log(scores);
