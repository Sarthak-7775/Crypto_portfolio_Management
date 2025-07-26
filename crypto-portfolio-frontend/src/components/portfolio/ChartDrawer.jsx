import { Dialog, Transition } from "@headlessui/react";
import { useCandles } from "./hooks/useCandles";
import { createChart } from "lightweight-charts";
import { useEffect, useRef } from "react";

export default function ChartDrawer({ asset, onClose, children }) {
  const ref = useRef(null);
  const { candles } = useCandles(asset);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, { height: 300 });
    const series = chart.addCandlestickSeries();
    series.setData(candles);
    return () => chart.remove();
  }, [candles]);

  return (
    <Transition appear show as={Dialog} onClose={onClose}>
      <Dialog.Panel className="fixed bottom-0 md:right-0 md:top-0 md:w-[38rem] w-full bg-surface overflow-y-auto rounded-t-2xl md:rounded-none p-4 shadow-lg">
        <h2 className="font-semibold mb-2">{asset} Chart</h2>
        <div ref={ref} className="mb-4" />
        {children}
      </Dialog.Panel>
    </Transition>
  );
}
