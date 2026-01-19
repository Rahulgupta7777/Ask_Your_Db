import sys
import os
import streamlit as st

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.controllers import home_controller

if __name__ == "__main__":
    home_controller.run()
