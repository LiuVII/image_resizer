# Application 'image_resizer'
Single endpoint web server takes in an image and resizes (scales) it to the specified dimensions

## Setup
To setup application simply copy (or git clone) the application folder into any location with reading and writing access rights.

The application requires python 2 (version 2.7 or greater) with
installed libraries specified in 'requirements.txt'.

## Run
To run the application using the terminal
cd to the application folder and simply execute:
```
python app.py
```

On a success the application will provide an URL path to the server:
```
http://127.0.0.1:5000/
```

## Inside the browser
The application is tested with the Chrome browser
(there could be performance issues with other browsers) 

Put server address to the browser window to access the index page:
```
http://127.0.0.1:5000/
```

A simple form with 'choose file' button, 'height', 'width' fields and 'resize' button should appear

## Resizing images
Choose an image file to be uploaded
(supported formats: 'bmp', 'png', 'jpg', 'jpeg', 'gif')

Select the width and height you want to scale the image (accepted params from 0 to 999):
- If both sizes specified image will scale to fit specified size (not preserving aspect ratio);
- If only one size > 0, image will scale to the non-zero size, maintaining aspect ratio;
- In case both sizes left zero image size would be preserved;

Uploaded images are collected inside 'uploads' folder, resized images can be found in 'resized' folder within the application folder

File management implemented in a way that for every change of file new file will be created in the 'uploads' folder,
and for every resize action only the last version is saved in the 'resized' folder.

## Additional info
The application uses Pillow library and it's ANTIALIAS filter to perform overall good quality scaling.
Still, performance can be increased depending on the specific input and the way of resizing.
For example: upscaling of bit images could be done with an additional usage of SHARPEN and 
EDGE_ENHANCE filters for better results.
See more available filters:
http://pillow.readthedocs.io/en/3.4.x/reference/ImageFilter.html
