import { useMemo, useState } from "react";
import { uploadToCloudinary } from "../services/cloudinary";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg", "application/pdf"];
const MAX_MB = 5;

export default function FileUploader({
  label,
  multiple = false,
  required = false,
  folder,
  onUploaded,
  accept = "image/png,image/jpeg,image/jpg,application/pdf"
}) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const previews = useMemo(
    () => files.filter((f) => f.file.type.startsWith("image/")).map((f) => ({
      name: f.file.name,
      url: URL.createObjectURL(f.file)
    })),
    [files]
  );

  const validateFiles = (list) => {
    const entries = Array.from(list);
    for (const file of entries) {
      const sizeMb = file.size / (1024 * 1024);
      if (!ALLOWED_TYPES.includes(file.type)) {
        return `Tipo no permitido: ${file.name}`;
      }
      if (sizeMb > MAX_MB) {
        return `${file.name} supera ${MAX_MB}MB`;
      }
    }
    return "";
  };

  const onChange = (e) => {
    const selected = e.target.files;
    if (!selected?.length) return;

    const validationError = validateFiles(selected);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError("");
    setFiles(Array.from(selected).map((file) => ({ file })));
  };

  const onUpload = async () => {
    if (!files.length) {
      if (required) setError("Este archivo es obligatorio");
      return;
    }

    setUploading(true);
    setError("");

    try {
      const uploaded = [];
      for (const entry of files) {
        const result = await uploadToCloudinary(entry.file, folder);
        uploaded.push(result.url);
      }
      onUploaded(multiple ? uploaded : uploaded[0]);
    } catch (uploadError) {
      setError(uploadError.message || "No se pudo subir archivo");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-2">
      <label className="label">{label}{required ? " *" : ""}</label>
      <input type="file" className="input" accept={accept} multiple={multiple} onChange={onChange} />
      {previews.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {previews.map((p) => (
            <img key={p.name} src={p.url} alt={p.name} className="h-20 w-full object-cover rounded-lg border border-slate-200" />
          ))}
        </div>
      ) : null}
      <button type="button" className="btn-secondary" onClick={onUpload} disabled={uploading}>
        {uploading ? "Subiendo..." : "Subir a Cloudinary"}
      </button>
      {error ? <p className="error">{error}</p> : null}
    </div>
  );
}
