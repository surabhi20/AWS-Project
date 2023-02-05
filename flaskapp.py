import os
import sqlite3 
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory 
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "cloud_project"

@app.route('/uploads/<name>')
def download(name):
        return send_from_directory('uploads', name)

def register_user_to_db(username, password, firstname, lastname, email, filename):
     con = sqlite3.connect("/home/ubuntu/flaskapp/database.db")
     cur = con.cursor()
     cur.execute('INSERT INTO allusers(username,password,firstname,lastname,email,filename) values (?,?,?,?,?,?)',(username,password,firstname,lastname,email,filename))
     con.commit()
     con.close()

def check_user(username,password):
    con = sqlite3.connect('/home/ubuntu/flaskapp/database.db')
    cur = con.cursor()
    cur.execute('SELECT username,password,firstname,lastname,email,filename FROM allusers WHERE username=? and password=?',(username,password))

    result = cur.fetchall()
    for res in result:
        session["firstname"]=res[2]
        session["lastname"]=res[3]
        session["email"]=res[4]
        session["filename"]=res[5]
        file = ""
        numwords = 0
        print(session["filename"])
        if session["filename"]:
            file = url_for('download', name=session["filename"])
            print(file)
            uploaded_file = os.path.join("uploads",session["filename"])
            with open(uploaded_file, 'r') as f:
                for line in f:
                    words = line.split()
                    numwords += len(words)
        session["file"] = file
        session["numwords"] = numwords

    if result:
        return True
    else:
        return False

@app.route('/')
def index():
  return render_template('login.html')


@app.route('/register')
def reigster():
    return render_template('register.html')

@app.route('/register',methods=['POST','GET'])
def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email = request.form['email']
            filename, file = '', ''
            print(request.files)
            if 'upload' in request.files:
                print("File uploading...")
                file = request.files['upload']
                filepath = 'uploads'
                filename = secure_filename(file.filename)
                print(filename)
                if not os.path.exists(filepath):
                    os.makedirs(filepath)
                file.save(os.path.join(filepath, filename))
                print("File Saved")
                #file = url_for('download_file', name=filename)
            register_user_to_db(username,password,firstname,lastname,email,filename)
            return redirect(url_for('index'))
        else:
            return render_template('register.html')

@app.route('/login',methods=['POST','GET'])
def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if check_user(username, password):
                session['username'] = username

            return redirect(url_for('home'))
        else:
            return redirect(url_for('index'))

@app.route('/home', methods=['POST','GET'])
def home():
    if 'username' in session:
        return render_template('home.html',username=session['username'],firstname=session['firstname'],lastname=session['lastname'],
                email=session['email'], file=session['file'], filename=session['filename'],numwords=session['numwords'])
    else:
        return "Username or password is incorrect!"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(host="0.0.0.0", port="8000")
