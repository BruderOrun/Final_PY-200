"""
Программа для создания/редактирования/удаления каталога книг
"""


import sqlite3
from prettytable import PrettyTable
import os
import csv
import json
import argparse
import logging
import configparser


class Catalog:
    def __init__(self, db_name: str = None):
        """
        Инициализация экземпляра класса

        :param db_name: название каталога книг, с которым будет производиться взаимодействие
        """
        self.db_name = str(db_name)

    def create(self):
        """
        Метод для создания базы хранения каталога книг формата SQLite3

        :return: в зависимости от результата текстовое сообщение "База успешно создана", либо "Что-то пошло не так"
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE books (Название_книги text, Автор  text, Год_выпуска text, Жанр text)""")
            conn.commit()
            conn.close()
            print('Каталог успешно создан')
            logging.info('Каталог успешно создан')
        except Exception as exc:
            print('Что-то пошло не так')
            logging.error(exc)

    def add_book(self, book: list):
        """
        Метод для добавления книги/списка книг в каталог.

        :param book: добавляемая книга/список книг
        :return: текстовое сообщение "Книга успешно добавлена"
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            if type(book[0]) == list or type(book[0]) == tuple:
                book2 = []
                for i in book:
                    book2.append(tuple(map(lambda x: x.upper(), i)))
                book3 = []
                for i in book2:
                    book3.append(tuple(map(lambda x: x.strip(), i)))
                cursor.executemany("INSERT INTO books VALUES (?,?,?,?)", book3)
                conn.commit()
                conn.close()
                print('Книга успешно добавлена')
                logging.info('Книга успешно добавлена')
            elif type(book[0]) == str:
                book = list(map(lambda x: x.strip(), book))
                book = list(map(lambda x: x.upper(), book))
                book = [book]
                cursor.executemany("INSERT INTO books VALUES (?,?,?,?)", book)
                conn.commit()
                conn.close()
                print('Книга успешно добавлена')
                logging.info('Книга успешно добавлена')
        except Exception as exc:
            print('Что-то пошло не так')
            logging.error(exc)

    def output(self):
        """
        Метод для вывода на экран содержания каталога книг из базы SQLite3

        :return: список книг из каталога + вывод списка книг в табличной форме
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            sql = f'PRAGMA table_info(books)'
            cursor.execute(sql)
            row_names = ['№ строки']
            for i in cursor.fetchall():
                row_names.append(i[1])
            sql1 = f"SELECT * FROM books"
            cursor.execute(sql1)
            search_result = cursor.fetchall()
            new_result = []
            counter = 1
            for i in search_result:
                i = list(i)
                i.insert(0, counter)
                new_result.append(i)
                counter += 1
            table = PrettyTable(row_names)
            for i in new_result:
                table.add_row(i)
            print(table)
            conn.close()
            logging.info('Каталог выведен на печать')
            return search_result
        except Exception as exc:
            print('Что-то пошло не так')
            logging.error(exc)

    def search(self, request: str = None):
        """
        Метод для поиска информации о книге в базе SQLite3, а также для сохраннеия найденной книги
        в файле формата JSON/CSV

        :param request: строка для поиска в базе книг
        :return: список книг + вывод результата поиска в каталоге в табличной форме
        """
        if request is None:
            logging.info('Пустой запрос')
            return f'Пустой запрос'
        else:
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                request = request.strip()
                request = request.upper()
                sql = f"SELECT * FROM books WHERE Название_книги LIKE '%{request}%' OR Автор LIKE '%{request}%' " \
                    f"OR Год_выпуска LIKE '%{request}%' OR Жанр LIKE '%{request}%'"
                cursor.execute(sql)
                search_result = cursor.fetchall()
                new_result = []
                counter = 1
                for i in search_result:
                    i = list(i)
                    i.insert(0, counter)
                    new_result.append(i)
                    counter += 1
                if len(search_result) != 0:
                    sql1 = f'PRAGMA table_info(books)'
                    cursor.execute(sql1)
                    row_names = ['№ строки']
                    for i in cursor.fetchall():
                        row_names.append(i[1])
                    table = PrettyTable(row_names)
                    for i in new_result:
                        table.add_row(i)
                    print(table)
                    logging.info('Вывод результатов поиска')
                    valid = False
                    while not valid:
                        user_choice = int(input("1 - сохранить книгу в файл формата JSON, "
                                                "2 - сохранить книгу в файл формата CSV,"
                                                " 0 - отмена\n"))
                        try:
                            user_choice = int(user_choice)
                        except ValueError:
                            print("Некорректный ввод")
                            logging.error(ValueError)
                            continue
                        if user_choice == 1:
                            string_choice = int(input('Введите номер строки для записи файл\n'))
                            filename_input = input('Введите имя файла для записи\n')
                            self.to_json(filename_input, search_result[string_choice-1])
                            valid = True
                        elif user_choice == 2:
                            string_choice = int(input('Введите номер строки для записи файл\n'))
                            filename_input = input('Введите имя файла для записи\n')
                            self.to_csv(filename_input, search_result[string_choice-1])
                            valid = True
                        elif user_choice == 0:
                            valid = True
                        else:
                            print("Некорректный ввод")
                            logging.error("Некорректный ввод")
                            continue
                    return search_result
                else:
                    print('Ничего не найдено')
                    logging.info('Ничего не найдено')
                conn.close()
            except Exception as exc:
                print('Что-то пошло не так')
                logging.error(exc)

    def correct(self, request: str):
        """
        Метод для внесения изменений в конкретную книгу в базе

        :param request: строка для поиска в базе книг
        :return: None + в зависимости от результата соответствующее текстовое сообщение.
        """
        try:
            choice_list = self.search(request)
            if choice_list is None:
                return None
            valid = False
            while not valid:
                row_choice = input("Введите номер редактируемой строки\n")
                try:
                    row_choice = int(row_choice)
                    if row_choice in range(1, len(choice_list) + 1):
                        valid = True
                    else:
                        print('Некорректный ввод')
                        logging.error('Некорректный ввод')
                        continue
                except Exception as err:
                    print('Некорректный ввод')
                    logging.error(err)
                    continue
            user_choice = self.user_choice()
            if user_choice == 0:
                return None
            new_data = input('Введите новое значение\n')
            new_data = new_data.strip()
            new_data = new_data.upper()
            if user_choice == 1:
                sql = f"UPDATE books SET Название_книги = '{new_data}' " \
                    f"WHERE Название_книги = '{choice_list[row_choice - 1][0]}'"
            elif user_choice == 2:
                sql = f"UPDATE books SET Автор = '{new_data}' " \
                    f"WHERE Название_книги = '{choice_list[row_choice - 1][0]}'"
            elif user_choice == 3:
                sql = f"UPDATE books SET Год_выпуска = '{new_data}' " \
                    f"WHERE Название_книги = '{choice_list[row_choice - 1][0]}'"
            elif user_choice == 4:
                sql = f"UPDATE books SET Жанр = '{new_data}' " \
                    f"WHERE Название_книги = '{choice_list[row_choice - 1][0]}'"
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            conn.close()
            print('Данные успешно обновлены')
            logging.info('Данные успешно обновлены')
        except Exception as exc:
            print('Что-то пошло не так')
            logging.error(exc)

    def book_delete(self, request: str = None):
        """
        Метод для удаления книги из каталога

        :param request: удаляемая книга,
        в случае None - предлагается самостоятельно выбрать книги для удаления из распечатанной таблицы
        :return: None + в зависимости от результата соответствующее текстовое сообщение.
        """
        try:
            if request is None:
                self.output()
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                row_for_delete = input("Введите номера удаляемых строк через запятую\n")
                row_for_delete = list(row_for_delete.split(','))
                row_for_delete = list(map(lambda x: x.strip(), row_for_delete))
                row_for_delete = set(int(i) for i in row_for_delete)
                for j in row_for_delete:
                    sql = f"DELETE FROM books WHERE rowid={j}"
                    cursor.execute(sql)
                    conn.commit()
                conn.close()
                print('Книга успешно удалена')
                logging.info('Книга успешно удалена')
            else:
                choice_list = self.search(request)
                row_for_delete = int(input("Введите номер удаляемой строки\n"))
                sql = f"DELETE FROM books WHERE Название_книги LIKE '%{choice_list[row_for_delete-1][0]}%'"
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute(sql)
                conn.commit()
                conn.close()
                print('Книга успешно удалена')
                logging.info('Книга успешно удалена')
        except Exception as exc:
            print('Что-то пошло не так')
            logging.error(exc)

    def db_clear(self):
        """
        Метод для удаления всех книг из каталога

        :return: None
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            sql = "DELETE FROM books"
            cursor.execute(sql)
            conn.commit()
            conn.close()
            print('База успешно очищена')
            logging.info('База успешно очищена')
        except Exception as exc:
            print('Что-то пошло не так')
            logging.error(exc)

    def catalog_delete(self):
        """
        Метод для удаления каталога книг

        :return: в зависимости от результата соответствующее текстовое сообщение
        """
        try:
            conn = sqlite3.connect(self.db_name)
            conn.close()
            os.path.isfile(self.db_name)
            os.remove(self.db_name)
            print("Каталог успешно удален")
            logging.info("Каталог успешно удален")
        except Exception as exc:
            print("Каталог не найден")
            logging.error(exc)

    @staticmethod
    def user_choice():
        """
        Метод для получения от пользователя информации для дальнейшего взаимодействия с программой

        :return: Выбор пользователя
        """
        valid = False
        while not valid:
            user_input = input('С чем взаимодействуем: 1 - Название_книги, 2 - Автор, '
                               '3 - Год_выпуска, 4 - Жанр, 0 - Отмена\n')
            try:
                user_input = int(user_input)
                if user_input in [0, 1, 2, 3, 4]:
                    valid = True
                    logging.info('Успешный ввод данных')
                    return user_input
                else:
                    print("Некорректный ввод")
                    logging.info('Некорректный ввод')
                    continue
            except ValueError:
                print("Некорректный ввод")
                logging.error(ValueError)
                continue

    def to_csv(self, filename: str = None, book: list = None):
        """
        Метод для сохранения каталога книг/списка книг в файл формата CSV

        :param filename: название файла для сохранения
        :param book: книга/список книг для сохранения. В случае None сохраняется каталог книг.
        :return: в зависимости от результата соответствующее текстовое сообщение
        """
        if len(filename) == 0:
            filename = 'output.csv'
        else:
            if filename[-4:] != '.csv':
                filename = filename + '.csv'
        try:
            if book is None:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM books")
                with open(filename, 'x', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow([i[0] for i in cursor.description])
                    for result in cursor:
                        writer.writerow(result)
                conn.close()
                print('CSV-файл успешно записан')
                logging.info('CSV-файл успешно записан')
            else:
                with open(filename, 'x', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(book)
                    print('CSV-файл успешно записан')
                    logging.info('CSV-файл успешно записан')
        except FileExistsError:
            print('Файл с таким названием уже существует\n')
            logging.error(FileExistsError)

    def to_json(self, filename: str = 'output.csv', book: list = None):
        """
        Метод для сохранения каталога книг в файл формата JSON

        :return: в зависимости от результата соответствующее текстовое сообщение
        """
        if len(filename) == 0:
            filename = 'output.json'
        else:
            if filename[-5:] != '.json':
                filename = filename + '.json'
        try:
            if book is None:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM books")
                result = cursor.fetchall()
                with open(filename, 'x', newline='') as file:
                    json.dump(result, file)
                conn.close()
                print('JSON-файл успешно записан')
                logging.info('JSON-файл успешно записан')
            else:
                with open(filename, 'x', newline='') as file:
                    json.dump(book, file)
                    print('JSON-файл успешно записан')
                    logging.info('JSON-файл успешно записан')
        except FileExistsError:
            print('Файл с таким названием уже существует\n')
            logging.error(FileExistsError)

    def from_csv(self, filename: str):
        """
        Метод для добавления книги в каталога из файла формата CSV

        :param filename: имя файла
        :return: в зависимости от результата соответствующее текстовое сообщение
        """
        if filename[-4:] != '.csv':
            filename = filename + '.csv'
        if not os.path.exists(filename):
            print('Файл с таким названием не существует')
            logging.info('Файл с таким названием не существует')
        else:
            try:
                catalog = []
                with open(filename, 'r') as file:
                    reader = csv.reader(file, delimiter=';')
                    for row in reader:
                        catalog.append(row)
                self.add_book(catalog)
                print('Книга успешно добавлена')
                logging.info('Книга успешно добавлена')
            except Exception as exc:
                print('Что-то пошло не так')
                logging.error(exc)

    def from_json(self, filename: str):
        """
        Метод для добавления книги в каталога из файла формата JSON

        :param filename: имя файла
        :return: в зависимости от результата соответствующее текстовое сообщение
        """
        if filename[-5:] != '.json':
            filename = filename + '.json'
        if not os.path.exists(filename):
            print('Файл с таким названием не существует')
            logging.info('Файл с таким названием не существует')
        try:
            with open(filename, 'r') as file:
                reader = json.load(file)
            self.add_book(reader)
            print('Книга успешно добавлена')
            logging.info('Книга успешно добавлена')
        except Exception as exc:
            print('Что-то пошло не так')
            logging.error(exc)


class Book:
    @staticmethod
    def book_create(book_data: list or tuple = None):
        """
        Метод для создания книги

        :param book_data: книга в виде списка/кортежа данных,
        в случае вызова без аргумента - запрос от пользователя информации о создаваемой книге
        :return: None
        """
        if book_data is None:
            book_name = input('Введите информацию о названии книги\n')
            author = input('Введите информацию об авторе книги\n')
            year_of_creation = input('Введите информацию об годе создания книги\n')
            genre = input('Введите информацию о жанре книги\n')
            book_data = [book_name, author, year_of_creation, genre]
        writer = Catalog()
        valid = False
        while not valid:
            user_choice = int(input("1 - сохранить книгу в файл формата JSON, 2 - сохранить книгу в файл формата CSV,"
                                    " 0 - выход\n"))
            try:
                user_choice = int(user_choice)
            except ValueError:
                print("Некорректный ввод")
                logging.info("Некорректный ввод")
                continue
            if user_choice == 1:
                filename_input = input('Введите имя файла для записи\n')
                writer.to_json(filename_input, book_data)
                valid = True
            elif user_choice == 2:
                filename_input = input('Введите имя файла для записи\n')
                writer.to_csv(filename_input, book_data)
                valid = True
            elif user_choice == 0:
                valid = True
            else:
                print("Некорректный ввод")
                logging.info("Некорректный ввод")
                continue

    @staticmethod
    def book_delete(filename: str):
        """
        Метод для удаления файла(книги)

        :param filename: название файла
        :return: None
        """
        try:
            os.path.isfile(filename)
            os.remove(filename)
            print("Файл успешно удален")
            logging.info("Файл успешно удален")
        except Exception as exc:
            print("Файл не найден")
            logging.error(exc)


class Config:
    def __init__(self):
        """
        Инициализация класса для создания файла конфигурации (запись количества вызова программы
        и названия последнего подключенного каталога)
        """
        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.number_of_calls = int(config.get('Settings', 'number_of_calls'))
        self.db_name = config.get('Settings', 'db_name')

    @staticmethod
    def create():
        """
        Метод для создание файла конфигурации

        :return: None
        """
        config = configparser.ConfigParser()
        config.add_section('Settings')
        config.set('Settings', 'number_of_calls', '0')
        config.set('Settings', 'db_name', '')
        with open('settings.ini', 'w') as config_file:
            config.write(config_file)

    def get_calls(self):
        """
        Метод для получения количества вызовов программы из файла конфигурации

        :return: self.number_of_calls
        """
        return self.number_of_calls

    def inc_calls(self):
        """
        Метод для инкрементирования количества вызовов программы

        :return: self.number_of_calls
        """
        self.number_of_calls += 1
        return self.number_of_calls

    def get_db_name(self):
        """
        Метод для получения названия последнего подключенного каталога

        :return: self.db_name
        """
        return self.db_name

    def set_db_name(self, db_name: str):
        """
        Метод для записи названия последнего подключенного каталога

        :param db_name: название каталога, получаемого в Frontend.sub_main
        :return: self.db_name
        """
        if not isinstance(db_name, str):
            print('Некорректный ввод')
        self.db_name = db_name
        return self.db_name

    def change_settings(self):
        """
        Метод для записи сделанных изменений в файл конфигурации

        :return: None
        """
        config = configparser.ConfigParser()
        config.read('settings.ini')
        config.set('Settings', 'number_of_calls', str(self.number_of_calls))
        config.set('Settings', 'db_name', self.db_name)
        with open('settings.ini', 'w') as config_file:
            config.write(config_file)


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
