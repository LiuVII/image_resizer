import os
from flask import Flask, request, render_template, redirect, \
	url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from PIL import Image

# Initialize the Flask application
app = Flask(__name__)

# Setup session and secret key (error free execution of flash messages)
# [In case we would want any for UI]
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# The path to the upload directory
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create a directory to store uploaded images
if not os.path.exists(UPLOAD_FOLDER):
	try:
		os.makedirs(UPLOAD_FOLDER)
	except:
		# error
		print("Cannot create folder for uploaded images")
		exit(1)

# The path to the resized image directory
RESIZED_FOLDER = "resized/"
app.config['RESIZED_FOLDER'] = RESIZED_FOLDER

# Create a directory to store resized images
if not os.path.exists(RESIZED_FOLDER):
	try:
		os.makedirs(RESIZED_FOLDER)
	except:
		# error
		print("Cannot create folder for resized images")
		exit(1)

# Extensions we choose to accept (for example)
# [PIL supports http://pillow.readthedocs.io/en/3.4.x/handbook/image-file-formats.html]
ALLOWED_EXTENSIONS = set(['bmp', 'png', 'jpg', 'jpeg', 'gif'])
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# For a given image, resize (scale) an image and return it's filename:
def resize_image(filename, width, height):
	
	# Open image
	try:
		img = Image.open(os.path.join(UPLOAD_FOLDER, filename))
	except:
		# error
		print("Failed to load the image: %s" % (filename))
		return 0
	
	# Assign original size if both sizes are not set,
	# Scale to the set size maintaining aspect ratio if one of the sizes is not set
	if width <= 0 and height <= 0:
		width = img.size[0]
		height = img.size[1]
	elif img.size[1] and not width:
		width = int(height * (float(img.size[0]) / (float(img.size[1]))))
	elif img.size[0] and not height:
		height = int(width * (float(img.size[1]) / (float(img.size[0]))))
	
	# Resize (scale) image (antialias filter provides good quality)
	img = img.resize((width, height), Image.ANTIALIAS)
	
	# Save the image to the resized folder
	resized_filename = "resized_" + filename
	img.save(os.path.join(RESIZED_FOLDER, resized_filename))
	return resized_filename

# The initial route to our index page
@app.route('/index')
def index():
	return render_template('index.html')

# The route to upload, save image locally and resize it
@app.route('/upload', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		
		# Check if the post request has the file part
		check = (('file' in request.files), ('height' in request.form), ('width' in request.form))
		if not all(check):
			# error
			print('File(%d), Height(%d) and/or Width(%d) are missing' % (check))
			return redirect(url_for('index'))
		
		# Get the values that were POSTed
		file = request.files['file']
		height = int(request.form['height']) if request.form['height'] else 0
		width = int(request.form['width']) if request.form['width'] else 0
		
		# Check if the filename is empty
		if file.filename == '':
			# error
			print('No file is selected')
			return redirect(url_for('index'))
		
		# Check if the file has an allowed extension
		elif allowed_file(file.filename):
			
			# Make a secure filename (getting rid of directories in the filename)
			filename = secure_filename(file.filename)
			
			# Save the file locally
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			
			# Attempt to resize the file
			resized_filename = resize_image(filename, width, height)
			
			# In the case of success display resized file in the browser
			if resized_filename:
				return redirect(url_for('resized_filename', filename=resized_filename))
			#error
			print('File could not be resized')
			return redirect(url_for('index'))
		else:
			# error
			print('File extension is not supported')
			return redirect(url_for('index'))
	# error
	print('Not a POST method')
	return redirect(url_for('index'))

# The route to display thr resized file
@app.route('/resized/<filename>')
def resized_filename(filename):
	# success
	print("Displaying image")
	return send_from_directory(RESIZED_FOLDER, filename)

# THe route to display the uploaded file
# [Currently not used]
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
	app.run(debug=True, host='127.0.0.1')