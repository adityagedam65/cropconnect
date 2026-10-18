import React from "react";
import { Button } from "./button";

export function ErrorState({
  title = "Something went wrong",
  message = "An error occurred while loading this data. Please try again.",
  onRetry,
  retryLabel = "Try again",
  className = "",
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center rounded-xl border border-red-200 dark:border-red-900/60 bg-red-50/50 dark:bg-red-950/20 ${className}`}
      role="alert"
    >
      <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-950 flex items-center justify-center text-red-600 dark:text-red-400 mb-3">
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 className="text-base font-semibold text-stone-900 dark:text-stone-100">{title}</h3>
      <p className="text-sm text-stone-600 dark:text-stone-400 max-w-sm mt-1 mb-4">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="border-red-300 dark:border-red-800 hover:bg-red-100/50 text-red-700 dark:text-red-300">
          {retryLabel}
        </Button>
      )}
    </div>
  );
}

export default ErrorState;
