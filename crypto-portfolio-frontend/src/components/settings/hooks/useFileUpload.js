import { useState } from "react";

export default function useFileUpload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");

  const onSelect = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const reset = () => {
    setFile(null);
    setPreview("");
  };

  return { file, preview, onSelect, reset };
}
