import { useEffect, useRef, useState } from "react";

export default function SignaturePad({ onSigned, signerName = "" }) {
  const canvasRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [tab, setTab] = useState("draw");
  const [typedName, setTypedName] = useState(signerName);
  const [signed, setSigned] = useState(false);
  const [signedAt, setSignedAt] = useState(null);
  const [signaturePreview, setSignaturePreview] = useState("");

  useEffect(() => {
    if (!modalOpen || tab !== "draw") return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.strokeStyle = "#0c4a6e";
    ctx.lineWidth = 2.5;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
  }, [modalOpen, tab]);

  const getPos = (event) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const touch = event.touches?.[0];
    const clientX = touch ? touch.clientX : event.clientX;
    const clientY = touch ? touch.clientY : event.clientY;
    return { x: clientX - rect.left, y: clientY - rect.top };
  };

  const startDraw = (e) => {
    const { x, y } = getPos(e);
    const ctx = canvasRef.current.getContext("2d");
    ctx.beginPath();
    ctx.moveTo(x, y);
    setDrawing(true);
  };

  const moveDraw = (e) => {
    if (!drawing) return;
    e.preventDefault();
    const { x, y } = getPos(e);
    const ctx = canvasRef.current.getContext("2d");
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const endDraw = () => setDrawing(false);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  const generateTypedSignature = () => {
    const c = document.createElement("canvas");
    c.width = 500;
    c.height = 130;
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.font = "italic 52px Georgia, serif";
    ctx.fillStyle = "#0c4a6e";
    ctx.textBaseline = "middle";
    ctx.fillText(typedName, 20, 65);
    return c.toDataURL("image/png");
  };

  const confirmSignature = () => {
    const dataUrl =
      tab === "draw"
        ? canvasRef.current.toDataURL("image/png")
        : generateTypedSignature();
    setSignaturePreview(dataUrl);
    setSigned(true);
    setSignedAt(new Date());
    onSigned(dataUrl);
    setModalOpen(false);
  };

  const removeSignature = () => {
    setSigned(false);
    setSignaturePreview("");
    setSignedAt(null);
    onSigned("");
  };

  const formatDate = (d) =>
    d
      ? d.toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" }) +
        " a las " +
        d.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" })
      : "";

  return (
    <div className="space-y-4">
      {/* Extracto del contrato */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600 leading-relaxed">
        <p className="font-bold text-slate-800 mb-2 text-base">
          Contrato de Prestación de Servicios — HogarFix S.A.S.
        </p>
        <p>
          El técnico registrado acepta cumplir con los estándares de calidad, seguridad y
          profesionalismo de la plataforma HogarFix. Se compromete a respetar los horarios
          acordados, mantener comunicación oportuna con los clientes y acatar las políticas de
          cancelación vigentes. HogarFix retendrá una comisión del{" "}
          <strong className="text-slate-800">15 %</strong> por cada servicio completado.
          Este acuerdo tiene vigencia indefinida y puede ser terminado con aviso previo de 15 días.
        </p>
        <a
          href="/tecnico/contrato/pdf"
          target="_blank"
          rel="noreferrer"
          className="inline-block mt-3 text-xs text-brand-700 underline hover:text-brand-900"
        >
          📄 Ver contrato completo en PDF →
        </a>
      </div>

      {/* Área de firma */}
      {signed ? (
        <div className="rounded-xl border-2 border-green-500 bg-green-50 p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-green-700 font-semibold text-sm">✓ Firmado digitalmente</span>
                <span className="rounded-full bg-green-100 text-green-800 text-xs px-2 py-0.5 border border-green-300 font-medium">
                  Válido
                </span>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white p-2 inline-block">
                <img src={signaturePreview} alt="Firma digital" className="h-14 object-contain" />
              </div>
              <p className="text-xs text-slate-400">Firmado el {formatDate(signedAt)}</p>
            </div>
            <button
              type="button"
              onClick={removeSignature}
              className="text-xs text-red-500 underline hover:text-red-700 shrink-0"
            >
              Quitar firma
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="w-full rounded-xl border-2 border-dashed border-brand-600 bg-brand-50 py-8 text-center hover:bg-brand-100 transition-colors group cursor-pointer"
        >
          <div className="text-4xl mb-2">✍️</div>
          <div className="text-brand-700 font-bold text-base group-hover:underline">
            Haz clic aquí para firmar
          </div>
          <div className="text-slate-500 text-sm mt-1">
            Acepto el contrato de prestación de servicios HogarFix
          </div>
        </button>
      )}

      {/* Modal de firma */}
      {modalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
            {/* Header modal */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Agregar tu firma</h3>
                <p className="text-xs text-slate-400 mt-0.5">HogarFix S.A.S. — Contrato de servicios</p>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 text-2xl leading-none w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100"
              >
                ×
              </button>
            </div>

            <div className="px-6 py-4 space-y-4">
              {/* Tabs */}
              <div className="flex rounded-lg border border-slate-200 overflow-hidden">
                <button
                  type="button"
                  onClick={() => setTab("draw")}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    tab === "draw"
                      ? "bg-brand-700 text-white"
                      : "bg-white text-slate-500 hover:bg-slate-50"
                  }`}
                >
                  ✏️ Dibujar
                </button>
                <button
                  type="button"
                  onClick={() => setTab("type")}
                  className={`flex-1 py-2 text-sm font-medium transition-colors ${
                    tab === "type"
                      ? "bg-brand-700 text-white"
                      : "bg-white text-slate-500 hover:bg-slate-50"
                  }`}
                >
                  ⌨️ Escribir nombre
                </button>
              </div>

              {/* Tab: Dibujar */}
              {tab === "draw" && (
                <div className="space-y-2">
                  <p className="text-xs text-slate-500">Dibuja tu firma en el área a continuación</p>
                  <div className="relative rounded-xl border-2 border-slate-200 bg-white overflow-hidden">
                    <div className="absolute bottom-8 left-6 right-6 border-b border-dashed border-slate-200 pointer-events-none" />
                    <canvas
                      ref={canvasRef}
                      width={500}
                      height={150}
                      className="w-full touch-none"
                      onMouseDown={startDraw}
                      onMouseMove={moveDraw}
                      onMouseUp={endDraw}
                      onMouseLeave={endDraw}
                      onTouchStart={startDraw}
                      onTouchMove={moveDraw}
                      onTouchEnd={endDraw}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={clearCanvas}
                    className="text-xs text-slate-400 underline hover:text-slate-600"
                  >
                    Borrar y reintentar
                  </button>
                </div>
              )}

              {/* Tab: Escribir nombre */}
              {tab === "type" && (
                <div className="space-y-3">
                  <p className="text-xs text-slate-500">
                    Escribe tu nombre completo — se generará una firma estilizada
                  </p>
                  <input
                    className="input"
                    placeholder="Tu nombre completo"
                    value={typedName}
                    onChange={(e) => setTypedName(e.target.value)}
                  />
                  {typedName && (
                    <div className="rounded-xl border-2 border-slate-200 bg-white flex items-center justify-center min-h-[90px] px-4">
                      <span
                        style={{
                          fontFamily: "Georgia, 'Times New Roman', serif",
                          fontSize: "2.2rem",
                          color: "#0c4a6e",
                          fontStyle: "italic",
                        }}
                      >
                        {typedName}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Footer modal */}
            <div className="flex gap-2 px-6 py-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="btn-secondary flex-1"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={confirmSignature}
                className="btn-primary flex-1"
              >
                Insertar firma
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
