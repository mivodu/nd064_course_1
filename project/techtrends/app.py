import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    try:
        connection = sqlite3.connect('database.db')
    except:
        app.logger.error('Database does not exist. Run python init_db.py to create it')
    else:
        connection.row_factory = sqlite3.Row
        app.config["DB_CONN_COUNTER"] += 1
        return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
# Flask configuration of database connection count 
app.config['DB_CONN_COUNTER'] = 0

# Define the main route of the web application 
@app.route('/')
def index():
    try:
        connection = get_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchall()
        connection.close()
        return render_template('index.html', posts=posts)
    except:
        return render_template('404.html'), 404

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None: 
        # Add logging: Article does not exist
        app.logger.error("Articel does not exist")
        return render_template('404.html'), 404
    else:
        # Add logging: Write retrieved Titel to log
        app.logger.info('%r article retrieved', post['title'])
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    # Add logging: About us page has been retrieved
    app.logger.info("About us page has been retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info("New articel '%s' created" %title)
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the health check endpoint functionality
@app.route('/healthz')
def healthz():
    try:
        connection = get_db_connection()
        test_table = connection.execute('SELECT * FROM posts').fetchall()
    except sqlite3.Error as error:
        response = app.response_class(
            response=json.dumps({"result":"NOT OK - unhealthy"}),
            status=500,
            mimetype='application/json'
        )
        app.logger.info('Health check not successful')
    else:
        response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
        )
        app.logger.info('Health check successfully executed')
    finally:
        if connection:
            connection.close()
    return response

# Define the metrics endpoint functionality
@app.route('/metrics')
def metrics():
#    global db_connection_counter
    connection = get_db_connection()
    # Query DB for number of posts
    if connection:
        try:
            test_table = connection.execute('SELECT * FROM posts').fetchall()
        except:
            app.logger.error('Table POSTS does not exist. Run python init_db.py to create it')
            response = app.response_class(
                response=json.dumps({"db_connection_count": app.config['DB_CONN_COUNTER'], "post_count": "Not available"}),
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            db_post_count = connection.execute('Select count(*) from posts').fetchone()
            response = app.response_class(
                response=json.dumps({"db_connection_count": app.config['DB_CONN_COUNTER'], "post_count": db_post_count[0]}),
                status=200,
                mimetype='application/json'
            )
            app.logger.info('Metrics request successfull')
            return response
        finally:
            if connection:
                connection.close()
    else:
        app.logger.error('Database does not exist. Run python init_db.py to create it')
        response = app.response_class(
            response=json.dumps({"db_connection_count": "Not available", "post_count": "Not available"}),
            status=200,
            mimetype='application/json'
        )
        return response

# start the application on port 3111
if __name__ == "__main__":

    # add logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    
    app.run(host='0.0.0.0', port='3111')
    