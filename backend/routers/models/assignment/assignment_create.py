from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    employee_number: str = Field(
        examples=['E001'],
        description='The employee number of the crew memeber',
        min_length=4,
        max_length=4
    )
    flight_number: str = Field(
        examples=['F1'],
        description='The number of the flight',
        min_length=2
    )