export function getApiErrorMessage(error, fallback = 'Something went wrong') {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((entry) => entry?.msg || entry).join(', ');
  }
  const message = error?.message;
  if (typeof message === 'string' && message.trim()) {
    return message;
  }
  return fallback;
}
