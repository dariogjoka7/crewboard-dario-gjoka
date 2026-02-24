import pytest

from backend.db.repos.crew_member_repo import CrewMemberRepo
from backend.db.repos.flight_repo import FlightRepo
from backend.services.assignment_service import AssignmentService


class TestAssignmentEndpoints:

    @pytest.mark.asyncio
    async def test_create_assignment(self, client, assignments_data):
        body = {
            'employee_number': 'E200',
            'flight_number': 'A1',
        }
        response = await client.post('/assignments/', json=body)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_assignment_missing_fields(self, client):
        body = {'flight_id': 1}
        response = await client.post('/assignments/', json=body)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_assignment_invalid_crew_member(self, client):
        body = {'crew_member_id': 9999, 'flight_id': 1}
        response = await client.post('/assignments/', json=body)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_auto_assign(self, client, assignments_data):
        r = await client.post('/assignments/auto/')
        data = r.json()

        assert r.status_code == 200
        assert isinstance(data.get('assigned'), list)
        assert len(data.get('assigned')) == 2
        assert data.get('failed') == []

    @pytest.mark.asyncio
    async def test_healthcheck(self, client, assignments_data):
        # run healthcheck - expect no violations (constraints lists empty)
        hr = await client.get('/assignments/healthcheck/')
        assert hr.status_code == 200
        hdata = hr.json()
        assert isinstance(hdata.get('data'), list)

        for item in hdata.get('data'):
            assert 'constraints' in item
            assert item['constraints'] == []

    @pytest.mark.asyncio
    async def test_rest_period_violation(self, assignment_data_second, db_session):
        cm, f2 = assignment_data_second
        crew_repo = CrewMemberRepo(db_session)
        flight_repo = FlightRepo(db_session)
        service = AssignmentService(crew_repo, flight_repo)

        reason = service._check_constraints(cm, f2)
        assert reason is not None
        assert 'Insufficient rest period' in reason[0]

    @pytest.mark.asyncio
    async def test_already_assiged_to_this_flight(self, assignment_data_third, db_session):
        cm, f = assignment_data_third
        crew_repo = CrewMemberRepo(db_session)
        flight_repo = FlightRepo(db_session)
        service = AssignmentService(crew_repo, flight_repo)

        reason = service._check_constraints(cm, f)
        assert reason is not None
        assert 'Already assigned to this flight' in reason[0]
