from exceptions import ServiceError


class AdsServiceError(ServiceError):
    service = 'ads'


class AdDoesNotExistError(AdsServiceError):
    pass


class SellerDoesNotExistError(AdsServiceError):
    pass


class AdsService:
    def __init__(self, connection):
        self.connection = connection

    def _get_seller(self, account_id):
        """
        Приватный метод получения id продавца. На вход подучает id аккаунта и делает
        запрос к БД. Возвращает id продавца.
        :param account_id: id аккаунта
        :return: seller_id: id продавца
        """
        cur = self.connection.execute(f'SELECT id FROM seller WHERE account_id = "{account_id}"')
        seller = cur.fetchone()
        return seller['id']

    def _get_images(self, ad_id):
        """
        Приватный метод получения списка изображений для объявления.
        На вход принимает id объявления, возвращает список объектов.
        :param ad_id: id объявления
        :return: [{"title": image_title, "url": image_url}, ... ]
        """
        cur = self.connection.execute(f'''
            SELECT image.title, image.url
            FROM image
                JOIN car ON car.id = image.id
                JOIN ad ON ad.car_id = car.id
            WHERE ad.id = {ad_id}
        ''')
        images = cur.fetchall()
        return [dict(image) for image in images]

    def _get_colors(self, ad_id):
        """
        Приватный метод получения списка цветов для объявления.
        На вход принимает id объявления, возвращает список объектов.
        :param ad_id: id объявления
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
        Приватный метод получения автомобиля для объявления.
        На вход принимает id объявления, возвращает список объект "автомобиль" с
        базовым набором полей.
        :param ad_id: id объявления
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
        Приватный метод получения списка уникальных тегов для объявления.
        На вход принимает id объявления, возвращает список тегов.
        :param ad_id: id объявления
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

    def _get_ads(self, filters=None, tags=None):
        """
        Приватный метод получения списка объявлений с базовым набором полей.
        На вход принимает набор фильтров и тегов. Оба параметра не обязательны
        Для фильтров применяется условие "И", для тегов - "ИЛИ", между
        фильтрами и тегами применяется условие "И", т.е. будут найдены все объявления,
        удовлетворяющие всем фильтрам и хотя бы одному тегу.

        :param filters: набор фильтров
        :param tags: набор тегов
        :return: список объектов "объявление"
        """
        # Шаблон для получения базовых полей уникальных объявлений, удовлетворяющих условиям
        query_template = '''
            SELECT DISTINCT ad.id, seller.id as seller_id, ad.title, ad.date
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
            seller_id = self._get_seller(account_id)
            if not seller_id:
                raise SellerDoesNotExistError
            # и добавляем/перезаписываем его в фильтрах, если продавец существует
            filters['seller_id'] = seller_id

        # Получаем список объявлений, удовлетворяющих параметрам
        ads = self._get_ads(filters, tags)

        # Для каждого объявления получаем его недостающие компоненты
        # и модифицируем, склеивая в требуюмую структуру
        for ad in ads:
            ad_id = ad['id']
            car = self._get_car(ad_id)
            car.update({'colors': self._get_colors(ad_id)})
            car.update({'images': self._get_images(ad_id)})
            ad.update({'tags': self._get_tags(ad_id)})
            ad.update({'car': car})
        return ads

    def get_ad(self, ad_id):
        """
        Метод для получения объявления по его id.
        На вход принимает id объявления, возвращает объявление.
        :param ad_id:
        :return: {ad}
        """
        query = (
            'SELECT * '
            'FROM ad '
            'WHERE id = ?'
        )
        params = (ad_id,)
        cur = self.connection.execute(query, params)
        ad = cur.fetchone()
        if ad is None:
            raise AdDoesNotExistError(ad_id)
        return dict(ad)