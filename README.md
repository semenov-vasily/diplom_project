REST API интернет-магазина – это полнофункциональный серверный сервис, разработанный для управления платформой электронной коммерции. Он предоставляет пользователям, клиентам и администраторам возможность взаимодействовать с основными функциями магазина, такими как товары, заказы и профили клиентов, посредством надежных и эффективных API-эндпоинтов. Построенный на Django Rest Framework (DRF), этот API оптимизирован для высокопроизводительных и масштабируемых веб-приложений, обеспечивая плавное и бесперебойное взаимодействие между фронтендом и бэкендом.

В проекте создана админ-панель для оперативного управления информацией в базе данных
При переходе на Products, можно дописать к URL-адресу /bulk-update/ и открыть форму массового изменения цены.

Также созданы юнит-тесты которые проверяют работоспособность API-эндпоинтов.
В частности, тест регистрирует и авторизует пользователя,
создаёт тестовый товар, а затем отправляет запрос GET к эндпоинту
/products/ и проверяет, что в ответе возвращается список с хотя
бы одним товаром.

Данные хранятся в БД Postgersql внутри контейнера.
Предусмотрен healthcheck для проверки доступности базы данных на уровне docker-compose.

Отправка е-мейл сообщений реализована с помощью celery
Внедрен drf-spectacular для удобного сваггера

### Запускаем базу данных
```bash
docker-compose up -d
```

### Формируем и запускаем миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

### Импортируем данные о товарах
```bash
python manage.py import_products
```

### Создаем суперпользователя для работы в админ-панели
```bash
python manage.py createsuperuser
```

### Cтартуем сервер
```bash
python manage.py runserver
```

### Стартуем Celery
#### в другом терминале:
```bash
celery -A e_shop worker -l info
```

### По адресу http://127.0.0.1:8000/api/schema/swagger-ui/ доступен Swagger UI
### По адресу http://127.0.0.1:8000/api/schema/redoc/ - Redoс   
### По адресу JSON/YAML схема по адресу http://127.0.0.1:8000/api/schema/ - JSON/YAML схема

### Создаем клиента магазина
```bash
curl -X POST http://127.0.0.1:8000/register/ \
    -H "Content-Type: application/json" \
    -d '{
        "username": "client1",
        "email": "cleint1@domain.com",
        "password": "12345"
    }'
```
response:
{"message":"Пользователь успешно создан"}

### Логин клиента и получение токена
```bash
curl -X POST http://127.0.0.1:8000/api-token-auth/ \
    -H "Content-Type: application/json" \
    -d '{
        "username": "client1",
        "password": "12345"
    }'
```
response:
{"token":"823d00aaf2a4065e601f70d31a90058b7580b138"}

### получаем список товаров
```bash
curl -X GET http://127.0.0.1:8000/products/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138"
```
response:
[{"id":1,"name":"Смартфон Apple iPhone XS Max 512GB (золотистый)","description":"","supplier":1,"price":"110000.00","quantity":14,"parameters":{"Диагональ (дюйм)":6.5,"Разрешение (пикс)":"2688x1242","Встроенная память (Гб)":512,"Цвет":"золотистый"}}, ...

### Получаем информацию о конкретном товаре
```bash
curl -X GET http://127.0.0.1:8000/products/\1/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138"
```
response:
{"id":1,"name":"Смартфон Apple iPhone XS Max 512GB (золотистый)","description":"","supplier":1,"price":"110000.00","quantity":14,"parameters":{"Диагональ (дюйм)":6.5,"Разрешение (пикс)":"2688x1242","Встроенная память (Гб)":512,"Цвет":"золотистый"}}

### Кладем товар в корзину
```bash
curl -X POST http://127.0.0.1:8000/cart/ \
    -H "Authorization: Token your-auth-token-here" \
    -H "Content-Type: application/json" \
    -d '{
        "product": 1,
        "quantity": 5
    }'
```
response:
{"id":2,"user":4,"product":1,"quantity":2}

### Просмотр корзины
```bash
curl -X GET http://127.0.0.1:8000/cart/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138"
```
response:
[{"id":2,"user":3,"product":1,"quantity":5}]

### Подтверждаем заказ
```bash
curl -X POST http://127.0.0.1:8000/orders/confirm/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138" \
    -H "Content-Type: application/json" \
    -d '{
        "cart_id": 2,
        "contact_id": 3
    }'
```
response:
{"status":"Заказ успешно подтвержден","order_id":8}

### Список заказов
```bash
curl -X GET http://127.0.0.1:8000/orders/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138"
``` 
response:
[{"id":6,"customer":4,"created_at":"2025-03-15T15:22:56.651235Z","updated_at":"2025-03-15T15:22:56.651235Z","contact":null,"items":[{"product":1,"quantity":2,"price":"110000.00"},{"product":3,"quantity":1,"price":"65000.00"}]}, ...]

### Информация о заказе
```bash
curl -X GET http://127.0.0.1:8000/orders/6/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138"
``` 
response:
{"id":6,"customer":4,"contact":null,"created_at":"2025-03-15T15:22:56.651235Z","updated_at":"2025-03-15T15:22:56.651235Z","status":"pending","items":[{"product":1,"quantity":2,"price":"110000.00"},{"product":3,"quantity":1,"price":"65000.00"}]}

### Изменение статуса заказа
```bash
curl -X PATCH http://127.0.0.1:8000/orders/1/update-status/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138" \
    -H "Content-Type: application/json" \
    -d '{
        "status": "shipped"
    }'
```
response:
{"status":"Статус заказа обновлен на shipped"}


## Добавляем контакт
```bash
curl -X POST http://127.0.0.1:8000/contacts/ \
    -H "Authorization: Token your-auth-token-here" \
    -H "Content-Type: application/json" \
    -d '{
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "ivan.ivan@mail.ru",
        "phone": "+79062332211",
        "address": "Калуга, ул. Ленина, д. 1 кв 1"
    }'
```
response:
{"id":5,"first_name":"Иван","last_name":"Иванов","email":"ivan.ivan@mail.ru","phone":"+79062332211","address":"Калуга, ул. Ленина, д. 1 кв 1"}

### Обновляем контакт
```bash
curl -X POST http://127.0.0.1:8000/contacts/ \
    -H "Authorization: Token <your_token>" \
    -H "Content-Type: application/json" \
    -d '{
        "id": 5,
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "ivan.ivan@mail.ru",
        "phone": "+79062332211",
        "address": "Калуга, ул. Маркса, д. 1 кв 1"
    }'
```
response:
{"id":5,"first_name":"Иван","last_name":"Иванов","email":"ivan.ivan@mail.ru","phone":"+79062332211","address":"Калуга, ул. Маркса, д. 1 кв 1"}
### Просмотр контактов
```bash
curl -X GET http://127.0.0.1:8000/contacts/ \
    -H "Authorization: Token your-auth-token-here"
```
response:
{"id":5,"first_name":"Иван","last_name":"Иванов","email":"ivan.ivan@mail.ru","phone":"+79062332211","address":"Калуга, ул. Ленина, д. 1 кв 1"}


### Удаляем контакт
```bash
curl -X DELETE http://127.0.0.1:8000/contacts/5/ \
    -H "Authorization: Token 823d00aaf2a4065e601f70d31a90058b7580b138"
```
