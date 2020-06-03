from exceptions import ServiceError
from werkzeug.security import check_password_hash


class AuthServiceError(ServiceError):
    service = 'auth'


class AuthorizationFailedError(AuthServiceError):
    pass


class SellerDoesNotExistError(AuthServiceError):
    pass


class AuthService:
    def __init__(self, connection):
        self.connection = connection

    def login(self, email, password):
        """
        Метод авторизации пользователя.
        :param email: логин (e-mail)
        :param password: пароль
        :return: идентификатор пользователя
        """
        query = (
            'SELECT id, password '
            'FROM account '
            'WHERE email = ?'
        )
        params = (email,)
        cur = self.connection.execute(query, params)
        account = cur.fetchone()
        if account is None:
            raise AuthorizationFailedError(email)
        if not check_password_hash(account['password'], password):
            raise AuthorizationFailedError(email)
        return account['id']

    def get_seller(self, account_id):
        """
        Метод получения идентификатора продавца по идентификатоу пользователя.
        :param account_id: идентификатор пользователя
        :return: идентификатор продавца
        """
        query = (
            'SELECT id '
            'FROM seller '
            'WHERE account_id = ?'
        )
        params = (account_id,)
        cur = self.connection.execute(query, params)
        seller = cur.fetchone()
        if seller is None:
            raise SellerDoesNotExistError(account_id)
        return seller['id']
