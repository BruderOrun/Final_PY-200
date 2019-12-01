import logging
from Catalog import Catalog

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