import { useBalances } from "./hooks/useBalances";
import CoinRow from "./CoinRow";

export default function HoldingsTable() {
  const { rows, loading } = useBalances();

  if (loading) return <p className="py-8 text-center">Loading…</p>;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left">
            <th>Asset</th>
            <th>Quantity</th>
            <th>Value (USD)</th>
            <th>P/L %</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows
            .filter((r) => r.qty > 0)
            .map((r) => (
              <CoinRow key={r.symbol} row={r} />
            ))}
        </tbody>
      </table>
    </div>
  );
}
