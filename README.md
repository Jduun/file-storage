# File Storage

Приложение написано на фреймфорке Flask с использованием базы данных PostgreSQL.

## Установка
Склонируйте репозиторий и перейдите в папку с проектом:
```sh
git clone https://github.com/Jduun/file-storage.git
cd file-storage/
```
Сделайте копию файла `.env.example`:
```sh 
cp .env.example .env
```
С помощью текстового редактора откройте `.env` файл и установите собственные значения для переменных окружения.
Подробнее о переменных окружения:

| Переменная             | Пример значения       | Назначение                                                |
| ---------------------- |-----------------------|-----------------------------------------------------------|
| **POSTGRES\_USER**     | `postgres`            | Имя пользователя базы данных PostgreSQL                   |
| **POSTGRES\_PASSWORD** | `12345`               | Пароль пользователя PostgreSQL                            |
| **POSTGRES\_HOST**     | `file-storage-db`     | Хост или имя контейнера, где запущен PostgreSQL           |
| **POSTGRES\_DB**       | `postgres`            | Имя базы данных PostgreSQL, к которой подключается приложение |
| **POSTGRES\_PORT**     | `5432`                | Порт PostgreSQL                                           |
| **POSTGRES\_FOLDER**   | `/data/postgres_data` | Локальный путь/папка для хранения данных PostgreSQL       |
| **APP\_PORT**          | `5000`                | Порт, на котором запускается само приложение              |
| **ROOT\_FOLDER**       | `/data/root_folder`   | Папка для хранения файлов, которые загружают пользователи |
| **DEBUG**              | `False`               | Режим отладки: `True` в разработке и `False` в продакшене |

Сборка приложения:
```sh
docker build -t file-storage:latest .
docker-compose up --build
```

---

## API
### Загрузка файла
**Запрос**: `POST /api/files` `multipart/form-data`
- `file`: `Шаблоны корпоративных прилож.pdf`
- `json`: `{"filepath": "/books/", "comment": "Learn patterns"}` 

**Ответ**: `application/json` `200 OK`
```json
{
    "comment": "Do you know what linked list is?",
    "created_at": "Wed, 17 Sep 2025 07:31:12 GMT",
    "extension": ".pdf",
    "filename": "Шаблоны корпоративных прилож",
    "filepath": "/books/",
    "id": 13,
    "size_bytes": 57034527,
    "updated_at": "Wed, 17 Sep 2025 07:31:12 GMT"
}
```

### Получение всех файлов
**Запрос**: `GET /api/files`

**Ответ**: `application/json` `200 OK`
```json
[
    {
        "comment": "Do you know what linked list is?",
        "created_at": "Wed, 17 Sep 2025 07:28:29 GMT",
        "extension": ".pdf",
        "filename": "grokaem_algoritmyi",
        "filepath": "/books/",
        "id": 12,
        "size_bytes": 72825117,
        "updated_at": "Wed, 17 Sep 2025 07:28:29 GMT"
    },
    {
        "comment": "Learn patterns",
        "created_at": "Wed, 17 Sep 2025 07:31:12 GMT",
        "extension": ".pdf",
        "filename": "Шаблоны корпоративных прилож",
        "filepath": "/books/",
        "id": 13,
        "size_bytes": 57034527,
        "updated_at": "Wed, 17 Sep 2025 07:31:12 GMT"
    }
]
```
### Получение файла по `id`
**Запрос**: `GET /api/files/12`

**Ответ**: `application/json` `200 OK`
```json
{
    "comment": "Do you know what linked list is?",
    "created_at": "Wed, 17 Sep 2025 07:28:29 GMT",
    "extension": ".pdf",
    "filename": "grokaem_algoritmyi",
    "filepath": "/books/",
    "id": 12,
    "size_bytes": 72825117,
    "updated_at": "Wed, 17 Sep 2025 07:28:29 GMT"
}
```

### Обновление информации о файле
**Запрос**: `PUT /api/files/12` `application/json`
```json
{
    "comment": "Book about algorithms",
    "filename": "grokaem",
    "filepath": "/algorithms/"
}
```

**Ответ**: `application/json` `200 OK`
```json
{
    "comment": "Book about algorithms",
    "created_at": "Wed, 17 Sep 2025 07:28:29 GMT",
    "extension": ".pdf",
    "filename": "grokaem",
    "filepath": "/algorithms/",
    "id": 12,
    "size_bytes": 72825117,
    "updated_at": "Wed, 17 Sep 2025 07:28:29 GMT"
}
```

### Удаление файла
**Запрос**: `DELETE /api/files/12`

**Ответ**: `application/json` `200 OK`
```json
{
    "comment": "Book about algorithms",
    "created_at": "Wed, 17 Sep 2025 07:28:29 GMT",
    "extension": ".pdf",
    "filename": "grokaem",
    "filepath": "/algorithms/",
    "id": 12,
    "size_bytes": 72825117,
    "updated_at": "Wed, 17 Sep 2025 07:42:19 GMT"
}
```

### Скачивание файла
**Запрос**: `GET /api/files/13/download`