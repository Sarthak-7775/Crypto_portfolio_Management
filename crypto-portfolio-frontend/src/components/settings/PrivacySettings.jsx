import { useSettings } from "./context/SettingsContext";

export default function PrivacySettings() {
  const { state, dispatch } = useSettings();
  const { privacy } = state;

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Privacy</h2>
      <label className="flex items-center gap-3 mb-3">
        <input
          type="checkbox"
          checked={privacy.profileVisible}
          onChange={() =>
            dispatch({ type: "SET_PRIVACY", payload: { profileVisible: !privacy.profileVisible } })
          }
        />
        <span>Allow my profile to be visible to others</span>
      </label>
      <p className="text-xs text-muted">
        Disabling this will hide your public statistics and social features.
      </p>
    </section>
  );
}
