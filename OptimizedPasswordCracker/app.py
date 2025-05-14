


from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO
import zipfile, os
import threading

app = Flask(__name__)
socketio = SocketIO(app)

UPLOAD_FOLDER = 'uploads'
EXTRACTED_FOLDER = 'extracted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)

# Global state to store results
results = {
    "cracked_password": None,
    "extracted_files": []
}

def crack_password(zip_path, wordlist_path):
    results["cracked_password"] = None
    results["extracted_files"].clear()

    with zipfile.ZipFile(zip_path) as zf, open(wordlist_path, 'r', errors='ignore') as wf:
        for line in wf:
            password = line.strip()
            socketio.emit("log", f"Trying password: {password}")
            try:
                zf.extractall(path=EXTRACTED_FOLDER, pwd=password.encode())
                results["cracked_password"] = password
                results["extracted_files"] = os.listdir(EXTRACTED_FOLDER)
                socketio.emit("log", f"✅ Password cracked: {password}")
                socketio.emit("done", {
                    "password": password,
                    "files": results["extracted_files"]
                })
                return
            except:
                continue

    socketio.emit("log", "❌ Password not found in wordlist.")
    socketio.emit("done", { "password": None, "files": [] })

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    zip_file = request.files['zipfile']
    wordlist_file = request.files['wordlist']

    zip_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
    wordlist_path = os.path.join(UPLOAD_FOLDER, wordlist_file.filename)
    zip_file.save(zip_path)
    wordlist_file.save(wordlist_path)

    threading.Thread(target=crack_password, args=(zip_path, wordlist_path)).start()

    return '', 204  # No content, frontend handles update via Socket.IO

@app.route('/download_file/<filename>')
def download_file(filename):
    path = os.path.join(EXTRACTED_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    socketio.run(app, debug=True)



