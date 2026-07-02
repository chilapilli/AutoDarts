from flask import Flask, request
import os

app = Flask(__name__)
os.makedirs('snapshots', exist_ok=True)

@app.route('/snapshot', methods=['POST'])
def receive():
    for key, file in request.files.items():
        file.save(f'snapshots/{file.filename}')
        print(f'Received {file.filename}')
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)