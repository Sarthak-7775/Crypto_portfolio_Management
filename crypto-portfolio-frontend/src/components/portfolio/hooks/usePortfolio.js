import { create } from "zustand";
import { getBinanceBalances, placeBinanceOrder } from "../services/binance.service";
import { placeCoinDCXOrder } from "../services/coindcx.service";
import { useBalances } from "./useBalance";
import usePrices from "./usePrices";

export const usePortfolioStore = create((set, get) => ({
  exchange: "BINANCE",
  setExchange: (ex) => set({ exchange: ex }),
  placeOrder: async (symbol, side, qty) => {
    const { exchange } = get();
    if (exchange === "BINANCE") {
      await placeBinanceOrder(side, symbol, qty);
    } else {
      await placeCoinDCXOrder({ side, symbol, qty });
    }
  },
}));

export function usePortfolio() {
  const { rows } = useBalances();
  const { prices } = usePrices();

  const invested = rows.reduce((t, r) => t + r.cost, 0);
  const totalValue = rows.reduce(
    (t, r) => t + r.qty * (prices[r.symbol] || 0),
    0
  );
  const pnl = totalValue - invested;

  return { invested, totalValue, pnl };
}
