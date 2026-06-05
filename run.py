import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(ROOT_DIR, "vintagelab")
if PACKAGE_DIR not in sys.path:
    sys.path.insert(0, PACKAGE_DIR)

from app import create_app

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    url = f'http://127.0.0.1:{port}'
    print(f'Open the website in your browser: {url}')
    print(f'If needed, use the local network address shown in the Flask logs.')

    app = create_app()
    app.run(debug=True, host=host, port=port)
