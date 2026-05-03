function buildHandlers(n: number): (() => number)[] {
  const handlers: (() => number)[] = [];
  for (var i = 0; i < n; i++) {
    handlers.push(() => i);
  }
  return handlers;
}

console.log(buildHandlers(3).map((h) => h()));
