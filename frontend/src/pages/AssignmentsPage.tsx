import { FormEvent, useState } from "react";
import { useApi } from "../api/client";
import { parseApiError } from "../api/parseApiError";
import ErrorDisplay from "../components/ErrorDisplay";

type AssignmentCreate = {
  employee_number: string;
  flight_number: string;
};

type AssignedFlight = {
  flight_number: string;
  assigned_to: string;
  name: string;
};

type UnassignableReason = {
  employee_number: string;
  reason: string;
};

type FailedFlight = {
  flight_number: string;
  unassignable_reasons: UnassignableReason[];
};

type CrewDutySummary = {
  employee_number: string;
  name: string;
  total_duty_hours: number;
};

type AutoAssignResponse = {
  assigned: AssignedFlight[];
  failed: FailedFlight[];
  duty_summary: CrewDutySummary[];
  fairness_gap_hours: number;
};

type ConstraintViolation = {
  flight_number: string;
  violations: string[];
};

type CrewConstraint = {
  employee_number: string;
  constraints: ConstraintViolation[];
};

type HealthcheckResponse = {
  data: CrewConstraint[];
};

type FlightAssignment = {
  number: string;
  scheduled_departure: string;
  scheduled_arrival: string;
};

type FullScheduleItem = {
  number?: string;
  from: string;
  to: string;
  rest_time: boolean;
};

type FullScheduleResponse = {
  data: FullScheduleItem[];
};

export function AssignmentsPage() {
  const api = useApi();
  const [employeeNumber, setEmployeeNumber] = useState("");
  const [flightNumber, setFlightNumber] = useState("");
  const [error, setError] = useState<unknown | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoAssignResult, setAutoAssignResult] = useState<AutoAssignResponse | null>(null);
  const [healthcheckResult, setHealthcheckResult] = useState<HealthcheckResponse | null>(null);
  const [expandedFailedFlight, setExpandedFailedFlight] = useState<string | null>(null);
  const [fullSchedule, setFullSchedule] = useState<FullScheduleResponse | null>(null);
  const [scheduleEmployeeNumber, setScheduleEmployeeNumber] = useState("");
  const [activeTab, setActiveTab] = useState<'healthcheck' | 'autoassign' | 'fullschedule'>('healthcheck');

  const handleAssign = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const body: AssignmentCreate = { employee_number: employeeNumber, flight_number: flightNumber };
    try {
      await api.post("/assignments/", body);
      setEmployeeNumber("");
      setFlightNumber("");
      setAutoAssignResult(null);
      setHealthcheckResult(null);

      setFullSchedule(null);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setError(null);
    setLoading(true);
    const params = new URLSearchParams({
      employee_number: employeeNumber,
      flight_number: flightNumber
    });
    try {
      await api.del(`/assignments/?${params.toString()}`);
      setEmployeeNumber("");
      setFlightNumber("");
      setAutoAssignResult(null);
      setHealthcheckResult(null);
      setFullSchedule(null);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleHealthcheck = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await api.get<HealthcheckResponse>("/assignments/healthcheck/");
      setHealthcheckResult(res);
      setAutoAssignResult(null);
      setFullSchedule(null);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleAutoAssign = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<AutoAssignResponse>("/assignments/auto/", {});
      setAutoAssignResult(res);
      setHealthcheckResult(null);
      setFullSchedule(null);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleViewFullSchedule = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.get<FullScheduleResponse>(
        `/assignments/${scheduleEmployeeNumber}`
      );
      setFullSchedule(res);
      setAutoAssignResult(null);
      setHealthcheckResult(null);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="page">
      <h1>Assignments</h1>

      <form onSubmit={handleAssign} className="form-inline">
            <input
              className="input"
              placeholder="Employee #"
              value={employeeNumber}
              onChange={(e) => setEmployeeNumber(e.target.value)}
              required
            />
            <input
              className="input"
              placeholder="Flight #"
              value={flightNumber}
              onChange={(e) => setFlightNumber(e.target.value)}
              required
            />
            <button className="btn btn-primary" type="submit" disabled={loading}>
              Assign
            </button>
            <button className="btn btn-secondary" type="button" onClick={handleDelete} disabled={loading}>
              Delete
            </button>
          </form>

      <div className="tabs-header">
        <button
          className={`tab-button ${activeTab === 'healthcheck' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('healthcheck')}
        >
          Healthcheck
        </button>
        <button
          className={`tab-button ${activeTab === 'autoassign' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('autoassign')}
        >
          Auto assign
        </button>
        <button
          className={`tab-button ${activeTab === 'fullschedule' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('fullschedule')}
        >
          View Full Schedule
        </button>
      </div>

      {activeTab === 'healthcheck' && (
        <>
          <button className="btn" type="button" onClick={handleHealthcheck} disabled={loading}>
            Run Healthcheck
          </button>

          {loading && <div>Working...</div>}
          <ErrorDisplay error={error} />

          {healthcheckResult && (
            <div className="results-container">
              <div className="card">
                <h2>Healthcheck Results</h2>
                {healthcheckResult.data.every((crew) => crew.constraints.length === 0) ? (
                  <div className="status-all-clear">✓ All assignments are valid</div>
                ) : (
                  <div className="status-violations-found">
                    ⚠ Constraint violations found
                  </div>
                )}
              </div>

              <div className="card">
                <h2>Crew Assignment Status</h2>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Employee #</th>
                      <th>Status</th>
                      <th>Violations</th>
                    </tr>
                  </thead>
                  <tbody>
                    {healthcheckResult.data.map((crew) => (
                      <tr
                        key={crew.employee_number}
                        className={crew.constraints.length > 0 ? "row-warning" : ""}
                      >
                        <td>{crew.employee_number}</td>
                        <td>
                          <span
                            className={
                              crew.constraints.length === 0
                                ? "status-badge status-ok"
                                : "status-badge status-error"
                            }
                          >
                            {crew.constraints.length === 0 ? "✓ Valid" : "✗ Violations"}
                          </span>
                        </td>
                        <td>
                          {crew.constraints.length > 0 ? (
                            <div className="violations-list">
                              {crew.constraints.map((constraint) => (
                                <div key={constraint.flight_number} className="violation-item">
                                  <strong>{constraint.flight_number}:</strong>{" "}
                                  {constraint.violations.join(", ")}
                                </div>
                              ))}
                            </div>
                          ) : (
                            "-"
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {activeTab === 'autoassign' && (
        <>
          <button className="btn" type="button" onClick={handleAutoAssign} disabled={loading}>
            Run Auto assign
          </button>

          {loading && <div>Working...</div>}
          <ErrorDisplay error={error} />

          {autoAssignResult && (
            <div className="results-container">
              <div className="card">
                <h2>Auto Assign Summary</h2>
                <div className="summary-stats">
                  <div className="stat-item">
                    <span className="stat-label">Assignments Success:</span>
                    <span className="stat-value">{autoAssignResult.assigned.length}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Flights Failed:</span>
                    <span className="stat-value">{autoAssignResult.failed.length}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Fairness Gap:</span>
                    <span className="stat-value">{autoAssignResult.fairness_gap_hours}h</span>
                  </div>
                </div>
              </div>

              {autoAssignResult.assigned.length > 0 && (
                <div className="card">
                  <h2>Successfully Assigned Flights</h2>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Flight #</th>
                        <th>Assigned To</th>
                        <th>Crew Name</th>
                      </tr>
                    </thead>
                    <tbody>
                      {autoAssignResult.assigned.map((flight) => (
                        <tr key={flight.flight_number}>
                          <td>{flight.flight_number}</td>
                          <td>{flight.assigned_to}</td>
                          <td>{flight.name}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="card">
                <h2>Duty Summary</h2>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Employee #</th>
                      <th>Name</th>
                      <th>Total Duty Hours</th>
                    </tr>
                  </thead>
                  <tbody>
                    {autoAssignResult.duty_summary.map((crew) => (
                      <tr key={crew.employee_number}>
                        <td>{crew.employee_number}</td>
                        <td>{crew.name}</td>
                        <td>{crew.total_duty_hours}h</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {autoAssignResult.failed.length > 0 && (
                <div className="card">
                  <h2>Failed Assignments</h2>
                  <div className="failed-flights-container">
                    {autoAssignResult.failed.map((flight) => (
                      <div key={flight.flight_number} className="failed-flight-item">
                        <button
                          className="failed-flight-header"
                          onClick={() =>
                            setExpandedFailedFlight(
                              expandedFailedFlight === flight.flight_number ? null : flight.flight_number
                            )
                          }
                        >
                          <span className="flight-number">Flight {flight.flight_number}</span>
                          <span className="reason-count">
                            {flight.unassignable_reasons.length} reasons
                          </span>
                          <span className="expand-icon">
                            {expandedFailedFlight === flight.flight_number ? "▼" : "▶"}
                          </span>
                        </button>
                        {expandedFailedFlight === flight.flight_number && (
                          <div className="failed-flight-details">
                            <table className="table">
                              <thead>
                                <tr>
                                  <th>Employee #</th>
                                  <th>Reason</th>
                                </tr>
                              </thead>
                              <tbody>
                                {flight.unassignable_reasons.map((reason) => (
                                  <tr key={reason.employee_number}>
                                    <td>{reason.employee_number}</td>
                                    <td>{reason.reason}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {activeTab === 'fullschedule' && (
        <>
          <div className="card" style={{ marginBottom: "1rem" }}>
            <h2 style={{ marginTop: 0, fontSize: "1rem" }}>View Full Schedule</h2>
            <form onSubmit={handleViewFullSchedule} className="form-inline">
              <input
                className="input"
                placeholder="Employee #"
                value={scheduleEmployeeNumber}
                onChange={(e) => setScheduleEmployeeNumber(e.target.value)}
                required
              />
              <button className="btn btn-primary" type="submit" disabled={loading}>
                View Schedule
              </button>
            </form>
          </div>

          {loading && <div>Working...</div>}
          <ErrorDisplay error={error} />

          {fullSchedule && (
            <div className="results-container">
              <div className="card">
                <h2>Full Schedule for {scheduleEmployeeNumber}</h2>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Flight #</th>
                      <th>Start Time</th>
                      <th>End Time</th>
                      <th>Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fullSchedule.data.map((item, idx) => (
                      <tr key={idx}>
                        <td>{item.number ?? "-"}</td>
                        <td>{formatDateTime(item.from)}</td>
                        <td>{formatDateTime(item.to)}</td>
                        <td>
                          <span className={item.rest_time ? "badge-rest" : "badge-duty"}>
                            {item.rest_time ? "Rest" : "Duty"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

