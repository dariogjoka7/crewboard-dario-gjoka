import { FormEvent, useCallback, useEffect, useState } from "react";
import { useApi } from "../api/client";
import { parseApiError } from "../api/parseApiError";
import ErrorDisplay from "../components/ErrorDisplay";

type Flight = {
  number: string;
  departure_airport: string;
  arrival_airport: string;
  scheduled_departure?: string;
  scheduled_arrival?: string;
  aircraft?: string;
};

type FlightListResponse = {
  data: Flight[];
  meta?: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
};

export function FlightsPage() {
  const { get, post } = useApi();
  const [data, setData] = useState<FlightListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown | null>(null);

  const [filterDepartureAfter, setFilterDepartureAfter] = useState("");
  const [filterArrivalBefore, setFilterArrivalBefore] = useState("");
  const [filterDepartureAirport, setFilterDepartureAirport] = useState("");
  const [filterAircraftType, setFilterAircraftType] = useState("");

  const [number, setNumber] = useState("");
  const [departureAirport, setDepartureAirport] = useState("");
  const [arrivalAirport, setArrivalAirport] = useState("");
  const [aircraft, setAircraft] = useState("");
  const [scheduledDeparture, setScheduledDeparture] = useState("");
  const [scheduledArrival, setScheduledArrival] = useState("");
  const [creating, setCreating] = useState(false);
  const [page, setPage] = useState(1);

  // Applied filters (used for querying); the filter* states above are editable inputs.
  const [appliedDepartureAfter, setAppliedDepartureAfter] = useState("");
  const [appliedArrivalBefore, setAppliedArrivalBefore] = useState("");
  const [appliedDepartureAirport, setAppliedDepartureAirport] = useState("");
  const [appliedAircraftType, setAppliedAircraftType] = useState("");

  // Convert a local datetime input (YYYY-MM-DDTHH:mm) to a UTC ISO string
  // that the backend expects, e.g. "2026-02-01T06:00:00Z".
  const toUtcIsoOrUndefined = (value: string) => {
    if (!value) return undefined;
    // Ensure we always send seconds and Z suffix so it matches the backend's normalized UTC datetimes
    // (the backend validator already sets tzinfo=UTC and zeroes seconds).
    const base = value.trim(); // "YYYY-MM-DDTHH:mm"
    if (!base) return undefined;
    return `${base}:00Z`;
  };

  const formatDateTimeDisplay = (dateString?: string) => {
    if (!dateString) return "-";
    try {
      return new Date(dateString).toLocaleString("en-US");
    } catch {
      return dateString;
    }
  };

  const load = useCallback(
    async (showLoading: boolean = true) => {
      if (showLoading) setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        params.append("page", String(page));
        params.append("limit", "10");
        const dep = toUtcIsoOrUndefined(appliedDepartureAfter);
        const arr = toUtcIsoOrUndefined(appliedArrivalBefore);
        if (dep) params.append("scheduled_departure", dep);
        if (arr) params.append("scheduled_arrival", arr);
        if (appliedDepartureAirport.trim()) params.append("departure_airport", appliedDepartureAirport.trim());
        if (appliedAircraftType.trim()) params.append("aircraft_type", appliedAircraftType.trim());
        const query = params.toString();
        const url = query ? `/flights/?${query}` : "/flights/";
        const res = await get<FlightListResponse>(url);
        setData(res);
      } catch (err) {
        setError(parseApiError(err));
      } finally {
        if (showLoading) setLoading(false);
      }
    },
    [get, appliedDepartureAfter, appliedArrivalBefore, appliedDepartureAirport, appliedAircraftType, page]
  );

  useEffect(() => {
    void load();
  }, [load]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    if (creating) return;
    setError(null);
    setCreating(true);
    try {
      const depIso = toUtcIsoOrUndefined(scheduledDeparture);
      const arrIso = toUtcIsoOrUndefined(scheduledArrival);
      await post("/flights/", {
        number,
        departure_airport: departureAirport,
        arrival_airport: arrivalAirport,
        aircraft,
        scheduled_departure: depIso,
        scheduled_arrival: arrIso
      });
      setNumber("");
      setDepartureAirport("");
      setArrivalAirport("");
      setAircraft("");
      setScheduledDeparture("");
      setScheduledArrival("");
      await load(false);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setCreating(false);
    }
  };

  const handleApplyFilters = () => {
    setPage(1);
    setAppliedDepartureAfter(filterDepartureAfter);
    setAppliedArrivalBefore(filterArrivalBefore);
    setAppliedDepartureAirport(filterDepartureAirport);
    setAppliedAircraftType(filterAircraftType);
  };

  const items = (data?.data ?? []).filter((f) => {
    const depTime = f.scheduled_departure ? new Date(f.scheduled_departure) : null;
    const arrTime = f.scheduled_arrival ? new Date(f.scheduled_arrival) : null;

    if (appliedDepartureAfter) {
      const filterDepIso = toUtcIsoOrUndefined(appliedDepartureAfter);
      const after = filterDepIso ? new Date(filterDepIso) : null;
      if (!depTime || !after || depTime < after) return false;
    }

    if (appliedArrivalBefore) {
      const filterArrIso = toUtcIsoOrUndefined(appliedArrivalBefore);
      const before = filterArrIso ? new Date(filterArrIso) : null;
      if (!arrTime || !before || arrTime > before) return false;
    }

    return true;
  });

  return (
    <div className="page">
      <h1>Flights</h1>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0, fontSize: "1rem" }}>Create flight</h2>
        <form className="form-inline" onSubmit={handleCreate}>
          <input
            className="input"
            placeholder="Number"
            value={number}
            onChange={(e) => setNumber(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="Departure airport"
            value={departureAirport}
            onChange={(e) => setDepartureAirport(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="Arrival airport"
            value={arrivalAirport}
            onChange={(e) => setArrivalAirport(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="Aircraft type"
            value={aircraft}
            onChange={(e) => setAircraft(e.target.value)}
            required
          />
          <input
            className="input"
            type="datetime-local"
            value={scheduledDeparture}
            onChange={(e) => setScheduledDeparture(e.target.value)}
            required
          />
          <input
            className="input"
            type="datetime-local"
            value={scheduledArrival}
            onChange={(e) => setScheduledArrival(e.target.value)}
            required
          />
          <button className="btn btn-primary" type="submit" disabled={creating}>
            {creating ? "Creating..." : "Create"}
          </button>
        </form>
      </div>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0, fontSize: "1rem" }}>Filters</h2>
        <div className="form-inline">
          <input
            className="input"
            type="datetime-local"
            value={filterDepartureAfter}
            onChange={(e) => setFilterDepartureAfter(e.target.value)}
          />
          <input
            className="input"
            type="datetime-local"
            value={filterArrivalBefore}
            onChange={(e) => setFilterArrivalBefore(e.target.value)}
          />
          <input
            className="input"
            placeholder="Departure airport"
            value={filterDepartureAirport}
            onChange={(e) => setFilterDepartureAirport(e.target.value)}
          />
          <input
            className="input"
            placeholder="Aircraft type"
            value={filterAircraftType}
            onChange={(e) => setFilterAircraftType(e.target.value)}
          />
          <button className="btn btn-secondary" type="button" onClick={handleApplyFilters}>
            Apply filters
          </button>
        </div>
      </div>

      {loading && <div>Loading...</div>}
      <ErrorDisplay error={error} />
      {!loading && (
        <>
          {items.length > 0 ? (
            <>
              <table className="table">
                <thead>
                  <tr>
                    <th>Number</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Departure</th>
                    <th>Arrival</th>
                    <th>Aircraft</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((f) => (
                    <tr key={f.number}>
                      <td>{f.number}</td>
                      <td>{f.departure_airport}</td>
                      <td>{f.arrival_airport}</td>
                      <td>{formatDateTimeDisplay(f.scheduled_departure)}</td>
                      <td>{formatDateTimeDisplay(f.scheduled_arrival)}</td>
                      <td>{f.aircraft ?? "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="pagination">
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                >
                  ← Prev
                </button>
                <span className="pagination-info">
                  Page {data?.meta?.page ?? page} of {data?.meta?.total_pages ?? "?"}
                </span>
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() => {
                    const totalPages = data?.meta?.total_pages ?? page;
                    setPage((p) => (p < totalPages ? p + 1 : p));
                  }}
                  disabled={data?.meta?.total_pages !== undefined ? page >= data.meta.total_pages : false}
                >
                  Next →
                </button>
              </div>
            </>
          ) : (
            <div>No flights found.</div>
          )}
        </>
      )}
    </div>
  );
}

