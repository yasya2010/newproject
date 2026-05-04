import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Глобальные переменные
movies = []
json_file = "movies.json"

def load_movies():
    global movies
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            movies = json.load(f)
    else:
        movies = []
    update_table()

def save_movies():
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)

def add_movie():
    # берём значения из полей
    name = entry_name.get().strip()
    genre = entry_genre.get().strip()
    year = entry_year.get().strip()
    rating = entry_rating.get().strip()

    # проверка на пустые поля
    if not name or not genre or not year or not rating:
        messagebox.showerror("Ошибка", "Заполните все поля!")
        return

    # проверка года
    if not year.isdigit():
        messagebox.showerror("Ошибка", "Год должен быть числом!")
        return
    year = int(year)

    # проверка рейтинга
    try:
        rating = float(rating)
        if rating < 0 or rating > 10:
            messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
            return
    except:
        messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
        return

    # добавляем фильм
    movies.append({
        "название": name,
        "жанр": genre,
        "год": year,
        "рейтинг": rating
    })
    save_movies()
    update_table()

    # очищаем поля
    entry_name.delete(0, tk.END)
    entry_genre.delete(0, tk.END)
    entry_year.delete(0, tk.END)
    entry_rating.delete(0, tk.END)

def update_table():
    # очищаем таблицу
    for row in table.get_children():
        table.delete(row)

    # получаем жанр и год для фильтрации
    filter_genre = filter_genre_var.get()
    filter_year = filter_year_var.get()

    # проходим по всем фильмам
    for m in movies:
        # фильтрация по жанру
        if filter_genre and filter_genre != "Все" and m["жанр"] != filter_genre:
            continue
        # фильтрация по году
        if filter_year:
            try:
                if int(filter_year) != m["год"]:
                    continue
            except:
                pass

        # вставляем в таблицу
        table.insert("", tk.END, values=(
            m["название"],
            m["жанр"],
            m["год"],
            m["рейтинг"]
        ))

def filter_changed(*args):
    update_table()

def delete_movie():
    selected = table.selection()
    if not selected:
        messagebox.showerror("Ошибка", "Выберите фильм для удаления!")
        return

    # получаем название фильма из выделенной строки
    item = table.item(selected[0])
    values = item["values"]
    movie_name = values[0]

    # удаляем
    global movies
    movies = [m for m in movies if m["название"] != movie_name]
    save_movies()
    update_table()

def get_unique_genres():
    genres = set()
    for m in movies:
        genres.add(m["жанр"])
    return sorted(list(genres))

def update_genre_filter():
    # обновляем список жанров в выпадающем меню
    genres = get_unique_genres()
    filter_genre_var.set("Все")
    menu = filter_genre_dropdown["menu"]
    menu.delete(0, "end")
    menu.add_command(label="Все", command=lambda: set_genre_filter("Все"))
    for g in genres:
        menu.add_command(label=g, command=lambda value=g: set_genre_filter(value))

def set_genre_filter(value):
    filter_genre_var.set(value)
    update_table()

# создаём окно
root = tk.Tk()
root.title("Movie Library - Личная кинотека")
root.geometry("700x500")
root.resizable(True, True)

# === РАМКА ДЛЯ ВВОДА ===
frame_input = tk.LabelFrame(root, text="Добавить фильм", padx=10, pady=10)
frame_input.pack(fill="x", padx=10, pady=5)

tk.Label(frame_input, text="Название:").grid(row=0, column=0, sticky="w")
entry_name = tk.Entry(frame_input, width=30)
entry_name.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame_input, text="Жанр:").grid(row=1, column=0, sticky="w")
entry_genre = tk.Entry(frame_input, width=30)
entry_genre.grid(row=1, column=1, padx=5, pady=2)

tk.Label(frame_input, text="Год выпуска:").grid(row=2, column=0, sticky="w")
entry_year = tk.Entry(frame_input, width=30)
entry_year.grid(row=2, column=1, padx=5, pady=2)

tk.Label(frame_input, text="Рейтинг (0-10):").grid(row=3, column=0, sticky="w")
entry_rating = tk.Entry(frame_input, width=30)
entry_rating.grid(row=3, column=1, padx=5, pady=2)

btn_add = tk.Button(frame_input, text="➕ Добавить фильм", command=add_movie, bg="lightgreen")
btn_add.grid(row=4, column=0, columnspan=2, pady=10)

# === РАМКА ДЛЯ ФИЛЬТРАЦИИ ===
frame_filter = tk.LabelFrame(root, text="Фильтрация", padx=10, pady=10)
frame_filter.pack(fill="x", padx=10, pady=5)

# фильтр по жанру
filter_genre_var = tk.StringVar()
filter_genre_var.set("Все")
filter_genre_var.trace("w", filter_changed)

tk.Label(frame_filter, text="Жанр:").grid(row=0, column=0, sticky="w")
filter_genre_dropdown = tk.OptionMenu(frame_filter, filter_genre_var, "Все")
filter_genre_dropdown.grid(row=0, column=1, padx=5)

# фильтр по году
tk.Label(frame_filter, text="Год:").grid(row=0, column=2, sticky="w", padx=(20, 0))
filter_year_var = tk.StringVar()
filter_year_var.trace("w", filter_changed)
entry_filter_year = tk.Entry(frame_filter, textvariable=filter_year_var, width=10)
entry_filter_year.grid(row=0, column=3, padx=5)

# === ТАБЛИЦА ===
frame_table = tk.LabelFrame(root, text="Список фильмов", padx=10, pady=10)
frame_table.pack(fill="both", expand=True, padx=10, pady=5)

# создаём таблицу
columns = ("название", "жанр", "год", "рейтинг")
table = ttk.Treeview(frame_table, columns=columns, show="headings", height=12)

table.heading("название", text="Название")
table.heading("жанр", text="Жанр")
table.heading("год", text="Год")
table.heading("рейтинг", text="Рейтинг")

table.column("название", width=200)
table.column("жанр", width=120)
table.column("год", width=80)
table.column("рейтинг", width=80)

# скроллбар
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)

table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# кнопка удаления
btn_delete = tk.Button(root, text="🗑 Удалить выбранный фильм", command=delete_movie, bg="lightcoral")
btn_delete.pack(pady=10)

# загружаем данные и обновляем фильтры
load_movies()
update_genre_filter()

# запускаем программу
root.mainloop()