from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
from models import Student
app = FastAPI(title="Student Management API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui")
def serve_ui():
    return FileResponse("static/index.html")

@app.get("/")
def greet():
    return {"message": "Hello This is my first APP", "ui_url": "/ui", "docs_url": "/docs"}


def load_data():
    with open("students.json", "r", encoding="utf-8") as file:
        return json.load(file)["students"]

# Save data
def save_data(students):
    with open("students.json","w", encoding="utf-8") as file:
        json.dump({"students": students},file, indent=4)


@app.get("/students")
def student():
    return load_data()

# Build the lookup once at startup: {1: {...}, 2: {...}, ...}
students_by_id = {student["id"]: student for student in load_data()}

@app.get("/students/{student_id}")
def get_id(student_id: int = Path(..., description="The ID of the student to retrieve")):
    student = students_by_id.get(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")
    return student

@app.get("/filter")
def filter_students(course: str):
    matches = [
        student for student in load_data()
        if student["course"].lower() == course.lower()
    ]
    if not matches:
        raise HTTPException(status_code=404, detail=f"No students found for course {course}")
    return matches

@app.get("/sorted_students")
def get_students(order: str = "desc"):
    students = load_data()
    reverse = order.lower() != "asc"
    return sorted(students, key=lambda s: s["id"], reverse=reverse)

@app.get("/marks")
def get_students(order: str = "desc"):
    students = load_data()
    reverse = order.lower() != "asc"
    return sorted(students, key=lambda s: s["marks"], reverse=reverse)

"""
PAGINATION : 
 Page - > whoch page you want to see
 Limit -> how many records you want to see in a page

 Formula : 
 
    start_index = (page - 1) * limit
    end_index = start_index + limit
"""
@app.get("/pagination")
def get_students(page: int = Query(1 , ge=1 , description="The page number to retrieve"), limit: int = Query(3, ge=1, description="The number of records to retrieve per page")):
    data = load_data()
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_data = data[start_index:end_index]
    return {
        "page": page,
        "limit": limit,
        "total_records": len(data),
        "data": paginated_data
    }

"""
POST 
"""

@app.post("/create",response_model=Student , status_code=201)
def create_student(student: Student):
    data = load_data()
    # Check if email already exists
    if any(s["email"] == student.email for s in data):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Check if ID already exists
    if any(s["id"] == student.id for s in data):
        raise HTTPException(status_code=400, detail="ID already exists")

    # Add the new student to the data
    student_dict = student.model_dump()
    data.append(student_dict)
    save_data(data)
    students_by_id[student.id] = student_dict

    return student

@app.put("/update/{student_id}", status_code=200)
def update_student(student_id: int, updated_student: Student):
    # Check if student with Id exists
    if student_id not in students_by_id:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")

    # Check if duplicate Email is prenet or not
    for s in students_by_id.values():
        if s["email"] == updated_student.email and s["id"] != student_id:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Update student data
    new_data = updated_student.model_dump(exclude={"grade"})  # Exclude computed field
    new_data["id"] = student_id  # Ensure the ID remains the same

    # replace old data with new data
    students_by_id[student_id] = new_data

    # Save updated data to file
    save_data(list(students_by_id.values()))
    return {"message": f"Student with id {student_id} updated successfully", "student": new_data}

@app.delete("/delete/{student_id}", status_code=200)
def delete_student(student_id: int):
    # Check if student with Id exists
    if student_id not in students_by_id:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found")

    # Remove the student from the dictionary
    deleted_student = students_by_id.pop(student_id)

    # Save updated data to file
    save_data(list(students_by_id.values()))
    return {"message": f"Student with id {student_id} deleted successfully", "student": deleted_student}