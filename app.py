import json
import os
from flask import Flask, session, render_template, request, redirect, url_for
from httpclient import client

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_KEY')

user_subscriptions = []


@app.route('/', methods=['GET'])
def landing():
    if 'username' in session:
        return load_home()
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        if not email or not password:
            raise Exception('Email and Password Required')

        response = client.get('/login', {'email': email, 'password': password})

        if response['status_code'] == 200:

            session['username'] = response['body']['user_name']
            return load_home()
        else:
            raise Exception(response['body'])

    except Exception as e:
        error = str(e)
        return render_template('login.html', error_message=error)


@app.route('/logout')
def logout():
    user_subscriptions.clear()
    session.pop('username', None)
    return redirect(url_for('landing'))


@app.route('/signup')
def signup():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    data = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'password': request.form.get('password')
    }
    response = client.post(path='/login', json=data)

    if response['status_code'] == 200:
        session['username'] = request.form.get('username')
        return load_home()
    else:
        return render_template('register.html', error_message=response['body'])


@app.route('/songs/search', methods=['POST', 'GET'])
def find_songs():
    data = {
        'artist': request.form.get('artist'),
        'title': request.form.get('title'),
        'year': request.form.get('year')
    }

    response = client.get(path='/music/query', params=data)['body']

    for sub in response:
        sub['subscribed'] = False
        song = sub['title'] + '###' + sub['artist']
        for subs in user_subscriptions:
            print(subs)
            if song in subs.values():
                sub['subscribed'] = True
                print(song)
    return render_template("query.html", songs=response)


@app.route('/songs', methods=['GET'])
def search():
    return render_template("subscription.html", songs=[])


@app.route('/subscription', methods=['POST'])
def add_subscription():
    data = {
        'username': session['username'],
        'artist': request.form.get('artist'),
        'title': request.form.get('title'),
        'path': request.form.get('path'),
        'year': request.form.get('year')
    }

    response = client.post(path='/subscription', json=data)['body']
    data['song'] = data['title'] + '###' + data['artist']
    user_subscriptions.append(data)

    return render_template("subscription.html")


@app.route('/subscription/remove', methods=['POST'])
def remove_subscription():
    data = {
        'username': session['username'],
        'song': request.form.get('title') + "###" + request.form.get('artist'),
    }
    response = client.delete(path='/subscription', params=data)
    return load_home()


@app.route('/home')
def home():
    return load_home()


def load_home():
    data = {'username': session['username']}
    response = client.get(path='/music', params=data)['body']
    user_subscriptions.clear()

    user_subscriptions.extend(response['Items'])

    return render_template('home.html',
                           data=session['username'],
                           songs=user_subscriptions,
                           )


if __name__ == '__main__':
    app.run()
