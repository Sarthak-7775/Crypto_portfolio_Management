import { useSettings } from "./context/SettingsContext";
import { useState } from "react";

export default function AccountSecuritySettings() {
  const { state, dispatch } = useSettings();
  const [password, setPassword] = useState("");
  const toggle2FA = () =>
    dispatch({ type: "SET_PRIVACY", payload: { twoFactor: !state.privacy.twoFactor } });

  const changePass = (e) => {
    e.preventDefault();
    if (password.length < 8) return alert("Password too short");
    alert("Password changed (mock)!");
    setPassword("");
  };

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Security</h2>
      <button className="btn-secondary mb-4" onClick={toggle2FA}>
        {state.privacy.twoFactor ? "Disable" : "Enable"} Two-Factor Authentication
      </button>

      <form onSubmit={changePass} className="space-y-3 max-w-sm">
        <input
          type="password"
          className="input w-full"
          placeholder="New Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="btn-primary w-full">Change Password</button>
      </form>
    </section>
  );
}
