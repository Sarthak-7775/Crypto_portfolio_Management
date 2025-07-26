import { useEffect } from "react";
import { usePortfolioStore } from "./usePortfolio";
import { subscribeTicker } from "../services/priceSocket.service";

export default function usePrices() {
  const prices = usePortfolioStore((s) => s.prices || {});
  const setPrices = (p) => usePortfolioStore.setState({ prices: p });

  useEffect(() => {
    const unsubscribe = subscribeTicker(setPrices);
    return unsubscribe;
  }, []);

  return { prices };
}
