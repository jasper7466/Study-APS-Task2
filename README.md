# Study-APS-Task2
Antida Python School. Итоговое задание второго блока. Учебный проект "REST API для сайта объявлений".

## Формулировка задания

Реализовать REST API сервиса по продаже автомобилей. За основу взять предметную область, описанную в курсе "Базы данных".

**Описание API:**

<details>
  <summary>Авторизация пользователя. Вход и выход</summary>
  
  ```javascript
  POST /auth/login
  ```
  ```javascript
  Request:
  {
    "email": str,
    "password": str
  }
  ```
  ```javascript
  POST /auth/logout
  ```
</details>

<details>
  <summary>Регистрация пользователя</summary>
  
  Поле is_seller показывает, является ли пользователь продавцом. Поля phone, zip_code, city_id, street, home указываются, только если пользователь является продавцом.
  ```javascript
  POST /users
  ```
  ```javascript
  Request:
  {
    "email": str,
    "password": str,
    "first_name": str,
    "last_name": str,
    "is_seller": bool,
    "phone": str?,
    "zip_code": int?,
    "city_id": int?,
    "street": str?,
    "home": str?
  }
  Response:
  {
    "id": int,
    "email": str,
    "first_name": str,
    "last_name": str,
    "is_seller": bool,
    "phone": str?,
    "zip_code": int?,
    "city_id": int?,
    "street": str?,
    "home": str?
  }
  ```
</details>

<details>
  <summary>Получение пользователя</summary>
  Доступно только авторизованным пользователям.
  
  ```javascript
  GET /users/<id>
  ```
  ```javascript
  Response:
  {
    "id": int,
    "email": str,
    "first_name": str,
    "last_name": str,
    "is_seller": bool,
    "phone": str?,
    "zip_code": int?,
    "city_id": int?,
    "street": str?,
    "home": str?
  }
  ```
</details>

<details>
  <summary>Частичное редактирование пользователя</summary>
  Доступно только текущему авторизованному пользователю. Поля phone, zip_code, city_id, street, home указываются, только если пользователь является продавцом. При установке флага is_seller в false должно происходить удаление сущностей продавца.
  
  ```javascript
  PATCH /users/<id>
  ```
  ```javascript
  Request:
  {
    "first_name": str?,
    "last_name": str?,
    "is_seller": bool?,
    "phone": str?,
    "zip_code": int?,
    "city_id": int?,
    "street": str?,
    "home": str?
  }
  Response:
  {
    "id": int,
    "email": str,
    "first_name": str,
    "last_name": str,
    "is_seller": bool,
    "phone": str?,
    "zip_code": int?,
    "city_id": int?,
    "street": str?,
    "home": str?
  }
  ```
</details>

<details>
  <summary>Получение списка объявлений</summary>
  Объявления: все и принадлежащих пользователю. Список можно фильтровать с помощью query string параметров, все параметры необязательные.
  
  ```javascript
  GET /ads
  ```
  ```javascript
  GET /users/<id>/ads
  Query string:
    seller_id: int?
    tags: str?
    make: str?
    model: str?
  Response:
  [
    {
      "id": int,
      "seller_id": int,
      "title": str,
      "date": str,
      "tags:": [str], // Список тегов строками
      "car": {
        "make": str,
        "model": str,
        "colors": [
          {
            "id": int,
            "name": str,
            "hex": str
          }
        ],
        "mileage": int,
        "num_owners": int,
        "reg_number": str,
        "images": [
          {
            "title": str,
            "url": str
          }
        ]
      }
    }
  ]
  ```
</details>

<details>
  <summary>Публикация объявления</summary>
  Доступно только авторизованным пользователям. Доступно только если пользователь является продавцом.
  
  ```javascript
  POST /ads
  ```
  ```javascript
  POST /users/<id>/ads
  ```
  ```javascript
  Request:
  {
    "title": str,
    "tags": [str, ...], // Список тегов строками
    "car": {
      "make": str,
      "model": str,
      "colors": [int], // Список ID цветов
      "mileage": int,
      "num_owners": int?,
      "reg_number": str,
      "images": [
        {
          "title": str,
          "url": str
        }
      ]
    }
  }
  Response:
  [
    {
      "id": int,
      "seller_id": int,
      "title": str,
      "date": str,
      "tags:": [str], // Список тегов строками
      "car": {
        "make": str,
        "model": str,
        "colors": [
          {
            "id": int,
            "name": str,
            "hex": str
          }
        ],
        "mileage": int,
        "num_owners": int,
        "reg_number": str,
        "images": [
          {
            "title": str,
            "url": str
          }
        ]
      }
    }
  ]
  ```
</details>

<details>
  <summary>Получение объявления</summary>
  
  ```javascript
  GET /ads/<id>
  ```
  ```javascript
  Response:
  {
    "id": int,
    "seller_id": int,
    "title": str,
    "date": str,
    "tags:": [str], // Список тегов строками
    "car": {
      "make": str,
      "model": str,
      "colors": [
        {
          "id": int,
          "name": str,
          "hex": str
        }
      ],
      "mileage": int,
      "num_owners": int,
      "reg_number": str,
      "images": [
        {
          "title": str,
          "url": str
        }
      ]
    }
  }
  ```
</details>

<details>
  <summary>Частичное редактирование объявления</summary>
  Доступно только авторизованным пользователям. Может совершать только владелец объявления.
  
  ```javascript
  PATCH /ads/<id>
  ```
  ```javascript
  Request:
  {
    "title": str?,
    "tags": [str]?, // Список тегов строками
    "car": {
      "make": str?,
      "model": str?,
      "colors": [int]?, // Список ID цветов
      "mileage": int?,
      "num_owners": int?,
      "reg_number": str?,
      "images": [
        {
          "title": str,
          "url": str
        }
      ]?
    }
  }
  ```
</details>

<details>
  <summary>Удаление объявления</summary>
  Доступно только авторизованным пользователям. Может совершать только владелец объявления.
  
  ```javascript
  DELETE /ads/<id>
  ```
</details>

<details>
  <summary>Получение списка городов</summary>
  
  ```javascript
  GET /cities
  ```
  ```javascript
  Response:
  [
    {
      "id": int,
      "name": str
    }
  ]
  ```
</details>

<details>
  <summary>Создание города</summary>
  При попытке создать уже существующий город (проверка по названию), должен возвращаться существующий объект.
  
  ```javascript
  POST /cities
  ```
  ```javascript
  Request:
  {
    "name": str
  }
  Response:
  {
    "id": int,
    "name": str
  }
  ```
</details>

<details>
  <summary>Получение списка цветов</summary>
  Доступно только авторизованным пользователям. Доступно только если пользователь является продавцом.
  
  ```javascript
  GET /colors
  ```
  ```javascript
  Response:
  [
    {
      "id": int,
      "name": str,
      "hex": str
    }
  ]
  ```
</details>

<details>
  <summary>Создание цвета</summary>
  Доступно только авторизованным пользователям. Доступно только если пользователь является продавцом. При попытке создать уже существующий цвет (проверка по названию), должен возвращаться существующий объект.
  
  ```javascript
  POST /colors
  ```
  ```javascript
  Request:
  {
    "name": str,
    "hex": str
  }
  Response:
  {
    "id": int,
    "name": str,
    "hex": str
  }
  ```
</details>

<details>
  <summary>Загрузка изображения</summary>
  Доступно только авторизованным пользователям. Доступно только если пользователь является продавцом.
  
  ```javascript
  POST /images
  ```
  ```javascript
  Request:
    файл изображения в поле формы file
  Response:
  {
    "url": str
  }
  ```
</details>

<details>
  <summary>Получение изображения</summary>
  
  ```javascript
  GET /images/<name>
  ```
  ```javascript
  Response:
    файл изображения
  ```
</details>

**Требования:**

- Приложение должно быть реализовано с помощью web-фреймворка Flask.
- Следуйте Python Zen: код должен быть минималистичным, лаконичным, но хорошо читаемым.
- Документирование модулей, функций, классов.
- Соблюдение PEP8 рекомендаций по стилевому оформлению кода.
- Исходный код решения должен быть загружен в систему контроля версий и опубликован на github, в качестве решения нужно приложить ссылку на репозиторий.
- В репозитории должен присутствовать файл requirements.txt со списком зависимостей и файл README.md с инструкцией по запуску приложения.

**Примечания:**

- Запросы и ответы представлены в JSON-подобной структуре и описывают JSON-документы
- Через двоеточие указываются типы полей
- Запись вида type? обозначает, что поле необязательное и может отсутствовать
- Запись вида [type] обозначает список значений типа type
- При тестировании приложения гарантируется корректность входных данных.

## Краткое описание и инструкция по использованию

Проект представляет собой приложение, написанное на языке Python с применением web-фреймворка Flask

## Актуальная версия

 - Версия: [v0.0.2](https://github.com/jasper7466/Study-APS-Task2/tree/v0.0.2)

## Как развернуть проект

Для запуска приложения, в системе должен быть установлен интерпретатор [Python](https://www.python.org/downloads/) версии 3.8 или новее. Совместимость с более ранними версиями не гарантируется.

**1. Виртуальное окружение** *(опционально)*
Разработку рекомендуется вести в изолированном режиме из под виртуального окружения. Для его установки потребуется установить пакет [virtualenv](https://pypi.org/project/virtualenv/):

`$ pip install virtualenv`

**2. Клонирование проекта**
Чтобы клонировать проект на локально - вызовите интерфейс командной строки (например, [Git Bash](https://gitforwindows.org)) в желаемой директории, выполните команду:

`$ git clone https://github.com/jasper7466/Study-APS-Task2.git`

и перейдите в директорию проекта:

`$ cd ./Study-APS-Task2`

**3. Установка виртуального окружения** *(опционально)*

`$ python -m virtualenv venv`

**4. Активация виртуального окружения** *(опционально)*

`$ . venv/Scripts/activate`

**5. Установка паетов из зависимостей**
Зависимости зафиксированы в файле `requirements.txt`. Для их автоматической установки достаточно выполнить команду:

`$ pip install -r requirements.txt`

*Примечание: если работа ведётся не из под venv - пакеты установятся в систему*

**6. Установка переменных окружения** 
Добавление в PYTHONPATH пути до корня приложения (где лежит модуль app.py):

`$ export PYTHONPATH=./src` (или `set PYTHONPATH=./src`)

Установка пути до приложения относительно PYTHONPATH в переменную окружения FLASK_APP:

`$ export FLASK_APP=app:create_app` (или `set FLASK_APP=app:create_app`)

Для запуска в режиме отладки следует устанавить переменную окружения FLASK_ENV в значение "development":

`$ export FLASK_ENV=development` (или `set FLASK_ENV=development`)

При такой настройке:
- сервер будет запущен в режиме автоматической "горячей" перезагрузки приложения при детектировании изменений в его исходных кодах
- при возникновении ошибок в браузере будет выводиться stack trace

Установку переменных окружения и некоторых других переменных параметров при каждом запуске приложения можно избежать, добавив в корневую директорию проекта файлы `.env` и `.flaskenv` следующего содержания:

*.env:*
```
DB_CONNECTION = example.db
SECRET_KEY = secret_key
```

*.flaskenv:*
```
PYTHONPATH = ./src
FLASK_APP = app:create_app
FLASK_ENV = development
```

Указанные в этих файлах параметры будут автоматически подтягиваться и применяться с помощью пакета [python-dotenv](https://pypi.org/project/python-dotenv/)

**7. Запуск приложения**
Для запуска приложения в настроенном на предыдущем шаге режиме выполните команду:

`$ flask run`

**8. Фиксирование зависимостей**
После завершения доработки проекта, в случае добаления новых пакетов - следует зафиксировать зависимости, обновив файл `requirements.txt`. Это можно сделать автоматически, выполнив команду:

`$ pip freeze > requirements.txt`

Команду имеет смысл выполнять из под виртуального окружения, если оно используется. В противном случае будут подтянуты все локальные пакеты из системы.

## Технологии

 - Python
 - Flask
 - HTTP
 - REST API
 - Sqlite

## Известные проблемы и что можно улучшить

- Реализована только часть требуемых интерфейсы. Некоторые реализованы частично или находятся в состоянии заготовки.
- Местами присутствует дублирование кода
- Код не покрыт автоматическими тестами