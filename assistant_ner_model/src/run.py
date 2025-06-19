import asyncio

from scheduler import NERModelScheduler


if __name__ == "__main__":
    current_loop = asyncio.get_event_loop()
    current_loop.run_until_complete(NERModelScheduler.run())

    current_loop.run_forever()
