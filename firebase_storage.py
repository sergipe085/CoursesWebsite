import pyrebase

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

def upload(filename):
    path_local = f"./{filename}"
    path_on_cloud = f"videos/video2.mp4"
    storage.child(path_on_cloud).put(path_local)