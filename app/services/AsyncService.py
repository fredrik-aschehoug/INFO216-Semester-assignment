from asyncio import gather, Semaphore


class AsyncService:
    """Base class with helper methods for services that need to send concurrent requests."""
    @staticmethod
    async def gather(tasks: list):
        """Run all tasks concurrently"""
        return await gather(*tasks)

    @staticmethod
    async def gather_with_concurrency(n: int, tasks: list):
        """
        Run n amount of tasks concurrently.
        This method is used when you want to limit the maximim amount of tasks being done simultaneously.
        """

        # If unlimited concurrency
        if (n == 0):
            return await gather(*tasks)

        semaphore = Semaphore(n)

        async def sem_task(task):
            async with semaphore:
                return await task
        return await gather(*(sem_task(task) for task in tasks))
