import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
	os.makedirs(UPLOAD_FOLDER)

RESIZED_FOLDER = "/resized"
app.config['RESIZED_FOLDER'] = RESIZED_FOLDER
if not os.path.exists(RESIZED_FOLDER):
	os.makedirs(RESIZED_FOLDER)

# These are the extension that we are accepting to be uploaded
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
	return '.' in filename and \
			ilename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Resize function
def resize(filename, width, height):
	
	# Valid values check
	if width <= 0 and height <= 0:
		return 
	
	# Open image
	try:
		img = Image.open(filename)
	except:
		return
	
	# Set sizes if one of the sizes is not set
	if not width:
		width = int(height * (float(img.size[0]) / (float(img.size[1]))))
	else if not height:
		height = int(width * (float(img.size[1]) / (float(img.size[0]))))
	
	# Resize image
	img = img.resize((basewidth, 100), Image.ANTIALIAS)
	
	# Save image to be uploded to webpage
	resized_file = "resized_" + filename
	img.save(os.path.join(RESIZED_FOLDER, resized_file))
	return redirect(url_for('resized_file', filename=resized_file))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect('index.html')
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect('index.html')
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			return redirect(url_for('uploaded_file', filename=filename))
	flash('Not a POST method')
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form method=post enctype=multipart/form-data>
		<p><input type=file name=file>
			<input type=submit value=Upload>
	</form>
	'''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/resized/<filename>')
def resized_file(filename):
	return send_from_directory(RESIZED_FOLDER, filename)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')