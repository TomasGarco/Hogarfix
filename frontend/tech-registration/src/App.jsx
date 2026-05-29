import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";

// ─── Detectar si venimos del registro Flask ─────────────────────────────────
const _params = new URLSearchParams(window.location.search);
const IS_POST_REGISTRO = _params.get("paso") === "contrato";
const NOMBRE_TECNICO = _params.get("nombre") || "";
const EMAIL_TECNICO = _params.get("email") || "";
// ────────────────────────────────────────────────────────────────────────────

import FormSection from "./components/FormSection";
import ProgressBar from "./components/ProgressBar";
import FileUploader from "./components/FileUploader";
import SignaturePad from "./components/SignaturePad";

import { categoryServices, weekdays } from "./data/services";
import { sendPhoneOtp, verifyPhoneOtp } from "./services/firebaseOtp";
import { verifyIdentity } from "./services/identityVerification";
import { technicianSchema } from "./validation/schema";

// ─── Vista post-registro: contrato + documentos adicionales ────────────────
function PostRegistroContrato({ nombre, email }) {
  const [firmado, setFirmado] = useState(false);
  const [signatureData, setSignatureData] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [listo, setListo] = useState(false);

  const handleGuardar = async () => {
    if (!signatureData) {
      setMensaje("Por favor firma el contrato antes de continuar.");
      return;
    }
    try {
      setGuardando(true);
      await axios.post("/api/technicians/firma-contrato", { email, signatureData });
      setListo(true);
      setMensaje("");
    } catch {
      setListo(true); // permitir continuar aunque falle el guardado
      setMensaje("");
    } finally {
      setGuardando(false);
    }
  };

  if (listo) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-100 to-slate-200 flex items-center justify-center px-4">
        <div className="card p-8 max-w-lg w-full text-center space-y-4">
          <div className="text-5xl">🎉</div>
          <h1 className="text-2xl font-extrabold text-slate-900">¡Todo listo, {nombre}!</h1>
          <p className="text-slate-600">Tu perfil de técnico está activo. Ya puedes iniciar sesión y comenzar a recibir solicitudes.</p>
          <a href="http://localhost:5000/auth/login" className="btn-primary block text-center">
            Ir al login →
          </a>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-100 to-slate-200 py-8 px-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="card p-6">
          <div className="flex items-center gap-3">
            <img
              src="http://localhost:5000/static/img/logo-hogarfix.svg"
              alt="HogarFix"
              className="h-8"
              onError={(e) => { e.target.style.display = "none"; }}
            />
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 mt-3">
            ¡Registro exitoso, {nombre}!
          </h1>
          <p className="text-slate-500 mt-1 text-sm">
            Solo falta firmar el contrato de prestación de servicios para activar tu perfil.
          </p>
        </div>

        {/* Paso 1: Descargar/leer el contrato */}
        <FormSection title="Paso 1 — Contrato de servicios" subtitle="Lee el contrato antes de firmar">
          <p className="text-sm text-slate-600">
            Este documento establece las condiciones de uso de la plataforma HogarFix, tus derechos y responsabilidades como técnico verificado.
          </p>
          <a
            href="http://localhost:5000/tecnico/contrato/pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary inline-flex items-center gap-2"
          >
            📄 Descargar contrato PDF
          </a>
          <div className="flex items-center gap-2 mt-3">
            <input
              type="checkbox"
              id="aceptaContrato"
              checked={firmado}
              onChange={(e) => setFirmado(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="aceptaContrato" className="text-sm text-slate-700">
              He leído y acepto el contrato de prestación de servicios de HogarFix
            </label>
          </div>
        </FormSection>

        {/* Paso 2: Firma digital */}
        <FormSection title="Paso 2 — Firma digital" subtitle="Firma con el dedo o el mouse">
          <SignaturePad onSigned={(dataUrl) => setSignatureData(dataUrl)} />
          {signatureData && (
            <p className="text-xs text-green-600 mt-1">✓ Firma capturada</p>
          )}
        </FormSection>

        {/* Botón final */}
        <div className="card p-5 space-y-3">
          {mensaje && <p className="text-sm text-amber-600">{mensaje}</p>}
          <button
            type="button"
            className="btn-primary w-full"
            disabled={!firmado || guardando}
            onClick={handleGuardar}
          >
            {guardando ? "Guardando firma..." : "Confirmar y activar perfil →"}
          </button>
          <p className="text-xs text-slate-400 text-center">
            Si tienes problemas, escríbenos a soporte@hogarfix.co
          </p>
        </div>
      </div>
    </main>
  );
}
// ─────────────────────────────────────────────────────────────────────────────

const TOTAL_SECTIONS = 6;

const defaultValues = {
  fullName: "",
  email: "",
  password: "",
  phone: "",
  phoneVerified: false,
  otpCode: "",
  documentType: "",
  documentNumber: "",
  documentFrontUrl: "",
  documentBackUrl: "",
  selfieUrl: "",
  identityStatus: "pending",
  category: "",
  services: [],
  yearsExperience: "",
  certificationsUrl: "",
  portfolioUrls: [],
  address: "",
  neighborhood: "",
  locality: "",
  chargeType: "hora",
  basePrice: "",
  days: [],
  startTime: "",
  endTime: "",
  signatureData: ""
};

export default function App() {
  // Si venimos de Flask post-registro, mostrar solo contrato
  if (IS_POST_REGISTRO) {
    return <PostRegistroContrato nombre={NOMBRE_TECNICO} email={EMAIL_TECNICO} />;
  }

  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [apiMessage, setApiMessage] = useState("");
  const [idProvider, setIdProvider] = useState("mock");

  const {
    register,
    setValue,
    watch,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm({
    resolver: zodResolver(technicianSchema),
    mode: "onChange",
    defaultValues
  });

  const category = watch("category");
  const selectedServices = watch("services") || [];
  const availableServices = useMemo(() => categoryServices[category] || [], [category]);

  const docFront = watch("documentFrontUrl");
  const docBack = watch("documentBackUrl");
  const selfie = watch("selfieUrl");

  // Auto-verificar identidad cuando los 3 documentos estén cargados
  useEffect(() => {
    if (docFront && docBack && selfie) {
      runIdentityCheck();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [docFront, docBack, selfie]);

  const completedSections = useMemo(() => {
    let done = 0;
    if (watch("fullName") && watch("email") && watch("password")) done += 1;
    if (watch("documentFrontUrl") && watch("documentBackUrl") && watch("selfieUrl")) done += 1;
    if (watch("category") && (watch("services") || []).length) done += 1;
    if (watch("address") && watch("locality")) done += 1;
    if (watch("basePrice") && (watch("days") || []).length) done += 1;
    if (watch("signatureData") && watch("phoneVerified") && watch("identityStatus") === "approved") done += 1;
    return done;
  }, [watch]);

  const toggleService = (service) => {
    const current = watch("services") || [];
    if (current.includes(service)) {
      setValue("services", current.filter((s) => s !== service), { shouldValidate: true });
    } else {
      setValue("services", [...current, service], { shouldValidate: true });
    }
  };

  const toggleDay = (day) => {
    const current = watch("days") || [];
    if (current.includes(day)) {
      setValue("days", current.filter((d) => d !== day), { shouldValidate: true });
    } else {
      setValue("days", [...current, day], { shouldValidate: true });
    }
  };

  const requestPhoneOtp = async () => {
    try {
      setSendingOtp(true);
      await sendPhoneOtp(watch("phone"));
      setApiMessage("OTP enviado por SMS.");
    } catch (error) {
      setApiMessage(error.message || "No se pudo enviar OTP");
    } finally {
      setSendingOtp(false);
    }
  };

  const confirmPhoneOtp = async () => {
    try {
      setVerifyingOtp(true);
      await verifyPhoneOtp(watch("otpCode"));
      setValue("phoneVerified", true, { shouldValidate: true });
      setApiMessage("Telefono verificado.");
    } catch (error) {
      setApiMessage(error.message || "OTP invalido");
    } finally {
      setVerifyingOtp(false);
    }
  };

  const runIdentityCheck = async () => {
    const result = await verifyIdentity({
      documentFrontUrl: watch("documentFrontUrl"),
      documentBackUrl: watch("documentBackUrl"),
      selfieUrl: watch("selfieUrl"),
      provider: idProvider
    });

    setValue("identityStatus", result.status, { shouldValidate: true });
    setApiMessage(`Identidad: ${result.status}`);
  };

  const autofillGeolocation = () => {
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setValue("address", `${coords.latitude}, ${coords.longitude}`, { shouldValidate: true });
      },
      () => setApiMessage("No se pudo obtener ubicacion")
    );
  };

  const onSubmit = async (payload) => {
    try {
      setSubmitLoading(true);
      setApiMessage("");

      await axios.post("/api/technicians/register", payload);
      setApiMessage("Registro enviado correctamente.");
    } catch (_error) {
      setApiMessage("Backend no conectado: payload listo para integrar API.");
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-100 to-slate-200 py-8 px-4">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="card p-6">
          <h1 className="text-2xl font-extrabold text-slate-900">Registro de Tecnicos Verificados</h1>
          <p className="text-sm text-slate-500 mt-1">Marketplace HogarFix - seguridad, identidad y cumplimiento profesional.</p>
        </div>

        <ProgressBar current={completedSections} total={TOTAL_SECTIONS} />

        <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <FormSection title="1) Cuenta y Telefono" subtitle="Credenciales + OTP SMS (Firebase)">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Nombre completo *</label>
                <input className="input" {...register("fullName")} />
                {errors.fullName ? <p className="error">{errors.fullName.message}</p> : null}
              </div>
              <div>
                <label className="label">Email *</label>
                <input className="input" type="email" {...register("email")} />
                {errors.email ? <p className="error">{errors.email.message}</p> : null}
              </div>
              <div>
                <label className="label">Contrasena segura *</label>
                <input className="input" type="password" {...register("password")} />
                {errors.password ? <p className="error">{errors.password.message}</p> : null}
              </div>
              <div>
                <label className="label">Telefono (E.164) *</label>
                <input className="input" placeholder="+573001112233" {...register("phone")} />
                {errors.phone ? <p className="error">{errors.phone.message}</p> : null}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_auto] gap-3 items-end">
              <div>
                <label className="label">Codigo OTP</label>
                <input className="input" {...register("otpCode")} />
              </div>
              <button type="button" className="btn-secondary" onClick={requestPhoneOtp} disabled={sendingOtp}>
                {sendingOtp ? "Enviando OTP..." : "Enviar OTP"}
              </button>
              <button type="button" className="btn-secondary" onClick={confirmPhoneOtp} disabled={verifyingOtp}>
                {verifyingOtp ? "Validando..." : "Validar OTP"}
              </button>
            </div>
            <input type="hidden" {...register("phoneVerified")} />
            {errors.phoneVerified ? <p className="error">{errors.phoneVerified.message}</p> : null}
            <div id="recaptcha-container" />
          </FormSection>

          <FormSection title="2) Identidad" subtitle="Documento + selfie + verificacion facial">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Tipo documento *</label>
                <select className="input" {...register("documentType")}>
                  <option value="">Selecciona</option>
                  <option value="cc">Cedula</option>
                  <option value="ce">Cedula extranjeria</option>
                  <option value="pasaporte">Pasaporte</option>
                </select>
                {errors.documentType ? <p className="error">{errors.documentType.message}</p> : null}
              </div>
              <div>
                <label className="label">Numero documento *</label>
                <input className="input" {...register("documentNumber")} />
                {errors.documentNumber ? <p className="error">{errors.documentNumber.message}</p> : null}
              </div>
            </div>

            {/* Selector de API de verificación */}
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <label className="label">API de verificación</label>
                <select
                  className="input"
                  value={idProvider}
                  onChange={(e) => {
                    setIdProvider(e.target.value);
                    setValue("identityStatus", "pending", { shouldValidate: false });
                  }}
                >
                  <option value="mock">Mock (pruebas)</option>
                  <option value="onfido">Onfido</option>
                  <option value="veriff">Veriff</option>
                </select>
              </div>
              {idProvider !== "mock" && (
                <p className="text-xs text-amber-600 mt-4">⚠️ Requiere credenciales en .env</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FileUploader label="Documento frontal" required folder="tech/docs" onUploaded={(url) => setValue("documentFrontUrl", url, { shouldValidate: true })} accept="image/png,image/jpeg,image/jpg" />
              <FileUploader label="Documento reverso" required folder="tech/docs" onUploaded={(url) => setValue("documentBackUrl", url, { shouldValidate: true })} accept="image/png,image/jpeg,image/jpg" />
              <FileUploader label="Selfie" required folder="tech/selfies" onUploaded={(url) => setValue("selfieUrl", url, { shouldValidate: true })} accept="image/png,image/jpeg,image/jpg" />
            </div>

            <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
              {watch("identityStatus") === "approved" ? (
                <span className="flex items-center gap-1 text-green-600 font-medium">✓ Identidad verificada automáticamente</span>
              ) : (docFront && docBack && selfie) ? (
                <span className="text-blue-600">⏳ Verificando identidad...</span>
              ) : (
                <span>Sube los 3 documentos para verificación automática</span>
              )}
            </div>
            <input type="hidden" {...register("identityStatus")} />
            {errors.identityStatus ? <p className="error">{errors.identityStatus.message}</p> : null}
          </FormSection>

          <FormSection title="3) Servicios y Experiencia" subtitle="Especialidad, portafolio y certificaciones">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Categoria *</label>
                <select className="input" {...register("category")}>
                  <option value="">Selecciona</option>
                  {Object.keys(categoryServices).map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                {errors.category ? <p className="error">{errors.category.message}</p> : null}
              </div>
              <div>
                <label className="label">Años de experiencia *</label>
                <select className="input" {...register("yearsExperience")}>
                  <option value="">Selecciona</option>
                  <option value="0-1">0-1</option>
                  <option value="2-4">2-4</option>
                  <option value="5-8">5-8</option>
                  <option value="9+">9+</option>
                </select>
                {errors.yearsExperience ? <p className="error">{errors.yearsExperience.message}</p> : null}
              </div>
            </div>

            <div>
              <label className="label">Servicios *</label>
              <div className="mt-2 flex flex-wrap gap-2">
                {availableServices.map((service) => {
                  const active = selectedServices.includes(service);
                  return (
                    <button
                      key={service}
                      type="button"
                      onClick={() => toggleService(service)}
                      className={`rounded-full px-3 py-1.5 text-sm border ${active ? "bg-brand-700 text-white border-brand-700" : "bg-white text-slate-700 border-slate-300"}`}
                    >
                      {service}
                    </button>
                  );
                })}
              </div>
              {errors.services ? <p className="error">{errors.services.message}</p> : null}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FileUploader label="Certificaciones (opcional)" folder="tech/certifications" onUploaded={(url) => setValue("certificationsUrl", url, { shouldValidate: false })} />
              <FileUploader label="Portafolio (multiple)" multiple required folder="tech/portfolio" onUploaded={(urls) => setValue("portfolioUrls", urls, { shouldValidate: true })} accept="image/png,image/jpeg,image/jpg" />
            </div>
            {errors.portfolioUrls ? <p className="error">{errors.portfolioUrls.message}</p> : null}
          </FormSection>

          <FormSection title="4) Ubicacion" subtitle="Direccion + geolocalizacion">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Direccion *</label>
                <input className="input" {...register("address")} />
                {errors.address ? <p className="error">{errors.address.message}</p> : null}
              </div>
              <div>
                <label className="label">Barrio *</label>
                <input className="input" {...register("neighborhood")} />
                {errors.neighborhood ? <p className="error">{errors.neighborhood.message}</p> : null}
              </div>
              <div>
                <label className="label">Localidad *</label>
                <input className="input" {...register("locality")} />
                {errors.locality ? <p className="error">{errors.locality.message}</p> : null}
              </div>
            </div>
            <button type="button" className="btn-secondary" onClick={autofillGeolocation}>Usar mi ubicacion</button>
          </FormSection>

          <FormSection title="5) Precio y Disponibilidad" subtitle="Tarifa y horario de trabajo">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Tipo de cobro *</label>
                <select className="input" {...register("chargeType")}>
                  <option value="hora">Por hora</option>
                  <option value="servicio">Por servicio</option>
                </select>
              </div>
              <div>
                <label className="label">Precio base *</label>
                <input className="input" type="number" min="1" {...register("basePrice", { valueAsNumber: true })} />
                {errors.basePrice ? <p className="error">{errors.basePrice.message}</p> : null}
              </div>
            </div>

            <div>
              <label className="label">Dias disponibles *</label>
              <div className="mt-2 flex flex-wrap gap-2">
                {weekdays.map((day) => {
                  const active = (watch("days") || []).includes(day);
                  return (
                    <button
                      key={day}
                      type="button"
                      onClick={() => toggleDay(day)}
                      className={`rounded-full px-3 py-1.5 text-sm border ${active ? "bg-brand-700 text-white border-brand-700" : "bg-white text-slate-700 border-slate-300"}`}
                    >
                      {day}
                    </button>
                  );
                })}
              </div>
              {errors.days ? <p className="error">{errors.days.message}</p> : null}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Hora inicio *</label>
                <input className="input" type="time" {...register("startTime")} />
                {errors.startTime ? <p className="error">{errors.startTime.message}</p> : null}
              </div>
              <div>
                <label className="label">Hora fin *</label>
                <input className="input" type="time" {...register("endTime")} />
                {errors.endTime ? <p className="error">{errors.endTime.message}</p> : null}
              </div>
            </div>
          </FormSection>

          <FormSection title="6) Firma de Contrato" subtitle="Firma digital en canvas">
            <SignaturePad onSigned={(dataUrl) => setValue("signatureData", dataUrl, { shouldValidate: true })} />
            {errors.signatureData ? <p className="error">{errors.signatureData.message}</p> : null}
          </FormSection>

          <div className="card p-5 space-y-3">
            <button type="submit" className="btn-primary w-full" disabled={submitLoading || isSubmitting}>
              {submitLoading ? "Enviando registro..." : "Enviar registro tecnico"}
            </button>
            {apiMessage ? <p className="text-sm text-slate-600">{apiMessage}</p> : null}
          </div>
        </form>
      </div>
    </main>
  );
}
