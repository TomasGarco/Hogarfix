export default function ProgressBar({ current, total }) {
  const ratio = Math.max(0, Math.min(100, Math.round((current / total) * 100)));

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between text-sm mb-2">
        <span className="font-semibold text-slate-700">Progreso del registro</span>
        <span className="text-slate-500">{current}/{total} secciones</span>
      </div>
      <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
        <div className="h-full bg-brand-700 transition-all duration-300" style={{ width: `${ratio}%` }} />
      </div>
    </div>
  );
}
