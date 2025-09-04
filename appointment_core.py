import pandas as pd
import os
from datetime import datetime

PATIENT_CSV = "./patients_sample_50.csv"
BOOKINGS_XLSX = "./bookings.xlsx"
DOCTOR_XLSX = "./doctor_schedules_sample.xlsx"  # <- your doctor schedule file

def load_patients():
    """Load all patients from CSV."""
    return pd.read_csv(PATIENT_CSV)

def get_doctors():
    """Load all available doctors from the doctor schedule file."""
    if not os.path.exists(DOCTOR_XLSX):
        raise FileNotFoundError(f"Doctor schedule file {DOCTOR_XLSX} not found")
    df = pd.read_excel(DOCTOR_XLSX)
    # Adjust column name if needed: e.g., "Doctor" or "doctor_name"
    doctor_col = None
    for col in df.columns:
        if col.lower() in ("doctor", "doctor_name", "name"):
            doctor_col = col
            break
    if doctor_col is None:
        raise ValueError(f"No doctor column found in {DOCTOR_XLSX}. Columns: {df.columns}")
    return df[doctor_col].unique()

def book_appointment(patient_id, doctor, date_time):
    """Book an appointment for a patient with a doctor at date_time."""
    # Validate patient exists
    patients = pd.read_csv(PATIENT_CSV)
    if patient_id not in patients['patient_id'].values:
        raise ValueError(f"Patient ID {patient_id} not found in {PATIENT_CSV}")
    patient = patients.loc[patients['patient_id'] == patient_id].iloc[0]

    # Validate doctor exists
    valid_doctors = get_doctors()
    if doctor not in valid_doctors:
        raise ValueError(
            f"No doctor '{doctor}' found in {DOCTOR_XLSX}. "
            f"Available doctors: {list(valid_doctors)}"
        )

    # Load existing bookings or create new DataFrame
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
    """Upload a form for a given booking."""
    if not os.path.exists(BOOKINGS_XLSX):
        raise FileNotFoundError(f"{BOOKINGS_XLSX} not found")

    bookings = pd.read_excel(BOOKINGS_XLSX)
    if booking_id not in bookings['booking_id'].values:
        raise ValueError(f"Booking ID {booking_id} not found in {BOOKINGS_XLSX}")

    os.makedirs("uploaded_forms", exist_ok=True)
    file_name = f"uploaded_forms/{booking_id}_{os.path.basename(file_path)}"
    with open(file_path, 'rb') as src, open(file_name, 'wb') as dst:
        dst.write(src.read())

    bookings.loc[bookings['booking_id'] == booking_id, "form_status"] = "uploaded"
    bookings.to_excel(BOOKINGS_XLSX, index=False)
    return file_name
