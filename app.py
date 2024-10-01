from flask import Flask, render_template, request, redirect, url_for, send_file
import cv2
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def remove_green_screen(image_path, background_image_path):
    image = cv2.imread(image_path)
    background = cv2.imread(background_image_path)
    background = cv2.resize(background, (image.shape[1], image.shape[0]))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    lower_green = np.array([0, 100, 0])
    upper_green = np.array([100, 255, 100])
    mask = cv2.inRange(image_rgb, lower_green, upper_green)
    mask_inv = cv2.bitwise_not(mask)
    subject = cv2.bitwise_and(image, image, mask=mask_inv)
    background_final = cv2.bitwise_and(background, background, mask=mask)
    final_output = cv2.add(subject, background_final)
    output_path = os.path.join(UPLOAD_FOLDER, 'output_image.png')
    cv2.imwrite(output_path, final_output)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files or 'background' not in request.files:
            return redirect(request.url)
        image = request.files['image']
        background = request.files['background']
        if image.filename == '' or background.filename == '':
            return redirect(request.url)
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        background_path = os.path.join(UPLOAD_FOLDER, background.filename)
        image.save(image_path)
        background.save(background_path)
        output_path = remove_green_screen(image_path, background_path)
        return send_file(output_path, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
