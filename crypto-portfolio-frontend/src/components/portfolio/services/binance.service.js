import axios from "axios";
import crypto from "crypto-js";

const api = axios.create({ baseURL: "https://api.binance.com" });
const KEY = import.meta.env.VITE_BINANCE_KEY;
const SECRET = import.meta.env.VITE_BINANCE_SECRET;

function sign(params) {
  const qs = new URLSearchParams(params).toString();
  const sig = crypto.HmacSHA256(qs, SECRET).toString();
  return { ...params, signature: sig };
}

export const getBinanceBalances = async () => {
  const params = sign({ timestamp: Date.now() });
  const { data } = await api.get("/api/v3/account", {
    params,
    headers: { "X-MBX-APIKEY": KEY },
  });
  return data.balances
    .filter((b) => +b.free + +b.locked > 0)
    .map((b) => ({ symbol: b.asset, qty: +b.free }));
};

export const placeBinanceOrder = async (side, symbol, qty) => {
  const params = sign({
    symbol: symbol + "USDT",
    side,
    type: "MARKET",
    quantity: qty,
    timestamp: Date.now(),
  });
  await api.post("/api/v3/order", null, {
    params,
    headers: { "X-MBX-APIKEY": KEY },
  });
};
