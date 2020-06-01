import sqlite3 as sqlite


class ColorsService:
    def __init__(self, connection):
        self.connection = connection

    # Создание цвета
    def add_color(self, color_name, color_hex):
        """
        Функция добавления цвета в таблицу "color".
        При вызове будет произведена попытка записи в БД с указанными параметрами.
        В случае возникновения конфликта имён - будут возвращёны параметры
        существующего в БД цвета с таким же именем.

        :param color_name: название цвета
        :param color_hex: hex-код цвета
        :return: {"id": color_id, "name": color_name, "hex": color_hex}
        """
        try:
            self.connection.execute(f'INSERT INTO color (name, hex) VALUES ("{color_name}", "{color_hex}")')
        except sqlite.IntegrityError:
            self.connection.rollback()
        finally:
            cur = self.connection.execute(f'SELECT * FROM color WHERE name = "{color_name}"')
            return dict(cur.fetchone())

    # Получение цвета
    def get_colors(self):
        """
        Функция получения списка цветов. Получает из БД все имеющиеся записи цветов и
        возвращает их в виде списка словарей с параметрами цвета.
        :return: [{"id": color_id, "name": color_name, "hex": color_hex}, ... ]
        """
        cur = self.connection.execute(f'SELECT * FROM color')
        colors = cur.fetchall()
        return [dict(color) for color in colors]

