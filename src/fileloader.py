import os
from os.path import (
    splitext,
    exists
)
import uuid


class FileLoader:
    """
    Класс-расширение для работы с файлами.
    Реализует функционал безопасного сохранения файла в директорию,
    путь до которой задан в конфигурации приложения.
    """
    def __init__(self, app=None):
        self._app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Метод инициализации приватной переменной приложения self._app.
        :param app: приложение
        :return: nothing
        """
        self._app = app

    def save_file(self, file):
        """
        Метод сохранения файла.
        Создаёт директорию для сохранения (если не создана).
        Дополняет имя файла уникальным идентификатором и сохраняет
        его по пути, полученному из файла конфигурации приложения.
        Возвращает относительный путь до сохранённого файла в случае успешного сохранения или
        пустую стороку в случае возникновения ошибки.
        :param file: объект "файл"
        :return: path: путь до файла
        """
        folder = self._app.config['UPLOAD_FOLDER']
        try:
            if not exists(folder):
                os.makedirs(folder)
        except OSError:
            return ''

        name = splitext(file.filename)[0]
        ext = splitext(file.filename)[1]
        result_name = f'{name}__{uuid.uuid4()}{ext}'

        file_path = os.path.join(self._app.config['UPLOAD_FOLDER'], result_name)

        try:
            file.save(file_path)
        except IOError or OSError:
            return ''
        return result_name

    def get_dir(self):
        """
        Метод получения пути до директории загрузки.
        Путь извлекается из конфигурации приложения.
        :return: path: путь к директории
        """
        return self._app.config['UPLOAD_FOLDER']


fl = FileLoader()
