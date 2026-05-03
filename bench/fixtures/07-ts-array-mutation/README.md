# 07-ts-array-mutation

`Array.prototype.sort` sorts the array in place. The function appears pure because it returns a new sliced array, but the caller's input has already been mutated. Fix: copy first (`[...items].sort(...)` or `.toSorted(...)`).
