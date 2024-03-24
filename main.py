from flask import Flask, render_template, request
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
    def __init__(self, title, user_name, text):
        self.title = title
        self.user_name = user_name
        self.text = text


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(request.form['username'], request.form['password'], request.form['description'])

        # Чтение данных из таблицы "users" в DataFrame с помощью Pandas
        df = pd.read_sql_table('users', engine)

        # Проверка наличия логина в столбце 'login'
        if new_user.login in df['login'].values:
            return 'Пользователь с таким логином уже существует!'
        # добавление пользователя в базу
        with engine.connect() as connection:
            connection.execute(
                sqlalchemy.text(f"INSERT INTO users (login, password, description, list_posts) VALUES ('{new_user.login}', '{new_user.password}', '{new_user.description}', '')"))
            connection.commit()

        return 'Вы успешно зарегистрированы!'

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']

        # Проверка наличия пользователя в базе данных
        df = pd.read_sql_table('users', engine)
        if login in df['login'].values and password == df.loc[df['login'] == login, 'password'].values[0]:
            return 'Вы успешно вошли!'
        else:
            return 'Неверный логин или пароль.'

    return render_template('login.html')


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        new_post = Post(request.form['title'], 1, request.form['text'])

        # Проверка наличия пользователя в базе данных
        df = pd.read_sql_table('posts', engine)
        if new_post.title in df['title'].values:
            return 'Запись с таким названием уже существует'
        with engine.connect() as connection:
            connection.execute(
                sqlalchemy.text(f"INSERT INTO posts (title, user_name, text) VALUES ('{new_post.title}', '{new_post.user_name}', '{new_post.text}')"))
            connection.commit()
        return 'Запись создана'

    return render_template('post.html')



if __name__ == '__main__':
    app.run(debug=True)