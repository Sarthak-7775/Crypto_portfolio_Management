import { useSettings } from "./context/SettingsContext";

export default function NotificationSettings() {
  const { state, dispatch } = useSettings();
  const notif = state.notifications;

  const toggle = (k) =>
    dispatch({ type: "SET_NOTIFICATIONS", payload: { [k]: !notif[k] } });

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Notifications</h2>
      <div className="space-y-3 max-w-sm">
        {["email", "sms", "push"].map((k) => (
          <label key={k} className="flex items-center gap-3">
            <input type="checkbox" checked={notif[k]} onChange={() => toggle(k)} />
            <span className="capitalize">{k} notifications</span>
          </label>
        ))}
      </div>
    </section>
  );
}
