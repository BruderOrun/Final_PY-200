"""
Программа для создания/редактирования/удаления каталога книг
"""

import configparser


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



