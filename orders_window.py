import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database import get_all_orders, get_order_by_id, update_order_status, search_orders, delete_order
from order_editor import create_order_editor

def create_orders_window(user_data):
    
    orders_window = tk.Toplevel()
    orders_window.title("Управление заказами")
    orders_window.geometry("1200x800")
    orders_window.configure(bg="#FFFFFF")
    
    user_role = user_data.get('role', 'guest')
    
    if user_role not in ['manager', 'admin']:
        messagebox.showerror("Ошибка доступа", "У вас нет прав для просмотра заказов")
        orders_window.destroy()
        return
    
    header_frame = tk.Frame(orders_window, bg="#7FFF00", height=100)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    try:
        header_logo = Image.open("static/Icon.png")
        header_logo = header_logo.resize((60, 60), Image.Resampling.LANCZOS)
        header_logo_photo = ImageTk.PhotoImage(header_logo)
        
        label_header_logo = tk.Label(header_frame, image=header_logo_photo, bg="#7FFF00")
        label_header_logo.image = header_logo_photo
        label_header_logo.pack(side="left", padx=20, pady=20)
    except Exception as e:
        print(f"Ошибка загрузки логотипа: {e}")
    
    label_app_name = tk.Label(
        header_frame,
        text="Управление заказами",
        font=("Times New Roman", 28, "bold"),
        bg="#7FFF00",
        fg="#000000"
    )
    label_app_name.pack(side="left", padx=10)
    
    user_frame = tk.Frame(header_frame, bg="#7FFF00")
    user_frame.pack(side="right", padx=30)
    
    label_user_info = tk.Label(
        user_frame,
        text=f"{user_data.get('full_name', 'Пользователь')} ({user_role})",
        font=("Times New Roman", 12),
        bg="#7FFF00",
        fg="#000000"
    )
    label_user_info.pack()
    
    def close_window():
        orders_window.destroy()
    
    btn_back = tk.Button(
        user_frame,
        text="Назад",
        font=("Times New Roman", 11),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        relief="raised",
        bd=3,
        cursor="hand2",
        command=close_window
    )
    btn_back.pack()
    
    control_frame = tk.Frame(orders_window, bg="#FFFFFF", height=80)
    control_frame.pack(fill="x", pady=10)
    control_frame.pack_propagate(False)
    
    control_container = tk.Frame(control_frame, bg="#FFFFFF")
    control_container.pack(expand=True)
    
    entry_search = tk.Entry(
        control_container,
        font=("Times New Roman", 12),
        width=50,
        relief="solid",
        bd=2
    )
    entry_search.pack(side="left", padx=10)
    
    def perform_search():
        search_text = entry_search.get().strip()
        if search_text:
            orders = search_orders(search_text)
        else:
            orders = get_all_orders()
        
        refresh_orders_list(orders)
    
    btn_search = tk.Button(
        control_container,
        text="Найти",
        font=("Times New Roman", 11),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        width=12,
        cursor="hand2",
        relief="raised",
        bd=3,
        command=perform_search
    )
    btn_search.pack(side="left", padx=10)
    
    if user_role == 'admin':
        def add_order():
            create_order_editor(None, user_data, lambda: refresh_orders_list())
        
        btn_add = tk.Button(
            control_container,
            text="+ Добавить заказ",
            font=("Times New Roman", 11),
            bg="#00FA9A",
            activebackground="#00FA9A",
            fg="#000000",
            activeforeground="#000000",
            width=18,
            cursor="hand2",
            relief="raised",
            bd=3,
            command=add_order
        )
        btn_add.pack(side="left", padx=10)
    
    canvas = tk.Canvas(orders_window, bg="#FFFFFF")
    scrollbar = tk.Scrollbar(orders_window, orient="vertical", command=canvas.yview)
    
    orders_container = tk.Frame(canvas, bg="#FFFFFF")
    
    canvas_window = canvas.create_window((0, 0), window=orders_container, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    orders_container.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def refresh_orders_list(orders=None):
        for widget in orders_container.winfo_children():
            widget.destroy()
        
        if orders is None:
            orders = get_all_orders()
        
        if not orders:
            label_no_orders = tk.Label(
                orders_container,
                text="Заказы не найдены",
                font=("Times New Roman", 16),
                bg="#FFFFFF",
                fg="#666666"
            )
            label_no_orders.pack(pady=50)
        else:
            for order in orders:
                card = create_order_card(orders_container, order, user_data, refresh_orders_list)
                card.pack(fill="x", padx=50, pady=15)
    
    # Загрузка заказов
    refresh_orders_list()
    
    return orders_window


def create_order_card(parent, order, user_data, refresh_callback):
    
    user_role = user_data.get('role', 'guest')
    
    card_frame = tk.Frame(
        parent,
        bg="#FFFFFF",
        relief="solid",
        bd=2
    )
    
    left_frame = tk.Frame(card_frame, bg="#FFFFFF")
    left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)
    
    items_text = ", ".join([f"{item.get('articul', 'Неизвестно')}, {item.get('quantity', 1)}" for item in order.get('items', [])])
    
    label_order_number = tk.Label(
        left_frame,
        text=items_text,
        font=("Times New Roman", 16),
        bg="#FFFFFF",
        fg="#000000"
    )
    label_order_number.pack(anchor="w", pady=(0, 5))
    
    label_status = tk.Label(
        left_frame,
        text=f"Статус: {order.get('status', 'Новый')}",
        font=("Times New Roman", 11),
        bg="#FFFFFF",
        fg="#000000"
    )
    label_status.pack(anchor="w", pady=(0, 5))
    
    label_pickup = tk.Label(
        left_frame,
        text=f"Пункт выдачи: {order.get('pick_up_location', 'Не указан')}",
        font=("Times New Roman", 11),
        bg="#FFFFFF",
        fg="#000000"
    )
    label_pickup.pack(anchor="w", pady=(0, 5))
    
    label_order_date = tk.Label(
        left_frame,
        text=f"Дата заказа: {order.get('order_date', '??')}",
        font=("Times New Roman", 11),
        bg="#FFFFFF",
        fg="#000000"
    )
    label_order_date.pack(anchor="w")
    
    right_frame = tk.Frame(card_frame, bg="#FFFFFF", width=200)
    right_frame.pack(side="right", fill="y", padx=20, pady=15)
    right_frame.pack_propagate(False)
    
    label_delivery_title = tk.Label(
        right_frame,
        text="Дата доставки:",
        font=("Times New Roman", 10),
        bg="#FFFFFF",
        fg="#000000"
    )
    label_delivery_title.pack(anchor="center", pady=(10, 0))
    
    label_delivery_date = tk.Label(
        right_frame,
        text=order.get('delivery_date', '??'),
        font=("Times New Roman", 16),
        bg="#FFFFFF",
        fg="#000000"
    )
    label_delivery_date.pack(anchor="center", pady=(5, 0))
    
    def on_card_click(event):
        # Проверка на наличие ID, чтобы не упало при клике
        order_id = order.get('id')
        if not order_id:
            messagebox.showerror("Ошибка", "У этого заказа нет ID")
            return

        if user_role == 'admin':
            create_order_editor(order_id, user_data, refresh_callback)
        else:
            view_order_details(order_id)
    
    def bind_click_recursive(widget):
        widget.bind("<Button-1>", on_card_click)
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            bind_click_recursive(child)
    
    bind_click_recursive(card_frame)
    
    return card_frame


def view_order_details(order_id):
    order = get_order_by_id(order_id)
    
    if not order:
        messagebox.showerror("Ошибка", "Заказ не найден")
        return
    
    details_window = tk.Toplevel()
    details_window.title(f"Заказ №{order.get('order_number', '???')}")
    details_window.geometry("600x500")
    details_window.configure(bg="#FFFFFF")
    
    # Заголовок
    label_title = tk.Label(
        details_window,
        text=f"Заказ №{order.get('order_number', '???')}",
        font=("Times New Roman", 20, "bold"),
        bg="#FFFFFF"
    )
    label_title.pack(pady=20)
    
    info_frame = tk.Frame(details_window, bg="#FFFFFF")
    info_frame.pack(fill="both", expand=True, padx=30, pady=10)
    
    # Безопасное получение данных
    status = order.get('status', 'Не указан')
    client_fio = order.get('client_fio', 'Не указан')
    client_code = order.get('client_code', 'Не указан')
    order_date = order.get('order_date', '??')
    delivery_date = order.get('delivery_date', '??')
    pickup_loc = order.get('pick_up_location', 'Не указан')

    info_text = f"""
    Статус: {status}
    
    Клиент: {client_fio}
    Код клиента: {client_code}
    
    Дата заказа: {order_date}
    Дата доставки: {delivery_date}
    
    Пункт выдачи: {pickup_loc}
    
    Товары в заказе:
    """

    for item in order.get('items', []):
        art = item.get('articul', 'Без артикула')
        qty = item.get('quantity', 1) 
        info_text += f"\n  • {art} - {qty} шт"
    
    label_info = tk.Label(
        info_frame,
        text=info_text,
        font=("Times New Roman", 12),
        bg="#FFFFFF",
        justify="left"
    )
    label_info.pack(anchor="w")
    
    btn_close = tk.Button(
        details_window,
        text="Закрыть",
        font=("Times New Roman", 12),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        width=15,
        cursor="hand2",
        relief="raised",
        bd=3,
        command=details_window.destroy
    )
    btn_close.pack(pady=20)


if __name__ == "__main__":
    test_user = {
        'id': 1,
        'role': 'admin',
        'full_name': 'Администратор',
        'login': 'admin@test.com'
    }
    create_orders_window(test_user)