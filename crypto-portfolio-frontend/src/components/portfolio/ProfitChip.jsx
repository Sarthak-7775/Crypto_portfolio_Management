export default function ProfitChip({ value }) {
  const color =
    value > 0 ? "bg-green-600" : value < 0 ? "bg-red-600" : "bg-gray-500";
  return (
    <span className={`${color} text-white text-xs px-2 py-0.5 rounded-full`}>
      {value.toFixed(2)}%
    </span>
  );
}
