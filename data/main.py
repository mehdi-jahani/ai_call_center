import pandas as pd
import os
import random

# مسیر فایل CSV محصولات
CSV_FILE_PATH = 'products.csv' # در همان دایرکتوری اصلی ai_call_center

# مسیر تصاویر (نسبت به روت پروژه FastAPI)
# این آدرس‌ها باید از دید مرورگر قابل دسترس باشند.
# فرض می‌کنیم فایل‌ها در ai_call_center/data/images هستند و FastAPI آنها را سرو می‌کند
# برای اینکه FastAPI این پوشه رو سرو کنه، بعدا یک استاتیک روت اضافه می‌کنیم
IMAGE_DIR_FOR_URL = "/static/images/"
IMAGE_FILENAMES = ["test-1.jpg", "test-2.jpg", "test-3.jpg", "test-4.jpg", "test-5.jpg"]

# لیست URLهای تصادفی (میتونی اینجا رو با URLهای واقعی خودت جایگزین کنی)
RANDOM_URLS = [
    "https://example.com/product/1",
    "https://example.com/product/2",
    "https://example.com/product/3",
    "https://example.com/product/4",
    "https://example.com/product/5",
    "https://example.com/product/details/a",
    "https://example.com/product/info/b",
    "https://shop.example.com/item/xyz",
    "https://bestbuy.example.com/sku/123",
    "https://product.example.com/view/789"
]

def generate_random_url():
    return random.choice(RANDOM_URLS)

def generate_random_image_url():
    return IMAGE_DIR_FOR_URL + random.choice(IMAGE_FILENAMES)

if os.path.exists(CSV_FILE_PATH):
    df = pd.read_csv(CSV_FILE_PATH)
    print(f"Existing {CSV_FILE_PATH} found. Adding/updating 'image-url' and 'url' columns.")
else:
    # اگر فایل CSV موجود نیست، یک DataFrame نمونه ایجاد می‌کنیم
    print(f"No existing {CSV_FILE_PATH} found. Creating a sample one.")
    data = {
        'ID': [5772, 1234, 5678, 9012, 3456],
        'Title': ['13pcs Premium Makeup Brush Set', 'Xiaomi Electric Shaver', 'Smart LED Strip', 'Ergonomic Office Chair', 'Portable Bluetooth Speaker'],
        'Description': ['Introducing a high-quality makeup brush set.', 'USB Rechargeable, Waterproof, Portable Travel Trimmer.', 'Colorful light strip with app control.', 'Comfortable chair for long working hours.', 'Powerful sound in a compact design.'],
        'Variation': ['Handle Cc', 'Electric Shaver', '5M RGB', 'Black Mesh', 'Waterproof'],
        'Category': ['Beauty & Health', 'Electronics', 'Smart Home', 'Furniture', 'Audio'],
        'Price': [37.87, 75.99, 25.00, 250.00, 45.00]
    }
    df = pd.DataFrame(data)

# اضافه کردن یا به روز رسانی ستون های image-url و url
df['image-url'] = [generate_random_image_url() for _ in range(len(df))]
df['url'] = [generate_random_url() for _ in range(len(df))]

# ذخیره DataFrame به عنوان CSV
df.to_csv(CSV_FILE_PATH, index=False)
print(f"Updated {CSV_FILE_PATH} with 'image-url' and 'url' columns.")