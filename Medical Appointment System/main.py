from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi import Query

app = FastAPI()


doctors = [
    {"id": 1, "name": "Dr. Sharma", "specialization": "Cardiologist", "fee": 500, "experience_years": 10, "is_available": True},
    {"id": 2, "name": "Dr. Mehta", "specialization": "Dermatologist", "fee": 300, "experience_years": 6, "is_available": True},
    {"id": 3, "name": "Dr. Khan", "specialization": "Pediatrician", "fee": 400, "experience_years": 8, "is_available": False},
    {"id": 4, "name": "Dr. Singh", "specialization": "General", "fee": 200, "experience_years": 5, "is_available": True},
    {"id": 5, "name": "Dr. Patel", "specialization": "Cardiologist", "fee": 600, "experience_years": 12, "is_available": False},
    {"id": 6, "name": "Dr. Verma", "specialization": "Dermatologist", "fee": 350, "experience_years": 7, "is_available": True}
]
appointments = []
appt_counter = 1


class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False


class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True


def find_doctor(doctor_id):
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc
    return None


def calculate_fee(base_fee, appointment_type, senior_citizen):
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee

    if senior_citizen:
        discounted_fee = fee * 0.85
    else:
        discounted_fee = fee

    return fee, discounted_fee


def filter_doctors_logic(specialization, max_fee, min_experience, is_available):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]

    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]

    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]

    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    return result


@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}


@app.get("/doctors")
def get_doctors():
    total = len(doctors)
    available_count = len([doc for doc in doctors if doc["is_available"]])

    return {
        "total": total,
        "available_count": available_count,
        "doctors": doctors
    }


@app.get("/appointments")
def get_appointments():
    return {
        "total": len(appointments),
        "appointments": appointments
    }


@app.get("/doctors/summary")
def doctors_summary():
    total = len(doctors)
    available = len([d for d in doctors if d["is_available"]])

    most_experienced = max(doctors, key=lambda x: x["experience_years"])
    cheapest_fee = min(doctors, key=lambda x: x["fee"])["fee"]

    specialization_count = {}
    for d in doctors:
        spec = d["specialization"]
        specialization_count[spec] = specialization_count.get(spec, 0) + 1

    return {
        "total_doctors": total,
        "available_doctors": available,
        "most_experienced": most_experienced["name"],
        "cheapest_fee": cheapest_fee,
        "specialization_count": specialization_count
    }

@app.get("/doctors/filter")
def filter_doctors(
    specialization: str = Query(None),
    max_fee: int = Query(None),
    min_experience: int = Query(None),
    is_available: bool = Query(None)
):
    filtered = filter_doctors_logic(
        specialization,
        max_fee,
        min_experience,
        is_available
    )
    return {
        "total": len(filtered),
        "doctors": filtered
    }


def filter_doctors_logic(specialization, max_fee, min_experience, is_available):
    result = doctors

    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]

    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]

    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]

    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    return result


@app.get("/doctors/search")
def search_doctors(keyword: str):
    result = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]

    if not result:
        return {"message": "No doctors found"}

    return {
        "total_found": len(result),
        "doctors": result
    }


@app.get("/doctors/sort")
def sort_doctors(
    sort_by: str = "fee"
):
    if sort_by not in ["fee", "name", "experience_years"]:
        return {"error": "Invalid sort field"}

    sorted_list = sorted(doctors, key=lambda x: x[sort_by])

    return {
        "sort_by": sort_by,
        "doctors": sorted_list
    }


@app.get("/doctors/page")
def paginate_doctors(
    page: int = 1,
    limit: int = 3
):
    total = len(doctors)

    start = (page - 1) * limit
    end = start + limit

    paginated = doctors[start:end]

    total_pages = (total + limit - 1) // limit  # ceiling division

    return {
        "page": page,
        "limit": limit,
        "total_doctors": total,
        "total_pages": total_pages,
        "doctors": paginated
    }


@app.get("/doctors/browse")
def browse_doctors(
    keyword: str = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = doctors

    # 🔍 FILTER (search)
    if keyword:
        result = [
            d for d in result
            if keyword.lower() in d["name"].lower()
            or keyword.lower() in d["specialization"].lower()
        ]

    # 🔄 SORT
    if sort_by not in ["fee", "name", "experience_years"]:
        return {"error": "Invalid sort field"}

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    # 📄 PAGINATION
    total = len(result)
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_results": total,
        "total_pages": total_pages,
        "data": paginated
    }


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc

    return {"error": "Doctor not found"}


@app.post("/appointments")
def create_appointment(request: AppointmentRequest):
    doctor = find_doctor(request.doctor_id)

    if not doctor:
        return {"error": "Doctor not found"}

    if not doctor["is_available"]:
        return {"error": "Doctor not available"}

    original_fee, final_fee = calculate_fee(
    doctor["fee"],
    request.appointment_type,
    request.senior_citizen
)

    global appt_counter

    appointment = {
        "appointment_id": appt_counter,
        "patient_name": request.patient_name,
        "doctor_name": doctor["name"],
        "date": request.date,
        "appointment_type": request.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appointment)
    appt_counter += 1

    return appointment


@app.post("/doctors", status_code=201)
def create_doctor(doctor: NewDoctor):
    # check duplicate name
    for d in doctors:
        if d["name"].lower() == doctor.name.lower():
            return {"error": "Doctor already exists"}

    new_doc = {
        "id": len(doctors) + 1,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "fee": doctor.fee,
        "experience_years": doctor.experience_years,
        "is_available": doctor.is_available
    }

    doctors.append(new_doc)

    return new_doc


@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    fee: int = None,
    is_available: bool = None
):
    doctor = find_doctor(doctor_id)

    if not doctor:
        return {"error": "Doctor not found"}

    if fee is not None:
        doctor["fee"] = fee

    if is_available is not None:
        doctor["is_available"] = is_available

    return doctor


@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)

    if not doctor:
        return {"error": "Doctor not found"}

    # check for active appointments
    for appt in appointments:
        if appt["doctor_name"] == doctor["name"] and appt["status"] == "scheduled":
            return {"error": "Doctor has active appointments"}

    doctors.remove(doctor)

    return {"message": "Doctor deleted successfully"}


@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "confirmed"
            return {"message": "Appointment confirmed"}

    return {"error": "Appointment not found"}


@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "cancelled"

            # make doctor available again
            for doc in doctors:
                if doc["name"] == appt["doctor_name"]:
                    doc["is_available"] = True

            return {"message": "Appointment cancelled"}

    return {"error": "Appointment not found"}


@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "completed"
            return {"message": "Appointment completed"}

    return {"error": "Appointment not found"}


@app.get("/appointments/active")
def get_active_appointments():
    active = [
        appt for appt in appointments
        if appt["status"] in ["scheduled", "confirmed"]
    ]

    return {
        "total": len(active),
        "appointments": active
    }


@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)

    if not doctor:
        return {"error": "Doctor not found"}

    result = [
        appt for appt in appointments
        if appt["doctor_name"] == doctor["name"]
    ]

    return {
        "doctor": doctor["name"],
        "total": len(result),
        "appointments": result
    }


@app.get("/appointments/search")
def search_appointments(patient_name: str):
    result = [
        appt for appt in appointments
        if patient_name.lower() in appt["patient_name"].lower()
    ]

    return {
        "total_found": len(result),
        "appointments": result
    }


@app.get("/appointments/sort")
def sort_appointments(sort_by: str = "date"):
    if sort_by not in ["date", "final_fee"]:
        return {"error": "Invalid sort field"}

    sorted_list = sorted(appointments, key=lambda x: x[sort_by])

    return {
        "sort_by": sort_by,
        "appointments": sorted_list
    }


@app.get("/appointments/page")
def paginate_appointments(page: int = 1, limit: int = 2):
    total = len(appointments)

    start = (page - 1) * limit
    end = start + limit

    paginated = appointments[start:end]

    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_appointments": total,
        "total_pages": total_pages,
        "appointments": paginated
    }
