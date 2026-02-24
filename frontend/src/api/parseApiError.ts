export function parseApiError(err: unknown): string | string[] | Record<string, any> {
  if (!err) return "Unknown error";

  if (err instanceof Error) {
    const msg = err.message || "";
    try {
      const parsed = JSON.parse(msg);
      if (parsed && typeof parsed === "object") {
        if (typeof parsed.detail === "string") return parsed.detail;
        return parsed;
      }
    } catch {
    }
    return msg;
  }

  try {
    return JSON.parse(String(err));
  } catch {
    return String(err);
  }
}
