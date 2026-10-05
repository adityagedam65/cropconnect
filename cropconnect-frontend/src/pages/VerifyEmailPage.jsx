import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";
import { CheckCircle, Leaf } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { API } from "../lib/api";

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const email = params.get("email") || "";
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [verified, setVerified] = useState(false);

  const handleVerify = async () => {
    if (code.length !== 6) {
      toast.error("Enter the 6-digit code from your email.");
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API}/auth/verify-email`, { email, code });
      setVerified(true);
      toast.success("Email verified! You can now use your account.");
      setTimeout(() => navigate("/dashboard"), 2000);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Invalid or expired code. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex justify-center mb-8">
          <span className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-[#1B4332]">
            <Leaf className="w-5 h-5 text-[#FDFBF7]" strokeWidth={2.5} />
          </span>
        </div>

        {verified ? (
          <div className="text-center space-y-3">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
            <h1 className="font-display text-2xl text-[#1A201C]">Email verified!</h1>
            <p className="text-sm text-[#1A201C]/60">Redirecting to your dashboard...</p>
          </div>
        ) : (
          <>
            <h1 className="font-display text-2xl text-[#1A201C] text-center mb-2">
              Verify your email
            </h1>
            <p className="text-sm text-[#1A201C]/60 text-center mb-8">
              We sent a 6-digit code to <strong data-no-translate="true">{email}</strong>.
              Enter it below to activate your account.
            </p>
            <div className="space-y-4">
              <Input
                type="text"
                inputMode="numeric"
                maxLength={6}
                placeholder="000000"
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, "").slice(0, 6))}
                className="text-center text-2xl tracking-[0.5em] h-14 bg-[#FDFBF7] border-[#D5D1C5]"
              />
              <Button
                onClick={handleVerify}
                disabled={loading || code.length !== 6}
                className="w-full h-11 bg-[#1B4332] hover:bg-[#0F2A1F] text-[#FDFBF7] rounded-full"
              >
                {loading ? "Verifying..." : "Verify email"}
              </Button>
            </div>
            <p className="mt-6 text-xs text-center text-[#1A201C]/40">
              Didn't get the email? Check your spam folder or{" "}
              <button type="button" onClick={() => navigate("/signin")} className="underline">
                sign up again
              </button>
              .
            </p>
          </>
        )}
      </div>
    </div>
  );
}
