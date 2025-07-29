import { useSettings } from "./context/SettingsContext";
import { useState } from "react";

export default function BankAccountSettings() {
  const { state, dispatch } = useSettings();
  const [form, setForm] = useState({ bank: "", accNumber: "", ifsc: "" });

  const add = () => {
    if (!form.bank || !form.accNumber) return;
    dispatch({ type: "SET_BANK_ACCOUNTS", payload: [...state.bankAccounts, form] });
    setForm({ bank: "", accNumber: "", ifsc: "" });
  };

  const remove = (idx) =>
    dispatch({
      type: "SET_BANK_ACCOUNTS",
      payload: state.bankAccounts.filter((_, i) => i !== idx),
    });

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Bank Accounts</h2>
      <div className="space-y-3">
        {state.bankAccounts.map((b, i) => (
          <div key={i} className="flex items-center justify-between bg-muted p-3 rounded">
            <span>{b.bank} • {b.accNumber}</span>
            <button onClick={() => remove(i)} className="text-red-600">Remove</button>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-3 gap-3 mt-4">
        <input
          className="input"
          placeholder="Bank Name"
          value={form.bank}
          onChange={(e) => setForm({ ...form, bank: e.target.value })}
        />
        <input
          className="input"
          placeholder="Account Number"
          value={form.accNumber}
          onChange={(e) => setForm({ ...form, accNumber: e.target.value })}
        />
        <input
          className="input"
          placeholder="IFSC"
          value={form.ifsc}
          onChange={(e) => setForm({ ...form, ifsc: e.target.value })}
        />
      </div>
      <button className="btn-primary mt-3" onClick={add}>Add Bank</button>
    </section>
  );
}
