import { FormEvent, useCallback, useEffect, useState } from "react";
import { useApi } from "../api/client";
import { parseApiError } from "../api/parseApiError";
import ErrorDisplay from "../components/ErrorDisplay";

type CrewMember = {
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  base_airport?: string | null;
  aircraft_qualifications?: string[];
};

type CrewMemberListResponse = {
  data: CrewMember[];
  meta?: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
};

export function CrewMembersPage() {
  const { get, post, patch } = useApi();
  const [data, setData] = useState<CrewMemberListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown | null>(null);
  const [page, setPage] = useState(1);

  const [filterBaseAirport, setFilterBaseAirport] = useState("");
  const [filterQualifications, setFilterQualifications] = useState("");

  const [employeeNumber, setEmployeeNumber] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [baseAirport, setBaseAirport] = useState("");
  const [qualificationsInput, setQualificationsInput] = useState("");
  const [creating, setCreating] = useState(false);

  const [editingEmployeeNumber, setEditingEmployeeNumber] = useState<string | null>(null);
  const [editFirstName, setEditFirstName] = useState("");
  const [editLastName, setEditLastName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editBaseAirport, setEditBaseAirport] = useState("");
  const [editQualificationsInput, setEditQualificationsInput] = useState("");
  const [updating, setUpdating] = useState(false);

  const load = useCallback(
    async (showLoading: boolean = true) => {
      if (showLoading) setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        params.append("page", String(page));
        params.append("limit", "10");
        if (filterBaseAirport.trim()) {
          params.append("base_airport", filterBaseAirport.trim());
        }
        const quals = filterQualifications
          .split(",")
          .map((q) => q.trim())
          .filter((q) => q.length > 0);
        for (const q of quals) {
          params.append("qualified_for", q);
        }
        const query = params.toString();
        const url = query ? `/crew_members/?${query}` : "/crew_members/";
        const res = await get<CrewMemberListResponse>(url);
        setData(res);
      } catch (err) {
        setError(parseApiError(err));
      } finally {
        if (showLoading) setLoading(false);
      }
    },
    [get, filterBaseAirport, filterQualifications, page]
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
      const quals = qualificationsInput
        .split(",")
        .map((q) => q.trim())
        .filter((q) => q.length > 0);
      await post("/crew_members/", {
        employee_number: employeeNumber,
        first_name: firstName,
        last_name: lastName,
        email,
        base_airport: baseAirport,
        aircraft_qualifications: quals
      });
      setEmployeeNumber("");
      setFirstName("");
      setLastName("");
      setEmail("");
      setBaseAirport("");
      setQualificationsInput("");
      await load(false);
    } catch (err) {
    setError(parseApiError(err));
    } finally {
      setCreating(false);
    }
  };

  const handleApplyFilters = async () => {
    setPage(1);
    await load();
  };

  const startEdit = (cm: CrewMember) => {
    setEditingEmployeeNumber(cm.employee_number);
    setEditFirstName(cm.first_name);
    setEditLastName(cm.last_name);
    setEditEmail(cm.email);
    setEditBaseAirport(cm.base_airport ?? "");
    setEditQualificationsInput((cm.aircraft_qualifications ?? []).join(", "));
  };

  const cancelEdit = () => {
    setEditingEmployeeNumber(null);
    setEditFirstName("");
    setEditLastName("");
    setEditEmail("");
    setEditBaseAirport("");
    setEditQualificationsInput("");
  };

  const handleUpdate = async (e: FormEvent) => {
    e.preventDefault();
    if (!editingEmployeeNumber || updating) return;
    setError(null);
    setUpdating(true);
    try {
      const quals = editQualificationsInput
        .split(",")
        .map((q) => q.trim())
        .filter((q) => q.length > 0);
      const body: Record<string, unknown> = {};
      if (editFirstName.trim()) body.first_name = editFirstName.trim();
      if (editLastName.trim()) body.last_name = editLastName.trim();
      if (editEmail.trim()) body.email = editEmail.trim();
      if (editBaseAirport.trim()) body.base_airport = editBaseAirport.trim();
      if (quals.length > 0) body.aircraft_qualifications = quals;

      await patch(`/crew_members/${editingEmployeeNumber}`, body);
      cancelEdit();
      await load(false);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setUpdating(false);
    }
  };

  const items = data?.data ?? [];

  return (
    <div className="page">
      <h1>Crew Members</h1>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0, fontSize: "1rem" }}>Create crew member</h2>
        <form className="form-inline" onSubmit={handleCreate}>
          <input
            className="input"
            placeholder="Employee #"
            value={employeeNumber}
            onChange={(e) => setEmployeeNumber(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="First name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="Last name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="Base airport"
            value={baseAirport}
            onChange={(e) => setBaseAirport(e.target.value)}
            required
          />
          <input
            className="input"
            placeholder="Qualifications (comma-separated)"
            value={qualificationsInput}
            onChange={(e) => setQualificationsInput(e.target.value)}
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
            placeholder="Base airport"
            value={filterBaseAirport}
            onChange={(e) => setFilterBaseAirport(e.target.value)}
          />
          <input
            className="input"
            placeholder="Qualifications (comma-separated)"
            value={filterQualifications}
            onChange={(e) => setFilterQualifications(e.target.value)}
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
                    <th>Employee #</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Base</th>
                    <th>Qualifications</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {items.map((cm) => (
                    <tr key={cm.employee_number}>
                      <td>{cm.employee_number}</td>
                      <td>
                        {cm.first_name} {cm.last_name}
                      </td>
                      <td>{cm.email}</td>
                      <td>{cm.base_airport ?? "-"}</td>
                      <td>{cm.aircraft_qualifications?.join(", ") ?? "-"}</td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          type="button"
                          onClick={() => startEdit(cm)}
                        >
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {editingEmployeeNumber && (
                <div className="card" style={{ marginTop: "1rem" }}>
                  <h2 style={{ marginTop: 0, fontSize: "1rem" }}>
                    Edit crew member {editingEmployeeNumber}
                  </h2>
                  <form className="form-inline" onSubmit={handleUpdate}>
                    <input
                      className="input"
                      placeholder="First name"
                      value={editFirstName}
                      onChange={(e) => setEditFirstName(e.target.value)}
                    />
                    <input
                      className="input"
                      placeholder="Last name"
                      value={editLastName}
                      onChange={(e) => setEditLastName(e.target.value)}
                    />
                    <input
                      className="input"
                      placeholder="Email"
                      type="email"
                      value={editEmail}
                      onChange={(e) => setEditEmail(e.target.value)}
                    />
                    <input
                      className="input"
                      placeholder="Base airport"
                      value={editBaseAirport}
                      onChange={(e) => setEditBaseAirport(e.target.value)}
                    />
                    <input
                      className="input"
                      placeholder="Qualifications (comma-separated)"
                      value={editQualificationsInput}
                      onChange={(e) => setEditQualificationsInput(e.target.value)}
                    />
                    <button className="btn btn-primary" type="submit" disabled={updating}>
                      {updating ? "Saving..." : "Save"}
                    </button>
                    <button
                      className="btn btn-secondary"
                      type="button"
                      onClick={cancelEdit}
                      disabled={updating}
                    >
                      Cancel
                    </button>
                  </form>
                </div>
              )}
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
            <div>No crew members found.</div>
          )}
        </>
      )}
    </div>
  );
}

