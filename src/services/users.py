import sqlite3 as sqlite
from exceptions import ServiceError
from werkzeug.security import generate_password_hash


class UsersServiceError(ServiceError):
    service = 'user'


class RegistrationFailedError(UsersServiceError):
    pass


class UserService:
    def __init__(self, connection):
        self.connection = connection

    def create_user(self, new_user):
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
