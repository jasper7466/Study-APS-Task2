import sqlite3 as sqlite
from exceptions import ServiceError
from werkzeug.security import generate_password_hash


class UsersServiceError(ServiceError):
    service = 'users'


class RegistrationFailedError(UsersServiceError):
    pass


class UserDoesNotExistError(UsersServiceError):
    pass


class UserUpdateFailedError(UserDoesNotExistError):
    pass


class UserService:
    def __init__(self, connection):
        self.connection = connection

    def create_user(self, new_user):
        """
        Метод создания пользователя
        :param new_user: параметры нового пользователя
        :return: новый пользователь
        """
        password_hash = generate_password_hash(new_user['password'])
        query_user = (
            'INSERT INTO account (email, password, first_name, last_name) '
            'VALUES (?, ?, ?, ?)'
        )
        query_seller = (
            'INSERT INTO seller (phone, zip_code, street, home, account_id) '
            'VALUES (?, ?, ?, ?, ?)'
        )
        params_user = (
            new_user['email'],
            password_hash,
            new_user['first_name'],
            new_user['last_name']
        )
        try:
            self.connection.execute('PRAGMA foreign_keys = ON')
            cur = self.connection.execute(query_user, params_user)
            account_id = cur.lastrowid
            if new_user['is_seller']:
                params_seller = (
                    new_user['phone'],
                    new_user['zip_code'],
                    new_user['street'],
                    new_user['home'],
                    account_id
                )
                self.connection.execute(query_seller, params_seller)
        except sqlite.IntegrityError:
            self.connection.rollback()
            raise RegistrationFailedError(new_user['email'])
        else:
            del new_user['password']
            new_user['id'] = account_id
            return new_user

    def get_user(self, account_id):
        """
        Метод получения данных пользователя.
        :param account_id: идентификатор пользователя
        :return: данные пользователя
        """
        query_user = (
            'SELECT id, email, first_name, last_name '
            'FROM account '
            'WHERE id = ?'
        )
        query_seller = (
            'SELECT phone, zip_code, street, home, account_id '
            'FROM seller '
            'WHERE account_id = ?'
        )
        params = (account_id,)

        cur = self.connection.execute(query_user, params)
        account = cur.fetchone()
        if account is None:
            raise UserDoesNotExistError(account_id)
        account = dict(account)
        account['is_seller'] = False

        cur = self.connection.execute(query_seller, params)
        seller = cur.fetchone()
        if seller is not None:
            seller = dict(seller)
            account['is_seller'] = True
            account = {**account, **seller}
        return account

    def edit_user(self, account_id, data):
        """
        Метод частичного редактирования пользователя
        :param account_id: идентификатор пользователя
        :param data: обновляемые параметры
        :return: данные пользователя
        """
        user = ('first_name', 'last_name')
        seller = ('zip_code', 'city_id', 'street', 'home')

        self.connection.execute('PRAGMA foreign_keys = ON')

        try:
            # Редактирование пользователя
            for key in user:
                try:
                    if data[key] is not None:
                        self.connection.execute(f'UPDATE account SET {key} = "{data[key]}" WHERE id = {account_id}')
                except KeyError:
                    pass

            # Редактирование продавца
            if data['is_seller']:
                for key in seller:
                    try:
                        if data[key] is not None:
                            self.connection.execute(f'''
                                UPDATE seller
                                SET {key} = "{data[key]}"
                                WHERE account_id = {account_id}
                            ''')
                    except KeyError:
                        pass

            # Удаление объявлений и сущности продавца
            if not data['is_seller']:
                self.connection.execute(f'''
                    DELETE FROM ad WHERE seller_id = 
                        (SELECT id FROM seller WHERE id = "{account_id}")
                ''')
                self.connection.execute(f'DELETE FROM seller WHERE account_id = "{account_id}"')
        except sqlite.IntegrityError:
            self.connection.rollback()
            raise UserUpdateFailedError()
        self.connection.commit()

        # Получение данных пользователя для формирования ответа
        cur = self.connection.execute(f'''
            SELECT id, email, first_name, last_name
            FROM account
            WHERE id = "{account_id}"
        ''')
        account = cur.fetchone()
        account = dict(account)
        account['is_seller'] = False

        # Получение данных продавца для формирования ответа
        cur = self.connection.execute(f'''
            SELECT seller.phone, seller.zip_code, zipcode.city_id, seller.street, seller.home
            FROM seller
                JOIN zipcode ON zipcode.zip_code = seller.zip_code 
            WHERE account_id = "{account_id}"
        ''')
        seller = cur.fetchone()

        # Формирование ответа
        if seller is not None:
            seller = dict(seller)
            account['is_seller'] = True
            account = {**account, **seller}
        return account
