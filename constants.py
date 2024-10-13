import os

# Define the path to the directory where you want to store the proxy files
PROXY_DIR = os.path.join(os.path.dirname(__file__), "proxy_files")

# Create the directory if it doesn't exist
os.makedirs(PROXY_DIR, exist_ok=True)

# Define the paths for the blacklist and working proxy files
BLACKLISTED_PROXY_PATH = os.path.join(PROXY_DIR, "blacklisted_proxies.txt")
WORKING_PROXY_PATH = os.path.join(PROXY_DIR, "working_proxies.txt")

# Maximum number of worker threads
MAX_WORKERS = 50