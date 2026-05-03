type UserId = { value: string };

function dedupe(ids: UserId[]): UserId[] {
  const seen: UserId[] = [];
  for (const id of ids) {
    if (!seen.includes(id)) {
      seen.push(id);
    }
  }
  return seen;
}

const a: UserId = { value: "u1" };
const b: UserId = { value: "u1" };
console.log(dedupe([a, b]).length);
