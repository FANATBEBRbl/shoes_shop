import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from database import get_all_products, get_products_by_category, calculate_discounted_price, get_filter_options, filter_and_sort_products

def create_main_window(user_data):
    
    main_window = tk.Tk()
    
    main_window.title("ShoeShop — каталог обуви")
    main_window.geometry("1200x800")
    main_window.configure(bg="#FFFFFF")
    
    user_role = user_data.get('role', 'guest')
    
    def refresh_products_list(container=None):
        target_container = container if container else products_container
        
        for widget in target_container.winfo_children():
            widget.destroy()
        
        products = get_all_products()
        
        if not products:
            label_no = tk.Label(
                target_container,
                text="Товары не найдены",
                font=("Times New Roman", 16),
                bg="#FFFFFF",
                fg="#666666"
            )
            label_no.pack(pady=50)
        else:
            for index, product in enumerate(products):
                card = create_product_card(target_container, product, user_role)
                card.pack(fill="x", padx=50, pady=15)
    
    header_frame = tk.Frame(
        main_window,
        bg="#7FFF00", 
        height=100
    )
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    try:
        header_logo = Image.open("static/Icon.png")
        header_logo = header_logo.resize((60, 60), Image.Resampling.LANCZOS)
        
        header_logo_photo = ImageTk.PhotoImage(header_logo)

        label_header_logo = tk.Label(
            header_frame, 
            image=header_logo_photo, 
            bg="#7FFF00"
        )
        label_header_logo.image = header_logo_photo
        label_header_logo.pack(side="left", padx=20, pady=20)
    except Exception as e:
        print(f"Ошибка загрузки логотипа: {e}")

    label_app_name = tk.Label(
        header_frame,
        text="Обувь - Главное окно",
        font=("Times New Roman", 28, "bold"),
        bg="#7FFF00",
        fg="#000000"
    )
    label_app_name.pack(side="left", padx=10)

    user_frame = tk.Frame(header_frame, bg="#7FFF00")
    user_frame.pack(side="right", padx=30)
    
    label_user_info = tk.Label(
        user_frame,
        text=f"{user_data['full_name']}",
        font=("Times New Roman", 12),
        bg="#7FFF00",
        fg="#000000",
        justify="right"
    )
    label_user_info.pack()

    def logout(window):
        window.destroy()
        from login_window import create_login_window
        create_login_window()

    exit_button = tk.Button(
        user_frame,
        text="Выход",
        font=("Times New Roman", 11),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        relief="raised",
        bd=3,
        cursor="hand2",
        command=lambda: logout(main_window)
    )
    exit_button.pack()

    orders_window_ref = {'window': None}
    
    if user_role in ['manager', 'admin']:
        management_button_frame = tk.Frame(header_frame, bg="#7FFF00")
        management_button_frame.pack(side="left", padx=20)
        
        def open_orders():
            if orders_window_ref['window'] and orders_window_ref['window'].winfo_exists():
                orders_window_ref['window'].lift()
                orders_window_ref['window'].focus_force()
            else:
                from orders_window import create_orders_window
                orders_window_ref['window'] = create_orders_window(user_data)
        
        button_orders = tk.Button(
            management_button_frame,
            text="Заказы",
            font=("Times New Roman", 11),
            bg="#00FA9A",
            activebackground="#00FA9A",
            fg="#000000",
            activeforeground="#000000",
            width=15,
            cursor="hand2",
            relief="raised",
            bd=3,
            command=open_orders
        )
        button_orders.pack(side="left", padx=5)
    
    if user_role == 'admin':
        def add_new_product():
            from product_editor import open_product_editor
            open_product_editor(
                product_id=None, 
                parent_window=main_window, 
                refresh_callback=lambda: refresh_products_list()
            )
        
        button_add_product = tk.Button(
            management_button_frame,
            text="Добавить товар",
            font=("Times New Roman", 11),
            bg="#00FA9A",
            activebackground="#00FA9A",
            fg="#000000",
            activeforeground="#000000",
            width=18,
            cursor="hand2",
            relief="raised",
            bd=3,
            command=add_new_product
        )
        button_add_product.pack(pady=5)

    def perform_search():
        apply_filters()

    if user_role in ['manager', 'admin']:
        search_frame = tk.Frame(main_window, bg="#FFFFFF", height=60)
        search_frame.pack(fill="x")
        search_frame.pack_propagate(False)

        search_container = tk.Frame(search_frame, bg="#FFFFFF")
        search_container.pack(expand=True)

        entry_search = tk.Entry(
            search_container,
            font=("Times New Roman", 12),
            width=100,
            relief="solid",
            bd=2
        )
        entry_search.pack(side="left", padx=(0, 10))

        button_search = tk.Button(
            search_container,
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
        button_search.pack(side="left", padx=(0,10))

        filter_frame = tk.Frame(main_window, bg="#7FFF00", height=120)
        filter_frame.pack(fill="x")
        filter_frame.pack_propagate(False)

        filter_options = get_filter_options()

        filters_container = tk.Frame(filter_frame, bg="#7FFF00")
        filters_container.pack(expand=True, pady=10)

        row1 = tk.Frame(filters_container, bg="#7FFF00")
        row1.pack(pady=5)

        tk.Label(row1, text="Категория:", font=("Times New Roman", 10), bg="#7FFF00").pack(side="left", padx=5)
        combo_category = ttk.Combobox(row1, values=["Все"] + filter_options['categories'], 
                                      state="readonly", width=20, font=("Times New Roman", 10))
        combo_category.set("Все")
        combo_category.pack(side="left", padx=5)

        tk.Label(row1, text="Производитель:", font=("Times New Roman", 10), bg="#7FFF00").pack(side="left", padx=5)
        combo_manufacturer = ttk.Combobox(row1, values=["Все"] + filter_options['manufacturers'], 
                                          state="readonly", width=20, font=("Times New Roman", 10))
        combo_manufacturer.set("Все")
        combo_manufacturer.pack(side="left", padx=5)

        tk.Label(row1, text="Поставщик:", font=("Times New Roman", 10), bg="#7FFF00").pack(side="left", padx=5)
        combo_provider = ttk.Combobox(row1, values=["Все"] + filter_options['providers'], 
                                      state="readonly", width=20, font=("Times New Roman", 10))
        combo_provider.set("Все")
        combo_provider.pack(side="left", padx=5)

        row2 = tk.Frame(filters_container, bg="#7FFF00")
        row2.pack(pady=5)

        tk.Label(row2, text="Скидка:", font=("Times New Roman", 10), bg="#7FFF00").pack(side="left", padx=5)
        combo_discount = ttk.Combobox(row2, values=["Все", "С большой скидкой", "С небольшой скидкой"], 
                                      state="readonly", width=15, font=("Times New Roman", 10))
        combo_discount.set("Все")
        combo_discount.pack(side="left", padx=5)

        tk.Label(row2, text="Наличие:", font=("Times New Roman", 10), bg="#7FFF00").pack(side="left", padx=5)
        combo_stock = ttk.Combobox(row2, values=["Все", "В наличии", "Нет на складе"], 
                                   state="readonly", width=15, font=("Times New Roman", 10))
        combo_stock.set("Все")
        combo_stock.pack(side="left", padx=5)

        tk.Label(row2, text="Сортировать по:", font=("Times New Roman", 10), bg="#7FFF00").pack(side="left", padx=5)
        combo_sort = ttk.Combobox(row2, values=["Названию", "Цене", "Скидке", "Количеству на складе"], 
                                  state="readonly", width=20, font=("Times New Roman", 10))
        combo_sort.set("Названию")
        combo_sort.pack(side="left", padx=5)

        combo_order = ttk.Combobox(row2, values=["По возрастанию", "По убыванию"], 
                                   state="readonly", width=15, font=("Times New Roman", 10))
        combo_order.set("По возрастанию")
        combo_order.pack(side="left", padx=5)

        def apply_filters():
            search_text = entry_search.get().strip()
            category = combo_category.get() if combo_category.get() != "Все" else None
            manufacturer = combo_manufacturer.get() if combo_manufacturer.get() != "Все" else None
            provider = combo_provider.get() if combo_provider.get() != "Все" else None
            
            discount_map = {
                "Все": None,
                "С большой скидкой": "with_big_discount",
                "С небольшой скидкой": "with_small_discount"
            }
            discount_filter = discount_map[combo_discount.get()]
            
            stock_map = {
                "Все": None,
                "В наличии": "in_stock",
                "Нет на складе": "out_of_stock"
            }
            stock_filter = stock_map[combo_stock.get()]
            
            sort_map = {
                "Названию": "name",
                "Цене": "price",
                "Скидке": "discount",
                "Количеству на складе": "stock_quantity"
            }
            sort_by = sort_map[combo_sort.get()]
            
            sort_order = "ASC" if combo_order.get() == "По возрастанию" else "DESC"
            
            products = filter_and_sort_products(
                category=category,
                manufacturer=manufacturer,
                provider=provider,
                discount_filter=discount_filter,
                stock_filter=stock_filter,
                sort_by=sort_by,
                sort_order=sort_order,
                search_text=search_text
            )
            
            for widget in products_container.winfo_children():
                widget.destroy()
            
            if not products:
                label_no_products = tk.Label(
                    products_container,
                    text="Товары по выбранным фильтрам не найдены",
                    font=("Times New Roman", 16),
                    bg="#FFFFFF",
                    fg="#666666"
                )
                label_no_products.pack(pady=50)
            else:
                for index, product in enumerate(products):
                    card = create_product_card(products_container, product, user_role)
                    card.pack(fill="x", padx=50, pady=15)



        def reset_filters():
            entry_search.delete(0, tk.END)
            combo_category.set("Все")
            combo_manufacturer.set("Все")
            combo_provider.set("Все")
            combo_discount.set("Все")
            combo_stock.set("Все")
            combo_sort.set("Названию")
            combo_order.set("По возрастанию")
            apply_filters()

        row3 = tk.Frame(filters_container, bg="#7FFF00")
        row3.pack(pady=5)

        button_apply = tk.Button(
            row3,
            text="Применить фильтры",
            font=("Times New Roman", 11),
            bg="#00FA9A",
            activebackground="#00FA9A",
            fg="#000000",
            activeforeground="#000000",
            width=18,
            cursor="hand2",
            relief="raised",
            bd=3,
            command=apply_filters
        )
        button_apply.pack(side="left", padx=10)

        button_reset = tk.Button(
            row3,
            text="Сбросить",
            font=("Times New Roman", 11),
            bg="#00FA9A",
            activebackground="#00FA9A",
            fg="#000000",
            activeforeground="#000000",
            width=12,
            cursor="hand2",
            relief="raised",
            bd=3,
            command=reset_filters
        )
        button_reset.pack(side="left", padx=10)
    
    content_frame = tk.Frame(main_window, bg="#FFFFFF")
    content_frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(content_frame, bg="#FFFFFF", highlightthickness=0)
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    products_container = tk.Frame(canvas, bg="#FFFFFF")
    canvas_window = canvas.create_window((0, 0), window=products_container, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    products_container.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)
    
    products = get_all_products()
    
    if not products:
        label_no_products = tk.Label(
            products_container,
            text="Товары не найдены",
            font=("Times New Roman", 16),
            bg="#FFFFFF",
            fg="#666666"
        )
        label_no_products.pack(pady=50)
    else:
        for product in products:
            card = create_product_card(products_container, product, user_role)
            card.pack(fill="x", padx=50, pady=15)
    
    main_window.mainloop()

def create_product_card(parent, product, user_role='guest'):
    
    stock_quantity = product.get('stock_quantity', 0)
    discount = product.get('discount', 0)
    
    if discount > 15:
        info_bg_color = "#2E8B57"
    else:
        info_bg_color = "#FFFFFF" 
    
    if stock_quantity == 0:
        stock_bg_color = "#87CEEB" 
    else:
        stock_bg_color = info_bg_color 
    
    card_frame = tk.Frame(
        parent,
        bg=info_bg_color,
        relief="solid",
        bd=2,
        width=1100,
        height=200,
        padx=15,
        pady=15
    )
    card_frame.pack_propagate(False)

    if user_role == 'admin':
        def open_edit_window(event=None):
            from product_editor import open_product_editor
            main_window = parent.winfo_toplevel()
            
            def refresh_callback():
                products_container = parent
                for widget in products_container.winfo_children():
                    widget.destroy()
                
                products = get_all_products()
                for prod in products:
                    card = create_product_card(products_container, prod, user_role)
                    card.pack(fill="x", padx=50, pady=15)
            
            open_product_editor(
                product_id=product['id'],
                parent_window=main_window,
                refresh_callback=refresh_callback
            )
        
        def bind_click_recursive(widget):
            widget.config(cursor="hand2")
            widget.bind("<Button-1>", open_edit_window)
            for child in widget.winfo_children():
                bind_click_recursive(child)
        
        bind_click_recursive(card_frame)
    
    left_frame = tk.Frame(card_frame, bg=info_bg_color, width=200, height=170)
    left_frame.pack(side="left", padx=(0, 20))
    left_frame.pack_propagate(False)
    
    try:
        photo_filename = product.get('photo', '')
        
        if photo_filename:
            photo_path = f"static/{photo_filename}"
        else:
            photo_path = "static/picture.png"
        
        try:
            product_image = Image.open(photo_path)
        except:
            try:
                product_image = Image.open("static/picture.png")
            except:
                product_image = Image.open("static/Icon.png")
        
        product_image = product_image.resize((200, 170), Image.Resampling.LANCZOS)
        product_photo = ImageTk.PhotoImage(product_image)
        
        label_photo = tk.Label(left_frame, image=product_photo, bg=info_bg_color)
        label_photo.image = product_photo
        label_photo.pack()
        
    except Exception as e:
        label_no_photo = tk.Label(
            left_frame,
            text="Фото\nне найдено",
            bg="#EEEEEE",
            fg="#666666",
            font=("Times New Roman", 10),
            width=20,
            height=10
        )
        label_no_photo.pack()
    
    center_frame = tk.Frame(card_frame, bg=info_bg_color, width=700)
    center_frame.pack(side="left", fill="y")
    center_frame.pack_propagate(False)
    
    header_text = f"{product['category']} | {product['name']}"
    label_header = tk.Label(
        center_frame,
        text=header_text,
        font=("Times New Roman", 14, "bold"),
        bg=info_bg_color,
        fg="#000000",
        justify="left"
    )
    label_header.pack(anchor="w", pady=(0, 6))
    
    description = product.get('description', 'Нет описания')
    if len(description) > 80:
        description = description[:80] + "..."
    
    label_desc = tk.Label(
        center_frame,
        text=f"Описание товара: {description}",
        font=("Times New Roman", 10),
        bg=info_bg_color,
        fg="#000000",
        justify="left",
        wraplength=680
    )
    label_desc.pack(anchor="w", pady=(0, 3))
    
    label_manuf = tk.Label(
        center_frame,
        text=f"Производитель: {product['manufacturer']}",
        font=("Times New Roman", 10),
        bg=info_bg_color,
        justify="left",
        fg="#000000"
    )
    label_manuf.pack(anchor="w", pady=(0, 3))
    
    label_prov = tk.Label(
        center_frame,
        text=f"Поставщик: {product['provider']}",
        font=("Times New Roman", 10),
        bg=info_bg_color,
        justify="left",
        fg="#000000"
    )
    label_prov.pack(anchor="w", pady=(0, 3))
    
    price = product['price']
    discount_val = product.get('discount', 0)
    unit = product.get('unit', '')

    if discount_val > 0:
        price_frame = tk.Frame(center_frame, bg=info_bg_color)
        price_frame.pack(anchor="w", pady=(0, 3))

        label_price_text = tk.Label(
            price_frame,
            text="Цена: ",
            font=("Times New Roman", 10, "bold"),
            bg=info_bg_color,
            fg="#000000"
        )
        label_price_text.pack(side="left")
        
        label_old_price = tk.Label(
            price_frame,
            text=f"{price} руб",
            font=("Times New Roman", 10, "overstrike"), 
            bg=info_bg_color,
            fg="#FF0000"
        )
        label_old_price.pack(side="left")
        
        new_price = calculate_discounted_price(price, discount_val)
        label_new_price = tk.Label(
            price_frame,
            text=f"  {new_price} руб",
            font=("Times New Roman", 10, "bold"),
            bg=info_bg_color,
            fg="#000000" 
        )
        label_new_price.pack(side="left")
    
    else:
        label_price = tk.Label(
            center_frame,
            text=f"Цена: {price} руб",
            font=("Times New Roman", 10, "bold"),
            bg=info_bg_color,
            fg="#000000"
        )
        label_price.pack(anchor="w", pady=(0, 3))
    
    label_unit = tk.Label(
        center_frame,
        text=f"Единица измерения: {unit}",
        font=("Times New Roman", 10),
        bg=info_bg_color,
        fg="#000000"
    )
    label_unit.pack(anchor="w", pady=(0, 3))

    label_stock = tk.Label(
        center_frame,
        text=f"Количество на складе: {stock_quantity}",
        font=("Times New Roman", 10),
        bg=stock_bg_color,
        fg="#000000",
        anchor="w"
    )
    label_stock.pack(anchor="w", fill="x", pady=(0, 3))
    
    right_frame = tk.Frame(card_frame, bg=info_bg_color, width=150)
    right_frame.pack(side="right", fill="y")
    right_frame.pack_propagate(False)
    
    if discount > 0:
        label_discount = tk.Label(
            right_frame,
            text=f"{discount}%",
            font=("Times New Roman", 48, "bold"),
            bg=info_bg_color,
            fg="#000000"
        )
        label_discount.pack(expand=True)
    else:
        pass
    
    return card_frame


if __name__ == "__main__":
    test_user = {
        'id': 1,
        'role': 'admin',
        'full_name': 'Иван Иванов',
        'login': 'admin@test.com'
    }
    create_main_window(test_user)
    tk.mainloop()
