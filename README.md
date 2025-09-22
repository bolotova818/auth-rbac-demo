# Auth / RBAC Demo  
_Python + FastAPI_

---

##  О проекте

Это учебное демо-приложение на **FastAPI**, где я реализовала систему аутентификации и авторизации с ролевой моделью доступа (RBAC).  
Основная цель — показать умение продумать схему ролей и прав, сделать рабочую авторизацию с токенами и разграничение доступа.  

### Что уже реализовано полностью:
- Регистрация и вход пользователя
- Хранение пароля в захэшированном виде (bcrypt)
- JWT access-токены и refresh-токены
- Возможность обновления access-токена по refresh-токену
- Выход из системы (отзыв refresh-токена) и logout со всех устройств
- Роли (`admin`, `user`)
- Таблица правил доступа (CRUD-флаги)
- Админка: просмотр и изменение правил доступа
- Бизнес-объекты: **просмотр** (админ видит все, пользователь — только свои)

### Что не реализовано до конца(важно!):
- Бизнес-объекты можно только читать (`GET /objects`, `GET /objects/{id}`).
  В коде заложена полноценная система прав (create/update/delete), и даже сиды для этих прав есть, но сами эндпоинты для создания/обновления/удаления я не выводила, чтобы не раздувать проект.  
  То есть «болванка» для CRUD есть, но в прод выведен только просмотр.  

---

##  Стек
- Python 3.11+  
- FastAPI  
- SQLAlchemy  
- PostgreSQL  
- bcrypt(хэширование паролей)  
- PyJWT (JWT-токены)  
- Pydantic  

---

##  Как запустить проект

1. Склонировать репозиторий и перейти в папку проекта:
```bash
git clone https://github.com/bolotova818/auth-rbac-demo.git
cd auth-rbac-demo
```

2. Создать виртуальное окружение и установить зависимости:
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

3. Скопировать `.env.example` в `.env` и указать параметры подключения к базе:
```bash
cp .env.example .env
```

4. Поднять базу данных PostgreSQL (через Docker):
```bash
docker-compose up -d
```

5. Инициализировать таблицы и загрузить тестовые данные:
```bash
python init_db.py
```

6. Запустить приложение:
```bash
uvicorn main:app --reload
```

Документация API будет доступна по адресу:  
 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

##  Тестовые пользователи

После инициализации базы создаются два пользователя:

- **Admin**  
  email: `admin@example.com`  
  password: `admin123`  

- **User**  
  email: `user@example.com`  
  password: `user123`  

---

##  Эндпоинты

### Пользователи
- `POST /users/register` — регистрация  
- `POST /users/login` — вход (access + refresh токены)  
- `POST /users/refresh` — обновление access токена  
- `POST /users/logout` — выход (отзыв refresh токена)  
- `POST /users/logout_all` — выход со всех устройств  
- `PUT /users/me` — обновление профиля  
- `DELETE /users/me` — деактивация аккаунта (is_active=false)  

### Объекты
- `GET /objects` — список объектов  
- `GET /objects/{id}` — получить объект по ID  

 Обновление, создание и удаление объектов **в коде предусмотрены через систему прав**, но в рамках тестового задания я реализовала только просмотр.

### Админка
- `GET /admin/rules` — список правил  
- `PUT /admin/rules` — создать/обновить правило  

---

##  Примеры запросов

Регистрация:
```bash
curl -X POST http://127.0.0.1:8000/users/register \
-H "Content-Type: application/json" \
-d '{"name": "Test", "email": "test@example.com", "password": "123456"}'
```

Логин:
```bash
curl -X POST http://127.0.0.1:8000/users/login \
-H "Content-Type: application/json" \
-d '{"email": "admin@example.com", "password": "admin123"}'
```

Запрос к защищённому эндпоинту:
```bash
curl -X GET http://127.0.0.1:8000/objects \
-H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

##  Контакты
Автор: *Анастасия  
Email: bolotova818@gmail.com
тг: @ban_any
