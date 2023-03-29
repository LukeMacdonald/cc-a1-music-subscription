import base64

from flask import Flask, session, render_template, request, redirect, url_for
import json
import boto3
import requests

app = Flask(__name__)
app.secret_key = "SECRETKEY"

lambda_client = boto3.client('lambda', region_name='us-east-1')
api = boto3.client('apigateway', region_name='us-east-1')
api_url = "https://ikv7ph4k04.execute-api.us-east-1.amazonaws.com/default/ccA1Lambda"
s3 = boto3.client('s3')
bucket_name = 'myfirstbucket-luke'
key = 'ArcadeFire.jpg'
url = 'https://et2jb8ggg8.execute-api.us-east-1.amazonaws.com/dev'


@app.route('/', methods=['GET'])
def login():
    if 'username' in session:
        return load_home()
    # response = s3.get_object(Bucket=bucket_name, Key=key)
    # image_data = response['Body'].read()
    # encoded_image = base64.b64encode(image_data).decode('utf-8')
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/findsongs', methods=['POST'])
def find_songs():
    data = {
        'artist': request.form.get('artist'),
        'title': request.form.get('title'),
        'year': request.form.get('year')
    }
    print(data)

    response = requests.get(
        url=url + '/music',
        headers={'Content-Type': 'application/json'},
        params=data
    )
    response_body = response.json()

    return render_template("subscription.html",songs=response_body['Items'])


@app.route('/addsubscription')
def add_subscription():
    # data = {
    #     'username': request.form.get('user_name'),
    #     'artist': request.form.get('artist'),
    #     'title': request.form.get('title'),
    #     'path': request.form.get('path'),
    #     'year': request.form.get('year')
    # }
    #
    # response = requests.post(
    #     url=url + '/subscription',
    #     headers={'Content-Type': 'application/json'},
    #     data=json.dumps(data)
    # )

    return render_template("subscription.html")


@app.route('/validate', methods=['POST'])
def validate():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        if not email or not password:
            raise Exception('Email and Password Required')

        response = requests.get(
            url=url + '/login',
            headers={'Content-Type': 'application/json'},
            params={'email': email}
        )
        response_body = response.json()
        if response.status_code == 200:
            if response_body['password'] != password:
                raise Exception('Incorrect Password')
            else:
                session['username'] = response_body['user_name']
                return load_home()
        else:
            raise Exception('Email Not Found')

    except Exception as e:
        error = str(e)
        return render_template('login.html', error_message=error)


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/signup')
def signup():
    return render_template('register.html')


def retrieve_body(response):
    return json.loads(response['Payload'].read().decode('utf-8'))['body']


def load_home():
    response = lambda_client.invoke(
        FunctionName='getSubscriptions',
        InvocationType='RequestResponse',
        Payload=json.dumps({'username': session['username']})
    )

    response_body = retrieve_body(response)

    return render_template('home.html', data=session['username'],
                           subscriptions=response_body['subscriptions'],
                           songs=response_body['songs'])


if __name__ == '__main__':
    app.run()
