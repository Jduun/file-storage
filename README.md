# File Storage

Приложение написано на фреймфорке Flask с использованием базы данных PostgreSQL.

## Установка и запуск приложения


1. Склонируйте репозиторий:
   ```sh
   git clone https://github.com/Jduun/file-storage.git
   cd file-storage/
   ```
   
2. **Настройка переменных окружения:**

    Создайте и заполните `.env` в корневой директории проекта в соответствии с примером `.env.example`

3. **Сборка и запуск Docker контейнеров:**

      ```sh
      docker-compose up --build
      ```
   
4. **Проверка работоспособности:**

   Загрузите файл в хранилище:
   ```sh
   curl -X POST http://localhost:5000/files \
        -F "file=@/path/to/your/file" \
        -F "json={\"filepath\":\"/storage/folder/\", \"comment\":\"my comment\"}"
   ```
   
   Проверьте появился ли он в хранилище:
   ```sh
   curl -X GET http://localhost:5000/files
   ```
   Чтобы проверить работоспособность RabbitMQ, запустите ```app/script.py``` и перейдите на ```http://localhost:15672``` для взаимодействия с веб интерфейсом RabbitMQ и отслеживания активности.
5. **Тестирование приложения**

   Создайте и заполните `.env.dev` в корневой директории проекта в соответствии с примером `.env.example`.   
   Тестирование приложения производится в отдельных docker-контейнерах:
   ```sh
   docker-compose -f docker-compose.dev.yml --env-file .env.dev up --build
   ```