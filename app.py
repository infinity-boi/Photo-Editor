from flask import Flask, render_template, request, flash
import cv2
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads'
CROPPED_FOLDER = 'static/cropped/'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.secret_key = 'gouravthegreat'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CROPPED_FOLDER'] = CROPPED_FOLDER

# Load OpenCV pre-trained face detector
cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
face_cascade_path = os.path.join(cv2_base_dir, 'data', 'haarcascade_frontalface_default.xml')

print(f"Face cascade path: {face_cascade_path}")

if not os.path.exists(face_cascade_path):
    raise FileNotFoundError(f"Haar cascade file not found at {face_cascade_path}")

face_cascade = cv2.CascadeClassifier(face_cascade_path)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgray":
            img_processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            new_filename = f"static/{filename}"
            cv2.imwrite(new_filename, img_processed)
            return new_filename
        case "cwebp":
            new_filename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(new_filename, img)
            return new_filename
        case "cjpg":
            new_filename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(new_filename, img)
            return new_filename
        case "cpng":
            new_filename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(new_filename, img)
            return new_filename
    pass


@app.route('/')
def home():  # put application's code here
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file Part', "error")
            return render_template("index.html")
        file = request.files['file']
        if file.filename == '':
            flash('Please Select a File', "warning")
            return render_template("index.html")
        if not allowed_file(file.filename):
            flash('Invalid File', "error")
            return render_template("index.html")
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(file_path):
                flash(f"Server Issue, Couldn't upload {filename}", "error")
                return render_template("index.html")
            file.save(file_path)
            action = request.form.get("action")
            if action == 'convert':
                return handle_convert(filename, operation)
            elif action == 'crop_face':
                return handle_crop_face(filename, file_path)
    return render_template("index.html")


def handle_convert(filename, operation):
    new = convert(filename, operation)
    flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
    return render_template("index.html")


def handle_crop_face(filename, file_path):
    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        flash("No faces detected", "info")
    for i, (x, y, w, h) in enumerate(faces):
        cropped_face = img[y:y + h, x:x + w]
        cropped_filename = f"face_{i}_{filename}"
        cropped_filepath = os.path.join(app.config['CROPPED_FOLDER'], cropped_filename)
        cv2.imwrite(cropped_filepath, cropped_face)
        flash(f"Your image has been processed and is available <a href='/{cropped_filepath}' target='_blank'>here</a>", "success")
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
