export function subscribeTicker(onUpdate) {
  const ws = new WebSocket(
    "wss://stream.binance.com:9443/ws/!miniTicker@arr"
  );

  const state = {};

  ws.onmessage = (e) => {
    JSON.parse(e.data).forEach((t) => {
      state[t.s.replace("USDT", "")] = +t.c;
    });
    onUpdate({ ...state });
  };

  return () => ws.close();
}
