# Tech Registration Frontend

React + Tailwind + Axios form for technician onboarding with:
- Cloudinary uploads (document front/back, selfie, portfolio)
- Identity verification mock (Onfido/Veriff-ready)
- Firebase OTP SMS
- Signature canvas
- Real-time validations with Zod + React Hook Form

## Setup

1. Install dependencies:
   npm install

2. Create `.env` from `.env.example` and fill keys.

3. Run:
   npm run dev

## Notes

- Backend submit endpoint in [src/App.jsx](src/App.jsx): `/api/technicians/register`.
- Change identity provider with `VITE_ID_PROVIDER=mock|onfido|veriff`.
