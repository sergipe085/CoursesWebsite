import os
import re
from uuid import uuid4
from cs50 import SQL
from flask import Flask, flash, render_template, redirect, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from helpers import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pyrebase import pyrebase

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

UPLOAD_FOLDER = "./videos_cache"
# Configure file upload folder
ALLOWED_EXTENSIONS = ["mp4"]
app.config["UPLOAD_FOLDER"]= UPLOAD_FOLDER

# Configure pyrebase
config = {
    "apiKey": "AIzaSyC0c1Ni5dqBYe4fx-j_j9RBVrfAbFRRtJs",
    "authDomain": "sitecursos-fb0f8.firebaseapp.com",
    "databaseURL": "https://sitecursos-fb0f8-default-rtdb.firebaseio.com",
    "projectId": "sitecursos-fb0f8",
    "storageBucket": "sitecursos-fb0f8.appspot.com",
    "messagingSenderId": "527634793144",
    "appId": "1:527634793144:web:6d943bc0ea3e4b4f9daa4d",
    "measurementId": "G-8QYPZ8BGE2"
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

#db = SQL("mysql+pymysql://root:@localhost:3306/sitecursos")
db = SQL("mysql+pymysql://sql10403857:uTPYI6esSr@sql10.freemysqlhosting.net:3306/sql10403857")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 1:
            return render_template("login.html", message="Invalid Username!")

        user = user[0]
        password_hash = user["password_hash"] 
        if not check_password_hash(password_hash, password):
            return render_template("login.html", message="Incorrect Password!")

        session["user_id"] = user["user_id"]

        return redirect("/")

    return render_template("login.html")  

@app.route("/logout")
@login_required
def logout():

    session.clear()

    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_hash = generate_password_hash(password)

        if username == "":
            return render_template("register.html", message="Please provide an username.")
        if password == "":
            return render_template("register.html", message="Please provide an password.")   

        db.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)", username, password_hash) 
        return redirect("/login")   

    return render_template("register.html")    

@app.route("/register_course", methods=["GET", "POST"])
@login_required
def register_course():

    if request.method == "POST":
        request.form = dict(request.form)
        request.files = dict(request.files)
        files = list(request.files)
        print(request.files)
        print(files)
        
        course_name = request.form.get("course_name")
        owner_id = session["user_id"]
        module_count = request.form.get("module_count")

        course_id = db.execute("INSERT INTO courses(course_name, module_count, owner_id) VALUES(?, ?, ?)", course_name, module_count, owner_id)

        upload = False
        for i in files:
            file = request.files[i]
            print(i)
            a = re.split("_|@", i)

            name = a[0]
            video_id = "_" + a[1]
            filename, file_extension = os.path.splitext(a[2])
            videoname = filename
            filename = video_id + file_extension
            class_module_num = name.replace("file", "").split("/")
            print(class_module_num)

            db.execute("INSERT INTO videos(file_name, video_name, course_id, class_num, module_num) VALUES(?, ?, ?, ?, ?)", filename, videoname, course_id, class_module_num[0], class_module_num[1])
            upload = True
            
        if upload == True:
            return render_template("register_course.html", message="Sucess!")
        return render_template("register_course.html", message="An error ocurred") 

    return render_template("register_course.html")

@app.route("/search")
@login_required
def search():
    search_input = request.args.get("search")

    courses = db.execute("SELECT * FROM courses WHERE course_name LIKE ?", f"%{search_input}%")
    return render_template("search.html", courses=courses)

@app.route("/course")
@login_required
def course():
    course_id = request.args.get("course_id")

    course = db.execute("SELECT * FROM courses WHERE course_id = ?", course_id)[0]
    videos = db.execute("SELECT * FROM videos WHERE course_id = ?", course["course_id"])

    return render_template("course.html", course=course, videos=videos)

@app.route("/video")
@login_required
def video():
    video_id = request.args.get("video_id")
    course_id = request.args.get("course_id")
    print(course_id)
    video = db.execute("SELECT * FROM videos WHERE id = ?", video_id)[0]
    videos = db.execute("SELECT * FROM videos WHERE id > ? AND course_id = ?", video_id, course_id)
    return render_template("video.html", video=video, videos=videos, course_id=course_id)

def upload(pathCloud, filename):
    path_local = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    path_on_cloud = f"{pathCloud}/{filename}"
    storage.child(path_on_cloud).put(path_local)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS   