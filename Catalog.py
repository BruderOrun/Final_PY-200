import sqlite3
from prettytable import PrettyTable
import os
import csv
import json
import logging


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