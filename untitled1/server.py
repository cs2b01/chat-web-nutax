from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import json

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')


@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')


@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'

@app.route('/static/authenticate', methods = ['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    session = db.getSession(engine)
    users = session.query(entities.User)

    for user in users:
        if user.username == username and user.password == password:
            return render_template("success.html")
    return render_template("fail.html")


@app.route('/static/authenticate2', methods = ['POST'])
def authenticate2():
    username = request.form['username']
    password = request.form['password']

    session = db.getSession(engine)

    try:
        user = session.query(entities.User).filter(entities.User.username == username).filter(entities.User.password == password).one()
        return render_template("success.html")
    except Exception:
        render_template("fail.html")

@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'


@app.route('/users', methods = ['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.User).filter(entities.User.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"


@app.route('/create_test_users', methods = ['GET'])
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(name="David", fullname="Lazo", password="1234", username="qwerty")
    db_session.add(user)
    db_session.commit()
    return "Test user created!"

if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))
