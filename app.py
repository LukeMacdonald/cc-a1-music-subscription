import os
from flask import Flask, session, render_template, request, redirect, url_for
import json
import boto3
import requests

app = Flask(__name__)

lambda_client = boto3.client('lambda', region_name='us-east-1')
url = os.environ.get('API_URL')
app.secret_key = os.environ.get('SESSION_KEY')


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

        response = get_request('/login', {'email': email, 'password': password})

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

    response = post_request('/login', data)

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

    response = get_request('/music/query', data)['body']
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

    response = post_request('/subscription', data)['body']

    return render_template("subscription.html")


@app.route('/subscription/remove', methods=['POST'])
def remove_subscription():
    data = {
        'username': session['username'],
        'song': request.form.get('song'),
    }
    response = delete_request('/subscription', data)
    return load_home()


@app.route('/home')
def home():
    return load_home()


def load_home():
    data = {'username': session['username']}

    response = get_request('/music', data)['body']
    print(response)

    return render_template('home.html',
                           data=session['username'],
                           songs=response['Items'],
                           )


def get_request(resource, params):
    response = requests.get(
        url=url + resource,
        headers={'Content-Type': 'application/json'},
        params=params
    )
    return {'status_code': response.status_code, 'body': response.json()}


def delete_request(resource, params):
    response = requests.delete(
        url=url + resource,
        headers={'Content-Type': 'application/json'},
        params=params
    )
    return {'status_code': response.status_code, 'body': response.json()}


def post_request(resource, data):
    response = requests.post(
        url=url + resource,
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )
    return {'status_code': response.status_code, 'body': response.json()}


if __name__ == '__main__':
    app.run()
