from pydantic import BaseModel, Field, EmailStr, field_validator, computed_field

class Student(BaseModel):
    id : int = Field(..., description="The unique identifier for the student")
    name: str = Field(..., min_length=1, max_length=100, description="The name of the student")
    age: int = Field(..., ge=0, le=100, description="The age of the student")
    email: EmailStr = Field(..., description="The email address of the student")
    course: str = Field(..., min_length=1, max_length=100, description="The course the student is enrolled in")
    marks: int = Field(..., ge=0, le=100, description="The marks obtained by the student")

    @field_validator('name')
    @classmethod
    def check_name(cls, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters and spaces")
        return value.title()  # Capitalize the name

    @computed_field
    @property
    def grade(self) -> str:
        if self.marks >=90:
            return "A+"
        elif self.marks >= 80:
            return "A"
        elif self.marks >= 70:
            return "B"
        else:
            return "FAIL"