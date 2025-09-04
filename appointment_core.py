import pandas as pd
import os
from datetime import datetime

PATIENT_CSV = "./patients_sample_50.csv"
BOOKINGS_XLSX = "./bookings.xlsx"

def load_patients():
    """Load patient data from CSV."""
    return pd.read_csv(PATIENT_CSV)


def book_appointment(
    patient_id,
    doctor_id,
    doctor_name,
    date,
    slot_start,
    slot_end,
    duration_mins,
    status="pending",
    insurance_carrier="",
    insurance_member_id="",
    cancel_reason="",
    calendly_event_link=""
):
    """
    Create a booking entry combining patient info with doctor/slot details.
    Automatically ensures all needed columns exist.
    """

    # 1. Load patient info
    patients = pd.read_csv(PATIENT_CSV)
    patient = patients.loc[patients['patient_id'] == patient_id].iloc[0]

    # 2. Define all columns you want in the bookings file
    required_columns = [
        "booking_id","patient_id","patient_name",
        "doctor_id","doctor_name","date","slot_start","slot_end","duration_mins",
        "status","insurance_carrier","insurance_member_id","cancel_reason","calendly_event_link",
        "form_status"  # add this now so upload_form can work
    ]

    # 3. Load or create the bookings file
    if os.path.exists(BOOKINGS_XLSX):
        bookings = pd.read_excel(BOOKINGS_XLSX)
        # Make sure all required columns exist
        for col in required_columns:
            if col not in bookings.columns:
                bookings[col] = ""
    else:
        bookings = pd.DataFrame(columns=required_columns)

    # 4. Generate booking_id
    booking_id = len(bookings) + 1

    # 5. Build the new row
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
        "form_status": ""  # initially empty
    }

    # 6. Append and save
    bookings = pd.concat([bookings, pd.DataFrame([new_row])], ignore_index=True)
    bookings.to_excel(BOOKINGS_XLSX, index=False)
    return booking_id


def upload_form(booking_id, file_path):
    """
    Upload a form file for a given booking and mark 'form_status' as uploaded.
    """
    # Load bookings and ensure form_status column exists
    if os.path.exists(BOOKINGS_XLSX):
        bookings = pd.read_excel(BOOKINGS_XLSX)
    else:
        raise FileNotFoundError("Bookings file not found")

    if booking_id not in bookings['booking_id'].values:
        raise ValueError("Booking ID not found")

    if 'form_status' not in bookings.columns:
        bookings['form_status'] = ""

    os.makedirs("uploaded_forms", exist_ok=True)
    file_name = f"uploaded_forms/{booking_id}_{os.path.basename(file_path)}"

    with open(file_path, 'rb') as src, open(file_name, 'wb') as dst:
        dst.write(src.read())

    # Update form_status
    bookings.loc[bookings['booking_id'] == booking_id, "form_status"] = "uploaded"
    bookings.to_excel(BOOKINGS_XLSX, index=False)
    return file_name
