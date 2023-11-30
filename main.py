import os

from exchange.BybitApi import BybitApi
from exchange.OkxApi import OkxApi


def main():
    okx = OkxApi()
    bybit = BybitApi()

    print(okx.logger)


if __name__ == "__main__":
    main()