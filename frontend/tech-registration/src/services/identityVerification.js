import axios from "axios";

const DEFAULT_PROVIDER = import.meta.env.VITE_ID_PROVIDER || "mock";
const MOCK_DELAY_MS = 1400;

export const verifyIdentity = async ({ documentFrontUrl, documentBackUrl, selfieUrl, provider }) => {
  const PROVIDER = provider || DEFAULT_PROVIDER;

  if (PROVIDER === "mock") {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));
    if (!documentFrontUrl || !documentBackUrl || !selfieUrl) {
      return { status: "rejected", reason: "Faltan evidencias" };
    }
    return { status: "approved", provider: "mock" };
  }

  if (PROVIDER === "onfido") {
    const endpoint = import.meta.env.VITE_ONFIDO_VERIFY_ENDPOINT;
    const apiKey = import.meta.env.VITE_ONFIDO_API_KEY;
    const { data } = await axios.post(
      endpoint,
      { documentFrontUrl, documentBackUrl, selfieUrl },
      { headers: { Authorization: `Token token=${apiKey}` } }
    );
    return { status: data.status || "pending", provider: "onfido", raw: data };
  }

  if (PROVIDER === "veriff") {
    const endpoint = import.meta.env.VITE_VERIFF_VERIFY_ENDPOINT;
    const apiKey = import.meta.env.VITE_VERIFF_API_KEY;
    const { data } = await axios.post(
      endpoint,
      { documentFrontUrl, documentBackUrl, selfieUrl },
      { headers: { "X-AUTH-CLIENT": apiKey } }
    );
    return { status: data.status || "pending", provider: "veriff", raw: data };
  }

  return { status: "pending", provider: PROVIDER };
};
