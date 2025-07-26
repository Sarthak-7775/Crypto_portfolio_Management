import { useState } from "react";
import ProfitChip from "./ProfitChip";
import ChartDrawer from "./ChartDrawer";
import TradePanel from "./TradePanel";

export default function CoinRow({ row }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <tr
        className="hover:bg-muted cursor-pointer"
        onClick={() => setOpen(true)}
      >
        <td className="flex items-center gap-2">
          <img
            src={`https://cryptoicons.org/api/icon/${row.symbol.toLowerCase()}/24`}
            alt=""
          />
          {row.symbol}
        </td>
        <td>{row.qty}</td>
        <td>${row.value.toFixed(2)}</td>
        <td>
          <ProfitChip value={row.pnlPercent} />
        </td>
        <td className="text-right text-primary">Details ▸</td>
      </tr>

      {open && (
        <ChartDrawer asset={row.symbol} onClose={() => setOpen(false)}>
          <TradePanel asset={row.symbol} />
        </ChartDrawer>
      )}
    </>
  );
}
