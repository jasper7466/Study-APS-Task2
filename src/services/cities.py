import sqlite3 as sqlite


class CitiesService:
    def __init__(self, connection):
        self.connection = connection

    # Создание города
    def add_city(self, city_name):
        """
        Функция добавления города в таблицу "city".
        При вызове будет произведена попытка записи в БД с указанными параметрами.
        В случае возникновения конфликта имён - будут возвращёны параметры
        существующего в БД города с таким же именем.

        :param city_name: название города
        :return: {"id": city_id, "name": city_name}
        """
        try:
            self.connection.execute(f'INSERT INTO city (name) VALUES ("{city_name}")')
        except sqlite.IntegrityError:
            self.connection.rollback()
        finally:
            cur = self.connection.execute(f'SELECT * FROM city WHERE name = "{city_name}"')
            return dict(cur.fetchone())

    # Получение списка городов
    def get_cities(self):
        """
        Функция получения списка городов. Получает из БД все имеющиеся записи и
        возвращает их в виде списка словарей с параметрами записи.
        :return: [{"id": city_id, "name": city_name}, ... ]
        """
        cur = self.connection.execute(f'SELECT * FROM city')
        cities = cur.fetchall()
        return [dict(city) for city in cities]
