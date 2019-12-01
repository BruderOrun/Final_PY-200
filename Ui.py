import os
import argparse
import logging

from Config import Config
from Catalog import Catalog
from Book import Book

class Frontend:
    @staticmethod
    def main():
        """
        Метод для определения источника названия каталога. Либо из файла 'settings.ini', либо при его отсутствии
        от пользователя

        :return: None
        """
        if not os.path.exists('settings.ini'):
            Config.create()
            config = Config()
            config.inc_calls()
            config.change_settings()
            Frontend.sub_main()
        else:
            config = Config()
            db_name = config.get_db_name()
            config.inc_calls()
            config.change_settings()
            Frontend.sub_sub_main(db_name)

    @staticmethod
    def sub_main():
        """
        Метод для запроса от пользователя названия каталога, с которым будет проводиться взаимодействие,
        в случае отсутствия последнего предлагается создать его

        :return: None
        """
        valid = False
        while not valid:
            db_name = input("Введите название базы данных\n")
            if db_name[-3:] != '.db':
                db_name = db_name + '.db'
            if os.path.exists(db_name) is False:
                print('Каталог с таким именем не существует',
                      '1 - создать каталог',
                      '2 - ввести новое название',
                      '0 - выход', sep='\n')
                logging.info('Каталог с таким именем не существует')
                user_choice = int(input())
                try:
                    user_choice = int(user_choice)
                except ValueError:
                    print("\nНекорректный ввод")
                    logging.info('Некорректный ввод')
                    continue
                if user_choice == 1:
                    valid = True
                elif user_choice == 2:
                    continue
                elif user_choice == 0:
                    print('Выход из программы')
                    logging.info('Выход из программы')
                    exit()
                else:
                    print("\nНекорректный ввод")
                    logging.info("Некорректный ввод")
                    continue
            else:
                valid = True
                logging.info('Каталог с таким именем существует')
        config = Config()
        config.set_db_name(db_name)
        config.change_settings()
        Frontend.sub_sub_main(db_name)

    @staticmethod
    def sub_sub_main(db_name):
        """
        Метод для вывода основного меню программы

        :param db_name: Название каталога для взаимодействия
        :return: None
        """
        try:
            sql = Catalog(db_name)
            if not os.path.exists(db_name):
                sql.create()
            valid = False
            while not valid:
                print('Основное меню:',
                      '1 - осуществить поиск книги в каталоге / сохранить выбранную книгу в файл формата CSV/JSON',
                      '2 - удалить каталог',
                      '3 - добавить книгу в каталог',
                      '4 - редактировать информацию о существующей книге',
                      '5 - удалить книгу из каталога',
                      '6 - очистить каталог',
                      '7 - вывести каталог на экран',
                      '8 - сохранить каталог в файл формата CSV',
                      '9 - сохранить каталог в файл формата JSON',
                      '10 - добавить книгу в каталог из файла формата CSV',
                      '11 - добавить книгу в каталог из файла формата JSON',
                      '12 - создать произвольную книгу',
                      '13 - удалить произвольный файл',
                      '14 - подключить/создать новый каталог',
                      '0 - выход', sep='\n')
                main_choice = input()
                try:
                    main_choice = int(main_choice)
                except ValueError:
                    print("Некорректный ввод")
                    logging.info("Некорректный ввод")
                    continue
                if main_choice == 1:
                    search_input = input('Введите текст для поиска в каталоге\n')
                    sql.search(search_input)
                    logging.info('Выбор пункта меню №1')
                elif main_choice == 2:
                    val = True
                    while val:
                        user_conf = input("Подтвердите действие. да/нет\n")
                        user_conf = user_conf.lower()
                        if user_conf == 'да':
                            sql.catalog_delete()
                            val = False
                        elif user_conf == "нет":
                            val = False
                            logging.info('Отказ от удаления книги')
                        else:
                            print('Некорректный ввод')
                            logging.info('Некорректный ввод')
                    logging.info('Выбор пункта меню №2')
                elif main_choice == 3:
                    book_name = input('Введите информацию о названии книги\n')
                    author = input('Введите информацию об авторе книги\n')
                    year_of_creation = input('Введите информацию об годе создания книги\n')
                    genre = input('Введите информацию о жанре книги\n')
                    book_data = [book_name, author, year_of_creation, genre]
                    sql.add_book(book_data)
                    logging.info('Выбор пункта меню №3')
                elif main_choice == 4:
                    search_input = input('Введите текст для поиска и изменения книги в каталоге\n')
                    sql.correct(search_input)
                    logging.info('Выбор пункта меню №4')
                elif main_choice == 5:
                    search_input = input('Введите текст для поиска и удаления книги из каталога\n')
                    sql.book_delete(search_input)
                    logging.info('Выбор пункта меню №5')
                elif main_choice == 6:
                    val = True
                    while val:
                        user_conf = input("Подтвердите действие. да/нет\n")
                        user_conf = user_conf.lower()
                        if user_conf == 'да':
                            sql.db_clear()
                            val = False
                        elif user_conf == "нет":
                            val = False
                            logging.info('Отказ от удаления каталога')
                        else:
                            print('Некорректный ввод')
                            logging.info('Некорректный ввод')
                    logging.info('Выбор пункта меню №6')
                elif main_choice == 7:
                    sql.output()
                    logging.info('Выбор пункта меню №7')
                elif main_choice == 8:
                    filename_input = input('Введите название файла для сохранения в него каталога:\n')
                    sql.to_csv(filename_input)
                    logging.info('Выбор пункта меню №8')
                elif main_choice == 9:
                    filename_input = input('Введите название файла для сохранения в него каталога:\n')
                    sql.to_json(filename_input)
                    logging.info('Выбор пункта меню №9')
                elif main_choice == 10:
                    filename_input = input('Введите название CSV-файла для добавления его в каталог:\n')
                    sql.from_csv(filename_input)
                    logging.info('Выбор пункта меню №10')
                elif main_choice == 11:
                    filename_input = input('Введите название JSON-файла для добавления его в каталог:\n')
                    sql.from_json(filename_input)
                    logging.info('Выбор пункта меню №11')
                elif main_choice == 12:
                    Book.book_create()
                    logging.info('Выбор пункта меню №12')
                elif main_choice == 13:
                    filename_input = input('Введите название файла для удаления\n')
                    Book.book_delete(filename_input)
                    logging.info('Выбор пункта меню №13')
                elif main_choice == 14:
                    Frontend.sub_main()
                    logging.info('Выбор пункта меню №13')
                elif main_choice == 0:
                    print('Завершение программы')
                    logging.info('Завершение программы')
                    exit()
        except Exception as exc:
            logging.error(exc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true', help='Запуск логгирования в режиме DEBUG')

    level = logging.ERROR
    if parser.parse_args().d is True:
        level = logging.DEBUG
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=level, filename='Final_PY-200.log')
    Frontend.main()