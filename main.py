import base64

from flask import Flask, url_for, redirect, render_template, request, session
import pandas as pd
import sqlalchemy

# подключение к базе
engine = sqlalchemy.create_engine('sqlite:///flask-database.db')
app = Flask(__name__)
app.secret_key = 'your_secret_key'


class User:
    def __init__(self, login, password, description):
        self.login = login
        self.password = password
        self.description = description


class Post:
    def __init__(self, title, type, user_name, text, audio, photo):
        self.title = title
        self.type = type
        self.user_name = user_name
        self.text = text
        self.audio = audio
        self.photo = photo


@app.route('/')
@app.route('/main', methods=['GET', 'POST'])
def main():
    if not (session['username'] and session['password']):  # проверка был ли вход у пользователя
        return redirect(url_for('login'), 301)
    df = pd.read_sql_table('posts', engine)
    posts = df.to_dict('records')
    type = ''
    if request.method == 'POST':
        type = request.form['class']
        if type != '':
            posts = list(filter(lambda x: x['type'] == type, posts))
    return render_template('main.html', posts=posts, type=type)


@app.route('/moderation', methods=['GET', 'POST'])
def moderation():
    if session['username'] != 'admin' and session['password'] != '54321':
        return 'Вы не являетесь админом и не можете модерировать записи'
    df = pd.read_sql_table('posts_proverka', engine)
    posts = df.to_dict('records')

    if request.method == 'POST':
        if 'approve_post' in request.form:
            title = request.form['title']
            user_name = request.form['user_name']
            typed = request.form['type']
            text = request.form['text']
            post_id = request.form['post_id']

            with engine.connect() as connection:
                if len(request.form) == 7:
                    connection.execute(
                        sqlalchemy.text(
                            "INSERT INTO posts (post_id, title, user_name, type, text, audio, photo) VALUES (:post_id, :title, :user_name, :type, :text, :audio, :photo)"),
                        {"post_id": post_id, "title": title, "user_name": user_name, "type": typed, "text": text,
                         "audio": request.form['audio'], "photo": request.form['photo']}
                    )
                else:
                    connection.execute(
                        sqlalchemy.text(
                            "INSERT INTO posts (post_id, title, user_name, type, text, audio, photo) VALUES (:post_id, :title, :user_name, :type, :text, :audio, :photo)"),
                        {"post_id": post_id, "title": title, "user_name": user_name, "type": typed, "text": text,
                         "audio": "", "photo": ""}
                    )
                connection.execute(
                    sqlalchemy.text("DELETE FROM posts_proverka WHERE post_id = :post_id"),
                    {"post_id": post_id}
                )
                connection.commit()
                return redirect(url_for('moderation'), 301)

    return render_template('moderation.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(request.form['username'], request.form['password'], request.form['description'])

        df = pd.read_sql_table('users', engine)

        if new_user.login in df['login'].values:
            return 'Пользователь с таким логином уже существует!'
        with engine.connect() as connection:
            connection.execute(
                sqlalchemy.text(f"INSERT INTO users (login, password, description, list_posts) VALUES ('{new_user.login}', '{new_user.password}', '{new_user.description}', '')"))
            connection.commit()
            session['username'] = new_user.login
            session['password'] = new_user.password
            session['description'] = new_user.description
        return redirect(url_for('main'), 301)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']
        df = pd.read_sql_table('users', engine)
        if login in df['login'].values and password == df.loc[df['login'] == login, 'password'].values[0]:
            session['username'] = login
            session['password'] = password
            return redirect(url_for('main'), 301)
        else:
            return 'Неверный логин или пароль.'

    return render_template('login.html')


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        new_post = Post(
            request.form['title'],
            request.form['class'],
            session['username'],
            request.form['text'],
            base64.b64encode(request.files['audio'].read()).decode('utf-8'),
            base64.b64encode(request.files['photo'].read()).decode('utf-8')
        )
        df = pd.read_sql_table('posts', engine)
        if new_post.title in df['title'].values:
            return 'Запись с таким названием уже существует'
        with engine.connect() as connection:
            connection.execute(
                sqlalchemy.text(
                    f"INSERT INTO posts_proverka (post_id,title, user_name, type, text, audio, photo) VALUES (NUll, '{new_post.title}', '{new_post.user_name}', '{new_post.type}', '{new_post.text}', :audio, :photo)"),
                {"audio": new_post.audio, "photo": new_post.photo}
            )
            connection.commit()
        return 'Запись создана'

    return render_template('post.html')


if __name__ == '__main__':
    app.run(debug=True)