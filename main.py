import asyncio
import time

from exchange.BybitApi import BybitApi
from exchange.OkxApi import OkxApi

if __name__ == '__main__':
    start_time = time.time()

    async def main():
        okx = OkxApi("Okx")
        bybit = BybitApi("Okx")

        # Запускаем оба метода одновременно
        task1 = asyncio.create_task(okx.get_full_info())
        task2 = asyncio.create_task(bybit.get_full_info())

        # Ждем, пока оба метода завершатся
        await asyncio.gather(task1, task2)

        # print(task1.result())
        # print(task2.result())

    asyncio.run(main())

    end_time = time.time()
    print(f'Код отработал за {end_time-start_time}')