import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database import add_product, update_product, delete_product, get_product_by_id, check_product_in_orders

editor_window_open = False

def open_product_editor(product_id=None, parent_window=None, refresh_callback=None):
    global editor_window_open
    
    if editor_window_open:
        messagebox.showwarning(
            "Предупреждение",
            "Окно редактирования уже открыто!\nЗакройте его перед открытием нового."
        )
        return
    
    editor_window = tk.Toplevel()
    
    editor_window_open = True
    
    def on_closing():
        global editor_window_open
        editor_window_open = False
        editor_window.destroy()
    
    editor_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    if product_id:
        editor_window.title("Редактирование товара")
        mode = "edit"
    else:
        editor_window.title("Добавление нового товара")
        mode = "add"
    
    editor_window.geometry("800x700")
    editor_window.configure(bg="#FFFFFF")

    if parent_window:
        editor_window.transient(parent_window)
        editor_window.grab_set()
    
    header_frame = tk.Frame(editor_window, bg="#7FFF00", height=80)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    if mode == "edit":
        title_text = "Редактирование товара"
    else:
        title_text = "Добавление нового товара"
    
    label_title = tk.Label(
        header_frame,
        text=title_text,
        font=("Times New Roman", 20, "bold"),
        bg="#7FFF00",
        fg="#000000"
    )
    label_title.pack(expand=True)
    
    
    canvas = tk.Canvas(editor_window, bg="#FFFFFF", highlightthickness=0)
    scrollbar = tk.Scrollbar(editor_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    form_frame = tk.Frame(canvas, bg="#FFFFFF")
    canvas_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    form_frame.bind("<Configure>", on_frame_configure)
    
    fields_container = tk.Frame(form_frame, bg="#FFFFFF")
    fields_container.pack(padx=40, pady=20)
    
    entries = {}
    
    def create_field(label_text, widget_type="entry", values=None, width=40):
        row_frame = tk.Frame(fields_container, bg="#FFFFFF")
        row_frame.pack(fill="x", pady=8)
        
        label = tk.Label(
            row_frame,
            text=label_text,
            font=("Times New Roman", 11),
            bg="#FFFFFF",
            width=20,
            anchor="w"
        )
        label.pack(side="left", padx=(0, 10))
        
        if widget_type == "entry":
            widget = tk.Entry(
                row_frame,
                font=("Times New Roman", 11),
                width=width,
                relief="solid",
                bd=1
            )
        elif widget_type == "combobox":
            widget = ttk.Combobox(
                row_frame,
                values=values,
                font=("Times New Roman", 11),
                width=width-2,
                state="normal"
            )
        elif widget_type == "spinbox":
            widget = tk.Spinbox(
                row_frame,
                from_=0,
                to=100000,
                font=("Times New Roman", 11),
                width=width-2,
                relief="solid",
                bd=1
            )
        elif widget_type == "text":
            widget = tk.Text(
                row_frame,
                font=("Times New Roman", 11),
                width=width,
                height=4,
                relief="solid",
                bd=1
            )
        
        widget.pack(side="left")
        return widget
    
    entries['articul'] = create_field("Артикул *:", width=30)
    entries['name'] = create_field("Название товара *:")
    entries['category'] = create_field("Категория *:", "combobox", 
                                       ["Женская обувь", "Мужская обувь"])
    entries['manufacturer'] = create_field("Производитель *:")
    entries['provider'] = create_field("Поставщик *:")
    entries['price'] = create_field("Цена (руб) *:", "spinbox")
    entries['unit'] = create_field("Единица измерения *:", "combobox",
                                   ["пара", "шт.", "компл."])
    entries['discount'] = create_field("Скидка (%) *:", "spinbox")
    entries['stock_quantity'] = create_field("Количество на складе *:", "spinbox")
    entries['description'] = create_field("Описание товара:", "text")
    entries['photo'] = create_field("Фото (название файла):", width=30)
    
    hint_label = tk.Label(
        fields_container,
        text="* - обязательные поля",
        font=("Times New Roman", 9, "italic"),
        bg="#FFFFFF",
        fg="#666666"
    )
    hint_label.pack(pady=(10, 0))
    
    if mode == "edit" and product_id:
        product = get_product_by_id(product_id)
        
        if product:
            entries['articul'].insert(0, product['articul'] or '')
            entries['name'].insert(0, product['name'] or '')
            entries['category'].set(product['category'] or '')
            entries['manufacturer'].insert(0, product['manufacturer'] or '')
            entries['provider'].insert(0, product['provider'] or '')
            entries['price'].delete(0, tk.END)
            entries['price'].insert(0, product['price'] or 0)
            entries['unit'].set(product['unit'] or 'пара')
            entries['discount'].delete(0, tk.END)
            entries['discount'].insert(0, product['discount'] or 0)
            entries['stock_quantity'].delete(0, tk.END)
            entries['stock_quantity'].insert(0, product['stock_quantity'] or 0)
            entries['description'].insert('1.0', product['description'] or '')
            entries['photo'].insert(0, product['photo'] or '')
    
    buttons_frame = tk.Frame(fields_container, bg="#FFFFFF")
    buttons_frame.pack(pady=30)
    
    def validate_and_save():
        
        articul = entries['articul'].get().strip()
        name = entries['name'].get().strip()
        category = entries['category'].get().strip()
        manufacturer = entries['manufacturer'].get().strip()
        provider = entries['provider'].get().strip()
        
        try:
            price = float(entries['price'].get())
        except:
            messagebox.showerror("Ошибка", "Цена должна быть числом!")
            return
        
        unit = entries['unit'].get().strip()
        
        try:
            discount = int(entries['discount'].get())
            if discount < 0 or discount > 100:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Скидка должна быть от 0 до 100!")
            return
        
        try:
            stock_quantity = int(entries['stock_quantity'].get())
            if stock_quantity < 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Количество должно быть положительным числом!")
            return
        
        description = entries['description'].get('1.0', tk.END).strip()
        photo = entries['photo'].get().strip()
        
        if not all([articul, name, category, manufacturer, provider, unit]):
            messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
            return
        
        if mode == "add":
            result = add_product(articul, name, unit, price, provider, manufacturer,
                               category, discount, stock_quantity, description, photo)
            if result:
                messagebox.showinfo("Успех", "Товар успешно добавлен!")
                if refresh_callback:
                    refresh_callback()
                on_closing()
        else:
            result = update_product(product_id, articul, name, unit, price, provider,
                                  manufacturer, category, discount, stock_quantity,
                                  description, photo)
            if result:
                messagebox.showinfo("Успех", "Товар успешно обновлен!")
                if refresh_callback:
                    refresh_callback()
                on_closing()
    
    button_save = tk.Button(
        buttons_frame,
        text="Сохранить",
        font=("Times New Roman", 12),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        width=20,
        height=2,
        cursor="hand2",
        relief="raised",
        bd=3,
        command=validate_and_save
    )
    button_save.pack(side="left", padx=10)
    
    button_cancel = tk.Button(
        buttons_frame,
        text="Отмена",
        font=("Times New Roman", 12),
        bg="#00FA9A",
        activebackground="#00FA9A",
        fg="#000000",
        activeforeground="#000000",
        width=20,
        height=2,
        cursor="hand2",
        relief="raised",
        bd=3,
        command=on_closing
    )
    button_cancel.pack(side="left", padx=10)
    
    if mode == "edit":
        def confirm_delete():
            if check_product_in_orders(product_id):
                messagebox.showerror("Ошибка", "Невозможно удалить товар, так как он присутствует в заказах.")
                return

            product_name = entries['name'].get().strip()
            result = messagebox.askyesno(
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить товар:\n{product_name}?",
                icon="warning"
            )
            if result:
                if delete_product(product_id):
                    messagebox.showinfo("Успех", "Товар успешно удален из базы данных")
                    if refresh_callback:
                        refresh_callback()
                    on_closing()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить товар")
        
        button_delete = tk.Button(
            buttons_frame,
            text="Удалить товар",
            font=("Times New Roman", 12),
            bg="#00FA9A",
            activebackground="#00FA9A",
            fg="#000000",
            activeforeground="#000000",
            width=20,
            height=2,
            cursor="hand2",
            relief="raised",
            bd=3,
            command=confirm_delete
        )
        button_delete.pack(side="left", padx=10)