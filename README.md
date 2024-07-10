# Flask приложение с PostgreSQL в Docker





## Установка и запуск приложения


1. Склонируйте репозиторий:
   ```sh
   git clone https://github.com/Jduun/file-storage.git
   cd file-storage/
   ```
   
2. **Настройка переменных окружения:**

    Создайте `.env` в корневой директории проекта в соответствии с `.env.example`.

3. **Сборка и запуск Docker контейнеров:**

      ```sh
      docker-compose up --build
      ```

4. **Проверка работоспособности:**

   Откройте браузер и перейдите по адресу `http://localhost:5000`. Вы увидите запущенное надпись "Hello, world!".

