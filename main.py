import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("700x500")

        self.weather_data = []
        # Укажем путь к файлу по умолчанию
        self.file_path = "weather_diary.json"

        # --- Фрейм для ввода данных ---
        input_frame = ttk.LabelFrame(root, text="Добавить новую запись")
        input_frame.pack(pady=10, padx=10, fill="x")

        # Дата
        ttk.Label(input_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        # Установка текущей даты по умолчанию
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=20)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=5)

        # Описание погоды
        ttk.Label(input_frame, text="Описание погоды:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Осадки (да/нет) - используем Checkbutton
        self.precip_var = tk.BooleanVar()
        self.precip_check = ttk.Checkbutton(input_frame, text="Были осадки", variable=self.precip_var)
        self.precip_check.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Кнопка "Добавить запись"
        add_button = ttk.Button(input_frame, text="Добавить запись", command=self.add_entry)
        add_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # --- Разделитель ---
        separator = ttk.Separator(root, orient='horizontal')
        separator.pack(pady=5, padx=10, fill='x')

        # --- Фрейм для фильтрации ---
        filter_frame = ttk.LabelFrame(root, text="Фильтр записей")
        filter_frame.pack(pady=10, padx=10, fill="x")

        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по температуре
        ttk.Label(filter_frame, text="Фильтр по температуре > (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Кнопка "Применить фильтр"
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=4, padx=5, pady=5)

        # Кнопка "Сбросить фильтр"
        reset_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        reset_filter_button.grid(row=0, column=5, padx=5, pady=5)

        # --- Фрейм для отображения данных ---
        list_frame = ttk.LabelFrame(root, text="Записи о погоде")
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Таблица для отображения данных
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        # Настройка колонок
        self.tree.column("Дата", width=100)
        self.tree.column("Температура", width=100)
        self.tree.column("Описание", width=300)
        self.tree.column("Осадки", anchors="center", width=80)

        # Добавление полосы прокрутки
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # --- Фрейм для кнопок управления файлами ---
        file_frame = ttk.Frame(root)
        file_frame.pack(pady=10, padx=10, fill="x")

        load_button = ttk.Button(file_frame, text="Загрузить из JSON", command=self.load_data_from_json)
        load_button.pack(side="left", padx=5)

        save_button = ttk.Button(file_frame, text="Сохранить в JSON", command=self.save_data_to_json)
        save_button.pack(side="left", padx=5)

        # Загрузка данных при старте, если файл существует
        self.load_data_from_json()
        self.update_treeview()

    def validate_date(self, date_str):
        """Проверяет корректность формата даты."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_temperature(self, temp_str):
        """Проверяет, является ли температура числом."""
        try:
            float(temp_str)
            return True
        except ValueError:
            return False

    def add_entry(self):
        """Добавляет новую запись о погоде."""
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        # 5. Проверка корректности ввода
        if not date or not self.validate_date(date):
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите дату в формате YYYY-MM-DD.")
            return
        if not temp_str or not self.validate_temperature(temp_str):
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите корректную температуру (число).")
            return
        if not desc:
            messagebox.showerror("Ошибка ввода", "Описание погоды не может быть пустым.")
            return

        temperature = float(temp_str)
        entry_data = {
            "date": date,
            "temperature": temperature,
            "description": desc,
            "precipitation": precip
        }

        self.weather_data.append(entry_data)
        self.update_treeview()

        # Очистка полей ввода после добавления
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False) # Сброс флажка
        # Восстановление текущей даты
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))


    def update_treeview(self, data_to_display=None):
        """Обновляет содержимое таблицы Treeview."""
        # Очищаем предыдущие записи
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Определяем, откуда брать данные для отображения
        data_source = data_to_display if data_to_display is not None else self.weather_data

        # Заполняем таблицу новыми записями
        for entry in data_source:
            precip_text = "Да" if entry.get("precipitation", False) else "Нет"
            self.tree.insert("", tk.END, values=(
                entry.get("date", ""),
                entry.get("temperature", ""),
                entry.get("description", ""),
                precip_text
            ))

    def apply_filter(self):
        """Применяет фильтрацию к отображаемым записям."""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered_data = self.weather_data[:] # Копируем все данные для фильтрации

        # Фильтр по дате
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка фильтра", "Некорректный формат даты для фильтра. Используйте YYYY-MM-DD.")
                return
            filtered_data = [entry for entry in filtered_data if entry.get("date") == filter_date]

        # Фильтр по температуре
        if filter_temp_str:
            if not self.validate_temperature(filter_temp_str):
                messagebox.showerror("Ошибка фильтра", "Некорректное значение температуры для фильтра. Введите число.")
                return
            filter_temp = float(filter_temp_str)
            filtered_data = [entry for entry in filtered_data if entry.get("temperature", float('-inf')) > filter_temp]

        self.update_treeview(filtered_data)

    def reset_filter(self):
        """Сбрасывает фильтры и отображает все записи."""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_treeview() # Отображает все данные

    def save_data_to_json(self):
        """Сохраняет текущие записи о погоде в JSON файл."""
        # Предлагаем пользователю выбрать место для сохранения файла
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить дневник погоды как..."
        )
        if not filepath: # Если пользователь отменил сохранение
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.weather_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные успешно сохранены в {filepath}")
            self.file_path = filepath # Обновляем текущий путь к файлу
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def load_data_from_json(self):
        """Загружает записи о погоде из JSON файла."""
        # Проверяем, существует ли файл по текущему пути
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Проверяем, что загруженные данные являются списком словарей (наш формат)
                    if isinstance(loaded_data, list) and all(isinstance(item, dict) for item in loaded_data):
                        self.weather_data = loaded_data
                        self.update_treeview()
                        messagebox.showinfo("Успех", f"Данные успешно загружены из {self.file_path}")
                    else:
                        messagebox.showwarning("Предупреждение", f"Файл {self.file_path} содержит данные некорректного формата. Начинаем с пустым дневником.")
                        self.weather_data = []
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка загрузки", f"Файл {self.file_path} имеет некорректный формат JSON.")
                self.weather_data = [] # Очищаем данные, если файл некорректен
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")
                self.weather_data = []
        else:
            # Если файла нет, просто инициализируем пустой список
            self.weather_data = []

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
