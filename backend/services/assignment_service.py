from collections import defaultdict
from typing import Tuple

from fastapi import Response, status

from backend.db.repos.crew_member_repo import CrewMemberRepo
from backend.db.repos.flight_repo import FlightRepo
from backend.db.models import CrewMember, Flight
from backend.exceptions.custom_exceptions import NotFoundException, BadRequestException
from backend.routers.models.assignment.assignment_auto_response import AssignmentAutoResponse, CrewDutySummary, AssignedFlight, UnassignableReason, \
    FailedFlight
from backend.routers.models.assignment.assignment_check_response import ConstraintViolated, Constraints
from backend.routers.models.assignment.assignment_create import AssignmentCreate
from backend.routers.models.assignment.assignment_full_schedule import AssignmentFullSchedule


class AssignmentService:
    def __init__(self, crew_member_repo: CrewMemberRepo, flight_repo: FlightRepo):
        self.crew_member_repo = crew_member_repo
        self.flight_repo = flight_repo

    async def assign_crew_member_to_flight(self, body: AssignmentCreate):
        crew_member = await self.crew_member_repo.get_by_id(body.employee_number, eager_load=[
            CrewMember.aircraft_qualifications,
            CrewMember.flight_assignments
        ])
        if not crew_member:
            raise NotFoundException(f'Crew member with employee number: {body.employee_number} not found')

        flight = await self.flight_repo.get_by_number(body.flight_number, eager_load=[
            Flight.aircraft
        ])
        if not flight:
            raise NotFoundException(f'Flight with number: {body.flight_number} not found')

        result = self._check_constraints(crew_member, flight)
        if result:
            raise NotFoundException(result[0]) if result[1] == status.HTTP_404_NOT_FOUND else BadRequestException(result[0])

        crew_member.flight_assignments.append(flight)
        await self.crew_member_repo.update(crew_member)

        return Response(status_code=status.HTTP_200_OK)

    # async def assign_crew_member_to_flight_second(self, body: AssignmentCreate):
    #     crew_member = await self.crew_member_repo.get_by_id(body.employee_number, eager_load=[
    #         CrewMember.aircraft_qualifications,
    #         CrewMember.flight_assignments
    #     ])
    #     if not crew_member:
    #         raise NotFoundException(f'Crew member with employee number: {body.employee_number} not found')
    #
    #     flight = await self.flight_repo.get_by_number(body.flight_number, eager_load=[
    #         Flight.aircraft
    #     ])
    #     if not flight:
    #         raise NotFoundException(f'Flight with number: {body.flight_number} not found')
    #
    #     if flight in crew_member.flight_assignments:
    #         raise BadRequestException(f'Crew member is already assigned to this flight')
    #
    #     if flight.aircraft not in crew_member.aircraft_qualifications:
    #         raise BadRequestException(f'Crew member does not posses an aircraft qualification for this flight')
    #
    #     if crew_member.flight_assignments:
    #         rest_hours = abs((flight.scheduled_departure - crew_member.flight_assignments[0].scheduled_arrival).total_seconds() / 3600)
    #         if rest_hours < 10:
    #             raise BadRequestException(f"There haven't been 10 hours of rest between flights")
    #
    #     scheduled_departure = flight.scheduled_departure.date().isoformat()
    #     scheduled_arrival = flight.scheduled_arrival.date().isoformat()
    #     if len(flight.duty_hours) == 1 and crew_member.daily_duty_hours[scheduled_departure] + flight.duty_hours[0] > 8:
    #         raise BadRequestException(f'Crew member exceeds daily duty hours (8h)')
    #     elif (
    #             len(flight.duty_hours) == 2
    #             and (crew_member.daily_duty_hours[scheduled_departure] + flight.duty_hours[0] > 8
    #                  or crew_member.daily_duty_hours[scheduled_arrival] + flight.duty_hours[1] > 8)
    #     ):
    #         raise BadRequestException(f'Crew member exceeds daily duty hours (8h)')
    #
    #     if any(self.overlaps(f, flight) for f in crew_member.flight_assignments):
    #         raise BadRequestException(f'Departure date times or arrival date times overlap')
    #
    #     crew_member.flight_assignments.append(flight)
    #     await self.crew_member_repo.update(crew_member)
    #
    #     return Response(status_code=status.HTTP_200_OK)

    async def remove_assignment(self, employee_number: str, flight_number: str):
        crew_member = await self.crew_member_repo.get_by_id(employee_number, eager_load=[
            CrewMember.flight_assignments
        ])
        if not crew_member:
            raise NotFoundException(f'Crew member with employee number: {employee_number} not found')

        if not crew_member.flight_assignments:
            raise NotFoundException(f'Crew member is not assigned to any flights')

        flight = await self.flight_repo.get_by_number(flight_number)
        if not flight:
            raise NotFoundException(f'Flight with number: {flight_number} not found')

        if flight not in crew_member.flight_assignments:
            raise NotFoundException(f'Crew member is not assigned to flight with number: {flight_number}')

        await self.crew_member_repo.remove_flight(crew_member, flight)

        return Response(status_code=status.HTTP_200_OK)
    
    async def get_full_schedule_sec(self, employee_number: str) -> dict:
        crew_member = await self.crew_member_repo.get_with_flight_assignments_asc(employee_number)
        if not crew_member:
            raise NotFoundException(f'Crew member with employee number: {employee_number} not found')

        flights = []

        for prev_flight, flight in zip(crew_member.flight_assignments, crew_member.flight_assignments[1:]):
            flights.append(AssignmentFullSchedule(
                number=prev_flight.number,
                from_time=prev_flight.scheduled_departure,
                to=prev_flight.scheduled_arrival,
                rest_time=False
            ))
            flights.append(AssignmentFullSchedule(
                from_time=prev_flight.scheduled_arrival,
                to=flight.scheduled_departure,
            ))

        if crew_member.flight_assignments:
            flights.append(AssignmentFullSchedule(
                number=crew_member.flight_assignments[-1].number,
                from_time=crew_member.flight_assignments[-1].scheduled_departure,
                to=crew_member.flight_assignments[-1].scheduled_arrival,
                rest_time=False
            ))

        return {'data': flights}

    async def get_full_schedule(self, employee_number: str):
        crew_member = await self.crew_member_repo.get_with_flight_assignments_asc(employee_number)
        if not crew_member:
            raise NotFoundException(f'Crew member with employee number: {employee_number} not found')

        flights = []
        prev_flight = None
        for flight_assignment in crew_member.flight_assignments:
            if prev_flight:
                flights.append(
                    AssignmentFullSchedule(
                        from_time=prev_flight.scheduled_arrival,
                        to=flight_assignment.scheduled_departure,
                    ).model_dump(by_alias=True, exclude_none=True)
                )

            flights.append(
                AssignmentFullSchedule(
                    number=flight_assignment.number,
                    from_time=flight_assignment.scheduled_departure,
                    to=flight_assignment.scheduled_arrival,
                    rest_time=False
                )
            )

            prev_flight = flight_assignment

        return {'data': flights}

    # async def check_assignments_second(self):
    #     assigned_crew_members = await self.crew_member_repo.get_all_flight_assignments()
    #     violated_constraints = {}
    #
    #     for crew_member in assigned_crew_members:
    #         crew_member_flights = crew_member.flight_assignments
    #         violated_constraints[crew_member.employee_number] = defaultdict(list)
    #
    #         for flight in crew_member_flights:
    #             for fl in crew_member_flights:
    #                 if flight == fl:
    #                     continue
    #
    #                 rest_hours = (fl.scheduled_departure - flight.scheduled_arrival).total_seconds() / 3600
    #                 if 0 < rest_hours < 10:
    #                     violated_constraints[crew_member.employee_number][flight.number].append(
    #                         f"There haven't been 10 hours of rest between flights {flight.number} - {fl.number}")
    #
    #                 if self.overlaps(flight, fl):
    #                     violated_constraints[crew_member.employee_number][flight.number].append(
    #                         f'Departure date times or arrival date times overlap {flight.number} - {fl.number}')
    #
    #         for flight in crew_member_flights:
    #             f_sd = flight.scheduled_departure.date().isoformat()
    #             f_sa = flight.scheduled_arrival.date().isoformat()
    #
    #             if len(flight.duty_hours) == 1 and crew_member.daily_duty_hours[f_sd] > 8:
    #                 violated_constraints[crew_member.employee_number][flight.number].append(f'Crew member exceeds daily duty hours (8h)')
    #             elif (
    #                     len(flight.duty_hours) == 2
    #                     and (crew_member.daily_duty_hours[f_sd] > 8
    #                          or crew_member.daily_duty_hours[f_sa] > 8)
    #             ):
    #                 violated_constraints[crew_member.employee_number][flight.number].append(f'Crew member exceeds daily duty hours (8h)')
    #
    #             flight_with_aircraft = await self.flight_repo.get_by_number(flight.number, eager_load=[Flight.aircraft])
    #             if flight_with_aircraft.aircraft not in crew_member.aircraft_qualifications:
    #                 violated_constraints[crew_member.employee_number][flight.number].append('Does not posses an aircraft '
    #                                                                                         'qualification for this flight')
    #
    #     return {'data': violated_constraints}

    async def check_assignments(self) -> dict:
        assigned_crew_members = await self.crew_member_repo.get_all_flight_assignments()
        violated_constraints = {}

        for crew_member in assigned_crew_members:
            violated_constraints[crew_member.employee_number] = defaultdict(list)

            for flight in crew_member.flight_assignments:
                flight_with_aircraft = await self.flight_repo.get_by_number(flight.number, eager_load=[Flight.aircraft])
                result = self._check_constraints(crew_member, flight_with_aircraft, skip_check=True)
                if result:
                    violated_constraints[crew_member.employee_number][flight.number].append(result[0])

        violated = [
            ConstraintViolated(
                employee_number=k,
                constraints=[
                    Constraints(
                        flight_number=fn,
                        violations=message
                    ) for fn, message in v.items()
                ]
            ) for k, v in violated_constraints.items()
        ]

        return {'data': violated}

    async def auto_assign_flights(self):
        # fetch all crew and flights (raise limit to cover full dataset)
        all_crew, _ = await self.crew_member_repo.get_all(eager_load=[
            CrewMember.aircraft_qualifications,
            CrewMember.flight_assignments
        ], limit=1000)

        flights_all, _ = await self.flight_repo.get_all(eager_load=[Flight.aircraft, Flight.crew_members], limit=1000)
        # sort flights chronologically
        flights_all.sort(key=lambda f: f.scheduled_departure)

        assigned = []
        reasons_for_failure = defaultdict(list)

        # We'll attempt to assign each crew member to as many flights as they can,
        # prioritizing the least-busy crew to improve fairness. Iterate until
        # no further assignments are possible.
        progress = True
        while progress:
            progress = False

            # sort crew by current total duty hours (least busy first)
            crew_order = sorted(all_crew, key=self.total_hours)

            for crew in crew_order:
                # try to assign this crew to any flight they are not already assigned to
                for flight in flights_all:
                    if flight in crew.flight_assignments:
                        continue

                    # check constraints for this candidate and flight
                    reason = self._check_constraints(crew, flight)
                    if reason is None:
                        # eligible: assign and persist
                        crew.flight_assignments.append(flight)
                        await self.crew_member_repo.update(crew)
                        assigned.append(AssignedFlight(
                            flight_number=flight.number,
                            assigned_to=crew.employee_number,
                            name=f"{crew.first_name} {crew.last_name}"
                        ))
                        progress = True
                        # continue attempting to add more flights to the same crew
                        continue
                    else:
                        # record why this crew couldn't be assigned to this flight
                        reasons_for_failure[flight.number].append(UnassignableReason(
                            employee_number=crew.employee_number,
                            reason=reason[0]
                        ))

        # Build duty summary for response
        duty_summary = [
            CrewDutySummary(
                employee_number=crew.employee_number,
                name=crew.full_name,
                total_duty_hours=sum(sum(f.duty_hours) for f in crew.flight_assignments)
            )
            for crew in all_crew
        ]

        hours_list = [d.total_duty_hours for d in duty_summary]
        fairness_gap = round(max(hours_list) - min(hours_list), 2) if hours_list else 0
        failed = [
            FailedFlight(
                flight_number=flight_number,
                unassignable_reasons=reasons_for_failure[flight_number]
            ) for flight_number in reasons_for_failure.keys()
        ]

        return AssignmentAutoResponse(
            assigned=assigned,
            failed=failed,
            duty_summary=duty_summary,
            fairness_gap_hours=fairness_gap
        )

    @staticmethod
    def total_hours(crew_member: CrewMember) -> int:
        return sum(crew_member.daily_duty_hours.values())

    @staticmethod
    def overlaps(existing: Flight, candidate: Flight) -> bool:
        return not (
            existing.scheduled_arrival < candidate.scheduled_departure
            or candidate.scheduled_arrival < existing.scheduled_departure
        ) and existing != candidate

    def _check_constraints(self, crew_member: CrewMember, flight: Flight, skip_check: bool = False) -> Tuple[str, int] | None:
        """
        Checks all hard constraints for assigning a crew member to a flight.
        Returns None if eligible, or a string reason if not.
        """

        if not skip_check and flight in crew_member.flight_assignments:
            return "Already assigned to this flight", status.HTTP_400_BAD_REQUEST

        if flight.aircraft not in crew_member.aircraft_qualifications:
            return f"Not qualified for aircraft type", status.HTTP_404_NOT_FOUND

        # Rest period check — must check against ALL existing assignments, not just index 0
        for assigned_flight in crew_member.flight_assignments:
            rest_after = (flight.scheduled_departure - assigned_flight.scheduled_arrival).total_seconds() / 3600
            rest_before = (assigned_flight.scheduled_departure - flight.scheduled_arrival).total_seconds() / 3600

            # The new flight departs after this one ends
            if 0 < rest_after < 10:
                return f"Insufficient rest period after flight {assigned_flight.number} ({rest_after:.1f}h < 10h)", 400

            # The new flight arrives before this one departs
            if 0 < rest_before < 10:
                return f"Insufficient rest period before flight {assigned_flight.number} ({rest_before:.1f}h < 10h)", 400

        # Daily duty limit check
        scheduled_departure = flight.scheduled_departure.date().isoformat()
        scheduled_arrival = flight.scheduled_arrival.date().isoformat()

        if len(flight.duty_hours) == 1:
            daily_duty_hours = crew_member.daily_duty_hours[scheduled_departure] + flight.duty_hours[0] if not skip_check else (
                crew_member.daily_duty_hours)[scheduled_departure]
            if daily_duty_hours > 8:
                return f"Would exceed 8h daily duty limit on {scheduled_departure}", status.HTTP_400_BAD_REQUEST

        elif len(flight.duty_hours) == 2:
            daily_duty_hours_1 = crew_member.daily_duty_hours[scheduled_departure] + flight.duty_hours[0] if not skip_check else (
                crew_member.daily_duty_hours)[scheduled_departure]
            daily_duty_hours_2 = crew_member.daily_duty_hours[scheduled_arrival] + flight.duty_hours[1] if not skip_check else (
                crew_member.daily_duty_hours)[scheduled_arrival]

            if daily_duty_hours_1 > 8:
                return f"Would exceed 8h daily duty limit on {scheduled_departure}", status.HTTP_400_BAD_REQUEST
            if daily_duty_hours_2 > 8:
                return f"Would exceed 8h daily duty limit on {scheduled_arrival}", status.HTTP_400_BAD_REQUEST

        if any(self.overlaps(f, flight) for f in crew_member.flight_assignments):
            return "Overlaps with an existing flight assignment", status.HTTP_400_BAD_REQUEST

        return None
