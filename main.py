from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import sqlalchemy

# подключение к базе
engine = sqlalchemy.create_engine('sqlite:///flask-database.db')
app = Flask(__name__)


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
@app.route('/main')
def main():
    return 'Приветствую вас на нашем сайте!;)'


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
            global user_id
            user_id = len(df['login']) + 1

        return redirect(url_for('main'), 301)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']

        df = pd.read_sql_table('users', engine)
        if login in df['login'].values and password == df.loc[df['login'] == login, 'password'].values[0]:
            global user_id
            user_id = [num + 1 for num, i in enumerate(df['login']) if i == login][0]
            return redirect(url_for('main'), 301)
        else:
            return 'Неверный логин или пароль.'

    return render_template('login.html')


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        new_post = Post(request.form['title'], request.form['class'], user_id, request.form['text'])

        df = pd.read_sql_table('posts', engine)
        if new_post.title in df['title'].values:
            return 'Запись с таким названием уже существует'
        with engine.connect() as connection:
            connection.execute(
                sqlalchemy.text(f"INSERT INTO posts_proverka (title, user_name, type, text) VALUES ('{new_post.title}', '{new_post.user_name}', '{new_post.type}', '{new_post.text}')"))
            connection.commit()
        return 'Запись создана'

    return render_template('post.html')



if __name__ == '__main__':
    app.run(debug=True)
    user_id = 1