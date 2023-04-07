import os
from flask import Flask, session, render_template, request, redirect, url_for
from httpclient import client

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_KEY')

user_subscriptions = []


@app.route('/', methods=['GET'])
def landing():
    if 'username' in session:
        return redirect(url_for('home'))
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
            return redirect(url_for('home'))
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


@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        response = client.post(path='/login', json=data)

        if response['status_code'] == 200:
            session['username'] = request.form.get('username')
            return redirect(url_for('home'))
        else:
            return render_template('register.html', error_message=response['body'])
    except Exception as e:
        return redirect(url_for("signup"))


@app.route('/songs/search', methods=['POST', 'GET'])
def find_songs():
    try:
        data = {
            'artist': request.form.get('artist'),
            'title': request.form.get('title'),
            'year': request.form.get('year')
        }
        response = client.get(path='/music/query', params=data)['body']
        for sub in response:
            sub['subscribed'] = False
            new_song = sub['title'] + '###' + sub['artist']

            if len(user_subscriptions) > 0:
                for subs in user_subscriptions:
                    if new_song in subs.values():
                        sub['subscribed'] = True
        return render_template("query.html", songs=response)
    except Exception as e:
        print(e)
        return render_template("query.html", songs=[])


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
    return redirect(url_for('home'))


@app.route('/home')
def home():
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
