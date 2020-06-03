import sqlite3 as sqlite
from datetime import datetime
from exceptions import ServiceError


class AdsServiceError(ServiceError):
    service = 'ads'


class AdDoesNotExistError(AdsServiceError):
    pass


class SellerDoesNotExistError(AdsServiceError):
    pass


class AdPermissionError(AdsServiceError):
    pass


class AdExecuteError(AdsServiceError):
    pass


class AdsService:
    def __init__(self, connection):
        self.connection = connection

    def _get_seller_id(self, account_id):
        """
        Метод получения id продавца. На вход подучает id аккаунта и делает
        запрос к БД. Возвращает id продавца.
        :param account_id: идентификатор аккаунта
        :return: seller_id: идентификатор продавца
        """
        cur = self.connection.execute(f'SELECT id FROM seller WHERE account_id = "{account_id}"')
        seller = cur.fetchone()
        return seller['id']

    def _get_images(self, ad_id):
        """
        Метод получения списка изображений для объявления.
        На вход принимает id объявления, возвращает список объектов.
        :param ad_id: идентификатор объявления
        :return: [{"title": image_title, "url": image_url}, ... ]
        """
        cur = self.connection.execute(f'''
            SELECT image.title, image.url
            FROM image
                JOIN car ON car.id = image.car_id
                JOIN ad ON ad.car_id = car.id
            WHERE ad.id = {ad_id}
        ''')
        images = cur.fetchall()
        return [dict(image) for image in images]

    def _get_colors(self, ad_id):
        """
        Метод получения списка цветов для объявления.
        На вход принимает id объявления, возвращает список объектов.
        :param ad_id: идентификатор объявления
        :return: [{"id": color_id, "name": color_name, "hex": color_hex-code}, ... ]
        """
        cur = self.connection.execute(f'''
            SELECT color.id, color.name, color.hex
            FROM color
                JOIN carcolor ON carcolor.color_id = color.id
                JOIN car ON car.id = carcolor.car_id
                JOIN ad ON ad.car_id = car.id
            WHERE ad.id = {ad_id}
        ''')
        colors = cur.fetchall()
        return [dict(color) for color in colors]

    def _get_car(self, ad_id):
        """
        Метод получения автомобиля для объявления.
        На вход принимает id объявления, возвращает список объект "автомобиль" с
        базовым набором полей.
        :param ad_id: идентификатор объявления
        :return: [{"make": car_make, "model": car_model, "mileage": car_mileage, "num_owners": car_nu,_owners}, ... ]
        """
        cur = self.connection.execute(f'''
            SELECT car.make, car.model, car.mileage, car.num_owners, car.reg_number
            FROM car
                JOIN ad ON ad.car_id = car.id
            WHERE ad.id = {ad_id}
        ''')
        car = cur.fetchone()
        return dict(car)

    def _get_tags(self, ad_id):
        """
        Метод получения списка уникальных тегов для объявления.
        На вход принимает id объявления, возвращает список тегов.
        :param ad_id: идентификатор объявления
        :return: ['tag 1', 'tag 2', ... 'tag N']: список тегов
        """
        cur = self.connection.execute(f'''
            SELECT DISTINCT tag.name
            FROM tag
                JOIN adtag ON adtag.tag_id = tag.id
                JOIN ad ON ad.id = adtag.ad_id
            WHERE ad.id = {ad_id}
        ''')
        tags = cur.fetchall()
        return [tag['name'] for tag in tags]

    def _get_base_ad(self, ad_id):
        """
        Метод получения базовой части параметров объявления по его id.
        :param ad_id: идентификатор объявления
        :return: {ad}
        """
        cur = self.connection.execute(f'''
           SELECT DISTINCT ad.id, seller.id as seller_id, ad.title, ad.date
           FROM ad
               INNER JOIN seller ON seller.id = ad.seller_id        
           WHERE ad.id = {ad_id}
        ''')
        instance = cur.fetchone()
        if not instance:
            raise AdDoesNotExistError
        return dict(instance)

    def _get_filtered_ads_ids(self, filters=None, tags=None):
        """
        Метод получения фильтрованного списка id объявлений.
        На вход принимает набор фильтров и тегов. Оба параметра не обязательны
        Для фильтров применяется условие "И", для тегов - "ИЛИ", между
        фильтрами и тегами применяется условие "И", т.е. будут найдены все объявления,
        удовлетворяющие всем фильтрам и хотя бы одному тегу.

        :param filters: набор фильтров
        :param tags: набор тегов
        :return: список объектов "объявление"
        """
        # Шаблон для получения уникальных id объявлений, удовлетворяющих условиям
        query_template = '''
            SELECT DISTINCT ad.id
            FROM ad
                INNER JOIN seller ON seller.id = ad.seller_id
                INNER JOIN car ON car.id = ad.car_id
                INNER JOIN adtag ON adtag.ad_id = ad.id
                INNER JOIN tag ON tag.id = adtag.tag_id
                INNER JOIN carcolor ON carcolor.car_id = ad.car_id
                INNER JOIN color ON color.id = carcolor.color_id        
            {where_clause}
        '''

        where_queries = []
        where_tags = []
        params = []

        # Заглушки на случай отстутвия параметров в запросе
        where_queries_string = '(TRUE)'
        where_tags_string = '(TRUE)'

        # Формируем строку-условие по обычным параметрам
        for key, value in filters.items():
            where_queries.append(f'{key} = ?')
            params.append(value)
        if where_queries:
            where_queries_string = f'({" AND ".join(where_queries)})'

        # Формируем строку-условие по тегам
        for tag in tags:
            where_tags.append('tag.name = ?')
            params.append(tag)
        if where_tags:
            where_tags_string = f'({" OR ".join(where_tags)})'

        # Формируем результирующую "WHERE-строку"
        where_clause = ''
        if where_queries or where_tags:
            where_clause = f'WHERE {where_queries_string} AND {where_tags_string}'

        # Выполняем запрос и получем список объявлений
        query = query_template.format(where_clause=where_clause)
        cur = self.connection.execute(query, params)
        ads = cur.fetchall()
        return [dict(ad) for ad in ads]

    def _create_ad(self, ad):
        """
        Метод создания записи в таблице "ad".
        На вход принимает объект с набором специфических полей,
        откуда получает необходимые аргументы.
        :param ad: объект
        :return: instance_id: идентификатор записи
        """
        keys = ', '.join(f'{key}' for key in ad.keys())
        values = ', '.join(f'"{value}"' for value in ad.values())

        self.connection.execute('PRAGMA foreign_keys = ON')
        cur = self.connection.execute(f'INSERT INTO ad ({keys}) VALUES ({values})')
        instance_id = cur.lastrowid
        return instance_id

    def _create_car(self, car):
        """
        Метод создания записи в таблице "car".
        На вход принимает объект с набором специфических полей,
        откуда получает необходимые аргументы.
        :param car: объект
        :return: instance_id: идентификатор записи
        """
        keys = ', '.join(f'{key}' for key in car.keys())
        values = ', '.join(f'"{value}"' for value in car.values())

        self.connection.execute('PRAGMA foreign_keys = ON')
        cur = self.connection.execute(f'INSERT INTO car ({keys}) VALUES ({values})')
        instance_id = cur.lastrowid
        return instance_id

    def _create_tags(self, ad_id, tags):
        """
        Метод создания записи в таблицах "tag" и "adtag".
        :param ad_id: идентификатор объявления
        :param tags: список тегов
        :return: nothing
        """
        self.connection.execute('PRAGMA foreign_keys = ON')
        for tag in tags:
            self.connection.execute(f'INSERT OR IGNORE INTO tag (name) VALUES ("{tag}")')
            cur = self.connection.execute(f'SELECT id FROM tag WHERE name = "{tag}"')
            tag_id = dict(cur.fetchone())['id']
            self.connection.execute(f'INSERT INTO adtag (tag_id, ad_id) VALUES ({tag_id}, {ad_id})')

    def get_color_id(self, name):   # TODO не используется
        """
        Метод получения id цвета по его названию.
        :param name: назавние цвета
        :return: id: идентификатор цвета
        """
        cur = self.connection.execute(f'SELECT * FROM color WHERE name = {name}')
        instance = cur.fetchone()
        return dict(instance)['id']

    def _create_colors(self, car_id, colors):
        """
        Метод создания записи в таблице "carcolor".
        :param car_id: идентификатор автомобиля
        :param colors: список идентификаторов цветов
        :return: nothing
        """
        self.connection.execute('PRAGMA foreign_keys = ON')
        for color_id in colors:
            self.connection.execute(f'INSERT INTO carcolor (color_id, car_id) VALUES ({color_id}, {car_id})')

    def _create_images(self, car_id, images):
        """
        Метод создания записи в таблице "image".
        :param car_id: идентификатор автомобиля
        :param images: объект с данными изображений
        :return: nothing
        """
        self.connection.execute('PRAGMA foreign_keys = ON')
        for image in images:
            title = image['title']
            url = image['url']
            self.connection.execute(f'INSERT INTO image (title, url, car_id) VALUES ("{title}", "{url}", {car_id})')

    def _is_owner(self, ad_id, seller_id):
        """
        Метод проверки является ли продавец владельцем объявления.
        :param ad_id: идентификатор объявления
        :param seller_id: идентификатор продавца
        :return: bool
        """
        ad = self.get_formatted_ad(ad_id)
        if ad['seller_id'] != seller_id:
            return False
        else:
            return True

    def _update_title(self, ad_id, title):
        """
        Метод обновления заголовка объявления.
        :param ad_id: идентификатор объявления
        :param title: заголовок
        :return: nothing
        """
        self.connection.execute(f'UPDATE ad SET title = "{title}" WHERE id = {ad_id}')

    def _delete_tags(self, ad_id):
        """
        Метод удаления тегов для объявления.
        :param ad_id: идентификатор объявления
        :return: nothing
        """
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.connection.execute(f'DELETE FROM adtag WHERE ad_id = {ad_id}')

    def _delete_colors(self, car_id):
        """
        Метод удаления цветов для автомобиля.
        :param car_id: идентификатор автомобиля
        :return: nothing
        """
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.connection.execute(f'DELETE FROM carcolor WHERE car_id = {car_id}')

    def _delete_ad(self, ad_id):
        """
        Метож удаления объявления.
        :param ad_id: идентификатор объявления
        :return: nothing
        """
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.connection.execute(f'DELETE FROM ad WHERE id = {ad_id}')

    def _update_car(self, car_id, car):
        """
        Метод обновления сведений об автомобиле.
        :param car_id: идентификатор автомобиля
        :param car: список параметров "ключ: значение"
        :return: nothing
        """
        records = ', '.join(f'{key} = "{value}"' for key, value in car.items())
        self.connection.execute(f'UPDATE car SET {records} WHERE id = {car_id}')

    def _get_car_id(self, ad_id):
        """
        Метод получения идентификатора автомобиля по идентификатору объявления.
        :param ad_id: идентификатор объявления
        :return car_id: идентификатор автомобиля
        """
        cur = self.connection.execute(f'SELECT car_id AS id FROM ad WHERE ad.id = {ad_id}')
        instance = cur.fetchone()
        return instance['id']

    def _delete_images(self, car_id):
        """
        Метод удаления изображений для автомобиля.
        :param car_id: идентификатор автомобиля
        :return: nothing
        """
        self.connection.execute(f'DELETE FROM image WHERE car_id = {car_id}')

    def get_ads(self, account_id=None, qs=None):
        """
        Метод для получения объявлений: всех или от конкретного пользователя,
        с фильтрацией или без неё. Содержит в себе бизнес-логику сервиса получения
        объявлений.
        На вход принимает необязательные аргументы: id аккаунта и список query_string-параметров.
        Возвращает список объектов "объявление", сформированных в соответствии с заданной структурой.
        :param account_id: id аккаунта
        :param qs: набор параметров
        :return: [{ad 1}, {ad 2}, ... {ad N}]
        """
        filters = {}
        tags = []

        # Выделяем из фильтров список тегов
        if qs:
            if 'tags' in qs:
                tags = qs['tags'].split(',')
                del qs['tags']
            filters.update(qs)

        # Если передан id аккаунта
        if account_id:
            # Пытаемся получить из БД id продавца
            seller_id = self._get_seller_id(account_id)
            if not seller_id:
                raise SellerDoesNotExistError
            # и добавляем/перезаписываем его в фильтрах, если продавец существует
            filters['seller_id'] = seller_id

        # Получаем список объявлений, удовлетворяющих параметрам
        ads = self._get_filtered_ads_ids(filters, tags)

        # Для каждого объявления получаем его недостающие компоненты
        # и модифицируем, склеивая в требуемую структуру
        response = []
        for ad in ads:
            ad_id = ad['id']
            response.append(self.get_formatted_ad(ad_id))
        return response

    def get_formatted_ad(self, ad_id):
        """
        Метод для получения объявления по его id.
        На вход принимает id объявления, возвращает объявление.
        :param ad_id: id объявления
        :return: {ad}
        """
        ad = self._get_base_ad(ad_id)
        if ad is None:
            raise AdDoesNotExistError(ad_id)

        car = self._get_car(ad_id)
        car.update({'colors': self._get_colors(ad_id)})
        car.update({'images': self._get_images(ad_id)})
        ad.update({'tags': self._get_tags(ad_id)})
        ad.update({'car': car})

        return dict(ad)

    def publish(self, ad, seller_id):
        """
        Метод создания объявления в БД.
        На вход принимает объект с набором специфических полей, откуда получает
        необходимые аргументы или передаёт его в другие методы.
        :param ad: объект с аргументами
        :param seller_id: идентификатор аккаунта
        :return:
        """
        car = ad.pop('car', None)
        images = car.pop('images', None)
        colors = car.pop('colors', None)
        tags = ad.pop('tags', None)

        ad.update({'date': int(datetime.now().timestamp())})
        ad.update({'seller_id': seller_id})

        try:
            car_id = self._create_car(car)
            ad.update({'car_id': car_id})
            ad_id = self._create_ad(ad)
            self._create_colors(car_id, colors)
            self._create_tags(ad_id, tags)
            self._create_images(car_id, images)
            response = self.get_formatted_ad(ad_id)
        except sqlite.IntegrityError:
            raise AdExecuteError
        else:
            return response

    def edit_ad(self, ad_id, seller_id, data):
        """
        Метод частичного редактирования объявления.
        :param ad_id: идентификатор объявления
        :param seller_id: идентификатор продавца
        :param data: объект с аргументами
        :return: nothing
        """
        if not self._is_owner(ad_id, seller_id):
            raise AdPermissionError

        title = data.get('title', None)
        tags = data.get('tags', None)
        car = data.get('car', None)
        colors = None
        images = None
        car_id = self._get_car_id(ad_id)

        try:
            if title:
                self._update_title(ad_id, title)
            if tags is not None:
                self._delete_tags(ad_id)
                if tags:
                    self._create_tags(ad_id, tags)
            if car:
                colors = car.pop('colors', None)
                images = car.pop('images', None)
                self._update_car(car_id, car)
            if colors is not None:
                self._delete_colors(car_id)
                if colors:
                    self._create_colors(car_id, colors)
            if images is not None:
                self._delete_images(car_id)
                if images:
                    self._create_images(car_id, images)
        except sqlite.IntegrityError:
            raise AdExecuteError

    def delete_ad(self, ad_id, seller_id):
        """
        Метод для удаления объявления.
        :param ad_id: идентификатор объявления
        :param seller_id: идентификатор продавца
        :return: nothing
        """
        if not self._is_owner(ad_id, seller_id):
            raise AdPermissionError

        car_id = self._get_car_id(ad_id)

        try:
            self._delete_images(car_id)
            self._delete_colors(car_id)
            self._delete_tags(ad_id)
            self._delete_ad(ad_id)
        except sqlite.IntegrityError:
            raise AdExecuteError
