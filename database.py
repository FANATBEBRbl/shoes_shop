import psycopg2 
from psycopg2 import Error  
from configparser import Error as ConfigError
from db_config import load_db_config

def create_connection():
    connection = None
    
    try:
        connection = psycopg2.connect(**load_db_config())
        
        print("Подключение к PostgreSQL успешно установлено")
        return connection
        
    except (ConfigError, KeyError, OSError, ValueError):
        print("Не удалось прочитать настройки PostgreSQL.")
        return None
    except Error:
        print("Ошибка при подключении к PostgreSQL.")
        return None

def check_user_credentials(login, password):
    connection = create_connection()
    
    
    if connection is None:
        print("Не удалось подключиться к базе данных")
        return None
    
    try:
        cursor = connection.cursor()

        query = """
            SELECT id, role, full_name, login 
            FROM users 
            WHERE login = %s AND password = %s
        """

        cursor.execute(query, (login, password))
 
        user = cursor.fetchone()
        
        if user:
            user_data = {
                'id': user[0],          
                'role': user[1],        
                'full_name': user[2],   
                'login': user[3]        
            }
            print(f"Пользователь найден: {user_data['full_name']}")
            return user_data
        else:
            print("Неверный email или пароль")
            return None
            
    except Error as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
        
    finally:
        if connection:
            cursor.close()  
            connection.close()  
            print("Соединение с PostgreSQL закрыто")

def get_all_users():
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT id, role, full_name, login FROM users"
        
        cursor.execute(query)
        
        users = cursor.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'role': user[1],
                'full_name': user[2],
                'login': user[3]
            })
        
        print(f"Найдено пользователей: {len(users_list)}")
        return users_list
        
    except Error as e:
        print(f"Ошибка при получении пользователей: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_all_products(limit=None):
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT * FROM product"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        
        products = cursor.fetchall()
        products_list = []
        for product in products:
            products_list.append({
                'id': product[0],
                'articul': product[1],
                'name': product[2],
                'unit': product[3],
                'price': product[4],
                'provider': product[5],
                'manufacturer': product[6],
                'category': product[7],
                'discount': product[8],
                'stock_quantity': product[9],
                'description': product[10],
                'photo': product[11]
            })
        
        print(f"Получено товаров: {len(products_list)}")
        return products_list
        
    except Error as e:
        print(f"Ошибка при получении товаров: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()

def search_products(search_text):
    connection = create_connection()

    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        search_pattern = f"%{search_text}%"

        query = """
            SELECT * FROM product 
            WHERE 
                LOWER(atricle) LIKE LOWER(%s) OR
                LOWER(name) LIKE LOWER(%s) OR
                LOWER(provider) LIKE LOWER(%s) OR
                LOWER(manufacturer) LIKE LOWER(%s) OR
                LOWER(category) LIKE LOWER(%s) OR
                LOWER(description) LIKE LOWER(%s)
            ORDER BY name
        """

        cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))

        products = cursor.fetchall()
        products_list = []
        for product in products:
            products_list.append({
                'id': product[0],
                'articul': product[1],
                'name': product[2],
                'unit': product[3],
                'price': product[4],
                'provider': product[5],
                'manufacturer': product[6],
                'category': product[7],
                'discount': product[8],
                'stock_quantity': product[9],
                'description': product[10],
                'photo': product[11]
            })

        print(f"Найдено товаров по запросу '{search_text}': {len(products_list)}")
        return products_list
    
    except Error as e:
        print(f"Ошибка при поиске: {e}")
        return []
    
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_products_by_category(category, limit=None):
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT * FROM product WHERE category = %s"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (category,))
        
        products = cursor.fetchall()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': product[0],
                'articul': product[1],
                'name': product[2],
                'unit': product[3],
                'price': product[4],
                'provider': product[5],
                'manufacturer': product[6],
                'category': product[7],
                'discount': product[8],
                'stock_quantity': product[9],
                'description': product[10],
                'photo': product[11]
            })
        
        print(f"Найдено товаров в категории '{category}': {len(products_list)}")
        return products_list
        
    except Error as e:
        print(f"Ошибка: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def calculate_discounted_price(price, discount):
    if discount > 0:
        discounted_price = price * (100 - discount) / 100
        return round(discounted_price, 2)
    return price

def get_filter_options():
    connection = create_connection()
    
    if connection is None:
        return {'categories': [], 'manufacturers': [], 'providers': []}
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM product WHERE category IS NOT NULL ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT manufacturer FROM product WHERE manufacturer IS NOT NULL ORDER BY manufacturer")
        manufacturers = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT provider FROM product WHERE provider IS NOT NULL ORDER BY provider")
        providers = [row[0] for row in cursor.fetchall()]
        
        return {
            'categories': categories,
            'manufacturers': manufacturers,
            'providers': providers
        }
        
    except Error as e:
        print(f"Ошибка при получении опций фильтрации: {e}")
        return {'categories': [], 'manufacturers': [], 'providers': []}
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def filter_and_sort_products(category=None, manufacturer=None, provider=None, 
                             discount_filter=None, stock_filter=None, sort_by='name', sort_order='ASC', search_text=None):
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT * FROM product WHERE 1=1"
        params = []
        
        if search_text:
            search_pattern = f"%{search_text}%"
            query += """ AND (
                LOWER(atricle) LIKE LOWER(%s) OR
                LOWER(name) LIKE LOWER(%s) OR
                LOWER(provider) LIKE LOWER(%s) OR
                LOWER(manufacturer) LIKE LOWER(%s) OR
                LOWER(category) LIKE LOWER(%s) OR
                LOWER(description) LIKE LOWER(%s)
            )"""
            params.extend([search_pattern] * 6)
        
        if category and category != "Все":
            query += " AND category = %s"
            params.append(category)
        
        if manufacturer and manufacturer != "Все":
            query += " AND manufacturer = %s"
            params.append(manufacturer)
        
        if provider and provider != "Все":
            query += " AND provider = %s"
            params.append(provider)
        
        if discount_filter == 'with_big_discount':
            query += " AND discount > 15"
        elif discount_filter == 'with_small_discount':
            query += " AND discount <= 15"
        
        if stock_filter == 'in_stock':
            query += " AND stock_quantity > 0"
        elif stock_filter == 'out_of_stock':
            query += " AND stock_quantity = 0"
        
        valid_sort_fields = {
            'name': 'name',
            'price': 'price',
            'discount': 'discount',
            'stock_quantity': 'stock_quantity'
        }
        
        if sort_by in valid_sort_fields:
            sort_field = valid_sort_fields[sort_by]
            if sort_order.upper() in ['ASC', 'DESC']:
                # Для цены учитываем скидку при сортировке
                if sort_field == 'price':
                    query += f" ORDER BY (price * (100 - COALESCE(discount, 0)) / 100) {sort_order.upper()}"
                else:
                    query += f" ORDER BY {sort_field} {sort_order.upper()}"
        else:
            # Сортировка по умолчанию
            query += " ORDER BY name ASC"
        
        cursor.execute(query, params)
        
        products = cursor.fetchall()
        products_list = []
        for product in products:
            products_list.append({
                'id': product[0],
                'articul': product[1],
                'name': product[2],
                'unit': product[3],
                'price': product[4],
                'provider': product[5],
                'manufacturer': product[6],
                'category': product[7],
                'discount': product[8],
                'stock_quantity': product[9],
                'description': product[10],
                'photo': product[11]
            })
        
        print(f"Найдено товаров с фильтрами: {len(products_list)}")
        return products_list
        
    except Error as e:
        print(f"Ошибка при фильтрации и сортировке: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()

def add_product(articul, name, unit, price, provider, manufacturer, category, discount, stock_quantity, description, photo):
    connection = create_connection()
    
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor()
        
        query = """
            INSERT INTO product (atricle, name, unit, price, provider, manufacturer, 
                                 category, discount, stock_quantity, description, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        cursor.execute(query, (articul, name, unit, price, provider, manufacturer, 
                              category, discount, stock_quantity, description, photo))
        
        connection.commit() 
        
        product_id = cursor.fetchone()[0]
        print(f"Товар добавлен с ID: {product_id}")
        return product_id
        
    except Error as e:
        print(f"Ошибка при добавлении товара: {e}")
        connection.rollback()  # Откатываем изменения при ошибке
        return None
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def update_product(product_id, articul, name, unit, price, provider, manufacturer, 
                   category, discount, stock_quantity, description, photo):
    connection = create_connection()
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = """
            UPDATE product 
            SET atricle = %s, name = %s, unit = %s, price = %s, 
                provider = %s, manufacturer = %s, category = %s, 
                discount = %s, stock_quantity = %s, description = %s, photo = %s
            WHERE id = %s
        """
        
        cursor.execute(query, (articul, name, unit, price, provider, manufacturer, 
                              category, discount, stock_quantity, description, photo, product_id))
        
        connection.commit()
        
        print(f"Товар ID {product_id} успешно обновлен")
        return True
        
    except Error as e:
        print(f"Ошибка при обновлении товара: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def delete_product(product_id):
    connection = create_connection()
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "DELETE FROM product WHERE id = %s"
        cursor.execute(query, (product_id,))
        
        connection.commit()
        
        print(f"Товар ID {product_id} удален")
        return True
        
    except Error as e:
        print(f"Ошибка при удалении товара: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def get_product_by_id(product_id):
    connection = create_connection()
    
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT * FROM product WHERE id = %s"
        cursor.execute(query, (product_id,))
        
        product = cursor.fetchone()
        
        if product:
            return {
                'id': product[0],
                'articul': product[1],
                'name': product[2],
                'unit': product[3],
                'price': product[4],
                'provider': product[5],
                'manufacturer': product[6],
                'category': product[7],
                'discount': product[8],
                'stock_quantity': product[9],
                'description': product[10],
                'photo': product[11]
            }
        return None
        
    except Error as e:
        print(f"Ошибка при получении товара: {e}")
        return None
        
    finally:
        if connection:
            cursor.close()
            connection.close()

# Тестирование функций при запуске этого файла напрямую
if __name__ == "__main__":
    print("\n=== Тест 1: Проверка подключения ===")
    conn = create_connection()
    if conn:
        conn.close()
    
    print("\n=== Тест 2: Получение всех пользователей ===")
    all_users = get_all_users()
    for user in all_users:
        print(f"  - {user['full_name']} ({user['login']}) - {user['role']}")
    
    print("\n=== Тест 3: Проверка учетных данных ===")
    result = check_user_credentials("admin@example.com", "123456")
    
    result = check_user_credentials("admin@example.com", "wrong_password")

def get_all_pick_up_locations():
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, location FROM pick_up ORDER BY id")
        locations = cursor.fetchall()
        
        locations_list = []
        for loc in locations:
            locations_list.append({
                'id': loc[0],
                'location': loc[1]
            })
        
        return locations_list
        
    except Error as e:
        print(f"Ошибка при получении пунктов выдачи: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def create_order(order_data, order_items):

    connection = create_connection()
    
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor()
        
        connection.autocommit = False
        
        insert_order_query = """
            INSERT INTO "orders" ("order_date", "delivery_date", "pick_up_id", 
                              "user_id", "client_code", "status")
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING "order_number"
        """
        
        cursor.execute(insert_order_query, (
            order_data['order_date'],
            order_data['delivery_date'],
            order_data['pick_up_id'],
            order_data['user_id'],
            order_data.get('client_code', ''),
            order_data.get('status', 'Новый')
        ))
        
        order_id = cursor.fetchone()[0] 
        
        insert_item_query = """
            INSERT INTO "orders_items" ("order_id", "product_id", "articul", "quantity")
            VALUES (%s, %s, %s, %s)
        """
        
        for item in order_items:
            cursor.execute("SELECT \"id\" FROM \"product\" WHERE \"atricle\" = %s", (item['articul'],))
            product_row = cursor.fetchone()
            product_id = product_row[0] if product_row else None
            
            cursor.execute(insert_item_query, (
                order_id,
                product_id,
                item['articul'],
                item['quantity']
            ))
        
        connection.commit()
        print(f"Заказ #{order_id} успешно создан")
        return order_id
        
    except Error as e:
        connection.rollback()
        print(f"Ошибка при создании заказа: {e}")
        return None
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def get_all_orders():
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = """
            SELECT "orders"."order_number", "orders"."order_number", "orders"."order_date", "orders"."delivery_date", 
                   "users"."full_name" as client_fio, "orders"."client_code", "orders"."status",
                   "pick_up"."location" as pick_up_location
            FROM "orders"
            LEFT JOIN "pick_up" ON "orders"."pick_up_id" = "pick_up"."id"
            LEFT JOIN "users" ON "orders"."user_id" = "users"."id"
            ORDER BY "orders"."order_date" DESC
        """
        
        cursor.execute(query)
        orders = cursor.fetchall()
        
        orders_list = []
        
        items_query = """
            SELECT "articul", "quantity" FROM "orders_items" WHERE "order_id" = %s
        """
        
        for order in orders:
            order_id = order[0]
            cursor.execute(items_query, (order_id,))
            items = cursor.fetchall()
            items_list = [{'articul': item[0], 'quantity': item[1]} for item in items]
            
            orders_list.append({
                'id': order[0],
                'order_number': order[1],
                'order_date': order[2],
                'delivery_date': order[3],
                'client_fio': order[4],
                'client_code': order[5],
                'status': order[6],
                'pick_up_location': order[7],
                'items': items_list
            })
        
        return orders_list
        
    except Error as e:
        print(f"Ошибка при получении заказов: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def get_order_by_id(order_id):
    connection = create_connection()
    
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor()
        
        order_query = """
            SELECT "orders"."order_number", "orders"."order_number", "orders"."order_date", "orders"."delivery_date", 
                   "users"."full_name" as client_fio, "orders"."client_code", "orders"."status",
                   "pick_up"."id" as pick_up_id, "pick_up"."location" as pick_up_location, "orders"."user_id"
            FROM "orders"
            LEFT JOIN "pick_up" ON "orders"."pick_up_id" = "pick_up"."id"
            LEFT JOIN "users" ON "orders"."user_id" = "users"."id"
            WHERE "orders"."order_number" = %s
        """
        
        cursor.execute(order_query, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return None
        
        items_query = """
            SELECT "orders_items"."id", "orders_items"."articul", "orders_items"."quantity",
                   "product"."name" as product_name, "product"."photo"
            FROM "orders_items"
            LEFT JOIN "product" ON "orders_items"."product_id" = "product"."id"
            WHERE "orders_items"."order_id" = %s
        """
        
        cursor.execute(items_query, (order_id,))
        items = cursor.fetchall()
        
        items_list = []
        for item in items:
            items_list.append({
                'id': item[0],
                'articul': item[1],
                'quantity': item[2],
                'product_name': item[3],
                'photo': item[4]
            })
        
        order_data = {
            'id': order[0],
            'order_number': order[1],
            'order_date': order[2],
            'delivery_date': order[3],
            'client_fio': order[4],
            'client_code': order[5],
            'status': order[6],
            'pick_up_id': order[7],
            'pick_up_location': order[8],
            'user_id': order[9],
            'items': items_list
        }
        
        return order_data
        
    except Error as e:
        print(f"Ошибка при получении заказа: {e}")
        return None
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def update_order_status(order_id, new_status):
    connection = create_connection()
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "UPDATE \"orders\" SET \"status\" = %s WHERE \"order_number\" = %s"
        cursor.execute(query, (new_status, order_id))
        
        connection.commit()
        print(f"Статус заказа #{order_id} обновлен на '{new_status}'")
        return True
        
    except Error as e:
        print(f"Ошибка при обновлении статуса заказа: {e}")
        return False
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def update_order(order_id, order_data, items_list=None):
    """Обновление заказа"""
    connection = create_connection()
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Обновляем основные данные заказа
        query = """
            UPDATE "orders" 
            SET "delivery_date" = %s, "pick_up_id" = %s, "user_id" = %s, 
                "client_code" = %s, "status" = %s
            WHERE "order_number" = %s
        """
        
        cursor.execute(query, (
            order_data['delivery_date'],
            order_data['pick_up_id'],
            order_data['user_id'],
            order_data.get('client_code', ''),
            order_data.get('status', 'Новый'),
            order_id
        ))
        
        # Если передан список товаров, обновляем их
        if items_list is not None:
            # Удаляем старые товары
            cursor.execute('DELETE FROM "orders_items" WHERE "order_id" = %s', (order_id,))
            
            # Добавляем новые товары
            insert_item_query = """
                INSERT INTO "orders_items" ("order_id", "product_id", "articul", "quantity")
                VALUES (%s, %s, %s, %s)
            """
            
            for item in items_list:
                # Получаем ID товара по артикулу
                cursor.execute('SELECT "id" FROM "product" WHERE "atricle" = %s', (item['articul'],))
                product_row = cursor.fetchone()
                product_id = product_row[0] if product_row else None
                
                cursor.execute(insert_item_query, (
                    order_id,
                    product_id,
                    item['articul'],
                    item['quantity']
                ))
        
        connection.commit()
        print(f"Заказ #{order_id} обновлен")
        return True
        
    except Error as e:
        print(f"Ошибка при обновлении заказа: {e}")
        connection.rollback()
        return False
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def delete_order(order_id):
    connection = create_connection()
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        connection.autocommit = False
        
        delete_items_query = "DELETE FROM \"orders_items\" WHERE \"order_id\" = %s"
        cursor.execute(delete_items_query, (order_id,))
        
        delete_order_query = "DELETE FROM \"orders\" WHERE \"order_number\" = %s"
        cursor.execute(delete_order_query, (order_id,))
        
        connection.commit()
        print(f"Заказ #{order_id} успешно удален")
        return True
        
    except Error as e:
        if connection:
            connection.rollback()
        print(f"Ошибка при удалении заказа: {e}")
        return False
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def search_orders(search_text):
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = """
            SELECT "orders"."order_number", "orders"."order_number", "orders"."order_date", "orders"."delivery_date", 
                   "users"."full_name" as client_fio, "orders"."client_code", "orders"."status",
                   "pick_up"."location" as pick_up_location
            FROM "orders"
            LEFT JOIN "pick_up" ON "orders"."pick_up_id" = "pick_up"."id"
            LEFT JOIN "users" ON "orders"."user_id" = "users"."id"
            WHERE CAST("orders"."order_number" AS TEXT) LIKE %s
               OR LOWER("users"."full_name") LIKE LOWER(%s)
               OR LOWER("orders"."client_code") LIKE LOWER(%s)
            ORDER BY "orders"."order_date" DESC
        """
        
        search_pattern = f"%{search_text}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        
        orders = cursor.fetchall()
        
        orders_list = []
        
        items_query = """
            SELECT "articul", "quantity" FROM "orders_items" WHERE "order_id" = %s
        """
        
        for order in orders:
            order_id = order[0]
            cursor.execute(items_query, (order_id,))
            items = cursor.fetchall()
            items_list = [{'articul': item[0], 'quantity': item[1]} for item in items]
            
            orders_list.append({
                'id': order[0],
                'order_number': order[1],
                'order_date': order[2],
                'delivery_date': order[3],
                'client_fio': order[4],
                'client_code': order[5],
                'status': order[6],
                'pick_up_location': order[7],
                'items': items_list
            })
        
        return orders_list
        
    except Error as e:
        print(f"Ошибка при поиске заказов: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def check_product_in_orders(product_id):
    connection = create_connection()
    
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT COUNT(*) FROM \"orders_items\" WHERE \"product_id\" = %s"
        cursor.execute(query, (product_id,))
        
        count = cursor.fetchone()[0]
        return count > 0
        
    except Error as e:
        print(f"Ошибка при проверке товара в заказах: {e}")
        return False
        
    finally:
        if connection:
            cursor.close()
            connection.close()


def get_orders_by_product(product_id):
    connection = create_connection()
    
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = """
            SELECT DISTINCT "orders"."order_number", "orders"."order_number", "orders"."order_date", "users"."full_name" as client_fio, "orders"."status"
            FROM "orders"
            JOIN "orders_items" ON "orders"."order_number" = "orders_items"."order_id"
            LEFT JOIN "users" ON "orders"."user_id" = "users"."id"
            WHERE "orders_items"."product_id" = %s
            ORDER BY "orders"."order_date" DESC
        """
        
        cursor.execute(query, (product_id,))
        orders = cursor.fetchall()
        
        orders_list = []
        for order in orders:
            orders_list.append({
                'id': order[0],
                'order_number': order[0],
                'order_date': order[1],
                'client_fio': order[2],
                'status': order[3]
            })
        
        return orders_list
        
    except Error as e:
        print(f"Ошибка при получении заказов с товаром: {e}")
        return []
        
    finally:
        if connection:
            cursor.close()
            connection.close()
