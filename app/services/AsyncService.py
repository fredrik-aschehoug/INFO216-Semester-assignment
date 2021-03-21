import asyncio


class AsyncService:
    @staticmethod
    async def gather(tasks):
        return await asyncio.gather(*tasks)

    @staticmethod
    async def gather_with_concurrency(n, tasks):
        """Run n amount of tasks concurrently"""

        # If unlimited concurrency
        if (n == 0):
            return await asyncio.gather(*tasks)

        semaphore = asyncio.Semaphore(n)

        async def sem_task(task):
            async with semaphore:
                return await task
        return await asyncio.gather(*(sem_task(task) for task in tasks))
