import pytest


class TestCrewMembersEndpoints:

    @pytest.mark.asyncio
    async def test_create_crew_member(self, client, crew_member_seeded_data, db_session):
        ap, a = crew_member_seeded_data
        body = {
            'employee_number': 'E001',
            'first_name': 'Create',
            'last_name': 'Crew',
            'email': 'create@example.com',
            'base_airport': ap.code,
            'aircraft_qualifications': [a.type]
        }

        response = await client.post('/crew_members/', json=body)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_crew_member_missing_fields(self, client, crew_member_seeded_data):
        ap, a = crew_member_seeded_data
        # Missing required field 'employee_number'
        body = {
            'first_name': 'NoEmp',
            'last_name': 'Crew',
            'email': 'noemp@example.com',
            'base_airport': ap.code,
            'aircraft_qualifications': [a.type]
        }
        response = await client.post('/crew_members/', json=body)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_crew_member_invalid_email(self, client, crew_member_seeded_data):
        ap, a = crew_member_seeded_data
        body = {
            'employee_number': 'E002',
            'first_name': 'Bad',
            'last_name': 'Email',
            'email': 'not-an-email',
            'base_airport': ap.code,
            'aircraft_qualifications': [a.type]
        }
        response = await client.post('/crew_members/', json=body)
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_create_crew_member_duplicate_employee_number(self, client, crew_member_seeded_data, db_session):
        ap, a = crew_member_seeded_data
        body = {
            'employee_number': 'E001',
            'first_name': 'Dup',
            'last_name': 'Crew',
            'email': 'dup@example.com',
            'base_airport': ap.code,
            'aircraft_qualifications': [a.type]
        }
        response1 = await client.post('/crew_members/', json=body)
        response2 = await client.post('/crew_members/', json=body)
        assert response2.status_code == 400

    @pytest.mark.asyncio
    async def test_get_crew_members(self, client):
        response = await client.get('/crew_members/')
        data = response.json()

        assert response.status_code == 200
        assert 'data' in data

    @pytest.mark.asyncio
    async def test_update_crew_members(self, client, crew_member_seeded_data):
        response = await client.patch(f"/crew_members/E100", json={'first_name': 'Updated'})

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_nonexistent_crew_member(self, client):
        response = await client.patch('/crew_members/DOESNOTEXIST', json={'first_name': 'Nobody'})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_one_crew_member(self, client, crew_member_seeded_data):
        response = await client.get(f"/crew_members/E100")
        data = response.json()

        user = data.get('data')[0]

        assert user['first_name'] == 'Test'
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_nonexistent_crew_member(self, client):
        response = await client.get('/crew_members/DOESNOTEXIST')
        assert response.status_code == 404