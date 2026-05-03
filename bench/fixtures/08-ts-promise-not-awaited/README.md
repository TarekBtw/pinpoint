# 08-ts-promise-not-awaited

`Array.prototype.forEach` does not await its callback. Each `saveUser(...)` call returns a Promise that is dropped on the floor. The fix is `for...of` with `await`, or `Promise.all(rows.map(saveUser))`. Root cause is the use of forEach with an async callback, not the saveUser implementation.
