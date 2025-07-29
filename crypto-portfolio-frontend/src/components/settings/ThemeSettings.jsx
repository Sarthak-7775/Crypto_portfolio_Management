import useThemeSettings from "./hooks/useTheme";

export default function ThemeSettings() {
  const { theme, changeTheme } = useThemeSettings();
  const options = ["light", "dark"];

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Appearance</h2>
      <div className="flex gap-3">
        {options.map((opt) => (
          <button
            key={opt}
            className={`px-4 py-1.5 rounded-full border ${
              theme === opt ? "bg-blue-600 text-white border-blue-600" : "border-gray-300 dark:border-gray-600"
            }`}
            onClick={() => changeTheme(opt)}
          >
            {opt.charAt(0).toUpperCase() + opt.slice(1)}
          </button>
        ))}
      </div>
    </section>
  );
}
