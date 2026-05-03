async function saveUser(id: string, data: object): Promise<void> {
  await new Promise((r) => setTimeout(r, 10));
}

async function importUsers(rows: { id: string; data: object }[]): Promise<number> {
  let saved = 0;
  rows.forEach((row) => {
    saveUser(row.id, row.data);
    saved += 1;
  });
  return saved;
}

importUsers([{ id: "a", data: {} }, { id: "b", data: {} }]).then((n) => console.log("imported", n));
