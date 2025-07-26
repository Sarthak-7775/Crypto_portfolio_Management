import { usePortfolioStore } from "./hooks/usePortfolio";

const EXCHANGES = ["BINANCE", "COINDCX"];

export default function ExchangeSelector() {
  const { exchange, setExchange } = usePortfolioStore((s) => ({
    exchange: s.exchange,
    setExchange: s.setExchange,
  }));

  return (
    <div className="flex gap-3 mb-6">
      {EXCHANGES.map((ex) => (
        <button
          key={ex}
          onClick={() => setExchange(ex)}
          className={`px-4 py-1.5 rounded-full border ${
            exchange === ex
              ? "bg-primary text-white border-primary shadow"
              : "bg-surface border-muted hover:bg-muted"
          }`}
        >
          {ex}
        </button>
      ))}
    </div>
  );
}
