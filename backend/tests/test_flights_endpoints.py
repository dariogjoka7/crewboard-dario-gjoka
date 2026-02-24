import pytest
from datetime import datetime, timedelta, timezone


class TestFlightEndpoints:

    @pytest.mark.asyncio
    async def test_create_and_list_flight(self, client, flights_data, db_session):
        ap, ap2, a = flights_data

        now = datetime.now(timezone.utc) + timedelta(days=2)
        body = {
            'number': 'FL100',
            'departure_airport': ap.code,
            'arrival_airport': ap2.code,
            'aircraft': a.type,
            'scheduled_departure': now.isoformat(),
            'scheduled_arrival': (now + timedelta(hours=2)).isoformat()
        }

        response = await client.post('/flights/', json=body)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_flights(self, client, db_session):
        response = await client.get('/flights/')
        data = response.json()

        assert response.status_code == 200
        assert 'data' in data

    @pytest.mark.asyncio
    async def test_create_flight_missing_fields(self, client, flights_data):
        ap, ap2, a = flights_data
        now = datetime.now(timezone.utc) + timedelta(days=2)
        body = {
            'departure_airport': ap.code,
            'arrival_airport': ap2.code,
            'aircraft': a.type,
            'scheduled_departure': now.isoformat(),
            'scheduled_arrival': (now + timedelta(hours=2)).isoformat()
        }
        response = await client.post('/flights/', json=body)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_flight_invalid_airport(self, client, flights_data):
        ap, ap2, a = flights_data
        now = datetime.now(timezone.utc) + timedelta(days=2)
        body = {
            'number': 'FL101',
            'departure_airport': 'INVALID',
            'arrival_airport': ap2.code,
            'aircraft': a.type,
            'scheduled_departure': now.isoformat(),
            'scheduled_arrival': (now + timedelta(hours=2)).isoformat()
        }
        response = await client.post('/flights/', json=body)
        assert response.status_code in (400, 422, 404)

    @pytest.mark.asyncio
    async def test_create_flight_duplicate_number(self, client, flights_data, db_session):
        ap, ap2, a = flights_data
        now = datetime.now(timezone.utc) + timedelta(days=2)
        body = {
            'number': 'FL100',
            'departure_airport': ap.code,
            'arrival_airport': ap2.code,
            'aircraft': a.type,
            'scheduled_departure': now.isoformat(),
            'scheduled_arrival': (now + timedelta(hours=2)).isoformat()
        }
        await client.post('/flights/', json=body)
        response2 = await client.post('/flights/', json=body)

        assert response2.status_code == 400

    @pytest.mark.asyncio
    async def test_get_nonexistent_flight(self, client):
        response = await client.get('/flights/DOESNOTEXIST')
        assert response.status_code == 404
