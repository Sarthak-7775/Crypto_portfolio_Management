import axios from "axios";
import crypto from "crypto-js";

const KEY = import.meta.env.VITE_COINDCX_KEY;
const SECRET = import.meta.env.VITE_COINDCX_SECRET;
const api = axios.create({ baseURL: "https://api.coindcx.com" });

function hdr(body) {
  return {
    "X-AUTH-APIKEY": KEY,
    "X-AUTH-SIGNATURE": crypto.HmacSHA256(
      JSON.stringify(body),
      SECRET
    ).toString(),
  };
}

export const getCoinDCXBalances = async () => {
  const { data } = await api.post("/exchange/v1/users/balances", {}, { headers: hdr({}) });
  return data
    .filter((b) => +b.balance > 0)
    .map((b) => ({ symbol: b.currency, qty: +b.balance }));
};

export const placeCoinDCXOrder = async ({ side, symbol, qty }) => {
  const body = {
    side,
    order_type: "market_order",
    market: symbol + "USDT",
    total_quantity: qty.toString(),
    timestamp: Date.now(),
  };
  await api.post("/exchange/v1/orders/create", body, { headers: hdr(body) });
};
