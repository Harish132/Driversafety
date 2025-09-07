from flask import Flask, render_template, jsonify, request, redirect, url_for
import os, random, base64, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# === Upload Folder Setup ===
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Email Config ===
SENDER_EMAIL = "hariharish1321@gmail.com"
APP_PASSWORD = "bwqddyvxnbcxkdfd"  # Gmail App Password
RECEIVER_EMAIL = "22091a3228@rgmcet.edu.in"

# === State ===
data_active = False
last_uploaded_file = None

# === Simulated Sensor Data ===
def get_sensor_data():
    return {
        'alcohol_level': round(random.choice([0.0, 0.08, 0.12]), 2),
        'seatbelt_status': random.choice(['Worn', 'Not Worn']),
        'temperature': random.randint(25, 37),
        'gyroscope': {
            'x': round(random.uniform(-2, 2), 2),
            'y': round(random.uniform(-2, 2), 2),
            'z': round(random.uniform(-2, 2), 2)
        },
        'location': {'lat': 17.385, 'lng': 78.4867},
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }

def get_zero_data():
    return {
        'alcohol_level': 0.0,
        'seatbelt_status': 'Unknown',
        'temperature': 0,
        'gyroscope': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'location': {'lat': 0.0, 'lng': 0.0},
        'timestamp': '--:--:--'
    }

# === Send Email Alert with Optional Location ===
def send_email_alert(subject, body, lat=None, lng=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = subject

        if lat is not None and lng is not None:
            body += f"\n\n📍 Live Location: https://www.google.com/maps?q={lat},{lng}"

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📨 Email sent to admin.")
    except Exception as e:
        print("❌ Failed to send email:", e)

# === Web Routes ===
@app.route('/')
def index():
    global data_active, last_uploaded_file
    sensor_data = get_sensor_data() if data_active else None
    return render_template('index.html', data=sensor_data, filename=last_uploaded_file)

@app.route('/data')
def data():
    global data_active

    if not data_active:
        return jsonify(get_zero_data())

    sensor_data = get_sensor_data()

    alerts = []
    if sensor_data['seatbelt_status'] == 'Not Worn':
        alerts.append("⚠️ Seatbelt is not worn.")
    if sensor_data['alcohol_level'] > 0.0:
        alerts.append(f"🚨 Alcohol detected: {sensor_data['alcohol_level']}%")

    if alerts:
        alert_msg = "\n".join(alerts)
        send_email_alert(
            subject="🚗 Driver Safety Alert",
            body=f"The following unsafe conditions were detected:\n\n{alert_msg}\n\nTimestamp: {sensor_data['timestamp']}",
            lat=sensor_data['location']['lat'],
            lng=sensor_data['location']['lng']
        )

    return jsonify(sensor_data)

@app.route('/upload', methods=['POST'])
def upload():
    global data_active, last_uploaded_file
    file = request.files['media']
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    last_uploaded_file = filename
    data_active = True

    send_email_alert(
        subject="📎 Image Upload Alert",
        body=f"An image was uploaded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        lat=17.385,
        lng=78.4867
    )

    return redirect(url_for('index'))

@app.route('/upload_live_image', methods=['POST'])
def upload_live_image():
    global data_active, last_uploaded_file
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    filename = f"live_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)
    last_uploaded_file = filename
    data_active = True

    send_email_alert(
        subject="📸 Live Image Captured",
        body=f"A live image was captured at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        lat=17.385,
        lng=78.4867
    )

    return jsonify({'status': 'success'})

# === Run App ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
