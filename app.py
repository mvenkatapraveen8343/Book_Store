from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from email.message import EmailMessage
from datetime import timedelta
import pymysql
import smtplib
import random
import base64

app = Flask(__name__)
app.secret_key = "BookHub_Secret_Key_2024"
app.permanent_session_lifetime = timedelta(minutes=60)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Praveen@8343',
    'database': 'book_store',
}

admin_email = 'mvenkatapraveen8343@gmail.com'
admin_password = 'nvap gqra joea cepa'

def get_connection():
    return pymysql.connect(**db_config)

def db_init():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            Product_ID INT PRIMARY KEY AUTO_INCREMENT,
            Product_Name VARCHAR(100) NOT NULL,
            Product_Image LONGBLOB NOT NULL,
            Category VARCHAR(30) NOT NULL,
            Actual_Price INT NOT NULL,
            Discount_Price INT,
            Stock INT NOT NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Admin(
            Admin_ID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(50) NOT NULL,
            Email VARCHAR(50) UNIQUE NOT NULL,
            Password VARCHAR(100) NOT NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            User_ID INT PRIMARY KEY AUTO_INCREMENT,
            Name VARCHAR(50) NOT NULL,
            Email VARCHAR(30) UNIQUE NOT NULL,
            Mobile BIGINT UNIQUE NOT NULL,
            Password VARCHAR(20)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Cart(
            User_ID INT NOT NULL,
            Product_ID INT NOT NULL,
            Quantity INT DEFAULT 1,
            PRIMARY KEY (User_ID, Product_ID)
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

db_init()

def send_mail(to_email, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["To"] = to_email
    msg["From"] = admin_email
    msg["Subject"] = "OTP Verification for Book Store"
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(admin_email, admin_password)
        smtp.send_message(msg)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        if password != cpassword:
            return render_template('message.html', message="Passwords do not match")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Admin (Name, Email, Password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('admin_login.html', message="Admin registered successfully.")
    return render_template('admin_signup.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Admin WHERE Email = %s', (email,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        if not admin:
            return render_template('message.html', message="Admin not found")
        elif admin[3] != password:
            return render_template('message.html', message="Invalid password")
        else:
            session.permanent = True
            session['admin_id'] = admin[0]
            session['admin_name'] = admin[1]
            return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM Products')
    total_books = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM Products WHERE Stock < 5')
    low_stock_books = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT Category) FROM Products')
    total_categories = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM Users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT * FROM Products ORDER BY Product_ID DESC LIMIT 3')
    recent_books = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         admin=session['admin_name'],
                         total_books=total_books,
                         low_stock_books=low_stock_books,
                         total_categories=total_categories,
                         total_users=total_users,
                         recent_books=recent_books)

@app.route('/add_products', methods=['GET', 'POST'])
def add_products():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        name = request.form.get('product_name')
        image_file = request.files.get('product_image')
        if not image_file:
            return "No image uploaded!", 400
        image = image_file.read()
        category = request.form.get('product_genre')
        price = request.form.get('actual_price')
        discount = request.form.get('discount_price')
        stock = request.form.get('quantity')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Products 
            (Product_Name, Product_Image, Category, Actual_Price, Discount_Price, Stock)
            VALUES (%s,%s,%s,%s,%s,%s)
        ''', (name, image, category, price, discount, stock))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('admin_add_products.html', message="Product added successfully")
    return render_template('admin_add_products.html')

@app.route('/manage_products')
def manage_products():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Products')
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    products = []
    for book in books:
        product_id, name, image, category, actual_price, discount_price, stock = book
        image_base64 = base64.b64encode(image).decode('utf-8')
        products.append((product_id, name, image_base64, category, actual_price, discount_price, stock))
    return render_template('admin_manage_products.html', products=products)

@app.route('/update_product/<int:p_id>', methods=['GET', 'POST'])
def update_product(p_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('product_name')
        image_file = request.files.get('product_image')
        category = request.form.get('product_genre')
        price = request.form.get('actual_price')
        discount = request.form.get('discount_price')
        stock = request.form.get('quantity')
        if image_file and image_file.filename != '':
            image = image_file.read()
            cursor.execute('''
                UPDATE Products
                SET Product_Name=%s, Product_Image=%s, Category=%s, Actual_Price=%s, Discount_Price=%s, Stock=%s
                WHERE Product_ID=%s
            ''', (name, image, category, price, discount, stock, p_id))
        else:
            cursor.execute('''
                UPDATE Products
                SET Product_Name=%s, Category=%s, Actual_Price=%s, Discount_Price=%s, Stock=%s
                WHERE Product_ID=%s
            ''', (name, category, price, discount, stock, p_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('manage_products'))
    cursor.execute('SELECT * FROM Products WHERE Product_ID=%s', (p_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if not product:
        return render_template('message.html', message="Product not found")
    product_data = {
        'id': product[0],
        'name': product[1],
        'category': product[3],
        'actual_price': product[4],
        'discount_price': product[5],
        'stock': product[6],
    }
    return render_template('admin_add_products.html', product=product_data, update=True)

@app.route('/delete_product/<int:p_id>')
def delete_product(p_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE Product_ID = %s", (p_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('manage_products'))

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect(url_for('admin_login'))

@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if password != cpassword:
            return render_template('message.html', message="Password doesn't match")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email=%s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return render_template('message.html', message='Email already exists!')
        otp = str(random.randint(100000, 999999))
        send_mail(email, f"Your OTP : {otp}")
        return render_template('verify_otp.html', name=name, email=email, mobile=mobile, password=password, otp=otp)
    return render_template('user_signup.html')

@app.route('/verify_otp', methods=['POST', 'GET'])
def verify_otp():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        otp = request.form.get('otp')
        cotp = request.form.get('cotp')
        if otp == cotp:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Users (Name, Email, Mobile, Password)
                VALUES (%s,%s,%s,%s)
            ''', (name, email, mobile, password))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('user_login.html', message="Account created successfully")
        else:
            return render_template('message.html', message="Invalid OTP")
    return render_template('verify_otp.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email=%s AND Password=%s', (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session.permanent = True
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('user_dashboard'))
        else:
            return render_template('user_login.html', message='Invalid credentials')
    return render_template('user_login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Email=%s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return render_template('message.html', message="Email not found")
        
        otp = str(random.randint(100000, 999999))
        session['reset_email'] = email
        session['reset_otp'] = otp
        send_mail(email, f"Your OTP for password reset: {otp}")
        
        return redirect(url_for('reset_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session or 'reset_otp' not in session:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        email = request.form.get('email')
        cotp = request.form.get('cotp')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if cotp != session['reset_otp']:
            return render_template('message.html', message="Invalid OTP")

        if new_password != confirm_password:
            return render_template('message.html', message="Passwords do not match")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE Users SET Password=%s WHERE Email=%s', (new_password, email))
        conn.commit()
        cursor.close()
        conn.close()

        session.pop('reset_otp', None)
        session.pop('reset_email', None)

        return render_template('user_login.html', message="Password reset successfully")

    email = session['reset_email']
    otp = session['reset_otp']
    return render_template('reset_password.html', email=email, otp=otp)

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Products')
    products_data = cursor.fetchall()
    cursor.close()
    conn.close()
    products = []
    for product in products_data:
        product_id, name, image, category, actual_price, discount_price, stock = product
        image_base64 = base64.b64encode(image).decode('utf-8')
        products.append((product_id, name, image_base64, category, actual_price, discount_price, stock))
    return render_template('user_dashboard.html', products=products, user_name=session['user_name'], user_id=session['user_id'])

@app.route('/user_logout')
def user_logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('user_login'))

@app.route('/add_to_cart/<int:p_id>', methods=['POST'])
def add_to_cart(p_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Stock FROM Products WHERE Product_ID=%s", (p_id,))
    stock_row = cursor.fetchone()
    if not stock_row or stock_row[0] <= 0:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "stock": 0, "error": "Out of stock"})

    cursor.execute("SELECT Quantity FROM Cart WHERE User_ID=%s AND Product_ID=%s", (user_id, p_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE Cart SET Quantity = Quantity + 1 WHERE User_ID=%s AND Product_ID=%s", (user_id, p_id))
    else:
        cursor.execute("INSERT INTO Cart (User_ID, Product_ID, Quantity) VALUES (%s, %s, 1)", (user_id, p_id))

    cursor.execute("UPDATE Products SET Stock = Stock - 1 WHERE Product_ID=%s", (p_id,))
    conn.commit()

    cursor.execute("SELECT Stock FROM Products WHERE Product_ID=%s", (p_id,))
    new_stock = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(Quantity) FROM Cart WHERE User_ID=%s", (user_id,))
    cart_count = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    return jsonify({
        "success": True, 
        "stock": new_stock, 
        "cart_count": cart_count
    })

@app.route('/update_cart/<int:p_id>/<int:user_id>/<string:action>')
def update_cart(p_id, user_id, action):
    if 'user_id' not in session or session['user_id'] != user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=False, message="Unauthorized"), 401
        return redirect(url_for('user_login'))

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT Quantity FROM Cart WHERE Product_ID=%s AND User_ID=%s", (p_id, user_id))
    cart_row = cursor.fetchone()
    cursor.execute("SELECT Stock, Actual_Price, Discount_Price FROM Products WHERE Product_ID=%s", (p_id,))
    product_row = cursor.fetchone()

    if not cart_row or not product_row:
        cursor.close()
        conn.close()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=False)
        return redirect(url_for('shopping_cart', user_id=user_id))

    current_qty = cart_row[0]
    stock, actual_price, discount_price = product_row
    discount = discount_price if discount_price else 0
    price_per_unit = max(actual_price - discount, 0)

    if action == "increase":
        if stock > 0:
            cursor.execute("UPDATE Cart SET Quantity = Quantity + 1 WHERE Product_ID=%s AND User_ID=%s", (p_id, user_id))
            cursor.execute("UPDATE Products SET Stock = Stock - 1 WHERE Product_ID=%s", (p_id,))
            cursor.execute("SELECT Stock FROM Products WHERE Product_ID=%s", (p_id,))
            stock = cursor.fetchone()[0]
    elif action == "decrease":
        if current_qty > 1:
            cursor.execute("UPDATE Cart SET Quantity = Quantity - 1 WHERE Product_ID=%s AND User_ID=%s", (p_id, user_id))
            cursor.execute("UPDATE Products SET Stock = Stock + 1 WHERE Product_ID=%s", (p_id,))
        else:
            cursor.execute("DELETE FROM Cart WHERE Product_ID=%s AND User_ID=%s", (p_id, user_id))
            cursor.execute("UPDATE Products SET Stock = Stock + 1 WHERE Product_ID=%s", (p_id,))

    conn.commit()

    cursor.execute("SELECT Quantity FROM Cart WHERE Product_ID=%s AND User_ID=%s", (p_id, user_id))
    new_cart = cursor.fetchone()
    
    cursor.execute("SELECT SUM((p.Actual_Price - IFNULL(p.Discount_Price, 0)) * c.Quantity) FROM Cart c JOIN Products p ON c.Product_ID=p.Product_ID WHERE c.User_ID=%s", (user_id,))
    grand_total = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(Quantity) FROM Cart WHERE User_ID=%s", (user_id,))
    cart_count = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if new_cart:
            new_qty = new_cart[0]
            total_price = price_per_unit * new_qty
            return jsonify(
                success=True, 
                quantity=new_qty, 
                total_price=total_price, 
                grand_total=grand_total,
                cart_count=cart_count,
                stock=stock
            )
        else:
            return jsonify(
                success=True, 
                removed=True, 
                grand_total=grand_total,
                cart_count=cart_count
            )
    return redirect(url_for('shopping_cart', user_id=user_id))

@app.route('/remove_cart_item/<int:p_id>/<int:user_id>')
def remove_cart_item(p_id, user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=False, message="Unauthorized"), 401
        return redirect(url_for('user_login'))

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT Quantity FROM Cart WHERE Product_ID=%s AND User_ID=%s", (p_id, user_id))
    cart_row = cursor.fetchone()
    
    if cart_row:
        quantity = cart_row[0]
        cursor.execute("DELETE FROM Cart WHERE Product_ID=%s AND User_ID=%s", (p_id, user_id))
        cursor.execute("UPDATE Products SET Stock = Stock + %s WHERE Product_ID=%s", (quantity, p_id))
    
    conn.commit()

    cursor.execute("SELECT SUM((p.Actual_Price - IFNULL(p.Discount_Price, 0)) * c.Quantity) FROM Cart c JOIN Products p ON c.Product_ID=p.Product_ID WHERE c.User_ID=%s", (user_id,))
    grand_total = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(Quantity) FROM Cart WHERE User_ID=%s", (user_id,))
    cart_count = cursor.fetchone()[0] or 0

    cursor.close()
    conn.close()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            success=True, 
            removed=True, 
            grand_total=grand_total,
            cart_count=cart_count
        )
    return redirect(url_for('shopping_cart', user_id=user_id))

@app.route('/shopping_cart/<int:user_id>')
def shopping_cart(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('user_login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Product_ID, Quantity FROM Cart WHERE User_ID=%s", (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        cursor.close()
        conn.close()
        return render_template("shopping_cart.html", data=[], total=0, user_id=user_id)

    data = []
    grand_total = 0
    for product_id, quantity in cart_items:
        cursor.execute("SELECT Product_Name, Product_Image, Actual_Price, Discount_Price, Stock FROM Products WHERE Product_ID=%s", (product_id,))
        product = cursor.fetchone()
        if product:
            name, image_blob, actual_price, discount_price, stock = product
            image_base64 = "data:image/jpeg;base64," + base64.b64encode(image_blob).decode('utf-8')
            discount = discount_price if discount_price else 0
            price_per_unit = max(actual_price - discount, 0)
            total_price = price_per_unit * quantity
            data.append({
                "product_id": product_id,
                "name": name,
                "image": image_base64,
                "price_per_unit": price_per_unit,
                "quantity": quantity,
                "total_price": total_price
            })
            grand_total += total_price

    cursor.close()
    conn.close()
    return render_template("shopping_cart.html", data=data, total=grand_total, user_id=user_id)

@app.route('/payment_success', methods=['POST'])
def payment_success():
    user_id = request.form.get('userid')
    payment_id = request.form.get('razorpay_payment_id')
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid user"})

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cart WHERE User_ID=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": "Payment successful"})

if __name__ == "__main__":
    app.run(debug=True)