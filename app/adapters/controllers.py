# controllers.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
data_file_path = os.path.join(os.path.dirname(__file__), 'data.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices = read_data("devices")
    return jsonify(devices)

@app.route('/assign_device/<sale_id>', methods=['POST'])
def assign_device(sale_id):
    # Get the selected device_id from the form
    selected_device_id = request.form.get('device')

    sale_id_int = int(sale_id)

    # Find the sale entry in the data
    sales_data = read_data("sales")
    sale_entry = next((sale for sale in sales_data if sale['eBay item ID'] == sale_id_int), None)

    # Update the assigned_device_id attribute
    if sale_entry:
        sale_entry['assigned_device_id'] = selected_device_id
        write_data(sale_entry, "sales")

    return redirect(url_for('sales'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['csv_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Process the CSV file and update data.json
            process_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('home'))
    return render_template('upload.html')

def strip_non_utf8(text):
    return ''.join(char if ord(char) < 128 else ' ' for char in text)

def process_csv(file_path):
    try:
        # Read the CSV file into a string
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_content = file.read()
        # Strip non-UTF-8 characters from the content
        cleaned_content = strip_non_utf8(csv_content)
        # Create a StringIO object to simulate a file-like object
        from io import StringIO
        cleaned_csv_file = StringIO(cleaned_content)
        # Read the cleaned CSV file using pandas
        df = pd.read_csv(file_path, encoding='utf-8', skiprows=range(9))
        # Convert the DataFrame to a list of dictionaries
        report_from_csv = df.to_dict(orient='records')
        # Read existing data for both devices and sales
        existing_sales = read_data("sales")
        # Append new sales data to the existing sales data
        existing_sales.extend(report_from_csv)
        # Write the updated sales data to data.json
        write_data(existing_sales, "sales")
        # Print a message to confirm successful execution
        print("Data successfully written to data.json")
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV: {e}")


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/device_management', methods=['GET'])
def devices():
    devices_data = read_data("devices")  # Assuming read_data() returns a list of devices
    return render_template('devices.html', devices=devices_data)

@app.route('/sales', methods=['GET'])
def sales():
    sales_data = read_data("sales")  # Assuming read_data() returns a list of devices
    devices_data = read_data("devices")  # Assuming read_data() returns a list of devices
    return render_template('sales.html', sales_data=sales_data, devices=devices_data)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        device_name = request.form.get('device_name')
        device_description = request.form.get('device_description')
        device_cost = float(request.form.get('device_cost'))
        date_purchased = request.form.get('date_purchased')
        condition = request.form.get('condition')
        transaction_id = request.form.get('transaction_id')
        if device_name and device_cost and condition:
            new_device = {
                'id': str(uuid.uuid4()),  # Generate a unique ID
                'device_name': device_name,
                'device_description': device_description,
                'device_cost': device_cost,
                'date_purchased': date_purchased,
                'condition': condition,
                'transaction_id': transaction_id,
            }

            write_data(new_device, "devices")
            return redirect(url_for('home'))
    return render_template('add_device.html')

def read_sales_report(file_path):
    try:
        # Assuming 'your_sales_data.csv' is the path to your CSV file
        df = pd.read_csv(file_path)
        # Get the expected columns
        expected_columns = list(df.columns)
        # If there are extra columns, you can drop them
        df = df[expected_columns]
        # If there are missing columns, you can add them with default values
        for column in expected_columns:
            if column not in df.columns:
                df[column] = ''

        sales_data = df.to_dict(orient='records')
        return sales_data
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV: {e}")
        return None

def read_data(type):
    with open(data_file_path, 'r') as f:
        data = json.load(f)
    if type != None:
        data = data.get(type)
        return data
    else:
        return data
    
def write_data(data, type):
    existing_data = read_data(None)
    existing_entries = existing_data[type]
    # Check if the data entry already exists
    entry_exists = False
    if type == 'sales':
        for entry in existing_entries:
            if entry.get('eBay item ID') == data.get('eBay item ID'):
                # Update the device_id attribute
                entry['assigned_device_id'] = data.get('assigned_device_id')
                entry_exists = True
                break
    # If the entry doesn't exist, append it
    if not entry_exists:
        existing_entries.append(data)
    with open(data_file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

if __name__ == '__main__':
    app.run(debug=True)
