# add_products.py
import random
from models import Product, db

# You may need to import and set up your app and database connection here, depending on your project structure.
# For example:
from app import app
app.app_context().push()

# Create a list of product names and prices
products_data = [
    ('Wireless Mouse', 29.99),
    ('Bluetooth Headphones', 59.99),
    ('LED Desk Lamp', 39.99),
    ('USB-C Hub', 49.99),
    ('Portable Charger', 24.99),
    ('Gaming Keyboard', 89.99),
    ('Gaming Mouse', 69.99),
    ('Smartphone Case', 19.99),
    ('Fitness Tracker', 99.99),
    ('Reusable Water Bottle', 15.99),
    ('Yoga Mat', 34.99),
    ('Resistance Bands', 12.99),
    ('Foam Roller', 29.99),
    ('Running Shoes', 79.99),
    ('Noise-Canceling Earbuds', 119.99),
    ('Wireless Charger', 39.99),
    ('Compact Mirrorless Camera', 499.99),
    ('External Hard Drive', 89.99),
    ('eBook Reader', 129.99),
    ('Tablet Stand', 24.99),
    ('Laptop Sleeve', 26.99),
    ('Stylus Pen', 19.99),
    ('Wireless Speaker', 89.99),
    ('Smart Light Bulb', 19.99),
    ('Aromatherapy Diffuser', 39.99),
    ('Mechanical Pencil', 4.99),
    ('Notebook', 9.99),
    ('Backpack', 59.99),
    ('Travel Mug', 24.99),
    ('Reusable Shopping Bag', 7.99),
    ('Insulated Food Container', 19.99),
    ('Adjustable Phone Stand', 14.99),
    ('Microfiber Cleaning Cloth', 8.99),
    ('Memory Foam Pillow', 49.99),
    ('Portable Bluetooth Speaker', 59.99),
    ('Smart Thermostat', 249.99),
    ('Electric Toothbrush', 79.99),
    ('Bamboo Cutting Board', 29.99),
    ('Kitchen Knife Set', 99.99),
    ('Cast Iron Skillet', 39.99),
    ('Food Storage Containers', 19.99),
    ('Wine Glasses', 29.99),
    ('Bath Towels', 39.99),
    ('Bed Sheets', 69.99),
    ('Clothes Hangers', 14.99),
    ('Laundry Hamper', 24.99),
    ('Vacuum Cleaner', 199.99),
    ('Air Purifier', 149.99),
    ('Slow Cooker', 59.99),
    ('Espresso Machine', 299.99),
    ('Electric Kettle', 39.99),
]


# # Add 50 random products to the list
# for i in range(3, 51):
#     product_name = f'Product {i}'
#     product_price = round(random.uniform(5.00, 100.00), 2)
#     products_data.append((product_name, product_price))

# Add the products to the database
for name, price in products_data:
    new_product = Product(name=name, price=price)
    db.session.add(new_product)

# Commit the changes
db.session.commit()

print("50 products have been added to the database.")
