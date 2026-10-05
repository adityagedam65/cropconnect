import "@/App.css";
import { lazy, Suspense, useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "sonner";
import { API, AUTH_CACHE_KEY, authHeaders, readAuthToken, readSessionUser } from "./lib/api";

import AppLoadingScreen from "./components/AppLoadingScreen";
import OfflineBanner from "./components/OfflineBanner";
import { LandingLanguageProvider } from "./contexts/AppLanguageContext";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const SignInPage = lazy(() => import("./pages/SignInPage"));
const ForgotPasswordPage = lazy(() => import("./pages/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("./pages/ResetPasswordPage"));
const VerifyEmailPage = lazy(() => import("./pages/VerifyEmailPage"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const CropPlanner = lazy(() => import("./pages/CropPlanner"));
const CropScanPage = lazy(() => import("./pages/CropScanPage"));
const LegalPage = lazy(() => import("./pages/LegalPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

export { AUTH_CACHE_KEY } from "./lib/api";
const AUTH_CACHE_TTL = 60_000;

export function ProtectedPage({ children }) {
  const location = useLocation();
  const [authState, setAuthState] = useState(() => {
    const cached = sessionStorage.getItem(AUTH_CACHE_KEY);
    if (cached) {
      try {
        const { ok, ts } = JSON.parse(cached);
        if (ok && readAuthToken() && Date.now() - ts < AUTH_CACHE_TTL) return "allowed";
      } catch {
        sessionStorage.removeItem(AUTH_CACHE_KEY);
      }
    }
    if (readSessionUser() && readAuthToken()) return "allowed";
    return "checking";
  });

  useEffect(() => {
    if (authState !== "checking") return undefined;
    let cancelled = false;

    fetch(`${API}/auth/profile`, {
      credentials: "include",
      headers: authHeaders(),
    })
      .then((response) => {
        if (!cancelled) {
          if (response.ok) {
            sessionStorage.setItem(AUTH_CACHE_KEY, JSON.stringify({ ok: true, ts: Date.now() }));
            setAuthState("allowed");
          } else {
            sessionStorage.setItem(AUTH_CACHE_KEY, JSON.stringify({ ok: false, ts: Date.now() }));
            setAuthState("denied");
          }
        }
      })
      .catch(() => {
        if (!cancelled) {
          sessionStorage.setItem(AUTH_CACHE_KEY, JSON.stringify({ ok: false, ts: Date.now() }));
          setAuthState("denied");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [authState]);

  if (authState === "checking") {
    return <AppLoadingScreen />;
  }

  if (authState === "denied") {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}

function App() {
  return (
    <div className="App grain" data-auto-translate-root="true">
      <LandingLanguageProvider>
        <OfflineBanner />
        <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
          <Suspense fallback={<AppLoadingScreen />}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signin" element={<SignInPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/terms" element={<LegalPage type="terms" />} />
              <Route path="/privacy" element={<LegalPage type="privacy" />} />
              <Route path="/dashboard" element={<ProtectedPage><Dashboard /></ProtectedPage>} />
              <Route path="/crop-planner" element={<ProtectedPage><CropPlanner /></ProtectedPage>} />
              <Route path="/crop-scan" element={<CropScanPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </LandingLanguageProvider>
      <Toaster
        position="top-right"
        richColors
        closeButton
        toastOptions={{
          style: {
            background: "#FDFBF7",
            color: "#1A201C",
            border: "1px solid #D5D1C5",
            fontFamily: "DM Sans, sans-serif",
          },
        }}
      />
    </div>
  );
}

export default App;
