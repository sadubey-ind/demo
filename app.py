from flask import Flask, render_template, request,jsonify,send_from_directory,redirect,url_for
import sqlite3
import os
app = Flask(__name__)

def initialize_database():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            gender TEXT,
            date_of_birth
                   
        )
    ''')
    conn.commit()
    conn.close()

# initialize_database()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, gender) VALUES (?, ?, ?)', (name, email,"Male"))
        conn.commit()
        conn.close()
        return redirect("/")
@app.route('/display')
def display():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    user_data = cursor.fetchall()
    conn.close()
    return render_template('display.html', user_data=user_data)

@app.route('/update/<int:ID>', methods=['GET', 'POST'])
def update(ID):
    # Check if the user ID exists
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (ID,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return "User not found", 404  # Return a 404 error if the user is not found

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        dob = request.form['dob']
        gen = request.form['gen']

        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name=?, email=?, gender=?, date_of_birth=? WHERE id=?',
                       (name, email, gen, dob, ID))
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template('update.html', user=user)

@app.route('/delete/<int:ID>', methods=['GET', 'POST'])
def delete_user(ID):
    if request.method == 'POST':
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (ID,))
        conn.commit()
        conn.close()
        return redirect(url_for('display'))

    return render_template('delete.html', ID=ID)


@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        # Assuming the request data is in JSON format
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')

        # Store data in the SQLite database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        conn.commit()
        conn.close()
        user_id = cursor.lastrowid

        conn.close()

        # Return JSON response with the message and user ID
        response_data = {
            "message": "User added successfully",
            "user_id": user_id
        }

        return jsonify(response_data)

@app.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if request.method == 'PUT':
        # Assuming the request data is in JSON format
        data = request.get_json()

        new_name = data.get('name')
        new_email = data.get('email')

        # Update data in the SQLite database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name=?, email=? WHERE id=?', (new_name, new_email, user_id))
        conn.commit()
        conn.close()

        return jsonify({"ID:{},Name:{}".format(user_id,new_name): "User updated successfully"})

# Function to fetch user data from the database
def get_user_data():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    user_data = cursor.fetchall()
    conn.close()
    return user_data

@app.route('/get_users', methods=['GET'])
def get_users():
    if request.method == 'GET':
        user_data = get_user_data()
        # Convert the data to JSON and return
        return jsonify({"users": user_data})
def get_user_by_id(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data
@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        # Convert the data to JSON and return
        return jsonify({"user": user_data})
    else:
        return jsonify({"message": "User not found"}), 404
    
def delete_user_by_id(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete(user_id):
    delete_user_by_id(user_id)
    return jsonify({"message": f"User with ID {user_id} deleted successfully"})
@app.route('/about')
def about_page():
    return render_template('about.html')
def sugg():
    conn = sqlite3.connect('suggestions.db', check_same_thread=False)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suggestions
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        suggestion TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()

@app.route('/save_suggestion', methods=['POST'])
def save_suggestion():
    conn = sqlite3.connect('suggestions.db')
    cursor = conn.cursor()
    suggestion = request.form['suggestion']
    cursor.execute('INSERT INTO suggestions (suggestion) VALUES (?)', (suggestion,))
    conn.commit()
    return render_template('about.html')

@app.route('/get_suggestions')
def get_suggestions():
    conn = sqlite3.connect('suggestions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM suggestions ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    suggestions = [{'id': row[0], 'suggestion': row[1], 'timestamp': row[2]} for row in rows]
    return render_template('suggestions.html', suggestions=suggestions)
@app.route('/blog')
def blog():
    return render_template('blog.html')

if __name__=="__main__":
    initialize_database()
    app.run(debug=False,port=8888)