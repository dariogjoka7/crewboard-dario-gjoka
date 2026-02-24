import React from "react";

export default function ErrorDisplay({ error }: { error: unknown }) {
  if (!error) return null;

  if (typeof error === "string") {
    return <div className="error-text">{error}</div>;
  }

  if (Array.isArray(error)) {
    return (
      <div className="error-text">
        {error.map((e, i) => (
          <div key={i}>{typeof e === "string" ? e : JSON.stringify(e)}</div>
        ))}
      </div>
    );
  }

  // object
  try {
    return <div className="error-text">{JSON.stringify(error)}</div>;
  } catch {
    return <div className="error-text">An error occurred</div>;
  }
}
