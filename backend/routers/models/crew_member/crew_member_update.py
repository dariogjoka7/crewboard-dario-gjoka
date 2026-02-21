from typing import List

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CrewMemberUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    first_name: str | None = Field(
        default=None,
        examples=['John'],
        description='The first name of the crew member'
    )
    last_name: str | None = Field(
        default=None,
        examples=['Doe'],
        description='The last name of the crew member'
    )
    email: EmailStr | None = Field(
        default=None,
        examples=['johndoe@example.com'],
        description='The email address of the crew member'
    )
    base_airport: str | None = Field(
        default=None,
        examples=['FR'],
        description="The IATA code of the crew member's base airport"
    )
    aircraft_qualifications: List[str] | None = Field(
        default=None,
        examples=[['A320']],
        description='The aircraft qualifications of the employee',
        min_length=1
    )