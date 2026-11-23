# ShoeShop — магазин обуви

Учебное настольное приложение на Python и Tkinter с базой данных PostgreSQL.

## Возможности

- Гостевой просмотр каталога обуви, цен, скидок и остатков.
- Поиск, фильтрация и сортировка товаров для менеджера и администратора.
- Просмотр и управление заказами для менеджера и администратора.
- Добавление, редактирование и удаление товаров администратором.

## Требования

- Python 3.10 или новее с Tkinter.
- PostgreSQL. Для проверки на Windows нужны команды `psql` и `createdb`.
- Библиотеки из `requirements.txt`.

## Установка и запуск в PowerShell

Откройте терминал в корне клонированного репозитория.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item config.ini.example config.ini
```

Используйте отдельную пустую базу. Замените `shoe_user` на имя существующей локальной роли PostgreSQL с правом создания базы либо попросите администратора PostgreSQL создать пустую базу, назначив эту роль владельцем.

```powershell
createdb -h localhost -p 5432 -U shoe_user shoe_store
$env:PGCLIENTENCODING = 'UTF8'
psql -h localhost -p 5432 -U shoe_user -d shoe_store -v ON_ERROR_STOP=1 -f database/shoe_store.sql
```

Укажите в локальном `config.ini` параметры созданной базы и пароль роли. Данные учебного каталога загружаются из SQL. На экране входа выберите «Войти как гость». Учётные записи для ролей с расширенными правами добавляются администратором в отдельной учебной базе.

```powershell
.\.venv\Scripts\python.exe login_window.py
```

Проект предназначен для учебной среды. В исходной логике приложения пароли пользователей сравниваются напрямую со значениями из таблицы `users`. Используйте только вымышленные учётные данные.

## Структура

- `login_window.py` — вход и гостевой режим.
- `main_window.py`, `orders_window.py`, `order_editor.py`, `product_editor.py` — окна приложения.
- `database.py`, `db_config.py` — SQL-запросы и загрузка локальных настроек.
- `static/` — изображения и иконки.
- `database/` — схема базы и вымышленные товары.
- `docs/` — документация базы.
- `tests/` — тесты построения SQL-запросов.

## ER-диаграмма базы данных

[ER-диаграмма PostgreSQL](docs/er-diagram.pdf) показывает таблицы `users`,
`product`, `pick_up`, `orders` и `orders_items`.

- `orders.user_id` и `orders.pick_up_id` указывают на пользователя и пункт выдачи.
- `orders_items.order_id` указывает на заказ. Один заказ может содержать несколько позиций.
- `orders_items.product_id` указывает на товар. Одна модель может встречаться в нескольких позициях заказов.

Первичные и внешние ключи определены в `database/shoe_store.sql`.

## Автор

Леонов Никита, группа ЩПКО-03-23.

## Запуск PostgreSQL через Docker Compose

Установите Docker Desktop с WSL 2 и Linux Engine. После включения компонентов
Windows может понадобиться перезагрузка. Полная инструкция для комплекта поставки:
[INSTALL.md](INSTALL.md).

```powershell
Copy-Item .env.example .env
# Укажите собственный локальный пароль в .env.
docker compose config --quiet
docker compose up --build -d
docker compose ps -a
docker compose run --rm db-check
```

Только для новой пустой базы:

```powershell
docker compose cp database/shoe_store.sql db:/tmp/shoe_store.sql
docker compose exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/shoe_store.sql
docker compose run --rm db-check
```

В Windows используйте `127.0.0.1:5433`, внутри Compose — `db:5432`.
Образец config.ini теперь рассчитан на Docker; для отдельно установленного
PostgreSQL замените порт на фактический (обычно 5432).
Одноразовый db-check завершается с кодом 0, PostgreSQL продолжает работать.
Изолированный контекст сборки — `docker/db-check`.

`compose.practice12.yaml` сохраняет этап №12 без именованного тома.
Для его воспроизведения используйте `docker compose -f compose.practice12.yaml ...`
вместо обычного `docker compose ...`. Не переключайте конфигурации действующей
базы до создания резервной копии. Основной compose.yaml — итог практики №13.

## Постоянное хранение и сети

Именованный том `shoe-shop_db_data` подключён к `/var/lib/postgresql/data`.
Оба сервиса находятся в сети bridge `shoe-backend`; имя сети Docker имеет
префикс `shoe-shop_`. Порт базы опубликован только на loopback хоста.

Перед переходом с этапа №12 на постоянный том создайте дамп:

```powershell
New-Item -ItemType Directory -Force backups
docker compose -f compose.practice12.yaml exec db pg_dump -U shoe_user -d shoe_store -f /tmp/before.sql
docker compose -f compose.practice12.yaml cp db:/tmp/before.sql backups/shoe_store_before_volume.sql
docker compose -f compose.practice12.yaml down
docker compose up --build -d
docker compose cp backups/shoe_store_before_volume.sql db:/tmp/restore.sql
docker compose exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/restore.sql
docker compose run --rm db-check
```

Восстановление выполняйте только в новую пустую базу. Если там уже есть таблицы,
остановитесь и выясните происхождение данных. Дампы, .env и config.ini исключены из Git.
Порядок обычного резервного копирования описан в INSTALL.md.

```powershell
docker compose exec db psql -U shoe_user -d shoe_store -c "CREATE TABLE IF NOT EXISTS docker_persistence_check (id integer PRIMARY KEY, note text NOT NULL); INSERT INTO docker_persistence_check VALUES (13, 'data survives recreation') ON CONFLICT (id) DO NOTHING;"
docker compose exec db psql -U shoe_user -d shoe_store -c "SELECT * FROM docker_persistence_check;"
docker compose up -d --force-recreate db
# Дождитесь healthy и повторите SELECT.
docker compose ps -a
docker compose exec db psql -U shoe_user -d shoe_store -c "SELECT * FROM docker_persistence_check;"
docker compose port db 5432
docker network inspect shoe-shop_shoe-backend
```

Диагностика неправильного имени без изменения основного файла:

```powershell
docker compose run --rm -e DB_HOST=wrong-db db-check
docker compose run --rm db-check
```

Для второй проверки временно укажите свободный неверный порт в config.ini,
проверьте сообщение приложения и верните порт 5433.
`stop` останавливает сервисы, `down` удаляет контейнеры и сеть, сохраняя именованный
том. `down -v` удаляет и том с данными — не выполняйте эту команду для учебной базы.

## Сборка Windows EXE

Используйте полноценный Python с Tkinter. Проверенная среда сборки: Python 3.12.10
и PyInstaller 6.22.3. Установленный через Python Install Manager вариант 3.10.11
не содержал tkinter, поэтому для Windows выбран имеющийся Python 3.12.
Python 3.10 по-прежнему используется в Dockerfile db-check.

```powershell
py -3.12 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv-build\Scripts\python.exe -m PyInstaller --clean --noconfirm ShoeStore.spec
.\scripts\build-release.ps1
```

Результат: `dist/ShoeStore/ShoeStore.exe` и `_internal`. ZIP с приложением,
инструкциями, SQL и исходниками контейнера создаётся в `output/`.
Локальный config.ini положите рядом с EXE, не в `_internal`.
Пути к изображениям определяются относительно пакета, независимо от рабочей папки.
Перенесите всю сборку в отдельный каталог и проверьте каталог, изображения,
ошибку при остановке базы и повторное подключение после её запуска.
