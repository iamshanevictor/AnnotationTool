from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import csv

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ANNOTATIONS_FILE = 'annotations.csv'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Write header to CSV file if it doesn't exist
if not os.path.exists(ANNOTATIONS_FILE):
    with open(ANNOTATIONS_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['image_id', 'class_name', 'x_min', 'y_min', 'x_max', 'y_max'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return redirect(url_for('annotate', filename=file.filename))
    return redirect(request.url)

@app.route('/annotate/<filename>')
def annotate(filename):
    return render_template('annotate.html', filename=filename)

@app.route('/save_annotation', methods=['POST'])
def save_annotation():
    annotations = request.form.get('annotations')
    annotations = eval(annotations)  # Convert string representation of list to list
    
    # Save to CSV
    with open(ANNOTATIONS_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for annotation in annotations:
            x_min = annotation['bbox'][0]
            y_min = annotation['bbox'][1]
            x_max = x_min + annotation['bbox'][2]
            y_max = y_min + annotation['bbox'][3]
            writer.writerow([annotation['filename'], annotation['label'], x_min, y_min, x_max, y_max])
    
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
