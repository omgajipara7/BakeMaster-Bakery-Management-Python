import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('bakery.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Orders (
    id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    total REAL NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS OrderItems (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders (id),
    FOREIGN KEY (product_id) REFERENCES Products (id)
)
''')

# Function to add a product to the inventory
def add_product(name, price, quantity):
    cursor.execute('INSERT INTO Products (name, price, quantity) VALUES (?, ?, ?)', (name, price, quantity))
    conn.commit()
    print("Product added successfully.")

# Function to display all products in the inventory
def display_products():
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    if not products:
        print("No products in inventory.")
    else:
        print("Inventory:")
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Quantity: {product[3]}")

# Function to place a new order
def place_order(customer_name):
    items = []
    while True:
        display_products()
        product_id = int(input("Enter product ID: "))
        quantity = int(input("Enter quantity: "))
        items.append((product_id, quantity))
        cont = input("Add another product? (y/n): ")
        if cont.lower() != 'y':
            break

    total = 0
    for item in items:
        cursor.execute('SELECT price FROM Products WHERE id=?', (item[0],))
        price = cursor.fetchone()[0]
        total += price * item[1]

    # Reduce quantity of products in inventory
    for item in items:
        cursor.execute('UPDATE Products SET quantity = quantity - ? WHERE id = ?', (item[1], item[0]))

    cursor.execute('INSERT INTO Orders (customer_name, total) VALUES (?, ?)', (customer_name, total))
    order_id = cursor.lastrowid

    for item in items:
        cursor.execute('INSERT INTO OrderItems (order_id, product_id, quantity) VALUES (?, ?, ?)', (order_id, item[0], item[1]))

    conn.commit()
    print("Order placed successfully. Grand Total:", total)

# Function to refill the inventory
def refill_inventory():
    display_products()
    product_id = int(input("Enter product ID to refill: "))
    quantity = int(input("Enter quantity to add: "))
    cursor.execute('UPDATE Products SET quantity = quantity + ? WHERE id = ?', (quantity, product_id))
    conn.commit()
    print("Inventory refilled successfully.")

# Function to display orders with detailed information about what products each customer bought and their quantities
def display_orders():
    cursor.execute('''
        SELECT Orders.customer_name, OrderItems.quantity, Products.name, Products.price, Orders.total
        FROM Orders
        JOIN OrderItems ON Orders.id = OrderItems.order_id
        JOIN Products ON OrderItems.product_id = Products.id
        ORDER BY Orders.customer_name
    ''')
    orders = cursor.fetchall()
    if not orders:
        print("No orders placed yet.")
    else:
        current_customer = None
        for order in orders:
            customer_name, quantity, product_name, price, total = order
            if current_customer != customer_name:
                if current_customer:
                    print(f"Total: {current_total}")
                print(f"\nCustomer: {customer_name}")
                current_customer = customer_name
                current_total = total
            print(f"Product: {product_name}, Quantity: {quantity}, Price: {price}")
            current_total += quantity * price
        print(f"Total: {current_total}")

# Main function to interact with the user
def main():
    while True:
        print("\nBakery Management System")
        print("1. Add Product")
        print("2. Display Products")
        print("3. Place Order")
        print("4. Refill Inventory")
        print("5. Display Orders")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter product name: ")
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            add_product(name, price, quantity)
        elif choice == '2':
            display_products()
        elif choice == '3':
            customer_name = input("Enter customer name: ")
            place_order(customer_name)
        elif choice == '4':
            refill_inventory()
        elif choice == '5':
            display_orders()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == "__main__":
    main()1