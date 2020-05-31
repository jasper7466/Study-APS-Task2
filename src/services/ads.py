from exceptions import ServiceError


class AdsServiceError(ServiceError):
    service = 'ads'


class AdDoesNotExistError(AdsServiceError):
    pass


class AdsService:
    def __init__(self, connection):
        self.connection = connection

    # Получение объявлений (всех или от конкретного пользователя)
    def get_ads(self, account_id=None, filters=None):
        # Базовый запрос - все объявления всех пользователей
        query = (
            'SELECT DISTINCT * '
            'FROM ad '
        )
        params = ()

        # Фильтрация через query string
        if filters:
            # Формируем набор условий для блока WHERE   TODO валидация условий
            conditions = ''
            for key in filters.keys():
                conditions += f'{key} = "{filters[key]}" AND '
            conditions += 'TRUE'    # Заглушка AND в конце
            print(conditions)
            query += f'''
                JOIN adtag ON adtag.ad_id = ad.id
                JOIN tag ON tag.id = adtag.tag_id
                JOIN car ON car.id = ad.car_id
                JOIN carcolor ON carcolor.car_id = ad.car_id
                JOIN color ON color.id = carcolor.color_id
                WHERE {conditions}
            '''

        # Запрос объявлений продавца по id его аккаунта
        if account_id is not None:
            query += f'''
                WHERE seller_id =
                    (SELECT id FROM seller WHERE id = ?) 
            '''
            params = (account_id,)

        cur = self.connection.execute(query, params)
        ads = cur.fetchall()
        return [dict(ad) for ad in ads]

    # Получение объявления по его id
    def get_ad(self, ad_id):
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