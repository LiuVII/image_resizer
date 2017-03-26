import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from PIL import Image

# Initialize the Flask application
app = Flask(__name__)

# The path to the upload directory
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Create directory to stroe uploaded images
if not os.path.exists(UPLOAD_FOLDER):
	try:
		os.makedirs(UPLOAD_FOLDER)
	except:
		# error
		exit(1)

# The path to the resized image directory
RESIZED_FOLDER = "resized/"
app.config['RESIZED_FOLDER'] = RESIZED_FOLDER
# Create directory to store resized images
if not os.path.exists(RESIZED_FOLDER):
	try:
		os.makedirs(RESIZED_FOLDER)
	except:
		# error
		exit(1)

# Extension that we are accepting to be uploaded
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# For a given image, resize (scale) image and return it's filename:
def resize_image(filename, width, height):
	
	# Open image
	try:
		img = Image.open(os.path.join(UPLOAD_FOLDER, filename))
	except:
		# error
		return 0
	
	# If both sizes are not set assign original size
	if width <= 0 and height <= 0:
		width = img.size[0]
		height = img.size[1]
	# If one of the sizes not set scale to the set size maintaing aspect ratio 
	elif not width:
		width = int(height * (float(img.size[0]) / (float(img.size[1]))))
	elif not height:
		height = int(width * (float(img.size[1]) / (float(img.size[0]))))
	
	# Resize (scale) image (several filters can be used to provide the best quality)
	img = img.resize((width, height), Image.ANTIALIAS)
	
	# Save image to the resized folder
	resized_filename = "resized_" + filename
	img.save(os.path.join(RESIZED_FOLDER, resized_filename))
	return resized_filename

# Initial route to our index page
@app.route('/index')
def index():
	return render_template('index.html')

# Route to upload, save image locally and resize it
@app.route('/upload', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		
		# Check if the post request has the file part
		if 'file' not in request.files:
			# error
			flash('No file part')
			return redirect(url_for('index'))
		
		# Get the values that were POSTed
		file = request.files['file']
		height = int(request.form['height'])
		width = int(request.form['width'])
		print('We are here')
		
		# Check if filename is empty
		if file.filename == '':
			# error
			flash('No selected file')
			return redirect(url_for('index'))
		
		# Check if file has an allowed extension
		elif allowed_file(file.filename):
			
			# Make a secure filename (getting rid of directories in the filename)
			filename = secure_filename(file.filename)
			
			# Save file locally
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			
			# Attempt to resize file
			resized_filename = resize_image(filename, width, height)
			
			# In case of success display resized file in the browser
			if resized_filename:
				return redirect(url_for('resized_filename', filename=resized_filename))
			#error
			print('File could not be resized')
			return redirect(url_for('index'))
		else:
			# error
			flash('File extension is not supported')
			return redirect(url_for('index'))
	# error
	flash('Not a POST method')
	return redirect(url_for('index'))

# Route to display resized file
@app.route('/resized/<filename>')
def resized_filename(filename):
	print("DISPLAY ME")
	return send_from_directory(RESIZED_FOLDER, filename)

# Route to display uploaded file [NOT CURRENTLY USED]
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')