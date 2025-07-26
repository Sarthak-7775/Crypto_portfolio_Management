import { useEffect, useState } from "react";
import { fetchCandles } from "../services";

export function useCandles(symbol) {
  const [candles, setCandles] = useState([]);

  useEffect(() => {
    fetchCandles(symbol).then(setCandles);
  }, [symbol]);

  return { candles };
}
