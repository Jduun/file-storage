# File Storage

## Установка

### docker-compose.yml
```yaml
services:
  file-storage:
    image: file-storage:latest
    restart: unless-stopped
    volumes:
      - /root_folder:/root_folder
    ports:
      - "5000:80"
    env_file:
      - .env

  file-storage-db:
    image: postgres:13
    restart: unless-stopped
    environment:
      POSTGRES_USER: "postgres"
      POSTGRES_PASSWORD: "postgres"
      POSTGRES_DB: "postgres"
    volumes:
      - /postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

### Пояснение к архитектуре
`file-storage` - Flask приложение, предоставляющее API для работы с файлами

`file-storage-db` - база данных PostgreSQL 

### config.yaml
```yaml
root_folder: "/root_folder"
debug: false

postgres:
  user: "postgres"
  password: "postgres"
  host: "file-storage-db"
  db: "postgres"
```

### Переменные окружения
- `APP_PORT=80`
- `APP_HOST=0.0.0.0`
- `YAML_PATH=/app/src/config/config.yaml`

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

**Ошибки**:
- `400`- указан некорректный путь; файл уже существует

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

**Ошибки**:
- `404` - файл не найден

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

**Ошибки**:
- `400` - файл с таким именем уже существует; указан некорректный путь; файл уже существует в этой директории 
- `404`- файл не найден
- `500` - ошибка ОС при переименовании или перемещении файла

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

**Ошибки**: 
- `404`- файл не найден
- `500` - ошибка ОС при удалении файла

### Скачивание файла
**Запрос**: `GET /api/files/13/download`