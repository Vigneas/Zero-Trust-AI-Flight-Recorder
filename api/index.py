import os
import sys

# Add 'src' directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from lending_api.main import app
