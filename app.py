import os
from flask import Flask, flash, redirect, render_template, request, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import decrypter as dec
import divider as dv
import encrypter as enc
import restore as rst
import tools

UPLOAD_FOLDER = './uploads/'
UPLOAD_KEY = './key/'
ALLOWED_EXTENSIONS = set(['pem'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/hybrid_crypto'
'''app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False'''
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_KEY'] = UPLOAD_KEY

db = SQLAlchemy(app)
class Users(db.Model):
    username = db.Column(db.String(100), nullable = False)
    email_id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(60), nullable=False)

@app.route('/signin',methods = ['GET', 'POST'])
def signin_page():
    if(request.method=='POST'):
        usname = request.form.get('username')
        email = request.form.get('email')
        paswd = request.form.get('password')
        entry = Users(username = usname , email_id = email , password = paswd)
        db.session.add(entry)
        db.session.commit()
    return render_template('home.html')

@app.route('/loggin',methods = ['GET','POST'])
def loggin():
    if(request.method=='POST'):
        user =request.form.get('username')
        password=request.form.get('password')

    usernamedata = db.execute("select username from users where username = '"+user+"' and password = '"+password+"'").fetchone()
    """ passworddata=db.execute('SELECT password FROM users WHERE username=:username',{'username':user}).fetchone()"""
    if usernamedata is None:
        flash('Invalid username or password','danger!')
        return render_template("home.html")
    else:
        """ for passwor_data in passworddata:
            if sha256_crypt.verify(password,passwor_data):
                session=True
                flash('You are now logged in!!','success')
                return render_template("index.html")
            else:
                flash('incorrect password','danger') """
        return render_template("index.html")

#port = int(os.getenv('PORT', 8000))


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def start_encryption():
    dv.divide()
    tools.empty_folder('uploads')
    enc.encrypter()
    return render_template('success.html')


def start_decryption():
    dec.decrypter()
    tools.empty_folder('key')
    rst.restore()
    return render_template('restore_success.html')


@app.route('/return-key')
def return_key():
    print("reached")
    list_directory = tools.list_dir('key')
    filename = './key/' + list_directory[0]
    print(filename)
    return send_file(filename, as_attachment=True)


@app.route('/return-file/')
def return_file():
    list_directory = tools.list_dir('restored_file')
    filename = './restored_file/' + list_directory[0]
    print("****************************************")
    print(list_directory[0])
    print("****************************************")
    return send_file(filename,as_attachment=True)


@app.route('/download/')
def downloads():
    return render_template('download.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload')
def call_page_upload():
    return render_template('upload.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/homee')
def back_home():
    tools.empty_folder('key')
    tools.empty_folder('restored_file')
    return render_template('index.html')



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/data', methods=['GET', 'POST'])
def upload_file():
    tools.empty_folder('uploads')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return 'NO FILE SELECTED'
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return start_encryption()
        return 'Invalid File Format !'


@app.route('/download_data', methods=['GET', 'POST'])
def upload_key():
    tools.empty_folder('key')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return 'NO FILE SELECTED'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_KEY'], file.filename))
            return start_decryption()
        return 'Invalid File Format !'


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=8000, debug=True)
    app.run()
