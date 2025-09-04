import pandas as pd
import os
from datetime import datetime

PATIENT_CSV = "./patients_sample_50.csv"
BOOKINGS_XLSX = "./bookings.xlsx"
DOCTOR_SCHEDULER_XLSX = ".data/doctor_schedules_sample.xlsx"


def load_patients():
    """Load patient data from CSV."""
    return pd.read_csv(PATIENT_CSV)


def book_appointment(patient_id, doctor_id, slot_index=0):
    """
    Book an appointment automatically by looking up doctor_id and slot info
    from the scheduler Excel. slot_index lets you pick which slot for that doctor.
    """

    # 1. Load patient info
    patients = pd.read_csv(PATIENT_CSV)
    patient = patients.loc[patients['patient_id'] == patient_id].iloc[0]

    # 2. Load doctor scheduler
    sched = pd.read_excel(DOCTOR_SCHEDULER_XLSX)

    # 3. Filter by doctor_id
    doctor_rows = sched[sched['doctor_id'] == doctor_id]
    if doctor_rows.empty:
        raise ValueError(f"No doctor_id {doctor_id} found in scheduler")

    # 4. Pick the slot_index-th row
    slot = doctor_rows.iloc[slot_index]

    # 5. Append booking row into bookings.xlsx
    return _append_booking(
        patient,
        slot['doctor_id'],
        slot['doctor_name'],
        slot['date'],
        slot['slot_start'],
        slot['slot_end'],
        slot['duration_mins'],
        slot['status'],
        slot.get('insurance_carrier', ""),
        slot.get('insurance_member_id', ""),
        slot.get('cancel_reason', ""),
        slot.get('calendly_event_link', "")
    )


def _append_booking(patient, doctor_id, doctor_name, date, slot_start, slot_end,
                    duration_mins, status, insurance_carrier, insurance_member_id,
                    cancel_reason, calendly_event_link):
    """internal helper to append booking row to Excel"""
    required_columns = [
        "booking_id", "patient_id", "patient_name",
        "doctor_id", "doctor_name", "date", "slot_start", "slot_end", "duration_mins",
        "status", "insurance_carrier", "insurance_member_id", "cancel_reason", "calendly_event_link",
        "form_status"
    ]

    # load or create bookings.xlsx
    if os.path.exists(BOOKINGS_XLSX):
        bookings = pd.read_excel(BOOKINGS_XLSX)
        for col in required_columns:
            if col not in bookings.columns:
                bookings[col] = ""
    else:
        bookings = pd.DataFrame(columns=required_columns)

    booking_id = len(bookings) + 1

    new_row = {
        "booking_id": booking_id,
        "patient_id": patient['patient_id'],
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
