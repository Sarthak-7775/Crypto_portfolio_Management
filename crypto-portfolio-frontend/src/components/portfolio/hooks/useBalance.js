import { useEffect, useState } from "react";
import { usePortfolioStore } from "./usePortfolio";
import { getBinanceBalances } from "../services/binance.service";
import { getCoinDCXBalances } from "../services/coindcx.service";

export function useBalances() {
  const exchange = usePortfolioStore((s) => s.exchange);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  async function fetchBalances() {
    setLoading(true);
    if (exchange === "BINANCE") {
      setRows(await getBinanceBalances());
    } else {
      setRows(await getCoinDCXBalances());
    }
    setLoading(false);
  }

  useEffect(() => {
    fetchBalances();
    const id = setInterval(fetchBalances, 60000);
    return () => clearInterval(id);
  }, [exchange]);

  return { rows, loading };
}
