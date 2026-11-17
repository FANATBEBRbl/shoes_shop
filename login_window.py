import tkinter as tk
from tkinter import messagebox
import re
from PIL import Image, ImageTk 
from database import check_user_credentials  
from main_window import create_main_window

root = tk.Tk()

root.title("Ботинки - Вход")

root.geometry("600x700")
root.configure(bg="#FFFFFF")

logo_image = Image.open("static/Icon.png")
logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)

logo_photo = ImageTk.PhotoImage(logo_image)

label_logo = tk.Label(root, image=logo_photo, bg="#FFFFFF")
label_logo.pack(pady=30)

label_title = tk.Label(
    root, 
    text="Вход в систему", 
    font=("Times New Roman", 24, "bold"),
    bg="#FFFFFF",
    fg="#000000"
)
label_title.pack(pady=20)

label_login = tk.Label(
    root,
    text="Логин (Email):", 
    font=("Times New Roman", 14),
    bg="#FFFFFF",
    fg="#000000"
)
label_login.pack(pady=(10, 5))

entry_login = tk.Entry(
    root,
    width=35, 
    font=("Times New Roman", 12),
    bg="#FFFFFF",
    fg="#000000",
    relief="solid",
    bd=2
)
entry_login.pack(pady=(0, 15))

label_password = tk.Label(
    root,
    text="Пароль:", 
    font=("Times New Roman", 14),
    bg="#FFFFFF",
    fg="#000000"
)
label_password.pack(pady=(10, 5))

entry_password = tk.Entry(
    root,
    width=35, 
    font=("Times New Roman", 12),
    show="*",
    bg="#FFFFFF",
    fg="#000000",
    relief="solid",
    bd=2
)
entry_password.pack(pady=(0, 20))

def is_valid_login(login):
    pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, login) is not None

def open_main_window(user_data):
    root.destroy()
    create_main_window(user_data)
    
def login():
    login = entry_login.get()
    password = entry_password.get()
    
    if not login or not password:
        messagebox.showerror("Ошибка", "Пожалуйста, введите email и пароль.")
        return 
    
    if not is_valid_login(login):
        messagebox.showerror("Ошибка", "Введите email в формате user@example.com.")
        return 
    
    user_data = check_user_credentials(login, password)
    
    if user_data:
        messagebox.showinfo(
            "Успех", 
            f"Добро пожаловать, {user_data['full_name']}!\n\n"
            f"Роль: {user_data['role']}\n"
            f"Email: {user_data['login']}"
        )
        open_main_window(user_data)
    else:
        messagebox.showerror(
            "Ошибка входа", 
            "Неверный email или пароль.\n\nПопробуйте еще раз."
        )

def login_as_guest():
    guest_user = {
        'id': 0,
        'role': 'guest',
        'full_name': 'Гость',
    }
    open_main_window(guest_user)

button_login = tk.Button(
    root, 
    text="Войти", 
    command=login,
    width=25, 
    font=("Times New Roman", 14),
    bg="#00FA9A",
    activebackground="#00FA9A",
    fg="#000000",
    activeforeground="#000000",
    relief="raised",
    bd=3,
    cursor="hand2" 
)
button_login.pack(pady=20)

button_guest = tk.Button(
    root,
    text="Войти как гость",
    command= login_as_guest,
    width=25,
    font=("Times New Roman", 12),
    bg="#00FA9A",
    activebackground="#00FA9A",
    fg="#000000",
    activeforeground="#000000",
    relief="raised",
    bd=3,
    cursor="hand2"
)

button_guest.pack(pady=10)

root.mainloop()
