# from flask import Flask, send_file, render_template
# from flask.globals import g
# import sqlite3

# app = Flask(__name__)
# app.config['DATABASE'] = 'emails.db'

# # Create the emails table if it doesn't exist
# def create_emails_table():
#     with app.app_context():
#         conn = get_db()
#         cursor = conn.cursor()
#         cursor.execute('''CREATE TABLE IF NOT EXISTS emails
#                           (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT)''')
#         conn.commit()

# # Create the requests table if it doesn't exist
# def create_requests_table():
#     with app.app_context():
#         try:
#             conn = get_db()
#             cursor = conn.cursor()
#             cursor.execute('''CREATE TABLE IF NOT EXISTS requests
#                               (id INTEGER PRIMARY KEY AUTOINCREMENT, email_id INTEGER UNIQUE, count INTEGER DEFAULT 0,
#                               FOREIGN KEY(email_id) REFERENCES emails(id))''')
#             conn.commit()
#             conn.close()
#         except sqlite3.Error as e:
#             print(f"Error creating 'requests' table: {e}")


# # Insert emails from file into the database
# def insert_emails():
#     with app.app_context():
#         conn = get_db()
#         cursor = conn.cursor()
#         with open('emails.txt', 'r') as file:
#             emails = file.read().splitlines()
#             email_data = [(email,) for email in emails]
#             cursor.executemany('''INSERT INTO emails (email) VALUES (?)''', email_data)
#             conn.commit()

# # Get the database connection
# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(app.config['DATABASE'])
#     return db

# # Close the database connection at the end of the request
# @app.teardown_appcontext
# def close_db(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask!'

# @app.route('/image/<int:email_id>')
# def track_image_request(email_id):
#     with app.app_context():
#         conn = get_db()
#         cursor = conn.cursor()

#         # Increment the view count
#         view_count = increment_view_count(cursor, email_id)

#         # Retrieve the email based on the email ID
#         email = get_email(cursor, email_id)

#         cursor.close()

#         if email:
#             return send_file('gg.gif', mimetype='image/gif')
#         else:
#             return 'Email not found', 404

# def increment_view_count(cursor, email_id):
#     cursor.execute('''INSERT OR IGNORE INTO requests (email_id, count)
#                       VALUES (?, 0)''', (email_id,))
#     if cursor.rowcount > 0:
#         # A new row was inserted, increment the ID
#         cursor.execute('''UPDATE sqlite_sequence SET seq = seq + 1 WHERE name = 'requests' ''')
#     cursor.execute('''UPDATE requests SET count = count + 1 WHERE email_id = ?''', (email_id,))
#     cursor.connection.commit()

#     cursor.execute('''SELECT count FROM requests WHERE email_id = ?''', (email_id,))
#     view_count = cursor.fetchone()[0]

#     return view_count

# def get_email(cursor, email_id):
#     cursor.execute('''SELECT email FROM emails WHERE id = ?''', (email_id,))
#     email = cursor.fetchone()
#     if email:
#         return email[0]
#     else:
#         return None

# if __name__ == '__main__':
#     create_emails_table()
#     create_requests_table()
#     insert_emails()
#     app.run()

from flask import Flask, send_file, render_template
from flask.globals import g
import mysql.connector

app = Flask(__name__)
app.config['DATABASE'] = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'emails'
}

# Create the emails table if it doesn't exist
def create_emails_table():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS emails
                          (id INT PRIMARY KEY AUTO_INCREMENT, email VARCHAR(255))''')
        conn.commit()

# Create the requests table if it doesn't exist
def create_requests_table():
    with app.app_context():
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS requests
                              (id INT PRIMARY KEY AUTO_INCREMENT, email_id INT UNIQUE, count INT DEFAULT 0,
                              FOREIGN KEY(email_id) REFERENCES emails(id))''')
            conn.commit()
            conn.close()
        except mysql.connector.Error as e:
            print(f"Error creating 'requests' table: {e}")

# Insert emails from file into the database
def insert_emails():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        with open('emails.txt', 'r') as file:
            emails = file.read().splitlines()
            email_data = [(email,) for email in emails]
            cursor.executemany('''INSERT INTO emails (email) VALUES (%s)''', email_data)
            conn.commit()

# Get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(**app.config['DATABASE'])
    return db

# Close the database connection at the end of the request
@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/image/<int:email_id>')
def track_image_request(email_id):
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Increment the view count
        view_count = increment_view_count(cursor, email_id)

        # Retrieve the email based on the email ID
        email = get_email(cursor, email_id)

        cursor.close()

        if email:
            return send_file('gg.gif', mimetype='image/gif')
        else:
            return 'Email not found', 404

def increment_view_count(cursor, email_id):
    cursor.execute('''INSERT INTO requests (email_id, count)
                      VALUES (%s, 1)
                      ON DUPLICATE KEY UPDATE count = count + 1''', (email_id,))

    # If a new row was inserted, retrieve the count from the inserted row
    if cursor.rowcount > 0:
        view_count = 1
    else:
        cursor.execute('''UPDATE requests SET count = count + 1 WHERE email_id = %s''', (email_id,))
        cursor.connection.commit()
        cursor.execute('''SELECT count FROM requests WHERE email_id = %s''', (email_id,))
        view_count = cursor.fetchone()[0]

    return view_count




def get_email(cursor, email_id):
    cursor.execute('''SELECT email FROM emails WHERE id = %s''', (email_id,))
    email = cursor.fetchone()
    if email:
        return email[0]
    else:
        return None

if __name__ == '__main__':
    create_emails_table()
    create_requests_table()
    insert_emails()
    app.run()
