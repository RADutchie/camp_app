# main.py
import streamlit as st
from pair_optimiser_app import show as page_one
from parent_info_app import show as page_two

st.set_page_config(page_title="School camp app", layout="wide")

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Home", "Student pair optimiser", "Parent info joiner"])

if selection == "Home":
    st.title("🏠 Welcome to the Home Page")
    st.write("Use the sidebar to navigate to different sections of the app.")
elif selection == "Student pair optimiser":
    page_one()
elif selection == "Parent info joiner":
    page_two()
