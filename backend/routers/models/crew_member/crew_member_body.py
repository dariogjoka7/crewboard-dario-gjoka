from typing import List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CrewMemberBody(BaseModel):
    employee_number: str = Field(
        examples=['E001'],
        description='The number of the employee',
        min_length=4,
        max_length=4
    )
    first_name: str = Field(
        examples=['John'],
        description='The first name of the crew member'
    )
    last_name: str = Field(
        examples=['Doe'],
        description='The last name of the crew member'
    )
    email: EmailStr = Field(
        examples=['johndoe@example.com'],
        description='The email address of the crew member'
    )
    base_airport: str = Field(
        examples=['FR'],
        description="The IATA code of the crew member's base airport"
    )
    aircraft_qualifications: List[str] = Field(
        examples=[['A320']],
        description='The aircraft qualifications of the employee',
        min_length=1
    )
