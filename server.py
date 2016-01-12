# # -*- coding: utf-8 -*-
from annotation.checker import Checker
from annotation.identifier import allowed_prefix
import os
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = '/tmp/annotation/'
if os.path.exists(app.config['UPLOAD_FOLDER']) is False:
    os.mkdir(app.config['UPLOAD_FOLDER'])
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'csv'])


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/qa')
def qa():
    return render_template('qa.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensionss
    if not file:
        err_msg = "Error: The file must be .txt or .csv"
        return render_template("results.html", msg=err_msg)

    if not allowed_file(file.filename):
        err_msg = "Error: The file must be .txt or .csv"
        return render_template("results.html", msg=err_msg)
    if not allowed_prefix(file.filename.split('.')[0]):
        err_msg = """
<pre>Error: The file prefix {} must be the same with video prefix
I.e., the file name must be looks like 'exp1_sub1_label.csv(or.txt)'
</pre>
""".format(file.filename.split('.')[0])
        return render_template("results.html", msg=err_msg)

    if file:
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file',
                                filename=filename))


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_fullpath = app.config['UPLOAD_FOLDER'] + filename
    if os.path.exists(file_fullpath):
        print("File is exist")
    else:
        print("File (%s) doesn't exist" % (file_fullpath))
        return file_fullpath

    checker = Checker(app.config['UPLOAD_FOLDER'] + filename)
    checker.check()
    msg = checker.results.as_string(lfc='\n')
    msg = '<pre>' + msg + '</pre>'
    return render_template("results.html", msg=msg)


if __name__ == '__main__':
    app.run(
        debug=True
    )
