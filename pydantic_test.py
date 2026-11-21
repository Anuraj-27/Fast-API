from models import Student
import json

def load_data():
    with open("students.json", "r", encoding="utf-8") as file:
        return json.load(file)["students"]

for student_data in load_data():
    try:
        student = Student(**student_data) # unpacking the dictionary into the Student model
        print(student)
    except Exception as e:
        print(f"Error creating Student object: {e}")