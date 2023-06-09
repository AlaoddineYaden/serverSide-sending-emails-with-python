from flask import Flask, send_file, render_template
from flask.globals import g
import mysql.connector
import time
import tempfile

app = Flask(__name__)
app.config['DATABASE'] = {
    'host': 'cuddy.mysql.pythonanywhere-services.com',
    'user': 'cuddy',
    'password': 'V8RC8gm@TfpJqDk',
    'database': 'cuddy$emails'
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
        with open('/home/cuddy/mysite/emails.txt', 'r') as file:
            emails = file.read().splitlines()
            email_data = [(email,) for email in emails]
            cursor.executemany('''INSERT INTO cuddy$emails.emails (email) VALUES (%s)''', email_data)
            conn.commit()

            # Wait until the emails are inserted
            expected_count = len(emails)
            while True:
                cursor.execute('''SELECT COUNT(*) FROM cuddy$emails.emails''')
                count = cursor.fetchone()[0]
                if count == expected_count:
                    break
                time.sleep(1)

        conn.close()


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

@app.route('/insert')
def insert():
    try:
        insert_emails()
        return 'inserted'
    except mysql.connector.Error as e:
            print(f"Error insert 'emails' table: {e}")
            return f"error : {e}"

@app.route('/download_emails')
def download_emails():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Retrieve all emails from the database
        cursor.execute('''SELECT id, email FROM emails''')
        rows = cursor.fetchall()

        conn.close()

        # Create a string to store the emails and IDs
        email_text = ""
        for row in rows:
            email_id = row[0]
            email = row[1]
            email_text += f"{email_id}: {email}\n"

        # Create a temporary file and write the email text into it
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(email_text.encode())
            temp_file.flush()

            # Return the emails as a text file
            return send_file(
                temp_file.name,
                mimetype="text/plain",
                as_attachment=True,
                attachment_filename="emails.txt"
            )


@app.route('/image/<int:email_id>')
def track_image_request(email_id):
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Increment the view count
        view_count = increment_view_count(cursor, email_id)


        # Retrieve the email based on the email ID
        email = get_email(cursor, email_id)
        conn.commit()
        cursor.close()
        conn.close()
        if email:
            return send_file('/home/cuddy/mysite/gg.gif', mimetype='image/gif')
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
    app.run()






# # A very simple Flask Hello World app for you to get started with...

# from flask import Flask, send_file

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask!'


# @app.route('/image')
# def track_image_request():
#     # Increment the view count
#     # view_count = 0
#     # with open('/home/cuddy/mysite/view_count.txt', 'w') as f:
#     #     f.write(str(view_count))
#     with open('/home/cuddy/mysite/view_count.txt', 'r') as f:
#         view_count = int(f.read().strip())
#     view_count += 1
#     with open('/home/cuddy/mysite/view_count.txt', 'w') as f:
#         f.write(str(view_count))

#     # Return a 1x1 pixel PNG image
#     return send_file('/home/cuddy/mysite/gg.gif', mimetype='image/gif')

