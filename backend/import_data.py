import csv
import random
from database import SessionLocal
import models


def run_import(filepath):
    db = SessionLocal()

    # Кэшируем существующие категории, чтобы не делать лишних запросов и не дублировать их
    existing_categories = {c.name: c for c in db.query(models.Category).all()}

    current_originator = "Неизвестный"
    current_crop = "Без категории"

    products_to_add = []

    # Открываем файл. utf-8-sig помогает убрать невидимые символы (BOM) в начале файла
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        # Пропускаем первые 4 строки с метаданными и заголовками
        for _ in range(4):
            next(reader, None)

        for row in reader:
            if not row or not any(row):
                continue

            # Безопасное извлечение нужных колонок
            col_0 = row[0].strip() if len(row) > 0 else ""
            col_3 = row[3].strip() if len(row) > 3 else ""
            col_5 = row[5].strip() if len(row) > 5 else ""

            # 1. Если заполнена только 1-я колонка -> это смена Оригинатора
            if col_0 and not col_3 and not col_5:
                current_originator = col_0

            # 2. Если заполнена только 4-я колонка -> это смена Вида культуры (Категория)
            elif not col_0 and col_3 and not col_5:
                current_crop = col_3
                # Добавляем категорию в БД, если её ещё нет
                if current_crop not in existing_categories:
                    new_cat = models.Category(name=current_crop)
                    db.add(new_cat)
                    db.commit()
                    db.refresh(new_cat)
                    existing_categories[current_crop] = new_cat

            # 3. Если заполнена только 6-я колонка -> это конкретный Сорт (Товар)
            elif not col_0 and not col_3 and col_5:
                # В конце строки находится статус (включен/исключен из реестра)
                # Берем только актуальные сорта
                if any("Включен" in cell for cell in row):
                    category = existing_categories.get(current_crop)

                    title = f"Семена: {current_crop} '{col_5}'"
                    desc = f"Оригинатор: {current_originator}.\nОфициальный сорт из государственного реестра."

                    # Формируем объект товара
                    product = models.Product(
                        title=title,
                        description=desc,
                        price=random.randint(50, 500),  # Генерируем базовую цену
                        stock_quantity=random.randint(10, 200),  # и случайный остаток на складе
                        category_id=category.id if category else None,
                        image_url=None
                    )
                    products_to_add.append(product)

    # Массовая вставка всех собранных товаров в MySQL (работает намного быстрее, чем по одному)
    if products_to_add:
        db.bulk_save_objects(products_to_add)
        db.commit()
        print(f"✅ Успешно добавлено {len(products_to_add)} товаров!")
    else:
        print("⚠️ Товары не найдены. Проверьте формат CSV-файла.")

    db.close()


if __name__ == "__main__":
    # Укажи точное имя файла
    run_import("data.csv")