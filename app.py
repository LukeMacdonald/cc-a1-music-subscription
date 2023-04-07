import os
from flask import Flask, session, render_template, request, redirect, url_for
from httpclient import client

# Initialize the Flask application and set a secret key
app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_KEY')

# Create an empty list to hold user subscriptions
user_subscriptions = []


# Define the landing page
@app.route('/', methods=['GET'])
def landing():
    if 'username' in session:
        # If the user is already logged in, redirect them to the home page
        return redirect(url_for('home'))
    # Otherwise, render the login page
    return render_template("login.html")


# Define the login page
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        if not email or not password:
            # If the user did not provide an email or password, raise an exception
            raise Exception('Email and Password Required')

        response = client.get('/login', {'email': email, 'password': password})

        if response['status_code'] == 200:
            # If the login is successful, store the user's username in a session and redirect to the home page
            session['username'] = response['body']['user_name']
            return redirect(url_for('home'))
        else:
            # If the login is unsuccessful, raise an exception with the response body
            raise Exception(response['body'])

    except Exception as e:
        # If an exception is raised, render the login page with an error message
        error = str(e)
        return render_template('login.html', error_message=error)


# Define the logout page
@app.route('/logout')
def logout():
    # Clear the list of user subscriptions and remove the user's username from the session
    user_subscriptions.clear()
    session.pop('username', None)
    # Redirect the user to the landing page
    return redirect(url_for('landing'))


# Define the signup page
@app.route('/signup')
def signup():
    # Render the registration page
    return render_template('register.html')


# Define the registration page
@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        # Get the user's registration data from the form
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        # Send a POST request to the API to register the user
        response = client.post(path='/login', json=data)

        if response['status_code'] == 200:
            # If the registration is successful, store the user's username in a session and redirect to the home page
            session['username'] = request.form.get('username')
            return redirect(url_for('home'))
        else:
            # If the registration is unsuccessful, render the registration page with an error message
            return render_template('register.html', error_message=response['body'])
    except Exception as e:
        # If an exception is raised, redirect the user to the signup page
        return redirect(url_for("signup"))


# This route searches for songs based on user input
@app.route('/songs/search', methods=['POST', 'GET'])
def find_songs():
    if 'username' not in session:
        # If the user is not already logged in, redirect them to the landing page
        return redirect(url_for('landing'))
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


# This route displays the search page
@app.route('/songs', methods=['GET'])
def search():
    if 'username' not in session:
        # If the user is not already logged in, redirect them to the landing page
        return redirect(url_for('landing'))
    return render_template("subscription.html", songs=[])


# This route handles adding a subscription to the user's account
@app.route('/subscription', methods=['POST'])
def add_subscription():
    if 'username' not in session:
        # If the user is not already logged in, redirect them to the landing page
        return redirect(url_for('landing'))
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


# This route handles removing a subscription to the user's account
@app.route('/subscription/remove', methods=['POST'])
def remove_subscription():
    if 'username' not in session:
        # If the user is not already logged in, redirect them to the landing page
        return redirect(url_for('landing'))
    data = {
        'username': session['username'],
        'song': request.form.get('title') + "###" + request.form.get('artist'),
    }
    response = client.delete(path='/subscription', params=data)
    return redirect(url_for('home'))


# This route handles defines the user home page
@app.route('/home')
def home():
    if 'username' not in session:
        # If the user is not already logged in, redirect them to the landing page
        return redirect(url_for('landing'))
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
