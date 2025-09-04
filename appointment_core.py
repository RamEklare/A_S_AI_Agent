import pandas as pd
import os
from datetime import datetime

PATIENT_CSV = "./patients_sample_50.csv"
BOOKINGS_XLSX = "./bookings.xlsx"
DOCTOR_XLSX = "./doctor_schedules_sample.xlsx"

def load_patients():
    return pd.read_csv(PATIENT_CSV)

def load_doctor_schedule():
    if not os.path.exists(DOCTOR_XLSX):
        raise FileNotFoundError(f"Doctor schedule file {DOCTOR_XLSX} not found")
    df = pd.read_excel(DOCTOR_XLSX)
    # ✅ fix the typo: "specialty"
    expected_cols = {"doctor_name", "start_time", "end_time", "doctor_id", "specialty"}
    if not expected_cols.issubset(df.columns):
        raise ValueError(f"Expected columns {expected_cols}, but found {set(df.columns)}")
    return df

def get_available_doctors():
    df = load_doctor_schedule()
    return df['doctor_name'].unique()

def book_appointment(patient_id, doctor_name, date_time):
    if not os.path.exists(PATIENT_CSV):
        raise FileNotFoundError(f"Patient file {PATIENT_CSV} not found")
    patients = pd.read_csv(PATIENT_CSV)
    if patient_id not in patients['patient_id'].values:
        raise ValueError(f"Patient ID {patient_id} not found")
    patient = patients.loc[patients['patient_id'] == patient_id].iloc[0]

    doc_df = load_doctor_schedule()
    if doctor_name not in doc_df['doctor_name'].values:
        raise ValueError(f"No doctor_name '{doctor_name}' found. Available: {list(doc_df['doctor_name'].unique())}")
    doc_info = doc_df.loc[doc_df['doctor_name'] == doctor_name].iloc[0]
    doctor_id = doc_info['doctor_id']
    start_time = doc_info['start_time']
    end_time = doc_info['end_time']
    specialty = doc_info['specialty']

    if os.path.exists(BOOKINGS_XLSX):
        bookings = pd.read_excel(BOOKINGS_XLSX)
    else:
        bookings = pd.DataFrame(columns=[
            "booking_id","patient_id","name",'dob','age','gender','phone','email','address',
            'medical_history','allergies','preferred_language','insurance_provider',
            'created_at','cancel_reason','confirmed','calendly_event_link',
            "doctor_name","doctor_id","start_time","end_time",'specialty',"date_time","form_status"
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
        "doctor_name": doctor_name,
        "doctor_id": doctor_id,
        "start_time": start_time,
        "end_time": end_time,
        'specialty': specialty,
        "date_time": date_time,
        "form_status": "pending"
    }

    bookings = pd.concat([bookings, pd.DataFrame([new_row])], ignore_index=True)
    bookings.to_excel(BOOKINGS_XLSX, index=False)
    return booking_id

def upload_form(booking_id, file_path):
    if not os.path.exists(BOOKINGS_XLSX):
        raise FileNotFoundError(f"{BOOKINGS_XLSX} not found")
    bookings = pd.read_excel(BOOKINGS_XLSX)
    if booking_id not in bookings['booking_id'].values:
        raise ValueError(f"Booking ID {booking_id} not found")

    os.makedirs("uploaded_forms", exist_ok=True)
    file_name = f"uploaded_forms/{booking_id}_{os.path.basename(file_path)}"
    with open(file_path, 'rb') as src, open(file_name, 'wb') as dst:
        dst.write(src.read())

    bookings.loc[bookings['booking_id'] == booking_id, "form_status"] = "uploaded"
    bookings.to_excel(BOOKINGS_XLSX, index=False)
    return file_name

if __name__ == "__main__":
    print("Available doctors:", get_available_doctors())
    booking_id = book_appointment(
        patient_id=1,
        doctor_name="Dr. Patel",   # must match Excel exactly
        date_time="2025-09-06 10:00"
    )
    print("Booking ID:", booking_id)
    uploaded_path = upload_form(booking_id, "myform.pdf")
    print("Uploaded file path:", uploaded_path)
