import asyncio


class Counter:
    def __init__(self):
        self.value = 0

    async def increment(self):
        current = self.value
        await asyncio.sleep(0)
        self.value = current + 1


async def main():
    c = Counter()
    await asyncio.gather(*(c.increment() for _ in range(100)))
    print(c.value)


if __name__ == "__main__":
    asyncio.run(main())
