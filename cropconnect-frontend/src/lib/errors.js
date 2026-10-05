export function getReadableError(error, status) {
  const message = typeof error === "string" ? error : error?.message || "";
  const inferredStatus = Number(status || error?.status || error?.response?.status || message.match(/\b(401|403|429|500|503)\b/)?.[1]);

  if (inferredStatus === 401 || inferredStatus === 403) {
    return "Session expired. Please log in again.";
  }
  if (inferredStatus === 429) {
    return "Too many requests — please wait a moment.";
  }
  if (inferredStatus === 500 || inferredStatus === 503) {
    return "Server error. We're looking into it.";
  }
  if (
    error instanceof TypeError ||
    /failed to fetch|network|load failed|couldn't fetch|connection/i.test(message)
  ) {
    return "Couldn't load data. Check your connection.";
  }
  return "Something went wrong. Please try again.";
}
