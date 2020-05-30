from exceptions import ServiceError


class AdsServiceError(ServiceError):
    service = 'ads'


class AdDoesNotExistError(AdsServiceError):
    pass


class AdsService:
    def __init__(self, connection):
        self.connection = connection

    def get_ads(self, account_id=None):
        query = (
            'SELECT * '
            'FROM ad '
        )
        params = ()
        if account_id is not None:
            query += 'WHERE seller_id = ?'
            params = (account_id,)              # TODO искать id продавца по id аккаунта
        cur = self.connection.execute(query, params)
        ads = cur.fetchall()
        return [dict(ad) for ad in ads]

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