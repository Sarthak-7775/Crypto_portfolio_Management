import { useState } from "react";
import { usePortfolioStore } from "./hooks/usePortfolio";

export default function TradePanel({ asset }) {
  const [side, setSide] = useState("BUY");
  const [qty, setQty] = useState("");
  const { placeOrder } = usePortfolioStore();

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        placeOrder(asset, side, qty);
        setQty("");
      }}
      className="space-y-3"
    >
      <div className="flex gap-2">
        <input
          type="number"
          step="0.0001"
          value={qty}
          onChange={(e) => setQty(e.target.value)}
          placeholder="Qty"
          className="input flex-1"
        />
        <select
          value={side}
          onChange={(e) => setSide(e.target.value)}
          className="input"
        >
          <option>BUY</option>
          <option>SELL</option>
        </select>
      </div>
      <button className="btn-primary w-full">Execute</button>
    </form>
  );
}
