import streamlit as st
import pandas as pd
from datetime import datetime
import tempfile
from appointment_core import load_patients, book_appointment, upload_form

st.set_page_config(page_title="Medical Appointment Scheduling AI Agent", page_icon="🩺")
st.title("🩺 Medical Appointment Scheduling AI Agent")

# --- Patient lookup ---
st.header("Patient Lookup")
patients = load_patients()
patient_choice = st.selectbox("Select Patient", patients['name'])
patient_id = patients.loc[patients['name']==patient_choice,'patient_id'].values[0]

# --- Book appointment ---
st.header("Book Appointment")
doctor = st.selectbox("Doctor", ["Dr. Smith","Dr. Patel","Dr. Lee"])
date = st.date_input("Date")
time = st.time_input("Time")
if st.button("Book Appointment"):
    booking_id = book_appointment(patient_id, doctor, datetime.combine(date,time))
    st.success(f"Appointment booked! Booking ID = {booking_id}")

# --- Upload intake form ---
st.header("Upload Intake Form")
booking_id_input = st.number_input("Enter your Booking ID",min_value=1,step=1)
uploaded_file = st.file_uploader("Upload your filled intake form PDF",type=["pdf"])
if uploaded_file and st.button("Upload Form"):
    # save to temp file first
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name
    saved_path = upload_form(int(booking_id_input), temp_path)
    st.success(f"Form uploaded and stored at {saved_path}")

# --- Admin view ---
st.header("Admin Review (Bookings)")
if st.checkbox("Show all bookings"):
    bookings_df = pd.read_excel("./bookings.xlsx") if os.path.exists("./bookings.xlsx") else pd.DataFrame()
    st.dataframe(bookings_df)
