import asyncio
import time

from exchange.BybitApi import BybitApi
from exchange.CoinWApi import CoinWApi
from exchange.OkxApi import OkxApi

if __name__ == '__main__':
    start_time = time.time()

    async def main():
        okx = OkxApi("Okx")
        bybit = BybitApi("Bybit")
        coinw = CoinWApi("CoinW")

        # Запускаем
        task1 = asyncio.create_task(okx.get_coins_price_vol())
        task2 = asyncio.create_task(bybit.get_coins_price_vol())
        task3 = asyncio.create_task(coinw.get_coins_price_vol())

        # Ждем, пока оба метода завершатся
        await asyncio.gather(task1, task2, task3)

        print(len(task1.result()))
        print(len(task2.result()))
        print(len(task3.result()))

    asyncio.run(main())

    end_time = time.time()
    print(f'Код отработал за {end_time-start_time}')