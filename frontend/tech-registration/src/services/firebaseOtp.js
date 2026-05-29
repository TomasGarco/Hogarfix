import { initializeApp, getApps } from "firebase/app";
import {
  getAuth,
  RecaptchaVerifier,
  signInWithPhoneNumber
} from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

const getFirebaseApp = () => {
  if (getApps().length) return getApps()[0];
  if (!firebaseConfig.apiKey || !firebaseConfig.authDomain) {
    throw new Error("Firebase no configurado. Define VITE_FIREBASE_* en .env");
  }
  return initializeApp(firebaseConfig);
};

export const setupRecaptcha = (containerId = "recaptcha-container") => {
  const app = getFirebaseApp();
  const auth = getAuth(app);

  if (!window.recaptchaVerifier) {
    window.recaptchaVerifier = new RecaptchaVerifier(auth, containerId, {
      size: "invisible"
    });
  }

  return { auth, recaptchaVerifier: window.recaptchaVerifier };
};

export const sendPhoneOtp = async (phone) => {
  const { auth, recaptchaVerifier } = setupRecaptcha();
  const confirmationResult = await signInWithPhoneNumber(auth, phone, recaptchaVerifier);
  window.confirmationResult = confirmationResult;
  return confirmationResult;
};

export const verifyPhoneOtp = async (code) => {
  if (!window.confirmationResult) {
    throw new Error("No hay OTP pendiente. Solicita un codigo primero.");
  }

  const result = await window.confirmationResult.confirm(code);
  return result.user;
};
