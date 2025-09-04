import pandas as pd
import os
from datetime import datetime

PATIENT_CSV = "./patients_sample_50.csv"
BOOKINGS_XLSX = "./bookings.xlsx"

def load_patients():
    return pd.read_csv(PATIENT_CSV)

def book_appointment(patient_id, doctor, date_time):
    """Simulate booking logic."""
    if os.path.exists(BOOKINGS_XLSX):
        bookings = pd.read_excel(BOOKINGS_XLSX)
    else:
        bookings = pd.DataFrame(columns=["patient_id","name",'dob','age','gender','phone','email','address','medical_history',
                                        'allergies','preferred_language','insurance_provider','created_at','cancel_reason',
                                          'confirmed','calendly_event_link',"doctor","date_time","form_status"])
    booking_id = len(bookings)+1
    new_row = {"patient_id":patient_id,
               "name":name,
               'dob':dob,
               'age':age,
               'gender':gender,
               'phone':phone,
               'email':email,
               'address':address,
               'medical_history':medical_history,
               'allergies':allergies,
               'preferred_language':preferred_language,
               'insurance_provider':insurance_provider,
               'created_at':created_at,
               'cancel_reason':cancel_reason,
               'confirmed':confirmed,
               'calendly_event_link':calendly_event_link,
               "doctor":doctor,
               "date_time":date_time,
               "form_status":form_status}
    bookings = pd.concat([bookings,pd.DataFrame([new_row])],ignore_index=True)
    bookings.to_excel(BOOKINGS_XLSX,index=False)
    return booking_id

def upload_form(booking_id, file_path):
    """Mark form as uploaded and save file to disk."""
    bookings = pd.read_excel(BOOKINGS_XLSX)
    if booking_id not in bookings['booking_id'].values:
        raise ValueError("Booking ID not found")
    os.makedirs("uploaded_forms",exist_ok=True)
    file_name = f"uploaded_forms/{booking_id}_{os.path.basename(file_path)}"
    # copy instead of move to preserve your file
    with open(file_path,'rb') as src, open(file_name,'wb') as dst:
        dst.write(src.read())
    bookings.loc[bookings['booking_id']==booking_id,"form_status"]="uploaded"
    bookings.to_excel(BOOKINGS_XLSX,index=False)
    return file_name
