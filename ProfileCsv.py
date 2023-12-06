import pstats
import csv

if __name__ == "__main__":

    """
    run cmd:
        python -m cProfile -s cumtime -o profile_stats.prof Core/DataHandler.py
    
    """

    # Загрузка данных из файла профилирования
    stats = pstats.Stats('profile_stats.prof')

    # Открываем файл для записи в CSV
    with open('profile_stats.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile,delimiter=";")

        # Записываем заголовки столбцов
        csv_writer.writerow(['ncalls', 'tottime', 'percall', 'cumtime', 'percall', 'filename:lineno(function)'])

        # Получаем статистику по функциям и записываем её в CSV
        for func_data, (cc, nc, tt, ct, callers) in stats.stats.items():
            filename, line, func_name = func_data
            csv_writer.writerow([nc, '%0.3f' % tt, '%0.3f' % (tt / nc if nc else 0),
                                 '%0.3f' % ct, '%0.3f' % (ct / cc if cc else 0), f'{filename}:{line}({func_name})'])


