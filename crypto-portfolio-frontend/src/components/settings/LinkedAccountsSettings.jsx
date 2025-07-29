import { useSettings } from "./context/SettingsContext";

export default function LinkedAccountsSettings() {
  const { state, dispatch } = useSettings();

  const unlink = (id) =>
    dispatch({
      type: "SET_LINKED_ACCOUNTS",
      payload: state.linkedAccounts.filter((a) => a.id !== id),
    });

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">Linked Crypto Exchanges</h2>
      {state.linkedAccounts.length
        ? state.linkedAccounts.map((acc) => (
            <div key={acc.id} className="flex justify-between items-center bg-muted p-3 rounded mb-2">
              <span>{acc.provider} • {acc.username}</span>
              <button onClick={() => unlink(acc.id)} className="text-red-600">Unlink</button>
            </div>
          ))
        : <p className="text-muted">No exchanges linked yet.</p>}
    </section>
  );
}
