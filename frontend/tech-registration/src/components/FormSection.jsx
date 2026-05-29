export default function FormSection({ title, subtitle, children }) {
  return (
    <section className="card p-5 space-y-4">
      <div>
        <h2 className="text-lg font-bold text-slate-900">{title}</h2>
        {subtitle ? <p className="text-sm text-slate-500 mt-1">{subtitle}</p> : null}
      </div>
      {children}
    </section>
  );
}
