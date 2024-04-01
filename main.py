from flask import Flask, url_for, redirect, render_template, request, session
import pandas as pd
import sqlalchemy
from selenium.webdriver.common.keys import Keys

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
    def __init__(self, title, type, user_name, text):
        self.title = title
        self.type = type
        self.user_name = user_name
        self.text = text


@app.route('/')
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')


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
                connection.execute(
                    sqlalchemy.text(
                        "INSERT INTO posts (post_id, title, user_name, type, text) VALUES (:post_id, :title, :user_name, :type, :text)"),
                    {"post_id": post_id, "title": title, "user_name": user_name, "type": typed, "text": text}
                )
                connection.execute(
                    sqlalchemy.text("DELETE FROM posts_proverka WHERE post_id = :post_id"),
                    {"post_id": post_id}
                )
                connection.commit()
                #Обновление страницы чтобы одобренная заметка исчезла
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
        new_post = Post(request.form['title'], request.form['class'], session['username'], request.form['text'])
        df = pd.read_sql_table('posts', engine)
        if new_post.title in df['title'].values:
            return 'Запись с таким названием уже существует'
        with engine.connect() as connection:
            connection.execute(
                sqlalchemy.text(f"INSERT INTO posts_proverka (post_id,title, user_name, type, text) VALUES (NUll, '{new_post.title}', '{new_post.user_name}', '{new_post.type}', '{new_post.text}')"))
            connection.commit()
        return 'Запись создана'

    return render_template('post.html')


if __name__ == '__main__':
    app.run(debug=True)