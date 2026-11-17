import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_order_by_id, get_all_pick_up_locations, create_order, update_order_status, get_all_products, delete_order, get_all_users, update_order

_editor_windows = {}

def create_order_editor(order_id, user_data, refresh_callback):
    window_key = f"order_{order_id}" if order_id else "new_order"
    
    if window_key in _editor_windows and _editor_windows[window_key].winfo_exists():
        _editor_windows[window_key].lift()
        _editor_windows[window_key].focus_force()
        return
    
    editor_window = tk.Toplevel()
    editor_window.title("Редактирование заказа" if order_id else "Создание заказа")
    editor_window.geometry("700x800")
    editor_window.configure(bg="#FFFFFF")
    
    _editor_windows[window_key] = editor_window
    
    def on_close():
        if window_key in _editor_windows:
            del _editor_windows[window_key]
        editor_window.destroy()
    
    editor_window.protocol("WM_DELETE_WINDOW", on_close)
    
    order_data = None
    if order_id:
        order_data = get_order_by_id(order_id)
        if not order_data:
            messagebox.showerror("Ошибка", "Заказ не найден")
            on_close()
            return
    
    label_title = tk.Label(
        editor_window,
        text="Редактирование заказа" if order_id else "Новый заказ",
        font=("Times New Roman", 20, "bold"),
        bg="#FFFFFF"
    )
    label_title.pack(pady=20)
    
    form_frame = tk.Frame(editor_window, bg="#FFFFFF")
    form_frame.pack(fill="both", expand=True, padx=40)
    
    if order_data:
        tk.Label(form_frame, text="Номер заказа:", font=("Times New Roman", 12), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
        entry_order_number = tk.Entry(form_frame, font=("Times New Roman", 12), width=40)
        entry_order_number.pack(anchor="w")
        entry_order_number.insert(0, order_data['order_number'])
        entry_order_number.config(state='disabled')
    
    tk.Label(form_frame, text="Клиент:", font=("Times New Roman", 12), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
    
    users = get_all_users()
    user_dict = {f"{u['full_name']} (ID: {u['id']})": u['id'] for u in users}
    
    combo_client = ttk.Combobox(form_frame, values=list(user_dict.keys()), state="readonly", width=38, font=("Times New Roman", 12))
    combo_client.pack(anchor="w")
    
    if order_data and order_data.get('user_id'):
        for key, uid in user_dict.items():
            if uid == order_data['user_id']:
                combo_client.set(key)
                break
    
    tk.Label(form_frame, text="Код клиента:", font=("Times New Roman", 12), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
    entry_client_code = tk.Entry(form_frame, font=("Times New Roman", 12), width=40)
    entry_client_code.pack(anchor="w")
    if order_data:
        entry_client_code.insert(0, order_data.get('client_code', ''))
    
    tk.Label(form_frame, text="Дата заказа (ГГГГ-ММ-ДД):", font=("Times New Roman", 12), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
    entry_order_date = tk.Entry(form_frame, font=("Times New Roman", 12), width=40)
    entry_order_date.pack(anchor="w")
    if order_data:
        entry_order_date.insert(0, str(order_data['order_date']))
    else:
        entry_order_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
    
    tk.Label(form_frame, text="Дата доставки (ГГГГ-ММ-ДД):", font=("Times New Roman", 12), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
    entry_delivery_date = tk.Entry(form_frame, font=("Times New Roman", 12), width=40)
    entry_delivery_date.pack(anchor="w")
    if order_data:
        entry_delivery_date.insert(0, str(order_data['delivery_date']))
    
    tk.Label(form_frame, text="Пункт выдачи:", font=("Times New Roman", 12), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
    
    pickup_locations = get_all_pick_up_locations()
    pickup_dict = {f"{loc['id']} - {loc['location']}": loc['id'] for loc in pickup_locations}
    
    combo_pickup = ttk.Combobox(form_frame, values=list(pickup_dict.keys()), state="readonly", width=38, font=("Times New Roman", 12))
    combo_pickup.pack(anchor="w")
    
    if order_data and order_data.get('pick_up_id'):
        for key, val in pickup_dict.items():
            if val == order_data['pick_up_id']:
                combo_pickup.set(key)
                break
    
    tk.Label(form_frame, text="Статус:", font=("Times New Roman", 12), bg="#FFFFFF").pack(anchor="w", pady=(10, 5))
    combo_status = ttk.Combobox(form_frame, values=["Новый", "Завершен", "Отменен"], state="readonly", width=38, font=("Times New Roman", 12))
    combo_status.pack(anchor="w")
    if order_data:
        combo_status.set(order_data['status'])
    else:
        combo_status.set("Новый")
    
    tk.Label(form_frame, text="Товары в заказе:", font=("Times New Roman", 12, "bold"), bg="#FFFFFF").pack(anchor="w", pady=(20, 5))
    
    items_frame = tk.Frame(form_frame, bg="#FFFFFF")
    items_frame.pack(anchor="w", fill="x")
    
    order_items = []
    
    def add_item_row(product_articul=None, quantity=1):
        item_row = tk.Frame(items_frame, bg="#FFFFFF")
        item_row.pack(anchor="w", pady=5)
        
        products = get_all_products()
        product_dict = {f"{p['articul']} - {p['name']}": p['articul'] for p in products}
        
        combo_product = ttk.Combobox(item_row, values=list(product_dict.keys()), state="readonly", width=40, font=("Times New Roman", 10))
        combo_product.pack(side="left", padx=(0, 10))
        
        if product_articul:
            for key, val in product_dict.items():
                if val == product_articul:
                    combo_product.set(key)
                    break
        
        tk.Label(item_row, text="Кол-во:", font=("Times New Roman", 10), bg="#FFFFFF").pack(side="left")
        entry_qty = tk.Entry(item_row, font=("Times New Roman", 10), width=10)
        entry_qty.insert(0, str(quantity))
        entry_qty.pack(side="left", padx=5)
        
        def remove_row():
            item_row.destroy()
            if (combo_product, entry_qty) in order_items:
                order_items.remove((combo_product, entry_qty))
        
        btn_remove = tk.Button(item_row, text="✖", font=("Times New Roman", 10), bg="#00FA9A", activebackground="#00FA9A", fg="#000000", activeforeground="#000000", relief="raised", bd=3, cursor="hand2", command=remove_row)
        btn_remove.pack(side="left", padx=5)
        
        order_items.append((combo_product, entry_qty))
    
    btn_add_item = tk.Button(form_frame, text="+ Добавить товар", font=("Times New Roman", 11), bg="#00FA9A", activebackground="#00FA9A", fg="#000000", activeforeground="#000000", relief="raised", bd=3, cursor="hand2", command=lambda: add_item_row())
    btn_add_item.pack(anchor="w", pady=10)
    
    if order_data and 'items' in order_data:
        for item in order_data['items']:
            add_item_row(item['articul'], item['quantity'])
    else:
        add_item_row()
    
    buttons_frame = tk.Frame(editor_window, bg="#FFFFFF")
    buttons_frame.pack(pady=20)
    
    def save_order():
        try:
            client_key = combo_client.get().strip()
            client_code = entry_client_code.get().strip()
            order_date = entry_order_date.get().strip()
            delivery_date = entry_delivery_date.get().strip()
            pickup_key = combo_pickup.get()
            status = combo_status.get()
            
            if not all([client_key, order_date, delivery_date, pickup_key]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
            
            user_id = user_dict[client_key]
            pickup_id = pickup_dict[pickup_key]
            
            # Сбор товаров
            items_list = []
            if not order_items:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один товар")
                return

            for combo, entry in order_items:
                product_key = combo.get()
                if not product_key:
                    continue
                
                products = get_all_products()
                articul = product_key.split(' - ')[0]
                try:
                    quantity = int(entry.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Количество должно быть числом")
                    return
                
                product = next((p for p in products if p['articul'] == articul), None)
                if product:
                    items_list.append({
                        'articul': articul,
                        'quantity': quantity,
                        'price': product['price'],
                        'discount': product.get('discount', 0)
                    })
            
            if not items_list:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один корректный товар")
                return

            if order_id:
                update_data = {
                    'delivery_date': delivery_date,
                    'pick_up_id': pickup_id,
                    'user_id': user_id,
                    'client_code': client_code,
                    'status': status
                }
                
                if update_order(order_id, update_data, items_list):
                    messagebox.showinfo("Успех", "Заказ обновлен")
                    on_close()
                    refresh_callback()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить заказ")
            else:
                order_info = {
                    'order_date': order_date,
                    'delivery_date': delivery_date,
                    'pick_up_id': pickup_id,
                    'user_id': user_id,
                    'client_code': client_code,
                    'status': status
                }
                
                new_order_id = create_order(order_info, items_list)
                
                if new_order_id:
                    messagebox.showinfo("Успех", f"Заказ #{new_order_id} создан")
                    on_close()
                    refresh_callback()
                else:
                    messagebox.showerror("Ошибка", "Не удалось создать заказ")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    
    btn_save = tk.Button(
        buttons_frame,
        text="Сохранить",
        font=("Times New Roman", 12),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        width=15,
        cursor="hand2",
        relief="raised",
        bd=3,
        command=save_order
    )
    btn_save.pack(side="left", padx=10)
    
    btn_cancel = tk.Button(
        buttons_frame,
        text="Отмена",
        font=("Times New Roman", 12),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        width=15,
        cursor="hand2",
        relief="raised",
        bd=3,
        command=on_close
    )
    btn_cancel.pack(side="left", padx=10)
    
    if order_id:
        def delete_order_action():
            result = messagebox.askyesno(
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить заказ №{order_data['order_number']}?"
            )
            if result:
                if delete_order(order_id):
                    messagebox.showinfo("Успех", "Заказ успешно удален")
                    on_close()
                    if refresh_callback:
                        refresh_callback()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить заказ")
        
        btn_delete = tk.Button(
            buttons_frame,
            text="Удалить",
            font=("Times New Roman", 12),
            bg="#00FA9A",
            activebackground="#00FA9A",
            fg="#000000",
            activeforeground="#000000",
            width=15,
            cursor="hand2",
            relief="raised",
            bd=3,
            command=delete_order_action
        )
        btn_delete.pack(side="left", padx=10)

