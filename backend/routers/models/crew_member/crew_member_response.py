from typing import List, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_serializer


class CrewMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    base_airport: Any = Field(
        description="The IATA code of the crew member's base airport",
        alias='base_airport'
    )
    aircraft_qualifications: List[Any] = Field(
        description='The aircraft qualifications of the employee',
        alias='aircraft_qualifications'
    )

    @field_serializer("base_airport")
    def serialize_base_airport(self, v):
        return v.code if v else None

    @field_serializer("aircraft_qualifications")
    def serialize_aircraft_qualifications(self, v):
        return [ac.type for ac in v]
