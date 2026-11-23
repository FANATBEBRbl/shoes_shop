# Установка и запуск ShoeStore

Комплект рассчитан на Windows 10/11 x64. Python и IDE для EXE не нужны.
PostgreSQL не входит в EXE: установите Docker Desktop, включите WSL 2,
перезагрузите Windows при запросе и дождитесь запуска Linux Engine.
На хосте приложение использует Tkinter. Контейнерный db-check использует Python 3.10.

## Подготовка базы

В PowerShell перейдите в каталог `deployment` распакованного комплекта:

```powershell
Copy-Item .env.example .env
notepad .env
```

Замените заглушку POSTGRES_PASSWORD своим локальным паролем. Сохраните файл.
Не публикуйте `.env` и не показывайте его на снимках экрана.

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps -a
docker compose run --rm db-check
```

При новой базе db-check показывает ноль таблиц. Только для пустой базы выполните:

```powershell
docker compose cp database/shoe_store.sql db:/tmp/shoe_store.sql
docker compose exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/shoe_store.sql
docker compose run --rm db-check
```

Ожидаются пять таблиц и два учебных товара. При изменении POSTGRES_USER или
POSTGRES_DB замените значения в командах. Не повторяйте импорт в заполненную базу.
Скрипт создания таблиц и данные входят в комплект, как и исходники db-check для сборки.

## Настройка и запуск приложения

Из корня комплекта скопируйте `config.ini.example` в
`application/ShoeStore/config.ini`. Укажите тот же пароль, что в `.env`.
Адрес Windows: `127.0.0.1`, порт `5433`, база `shoe_store`, пользователь `shoe_user`.
Если изменён POSTGRES_HOST_PORT, перенесите его в config.ini.

Откройте `application/ShoeStore/ShoeStore.exe` и нажмите «Войти как гость».
Переносите всю папку ShoeStore вместе с `_internal`. Консоль оставлена для диагностики.
Изображения загружаются из пакета, config.ini читается рядом с EXE.

## Проверка и диагностика

```powershell
docker compose ps -a
docker compose logs --tail=30 db-check
docker compose port db 5432
docker compose run --rm db-check
```

Состояние db должно быть healthy, завершение db-check с кодом 0 нормально.
В контейнере адрес базы `db:5432`, в Windows `127.0.0.1:5433`.
Если Engine недоступен, запустите Docker Desktop. Если порт занят, измените
POSTGRES_HOST_PORT и config.ini. Если отсутствуют изображения, проверьте, что
папка `_internal` перенесена целиком. При ошибке соединения проверьте пароль,
порт, имя базы и её состояние. Пароли в журнал ошибок приложение не выводит.

## Сохранение, резервное копирование и остановка

Данные находятся в именованном томе `shoe-shop_db_data`.
Из deployment выполните:

```powershell
New-Item -ItemType Directory -Force backups
docker compose exec db pg_dump -U shoe_user -d shoe_store -f /tmp/backup.sql
docker compose cp db:/tmp/backup.sql backups/shoe_store.sql
docker compose stop
```

Для продолжения: `docker compose start`. Для пересоздания контейнера с теми же
данными: `docker compose up -d --force-recreate db`. Дождитесь healthy.
`docker compose down` удаляет контейнеры и сеть, сохраняя именованный том.
Не выполняйте `docker compose down -v`: эта команда удаляет том с базой.
Том не заменяет отдельную резервную копию.

Восстанавливать дамп следует в новую пустую базу, а не поверх работающих таблиц:

```powershell
docker compose cp backups/shoe_store.sql db:/tmp/restore.sql
docker compose exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/restore.sql
docker compose run --rm db-check
```
