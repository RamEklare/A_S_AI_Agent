import pandas as pd
import os
from datetime import datetime

PATIENT_CSV = "./patients_sample_50.csv"
BOOKINGS_XLSX = "./bookings.xlsx"

def load_patients():
    return pd.read_csv(PATIENT_CSV)

def book_appointment(patient_id, doctor, date_time):
    patients = pd.read_csv(PATIENT_CSV)
    patient = patients.loc[patients['patient_id'] == patient_id].iloc[0]

    if os.path.exists(BOOKINGS_XLSX):
        bookings = pd.read_excel(BOOKINGS_XLSX)
    else:
        bookings = pd.DataFrame(columns=[
            "booking_id","patient_id","name",'dob','age','gender','phone','email','address',
            'medical_history','allergies','preferred_language','insurance_provider',
            'created_at','cancel_reason','confirmed','calendly_event_link',
            "doctor","date_time","form_status"
        ])

    booking_id = len(bookings) + 1

    new_row = {
        "booking_id": booking_id,
        "patient_id": patient_id,
        "name": patient['name'],
        "dob": patient['dob'],
        "age": patient['age'],
        "gender": patient['gender'],
        "phone": patient['phone'],
        "email": patient['email'],
        "address": patient['address'],
        "medical_history": patient['medical_history'],
        "allergies": patient['allergies'],
        "preferred_language": patient['preferred_language'],
        "insurance_provider": patient['insurance_provider'],
        "created_at": datetime.now(),
        "cancel_reason": "",
        "confirmed": True,
        "calendly_event_link": "",
        "doctor": doctor,
        "date_time": date_time,
        "form_status": "pending"
    }

    bookings = pd.concat([bookings, pd.DataFrame([new_row])], ignore_index=True)
    bookings.to_excel(BOOKINGS_XLSX, index=False)
    return booking_id

def upload_form(booking_id, file_path):
    bookings = pd.read_excel(BOOKINGS_XLSX)
    if booking_id not in bookings['booking_id'].values:
        raise ValueError("Booking ID not found")

    os.makedirs("uploaded_forms", exist_ok=True)
    file_name = f"uploaded_forms/{booking_id}_{os.path.basename(file_path)}"
    with open(file_path, 'rb') as src, open(file_name, 'wb') as dst:
        dst.write(src.read())

    bookings.loc[bookings['booking_id'] == booking_id, "form_status"] = "uploaded"
    bookings.to_excel(BOOKINGS_XLSX, index=False)
    return file_name
