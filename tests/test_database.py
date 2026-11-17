import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from database import check_user_credentials, filter_and_sort_products

# тест 1 (позитивный)
@patch('database.create_connection')
def test_filter_products_success(mock_create_connection):
    # подключение тестовой базы данных
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # эмулируем, что база вернула один товар 
    mock_cursor.fetchall.return_value = [
        (1, 'A001', 'Ботинки зимние', 'пара', 5000, 'ООО Обувь', 'BestShoes', 'Ботинки', 0, 10, 'Описание', 'photo.jpg')
    ]
    
    # вызов функции фильтрации
    products = filter_and_sort_products(category='Ботинки')
    
    # проверка результата
    assert len(products) == 1, "Должен вернуться ровно один товар"
    assert products[0]['name'] == 'Ботинки зимние'
    
    # анализируем вызываемый sql запрос
    call_args = mock_cursor.execute.call_args     # получаем аргументы
    sql_query, params = call_args[0]              # разбираем их 
    
    # проверяем, что в SQL-запрос добавилось условие по категории
    assert "AND category = %s" in sql_query, "SQL запрос должен содержать фильтр по категории"
    assert 'Ботинки' in params, "Значение 'Ботинки' должно передаваться как параметр запроса"


# тест 2 (sql инъекция)
@patch('database.create_connection')
def test_filter_products_sql_injection_attempt(mock_create_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_create_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    # попытка атаки
    malicious_input = "Зимняя обувь' OR '1'='1"
    
    filter_and_sort_products(category=malicious_input)
    
    # получаем исполненный запрос
    call_args = mock_cursor.execute.call_args
    sql_query, params = call_args[0]
    
    # проверяем, что в запросе стоит плейсхолдер
    assert "AND category = %s" in sql_query, "Параметр должен передаваться через плейсхолдер %s"
    
    # проверяем, что запрос ушел в нужное место
    assert malicious_input in params, "Вредоносная строка должна быть в списке параметров (params)"
    
    # проверяем, что запрос не попал напрямую в sql запрос
    assert malicious_input not in sql_query, "ОПАСНО: Пользовательский ввод попал напрямую в SQL запрос!"