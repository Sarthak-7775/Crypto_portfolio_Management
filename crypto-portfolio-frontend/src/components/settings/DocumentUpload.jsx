import { useSettings } from "./context/SettingsContext";
import useFileUpload from "./hooks/useFileUpload";

export default function DocumentUpload() {
  const { state, dispatch } = useSettings();
  const { file, preview, onSelect, reset } = useFileUpload();

  const upload = () => {
    if (!file) return;
    dispatch({ type: "SET_USER", payload: { kycDocs: [...state.user.kycDocs, file.name] } });
    reset();
    alert("Document uploaded (mock)");
  };

  return (
    <section>
      <h2 className="text-xl font-semibold mb-4">KYC Documents</h2>
      <input type="file" onChange={onSelect} />
      {preview && <img src={preview} alt="preview" className="w-40 my-3 rounded" />}
      <button className="btn-primary" onClick={upload}>Upload</button>

      <ul className="list-disc ml-6 mt-4 text-sm">
        {state.user.kycDocs.map((d, i) => <li key={i}>{d}</li>)}
      </ul>
    </section>
  );
}
