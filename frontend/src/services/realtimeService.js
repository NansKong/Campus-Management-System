function toWsBaseUrl() {
  const apiBase = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000/api';
  const wsBase = apiBase.replace(/^http/i, 'ws');
  return wsBase.replace(/\/api\/?$/i, '');
}

export function connectFoodRushSocket({ token, vendorId, onMessage, onError, onClose }) {
  const base = toWsBaseUrl();
  const query = new URLSearchParams({ token });
  if (vendorId) {
    query.set('vendor_id', String(vendorId));
  }

  const socket = new WebSocket(`${base}/api/realtime/ws/food-rush?${query.toString()}`);

  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      onMessage?.(payload);
    } catch (error) {
      onError?.(error);
    }
  };

  socket.onerror = (event) => onError?.(event);
  socket.onclose = (event) => onClose?.(event);

  return socket;
}
