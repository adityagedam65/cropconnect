import { Link } from "react-router-dom";
import { ArrowLeft, Leaf } from "lucide-react";

const COPY = {
  terms: {
    title: "Terms of Service",
    lastUpdated: "May 2026",
    sections: [
      {
        heading: "What CropConnect does",
        body: "CropConnect is an agricultural IoT dashboard. It receives sensor telemetry from an ESP32 field node via your SIM800L connection, stores readings in a MySQL database, and shows them in your browser dashboard. It also provides AI-assisted crop planning and remote pump command queuing.",
      },
      {
        heading: "AI advice is guidance, not instruction",
        body: "AI-generated crop planning, fertiliser suggestions, and irrigation advice are informational. Do not treat them as certified agronomy, medical, legal, or safety instructions. Always confirm critical decisions, especially chemical application, wiring, and pump operation, with qualified local experts.",
      },
      {
        heading: "You are responsible for your hardware",
        body: "You are responsible for the safe installation and operation of your ESP32 node, pump relay hardware, SIM800L cellular module, and field wiring. CropConnect queues pump commands but cannot verify physical safety conditions at your site.",
      },
      {
        heading: "Account security",
        body: "Keep your login credentials and ESP32 device API key private. You are responsible for all activity under your account. Notify us immediately at cropconnectco@gmail.com if you suspect unauthorised access.",
      },
      {
        heading: "Service availability",
        body: "CropConnect is a prototype platform. We do not guarantee uptime or data continuity. Do not use it as the sole control system for safety-critical irrigation. Always maintain manual override capability at your pump site.",
      },
      {
        heading: "Changes to these terms",
        body: "We may update these terms as the platform develops. Continued use after changes are posted constitutes acceptance.",
      },
    ],
  },
  privacy: {
    title: "Privacy Policy",
    lastUpdated: "May 2026",
    sections: [
      {
        heading: "What data we store",
        body: "We store your email address, hashed password, and profile fields such as name, phone, state, district, city, village, and land size. We also store your ESP32 device ID, sensor readings, pump state, pump timer schedules, and AI chat history associated with your account.",
      },
      {
        heading: "How sensitive data is protected",
        body: "Sensitive profile fields are encrypted at rest when the backend is configured with CROP_DATA_SECRET_KEY. Your password is not stored as plain text; the backend stores a password hash. Login uses an HTTP-only cookie plus a CSRF token.",
      },
      {
        heading: "Your browser storage",
        body: "CropConnect does not store your full profile or sensor data in localStorage. Browser storage may hold short-lived session helper data and user interface preferences such as language and theme.",
      },
      {
        heading: "Sensor and telemetry data",
        body: "Sensor readings sent by your ESP32 node are tied to your account and device identity. Each device has a unique API key so other accounts cannot write telemetry for your device.",
      },
      {
        heading: "Who can see your data",
        body: "Your data is visible to you when logged in. We do not sell your data. AI chat queries may be sent through the backend AI service to generate responses, so avoid entering unnecessary sensitive personal information in chat messages.",
      },
      {
        heading: "Data retention and deletion",
        body: "You can request deletion of your account and associated data by emailing cropconnectco@gmail.com. We will process deletion requests within 14 days.",
      },
      {
        heading: "Contact",
        body: "For privacy questions, contact us at cropconnectco@gmail.com or by phone at +91 94791 87552.",
      },
    ],
  },
};

export default function LegalPage({ type = "terms" }) {
  const copy = COPY[type] || COPY.terms;

  return (
    <div className="min-h-screen bg-[#FDFBF7] px-4 py-10">
      <div className="mx-auto max-w-3xl">
        <Link to="/" className="inline-flex items-center gap-2 text-[#1B4332]">
          <Leaf className="h-5 w-5" />
          <span className="font-display text-xl">CropConnect</span>
        </Link>

        <div className="mt-8 rounded-xl border border-[#D5D1C5] bg-white p-6 shadow-sm">
          <h1 className="font-display text-3xl text-[#1A201C]">{copy.title}</h1>
          <div className="mt-6 space-y-6 text-sm leading-6 text-[#1A201C]/75">
            {copy.sections.map((section) => (
              <div key={section.heading}>
                <h2 className="font-semibold text-[#1A201C] mb-1">{section.heading}</h2>
                <p>{section.body}</p>
              </div>
            ))}
          </div>
          {copy.lastUpdated && (
            <p className="mt-8 text-xs text-[#1A201C]/40">Last updated: {copy.lastUpdated}</p>
          )}
          <Link to="/login" className="mt-8 inline-flex items-center gap-2 text-sm font-medium text-[#1B4332]">
            <ArrowLeft className="h-4 w-4" />
            Back to sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
