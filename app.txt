import logging
from flask import Flask

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def hello_world():
    logger.info("Received a request on the root path.")
    return 'YukiOnna Bot running on Flask'

if __name__ == "__main__":
    # Ensure the app runs on port 8000 and listens on all IP addresses
    app.run(host='0.0.0.0', port=8000)
