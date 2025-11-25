import streamlit as st
from drill_library import drills_page
import json

with open('data/drill_pro2.json', 'r') as f:
    drill_data = json.load(f)

st.set_page_config(layout="wide")

drills_page(drill_data=drill_data)

