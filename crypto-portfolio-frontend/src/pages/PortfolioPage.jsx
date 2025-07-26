import ExchangeSelector from "../components/portfolio/ExchangeSelector";
import PortfolioSummary from "../components/portfolio/PortfolioSummary";
import HoldingsTable from "../components/portfolio/HoldingsTable";

export default function PortfolioPage() {
  return (
    <main className="p-4 md:p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">My Portfolio</h1>
      <ExchangeSelector />
      <PortfolioSummary />
      <HoldingsTable />
    </main>
  );
}
