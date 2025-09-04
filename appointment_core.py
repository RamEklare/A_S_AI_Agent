import pandas as pd
import os
from datetime import datetime

PATIENT_CSV = "./patients_sample_50.csv"
BOOKINGS_XLSX = "./bookings.xlsx"

def load_patients():
    return pd.read_csv(PATIENT_CSV)
def book_appointment(patient_id, doctor_id, doctor_name, date, slot_start, slot_end,
                     duration_mins, status, insurance_carrier, insurance_member_id,
                     cancel_reason, calendly_event_link):
    patients = pd.read_csv(PATIENT_CSV)
    patient = patients.loc[patients['patient_id'] == patient_id].iloc[0]

    if os.path.exists(BOOKINGS_XLSX):
        bookings = pd.read_excel(BOOKINGS_XLSX)
    else:
        bookings = pd.DataFrame(columns=[
            "booking_id","patient_id","patient_name","doctor_id","doctor_name",
            "date","slot_start","slot_end","duration_mins","status",
            "insurance_carrier","insurance_member_id","cancel_reason","calendly_event_link",
            # plus any extra patient columns you want to keep
        ])

    booking_id = len(bookings) + 1

    new_row = {
        "booking_id": booking_id,
        "patient_id": patient_id,
        "patient_name": patient['name'],
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "date": date,
        "slot_start": slot_start,
        "slot_end": slot_end,
        "duration_mins": duration_mins,
        "status": status,
        "insurance_carrier": insurance_carrier,
        "insurance_member_id": insurance_member_id,
        "cancel_reason": cancel_reason,
        "calendly_event_link": calendly_event_link,
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
