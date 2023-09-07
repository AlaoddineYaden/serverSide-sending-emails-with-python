from flask import Flask, send_file, render_template,Response
from flask.globals import g
import mysql.connector
import time
import tempfile
import requests
import json
import gevent

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
# def insert_emails():
#     with app.app_context():
#         conn = get_db()
#         cursor = conn.cursor()
#         with open('/home/cuddy/mysite/emails.txt', 'r') as file:
#             emails = file.read().splitlines()
#             email_data = [(email,) for email in emails]
#             cursor.executemany('''INSERT INTO cuddy$emails.emails (email) VALUES (%s)''', email_data)
#             conn.commit()

#             # Wait until the emails are inserted
#             expected_count = len(emails)
#             while True:
#                 cursor.execute('''SELECT COUNT(*) FROM cuddy$emails.emails''')
#                 count = cursor.fetchone()[0]
#                 if count == 64324:
#                     break
#                 time.sleep(1)

#         conn.close()

def check_inserted_emails(cursor, expected_count):
    cursor.execute(
        f"""SELECT COUNT(*) FROM cuddy$emails.emails"""
    )
    count = cursor.fetchone()[0]
    if count != expected_count:
        app.logger.info("Waiting for emails to be inserted...")
        app.logger.info(f"Inserted: {count} / Expected: {expected_count}")
        gevent.spawn_later(1, lambda: check_inserted_emails(cursor, expected_count))


def insert_emails():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        with open('/home/cuddy/mysite/emails.txt', 'r') as file:
            emails = file.read().splitlines()
            email_data = [(email,) for email in emails]
            cursor.executemany(
                f"INSERT INTO cuddy$emails.emails"
                + """ (email) VALUES (%s)""",
                email_data,
            )
            conn.commit()
            check_inserted_emails(cursor, len(emails))
            cursor.close()


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
    # ####################################################################################################### cookies
def extract_cookies_by_names(cookies, cookie_names):
    extracted_cookies = {name: cookies[name] for name in cookie_names if name in cookies}
    return extracted_cookies

# def store_cookies_in_text_format(file_path, cookies):
#     with open(file_path, 'w') as file:
#         for name, value in cookies.items():
#             file.write(f'.netflix.com\tTRUE\t/\tFALSE\t1684422900\t{name}\t{value}\n')

def store_cookies_in_json_format(file_path, cookies):
    cookie_list = []

    for name, value in cookies.items():
        cookie = {
            "domain": ".spotify.com",
            "expirationDate": 1725299331,  # Replace with the actual expiration date
            "hostOnly": False,
            "httpOnly": False,
            "name": name,
            "path": "/",
            "sameSite": "lax",  # Replace with the actual SameSite value
            "secure": False,
            "session": False,
            "storeId": None,
            "value": value,
        }
        cookie_list.append(cookie)

    with open(file_path, 'w') as file:
        json.dump(cookie_list, file, indent=4)  # Save as JSON format


def store_email_id(email_id):
    with open('/home/cuddy/mysite/cookies/unsubscribe_email_ids.txt', 'a') as file:
        file.write(email_id + '\n')

@app.route('/unsubscribe/<email_id>', methods=['GET'])
def unsubscribe(email_id):
    # school_url = "https://shorturl.at/ekHI9"  # Replace with the website's URL

    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    # response = requests.get(school_url, headers=headers)

    # # Define the names of the cookies you want to capture
    # desired_cookie_names = ['NetflixId', 'SecureNetflixId', 'nfvdid', 'OptanonConsent', 'flwssn', 'memclid']

    # # Get the cookies from the response
    # school_cookies = response.cookies

    # # Extract the desired cookies by their names
    # desired_cookies = extract_cookies_by_names(school_cookies, desired_cookie_names)

    # # Create a file with the email ID and store the desired cookies in the same format
    # file_path = f'/home/cuddy/mysite/cookies/{email_id}_desired_cookies.txt'
    # store_cookies_in_text_format(file_path, desired_cookies)

    # school_url = "https://open.spotify.com/"  # Replace with the website's URL

    # # Make a request to the website
    # response = requests.get(school_url)

    # # Define the names of the cookies you want to capture
    # desired_cookie_names = ['__Host-sp_csrf_sid', 'sss', 'sp_usid', 'sp_t', 'sp_m', 'sp_last_utm','sp_landing', 'sp_key', 'sp_gaid', 'sp_dc', 'sp_adid', 'rlas3','dextp', 'demdex', '_ttp', '_tt_enable_cookie', '_scid_r', '_scid','_gid', '_gcl_dc', '_gcl_aw', '_gcl_au', '_gac_UA-5784146-31', '_ga_ZWG1NSHWD8','_ga_S35RN5WNT2', '_ga', '_cs_s', '_cs_mk_ga', '_cs_id', '_cs_c','UID', 'OptanonConsent', 'OptanonAlertBoxClosed']

    # # Get the cookies from the response
    # school_cookies = response.cookies

    # # Extract the desired cookies by their names
    # desired_cookies = extract_cookies_by_names(school_cookies, desired_cookie_names)

    # # Create a file with the email ID and store the desired cookies in JSON format
    # file_path = f'/home/cuddy/mysite/cookies/{email_id}_desired_cookies.json'
    # store_cookies_in_json_format(file_path, desired_cookies)

    store_email_id(email_id)

    return 'Unsubscribe successful'
########################################################################################################################### end cookies


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
            email_text += f"{email_id}:{email}\n"

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

@app.route("/download_active_emails")
def download_active_emails():

    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Retrieve all emails from the database
        cursor.execute(
            f"""SELECT e.id AS email_id, e.email FROM requests AS r JOIN emails AS e ON r.email_id = e.id;"""
        )
        rows = cursor.fetchall()

        conn.close()

        # Create a string to store the emails and IDs
        email_text = ""
        for row in rows:
            email_id = row[0]
            email = row[1]
            email_text += f"{email_id}:{email}\n"

        # Create a response with the email text
        response = Response(
            email_text,
            content_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=active_emails.txt"},
        )

        return response



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
