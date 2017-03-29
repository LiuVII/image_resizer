import os
from datetime import datetime
from flask import Flask, request, render_template, redirect, \
	url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from PIL import Image
import imghdr

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

# Set the variable to detect file change during session
app.config['IS_CHANGED'] = 0
app.config['FILENAME'] = ""

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

	return img

# The initial route to our index page
@app.route('/')
def index():
	return render_template('index.html')

# The route to upload, save image locally and resize it
@app.route('/upload_and_resize', methods=['POST'])
def upload_and_resize():
	if request.method == 'POST':

		# Check if the post request has the file part
		check = (('file' in request.files), ('height' in request.form),\
			('width' in request.form), 'is_changed' in request.form)
		if not all(check):
			# error
			print('File(%d), Height(%d), Width(%d) and/or Is_Changed(%d) are missing' % (check))
			return redirect(url_for('index'))

		# Get the values that were POSTed
		file = request.files['file']
		change = request.form['is_changed']
		height = int(request.form['height']) if request.form['height'] else 0
		width = int(request.form['width']) if request.form['width'] else 0

		# Check if the filename is empty
		if file.filename == '':
			# error
			print('No file is selected')
			return redirect(url_for('index'))

		# Check if the file has an allowed extension
		elif allowed_file(file.filename):

			# Check if it the same file and if it's not save it
			if (change != app.config['IS_CHANGED']):
				# Make a secure filename (getting rid of directories in the filename)
				filename = secure_filename(file.filename)

				# Append a datetime stamp to avoid collisions with other files
				filename_split = filename.rsplit('.', 1)
				filename = filename_split[0] + "_" + datetime.now().strftime('%Y%m%d-%H%M%S')\
				+ '.' + filename_split[1].lower()

				# Check if the file's extension matches the content
				extension = filename_split[1].lower()
				if extension == "jpg":
					extension = "jpeg"
				if extension != str(imghdr.what(file)).lower():
					# error
					print("Invalid content")
					return redirect(url_for('index'))

				# Save the file locally
				try:
					file.save(os.path.join(UPLOAD_FOLDER, filename))
				except:
					# error
					print("Cannot save the file")
					return redirect(url_for('index'))

				# Setting env variables
				app.config['IS_CHANGED'] = change
				app.config['FILENAME'] = filename
			else:
				filename = app.config['FILENAME']
			
			# Attempt to resize the file and return an image
			img = resize_image(filename, width, height)

			resized_filename = "resized_" + filename
			# Save the image to the resized folder
			# For the same file we keep only the last resized version by replacing previous one
			# [Could also be implemneted in a manner to save a version if we want to]
			try:
				img.save(os.path.join(RESIZED_FOLDER, resized_filename))
			except:
				# error
				print("Cannot save the image")
				return redirect(url_for('index'))

			# Display the resized image
			return redirect(url_for('resized_filename', filename=resized_filename))
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
	# Run server with debug on to monitor status
	app.run(debug=True, host='127.0.0.1')