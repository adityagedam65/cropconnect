import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  Camera,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  ImagePlus,
  Leaf,
  LoaderCircle,
  RefreshCw,
  ScanLine,
  ShieldCheck,
  Trash2,
} from "lucide-react";
import { Button } from "../components/ui/button";
import {
  analyzeCropImage,
  CROP_SCAN_LIMITS,
  CROP_SCAN_STATES,
  validateCropImage,
} from "../services/cropScanService";

const qualityTips = [
  "Capture the affected leaf clearly",
  "Use good natural light and avoid blur",
  "Keep the leaf inside the frame",
  "Prefer a close-up without covering the leaf",
];

function BrandMark() {
  return (
    <Link to="/" className="inline-flex items-center gap-2" aria-label="CropConnect home">
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-[#1B4332] text-[#FDFBF7]"><Leaf className="h-4 w-4" /></span>
      <span className="font-display text-xl tracking-tight text-[#1A201C]">Crop<span className="text-[#1B4332]">Connect</span></span>
    </Link>
  );
}

function ScanError({ message, onDismiss }) {
  return (
    <div role="alert" className="flex items-start gap-3 rounded-xl border border-[#E07A5F]/35 bg-[#FFF4EF] p-4 text-sm text-[#8E3C2A]">
      <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
      <div className="flex-1"><p className="font-semibold">We could not use that photo</p><p className="mt-1">{message}</p></div>
      <button type="button" onClick={onDismiss} className="rounded p-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1B4332]" aria-label="Dismiss error">×</button>
    </div>
  );
}

function ResultCard({ result, onScanAgain }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><p className="text-sm font-semibold uppercase tracking-[0.16em] text-[#2D6A4F]">Scan result</p><h2 className="mt-2 font-display text-4xl text-[#1B4332]">{result.disease}</h2><p className="mt-1 text-[#4A5548]">Detected on {result.crop}</p></div>
        <div className="rounded-2xl bg-[#EDF6F0] px-5 py-3 text-right"><p className="text-xs uppercase tracking-wider text-[#52796F]">Confidence</p><p className="font-display text-3xl text-[#1B4332]">{result.confidence}%</p></div>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl bg-[#F4F1EA] p-4"><p className="text-xs uppercase tracking-wider text-[#52796F]">Crop</p><p className="mt-1 font-semibold text-[#1A201C]">{result.crop}</p></div>
        <div className="rounded-xl bg-[#F4F1EA] p-4"><p className="text-xs uppercase tracking-wider text-[#52796F]">Severity</p><p className="mt-1 font-semibold text-[#8E3C2A]">{result.severity}</p></div>
        <div className="rounded-xl bg-[#F4F1EA] p-4"><p className="text-xs uppercase tracking-wider text-[#52796F]">Model</p><p className="mt-1 font-mono text-xs text-[#4A5548]">{result.modelVersion}</p></div>
      </div>
      <div><h3 className="font-display text-2xl text-[#1B4332]">What we noticed</h3><p className="mt-2 leading-7 text-[#4A5548]">{result.symptoms}</p></div>
      <div><h3 className="font-display text-2xl text-[#1B4332]">Recommended next steps</h3><ul className="mt-3 space-y-3">{result.recommendations.map((recommendation) => <li key={recommendation} className="flex gap-3 text-sm leading-6 text-[#4A5548]"><CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-[#2D6A4F]" />{recommendation}</li>)}</ul></div>
      <div className="rounded-xl border border-[#E3C77B]/60 bg-[#FFF9E9] p-4 text-sm text-[#6C5A23]"><CircleHelp className="mr-2 inline h-4 w-4" />This result is guidance, not a confirmed diagnosis. Consult an agricultural expert before treatment.</div>
      <Button type="button" onClick={onScanAgain} className="h-11 rounded-full bg-[#1B4332] px-6 text-[#FDFBF7] hover:bg-[#0F2A1F]"><RefreshCw className="h-4 w-4" />Scan another crop</Button>
    </div>
  );
}

export default function CropScanPage() {
  const [state, setState] = useState(CROP_SCAN_STATES.IDLE);
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const cameraInputRef = useRef(null);
  const uploadInputRef = useRef(null);

  useEffect(() => () => { if (previewUrl) URL.revokeObjectURL(previewUrl); }, [previewUrl]);

  const selectFile = (nextFile) => {
    const validation = validateCropImage(nextFile);
    if (!validation.valid) { setError(validation.message); setState(CROP_SCAN_STATES.ERROR); return; }
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(nextFile); setPreviewUrl(URL.createObjectURL(nextFile)); setResult(null); setError(""); setState(CROP_SCAN_STATES.IMAGE_SELECTED);
  };

  const handleFileChange = (event) => { selectFile(event.target.files?.[0]); event.target.value = ""; };
  const removeImage = () => { if (previewUrl) URL.revokeObjectURL(previewUrl); setFile(null); setPreviewUrl(""); setResult(null); setError(""); setState(CROP_SCAN_STATES.IDLE); };
  const analyze = async () => {
    if (!file) { setError("Choose a crop photo before continuing."); setState(CROP_SCAN_STATES.ERROR); return; }
    setError(""); setState(CROP_SCAN_STATES.VALIDATING);
    try { setState(CROP_SCAN_STATES.ANALYZING); setResult(await analyzeCropImage(file)); setState(CROP_SCAN_STATES.RESULT); }
    catch (analysisError) { setError(analysisError.message || "The scan service is unavailable. Please try again."); setState(CROP_SCAN_STATES.ERROR); }
  };
  const scanAgain = () => { removeImage(); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const busy = state === CROP_SCAN_STATES.VALIDATING || state === CROP_SCAN_STATES.ANALYZING;

  return (
    <div className="min-h-screen bg-[#F4F1EA] text-[#1A201C]">
      <header className="border-b border-[#D5D1C5] bg-[#FDFBF7]/95 px-5 py-4 backdrop-blur sm:px-8"><div className="mx-auto flex max-w-6xl items-center justify-between"><BrandMark /><Link to="/dashboard" className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-[#1B4332] hover:bg-[#EDF6F0] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1B4332]"><ArrowLeft className="h-4 w-4" />Dashboard</Link></div></header>
      <main className="mx-auto max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
        <div className="mb-10 max-w-2xl"><div className="mb-4 inline-flex items-center gap-2 rounded-full bg-[#DDEDE2] px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-[#1B4332]"><ScanLine className="h-4 w-4" />Crop health check</div><h1 className="font-display text-4xl leading-tight text-[#1B4332] sm:text-6xl">Scan your crop</h1><p className="mt-4 max-w-xl text-base leading-7 text-[#4A5548]">Take a clear photo of an affected leaf or crop. CropConnect checks the image and returns guidance when it finds a reliable match.</p></div>
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
          <section className="rounded-2xl border border-[#D5D1C5] bg-[#FDFBF7] p-5 shadow-[0_12px_40px_rgba(27,67,50,0.06)] sm:p-8" aria-labelledby="scan-panel-title">
            {state === CROP_SCAN_STATES.RESULT && result ? <ResultCard result={result} onScanAgain={scanAgain} /> : <>
              <div className="mb-6 flex items-center gap-3"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#1B4332] text-[#FDFBF7]"><Camera className="h-5 w-5" /></div><div><h2 id="scan-panel-title" className="font-display text-2xl text-[#1B4332]">Add a crop photo</h2><p className="text-sm text-[#52796F]">JPG, PNG, or WebP up to 10 MB</p></div></div>
              {error && <div className="mb-5"><ScanError message={error} onDismiss={() => { setError(""); setState(file ? CROP_SCAN_STATES.IMAGE_SELECTED : CROP_SCAN_STATES.IDLE); }} /></div>}
              {previewUrl ? <div className="relative overflow-hidden rounded-2xl bg-[#0F2A1F]"><img src={previewUrl} alt="Selected crop for scanning" className="aspect-[4/3] w-full object-contain" /><div className="absolute inset-x-0 bottom-0 flex justify-between gap-3 bg-gradient-to-t from-black/70 to-transparent p-4 pt-12"><Button type="button" variant="outline" onClick={() => cameraInputRef.current?.click()} className="border-white/60 bg-black/25 text-white hover:bg-white/20"><RefreshCw className="h-4 w-4" />Retake</Button><Button type="button" variant="outline" onClick={removeImage} className="border-white/60 bg-black/25 text-white hover:bg-white/20"><Trash2 className="h-4 w-4" />Remove</Button></div></div> : <div className="rounded-2xl border-2 border-dashed border-[#B8CBBB] bg-[#F5FAF6] p-6 text-center sm:p-12"><div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[#DDEDE2] text-[#1B4332]"><ImagePlus className="h-8 w-8" /></div><h3 className="mt-5 font-display text-2xl text-[#1B4332]">Ready when you are</h3><p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-[#52796F]">Use your camera for a fresh photo or upload one from your phone.</p><div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row"><Button type="button" onClick={() => cameraInputRef.current?.click()} className="h-11 rounded-full bg-[#1B4332] px-6 text-[#FDFBF7] hover:bg-[#0F2A1F]"><Camera className="h-4 w-4" />Take a photo</Button><Button type="button" variant="outline" onClick={() => uploadInputRef.current?.click()} className="h-11 rounded-full border-[#1B4332]/25 px-6 text-[#1B4332]"><ImagePlus className="h-4 w-4" />Upload image</Button></div></div>}
              <input ref={cameraInputRef} type="file" accept={CROP_SCAN_LIMITS.acceptedTypes.join(",")} capture="environment" onChange={handleFileChange} className="sr-only" aria-label="Take a crop photo" /><input ref={uploadInputRef} type="file" accept={CROP_SCAN_LIMITS.acceptedTypes.join(",")} onChange={handleFileChange} className="sr-only" aria-label="Upload a crop image" />
              {previewUrl && <Button type="button" disabled={busy} onClick={analyze} className="mt-6 h-12 w-full rounded-full bg-[#E07A5F] text-white hover:bg-[#C9654A]">{busy ? <><LoaderCircle className="h-4 w-4 animate-spin" />Checking photo...</> : <><ScanLine className="h-4 w-4" />Continue to analysis</>}</Button>}
              {busy && <p className="mt-3 text-center text-xs text-[#52796F]" role="status">{state === CROP_SCAN_STATES.VALIDATING ? "Checking that the image contains a plant..." : "Preparing the development preview..."}</p>}
            </>}
          </section>
          <aside className="space-y-4"><div className="rounded-2xl bg-[#1B4332] p-6 text-[#FDFBF7]"><ShieldCheck className="h-6 w-6 text-[#E3C77B]" /><h2 className="mt-4 font-display text-2xl">A clearer photo helps</h2><ul className="mt-4 space-y-3 text-sm leading-6 text-[#E4EFE6]">{qualityTips.map((tip) => <li key={tip} className="flex gap-2"><CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-[#E3C77B]" />{tip}</li>)}</ul></div><div className="rounded-2xl border border-[#D5D1C5] bg-[#FDFBF7] p-6"><h2 className="font-display text-xl text-[#1B4332]">Need another view?</h2><p className="mt-2 text-sm leading-6 text-[#52796F]">Return to your farm dashboard to review your sensor readings and crop information.</p><Link to="/dashboard" className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-[#1B4332]">View farm dashboard <ChevronRight className="h-4 w-4" /></Link></div></aside>
        </div>
      </main>
    </div>
  );
}
