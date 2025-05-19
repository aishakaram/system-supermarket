import sqlite3
import atexit
import sys


# Secret key for admin registration
ADMIN_KEY = "admin123"  # Change this for security

# Function to connect to the database
conn = sqlite3.connect("supermarket.db")
cursor = conn.cursor()

# Ensure database connection closes on exit
def close_connection():
    if conn:
        conn.close()
        pass

atexit.register(close_connection)

# Create users table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                 )''')

# Create sections table
cursor.execute('''CREATE TABLE IF NOT EXISTS sections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                 )''')

# Create products table (linked to sections)
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    section_id INTEGER NOT NULL,
                    FOREIGN KEY (section_id) REFERENCES sections(id)
                 )''')

# Create orders table
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                 )''')
conn.commit()

# User Registration
def register():
    username = input("Enter a new username: ").strip()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

    if cursor.fetchone():
        print(" Username already exists. Try again.")
        return

    password = input("Enter a new password: ").strip()

    # Ask if the user is an admin
    is_admin = input("Are you registering as an admin? (yes/no): ").strip().lower()
    if is_admin == "yes":
        admin_key = input("Enter the admin key: ").strip()
        if admin_key == ADMIN_KEY:
            role = "admin"
        else:
            print(" Incorrect Admin key. Try again.")
            return
    elif is_admin == "no":
        role = "customer"
    else:
        print("Invalid choice!")
        return

    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    print(f" Registration successful! You are registered as a {role}.")

# User Login
def login():
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        print(f"Login successful! Welcome, {username} ({user[0]})")
        if user[0] == "admin":
            admin_menu()
        else:
            shop(username)
    else:
        print(" Invalid username or password.")

# Admin Menu
def admin_menu():
    while True:
        print("\n=== Admin Panel ===")
        print("1 Add Section")
        print("2 View Sections")
        print("3 Add Product")
        print("4 View Products")
        print("5 Remove Product")
        print("6 Update Product")
        print("7 View Order Logs")
        print("8 Logout")

        choice = input("Enter choice: ")
        if choice == "1": add_section()
        elif choice == "2": view_sections()
        elif choice == "3": add_product()
        elif choice == "4": view_products()
        elif choice == "5": remove_product()
        elif choice == "6": update_product()
        elif choice == "7": view_orders()
        elif choice == "8":
            print("\nExiting... Have a nice day!")
            break
        else:
            print("Invalid choice!")

def view_orders():
    cursor.execute("SELECT * FROM orders ORDER BY timestamp DESC")
    orders = cursor.fetchall()

    if not orders:
        print("\nNo orders found.")
        return

    print("\n=== Order Logs ===")
    print(f"{'ID':<5}{'Username':<15}{'Product':<20}{'Qty':<5}{'Total':<10}{'Timestamp'}")
    print("-" * 70)
    for order in orders:
        print(f"{order[0]:<5}{order[1]:<15}{order[2]:<20}{order[3]:<5}{order[4]:<10.2f}{order[5]}")


# Add a section (Admin)
def add_section():
    section_name = input("Enter new section name: ")
    try:
        cursor.execute("INSERT INTO sections (name) VALUES (?)", (section_name,))
        conn.commit()
        print(f" Section '{section_name}' added successfully!")
    except sqlite3.IntegrityError:
        print(f" Section '{section_name}' already exists!")

# View all sections
def view_sections():
    cursor.execute("SELECT * FROM sections")
    sections = cursor.fetchall()
    print("\n Sections List:")
    print("-" * 30)
    for section in sections:
        print(f"ID: {section[0]}, Name: {section[1]}")

# Add a product (Admin)
def add_product():
    name = input("Enter product name: ")
    price = float(input("Enter product price: "))
    stock = int(input("Enter product stock quantity: "))
    view_sections()
    section_id = int(input("Enter Section ID: "))

    cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
    if cursor.fetchone() is None:
        print(" Invalid Section ID!")
    else:
        cursor.execute("INSERT INTO products (name, price, stock, section_id) VALUES (?, ?, ?, ?)",
                       (name, price, stock, section_id))
        conn.commit()
        print(f" Product '{name}' added successfully!")

# View all products
def view_products():
    cursor.execute('''SELECT products.id, products.name, products.price, products.stock, sections.name 
                      FROM products 
                      LEFT JOIN sections ON products.section_id = sections.id''')
    products = cursor.fetchall()

    print("\nProduct List:")
    print("-" * 50)
    for product in products:
        print(f"ID: {product[0]}, Name: {product[1]}, Price: ${product[2]}, Stock: {product[3]}, Section: {product[4]}")

# Remove product
def remove_product():
    view_products()
    product_id = int(input("Enter Product ID to remove: "))
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        print(f" Product ID {product_id} removed successfully!")
    else:
        print(" Product not found!")

# Update product
def update_product():
    view_products()
    product_id = int(input("Enter Product ID to update: "))
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        print(" Product not found!")
        return

    print("Leave blank to keep the current value.")
    new_name = input(f"New Name [{product[1]}]: ") or product[1]
    new_price = input(f"New Price [{product[2]}]: ")
    new_price = float(new_price) if new_price else product[2]
    new_stock = input(f"New Stock [{product[3]}]: ")
    new_stock = int(new_stock) if new_stock else product[3]

    view_sections()
    new_section_id = input(f"New Section ID [{product[4]}]: ")
    new_section_id = int(new_section_id) if new_section_id else product[4]

    cursor.execute('''
        UPDATE products 
        SET name = ?, price = ?, stock = ?, section_id = ?
        WHERE id = ?
    ''', (new_name, new_price, new_stock, new_section_id, product_id))

    conn.commit()

    print(f" Product '{new_name}' updated successfully!")

# Shopping functions
def shop(username):
    print(f"\nWelcome, {username}! You can now start shopping.")
    cart = []
    while True:
        print("\n1  View Sections\n2  Add to Cart\n3  Checkout\n4  Logout")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            view_sections()
        elif choice == "2":
            add_to_cart(cart)
        elif choice == "3":
            checkout(cart, username)
        elif choice == "4":
            print(" Logging out...")
            break
        else:
            print(" Invalid choice!")
# Select section
def select_section():
    cursor.execute("SELECT * FROM sections")
    sections = cursor.fetchall()

    if not sections:
        print("No sections available.")
        return None

    print("\nAvailable Sections:")
    for section in sections:
        print(f"{section[0]}. {section[1]}")  # Display section ID and Name

    while True:
        try:
            section_id = int(input("\nSelect a section by entering its number: "))
            cursor.execute("SELECT * FROM sections WHERE id = ?", (section_id,))
            if cursor.fetchone():
                return section_id
            else:
                print("Invalid section ID. Try again.")
        except ValueError:
            print("Please enter a valid number.")

# Function to display products in a selected section
def show_products(section_id):
    cursor.execute("SELECT id, name, price, stock FROM products WHERE section_id = ?", (section_id,))
    products = cursor.fetchall()

    if not products:
        print("No products available in this section.")
        return []

    print("\nAvailable Products:")
    print(f"{'ID':<5}{'Name':<20}{'Price':<10}{'Stock':<10}")
    print("-" * 45)

    for product in products:
        print(f"{product[0]:<5}{product[1]:<20}{product[2]:<10.2f}{product[3]:<10}")  # Align text properly

    return products

# Shopping Function
def add_to_cart(cart):
    section_id = select_section()
    if section_id:
        products = show_products(section_id)

        if not products:
            return  # No products in the section

        while True:
            product_id = input("\nEnter the Product ID to add to cart or 'Done' to finish: ").strip()
            if product_id.lower() == "done":
                break

            try:
                product_id = int(product_id)
                quantity = int(input("Enter quantity: "))

                # Get product details, ensuring it belongs to the selected section
                cursor.execute("SELECT name, price, stock FROM products WHERE id = ? AND section_id = ?", (product_id, section_id))
                product = cursor.fetchone()

                if not product:
                    print("This Product is not in the selected section. Try again.")
                    continue

                if quantity > product[2]:
                    print("Not enough stock available.")
                    continue

                # Add to cart
                cart.append((product_id, product[0], product[1], quantity))
                print(f"Added {quantity} x {product[0]} (${product[1]} each) to cart.")

            except ValueError:
                print("Invalid input. Try again.")


# checkout Function
def checkout(cart, username):
    if not cart:
        print(" Your cart is empty!")
        return

    total = sum(item[2] * item[3] for item in cart)

    confirm = ""
    while confirm not in ["yes", "2"]:  # Loop until "yes" or "2"

        # Show cart items every time before asking for confirmation
        print("\n Your Cart:")
        for item in cart:
            print(f"{item[1]} (x{item[3]}) - ${item[2] * item[3]:.2f}") # item[1] = name , item[2] = price , item[3] = stock

        print(f" Total: ${total:.2f}")
        confirm = input("Proceed to checkout? (yes/no): ").strip().lower()

        if confirm == "yes":

            for item in cart:
                cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item[3], item[0]))
                cursor.execute("INSERT INTO orders (username, product_name, quantity, total_price) VALUES (?, ?, ?, ?)",
                               (username, item[1], item[3], item[2] * item[3]))
            conn.commit()

            cart.clear()
            print(" Purchase successful!")
            break  # Exit loop after purchase

        elif confirm == "no":
            clear_1 = input("Wanna clear your items (1) or Keep them (2)? ").strip()

            if clear_1 == "1":
                cart.clear()
                print(" Cart cleared.")
                break #Exit after clear
            elif clear_1 == "2":
                print(" Keeping your cart items. Exiting...")
                break  # Exit after keeping items
            else:
                print(" Invalid choice!")  # Handles incorrect input for clearing

        else:
            print(" Invalid Please enter (yes/no) ")  # Handles incorrect checkout input


# Main Program
try:
    while True:
        print("\n1 Login\n2 Register\n3 Exit")
        option = input("Enter choice: ").strip()
        if option == "1":
            login()
        elif option == "2":
            register()
        elif option == "3":
            print("\nExiting... Have a nice day!")
            break
        else:
            print(" Invalid choice!")

except KeyboardInterrupt: # Handles any Terminate error
    print("\n\nExiting... Have a nice day! ")
finally:
    close_connection()
    sys.exit(0)
