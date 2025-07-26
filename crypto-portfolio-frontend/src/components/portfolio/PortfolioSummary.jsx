import { usePortfolio } from "./hooks/usePortfolio";

function KPI({ label, value }) {
  return (
    <div className="bg-surface rounded-lg p-4 shadow flex flex-col">
      <span className="text-muted text-xs">{label}</span>
      <span className="text-lg font-medium mt-1">${value.toFixed(2)}</span>
    </div>
  );
}

export default function PortfolioSummary() {
  const { totalValue, invested, pnl } = usePortfolio();
  return (
    <section className="grid grid-cols-3 gap-4 my-6">
      <KPI label="Market Value" value={totalValue} />
      <KPI label="Invested" value={invested} />
      <KPI label="Net P/L" value={pnl} />
    </section>
  );
}
