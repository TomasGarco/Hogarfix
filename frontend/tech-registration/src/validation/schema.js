import { z } from "zod";

const strongPassword = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$/;

export const technicianSchema = z.object({
  fullName: z.string().min(3, "Nombre obligatorio"),
  email: z.string().email("Email invalido"),
  password: z.string().regex(strongPassword, "Contrasena insegura"),
  phone: z.string().min(8, "Telefono invalido"),
  documentType: z.string().min(1, "Selecciona tipo de documento"),
  documentNumber: z.string().min(5, "Numero de documento invalido"),
  category: z.string().min(1, "Selecciona categoria"),
  services: z.array(z.string()).min(1, "Selecciona al menos un servicio"),
  yearsExperience: z.string().min(1, "Selecciona años de experiencia"),
  address: z.string().min(5, "Direccion obligatoria"),
  neighborhood: z.string().min(2, "Barrio obligatorio"),
  locality: z.string().min(2, "Localidad obligatoria"),
  chargeType: z.enum(["hora", "servicio"]),
  basePrice: z.coerce.number().positive("Precio invalido"),
  days: z.array(z.string()).min(1, "Selecciona disponibilidad"),
  startTime: z.string().min(1, "Hora inicio obligatoria"),
  endTime: z.string().min(1, "Hora fin obligatoria"),
  phoneVerified: z.boolean().refine((v) => v, "Debes verificar telefono"),
  identityStatus: z.enum(["approved", "pending", "rejected"]).refine((v) => v === "approved", "Identidad no aprobada"),
  signatureData: z.string().min(1, "Firma obligatoria"),
  documentFrontUrl: z.string().url("Sube documento frontal"),
  documentBackUrl: z.string().url("Sube documento reverso"),
  selfieUrl: z.string().url("Sube selfie"),
  portfolioUrls: z.array(z.string().url()).min(1, "Sube al menos una foto de trabajo")
});
