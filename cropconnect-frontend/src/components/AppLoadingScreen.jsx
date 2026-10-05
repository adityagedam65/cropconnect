import { Leaf } from "lucide-react";

export default function AppLoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#FDFBF7]">
      <div className="flex flex-col items-center gap-4">
        <span className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-[#1B4332] text-[#FDFBF7] shadow-sm">
          <Leaf className="h-10 w-10" strokeWidth={2.5} />
        </span>
        <div className="flex gap-2" aria-label="Loading">
          {[0, 1, 2].map((item) => (
            <span
              key={item}
              className="h-2 w-2 rounded-full bg-[#1B4332] animate-pulse"
              style={{ animationDelay: `${item * 140}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
