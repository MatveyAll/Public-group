from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import sqlalchemy

# подключение к базе
engine = sqlalchemy.create_engine('sqlite:///flask-database')
app = Flask(__name__)


class User:
    def __init__(self, login, password, description):
        self.login = login
        self.password = password
        self.description = description


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
                sqlalchemy.text(f"INSERT INTO users (login, password, description) VALUES ('{new_user.login}', '{new_user.password}', '{new_user.description}')"))
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


if __name__ == '__main__':
    app.run(debug=True)
