from app import app
import os
from threading import Thread

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)
