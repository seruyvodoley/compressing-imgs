"""просто мэйн модуль"""
import argparse
import os
from compress import start_compression


def main():
    """
    просто мэйн
    """
    parser = argparse.ArgumentParser(description="сжатие на основе квадродерева")

    parser.add_argument("-f", "--file", dest="file", type=str, help="исходная фотОчка", required=True)
    parser.add_argument("-c", "--compress", dest="level", type=int, help="уровень сжатия", required=True)
    parser.add_argument("-s", "--show", dest="borders", action="store_true", help="отображение границ")
    parser.add_argument("-g", "--gif", dest="gif", action="store_true", help="создание гифки")

    try:
        args = parser.parse_args()

        if not os.path.exists(args.file):
            print(f"ошибОчка, файла нет: {args.file}")
            return

        if args.level not in range(0, 9):
            print("не тот уровень сжатияя (0, 8)")
            return

        print(f"сжимаем по уровню {args.level}...")
        start_compression(args.file, args.level, args.borders, args.gif)

    except argparse.ArgumentError as err:
        print(f"ошибОчка: {err}")


if __name__ == "__main__":
    main()
