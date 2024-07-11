from flask import Flask, render_template, request, flash
import cv2
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.secret_key = 'gouravthegreat'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image(filename, operation):
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


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = process_image(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            return render_template("index.html")
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
