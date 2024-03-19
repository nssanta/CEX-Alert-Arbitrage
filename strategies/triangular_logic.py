def edit_data_coin_pairs(full_info):
    """
    Функция создает словарь, содержащий данные разбитых монетных пар.
    :param full_info: принимает возвращаемые данные всех тикеров от апи
    :return: словарь вида {'RLTMUSDT': {'coin1': 'RLTM', 'coin2': 'USDT', 'price': '0.0066'}}
    """
    # Создаем словарь
    ret_dict = {}
    # Проходим по данным
    for item in full_info:
        # Проверяем окончание монетной пары и создаем соответствующий словарь
        if item['symbol'].endswith("USDT") or item['symbol'].endswith("USDC"):
            one = item['symbol'][:-4]
            two = item['symbol'][-4:]
            ret_dict[item["symbol"]] = {
                "coin1": one,
                "coin2": two,
                "price": item['lastPrice']
            }
        elif item['symbol'].endswith("BTC") or item['symbol'].endswith("EUR") or \
                item['symbol'].endswith("ETH") or item['symbol'].endswith("BRZ") or item['symbol'].endswith("DAI") \
                or item['symbol'].endswith("AUD"):
            one = item['symbol'][:-3]
            two = item['symbol'][-3:]
            ret_dict[item["symbol"]] = {
                "coin1": one,
                "coin2": two, "price": item['lastPrice']
            }
        else:
            # Если у нас нет данных для разбития
            pass
            # print(f"{item['symbol']} - pair skipped")
    return ret_dict

def find_chains(currency_data, start_currency, max_depth):
    """
    Функция для рекурсивного поиска связей между валютами (треугольный арбитраж).
    :param currency_data: словарь, содержащий данные о монетах
    :param start_currency: начальная валюта поиска
    :param max_depth: максимальная глубина рекурсии
    :return: список всех найденных цепочек связей
    """
    # Вспомогательная функция для рекурсивного поиска связей
    def search_chain(currency, depth, chain):
        # Проверяем глубину рекурсии
        if depth == max_depth:
            return
        
        # Если валюты нет в данных, пропускаем
        if currency not in currency_data:
            return

        # Цикл перебирает все валюты, на которые можно обменять текущую
        for next_currency in currency_data[currency]:
            if next_currency not in currency_data:
                continue
            
            # Если следующая валюта - начальная, и цепочка не пустая, сохраняем её
            if next_currency == start_currency and len(chain) > 1:
                chains.append(chain + [next_currency])
            # Иначе продолжаем рекурсивный поиск, если валюты еще нет в цепочке
            elif next_currency not in chain:
                search_chain(next_currency, depth + 1, chain + [next_currency])

    chains = []
    search_chain(start_currency, 0, [start_currency])
    return chains

if __name__ == '__main__':
    pass