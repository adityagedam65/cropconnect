import React from "react";
import { Button } from "./button";

export function EmptyState({
  title = "No data available",
  description = "Get started by connecting your device or creating a new crop plan.",
  actionLabel,
  onAction,
  icon,
  className = "",
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center rounded-xl border border-dashed border-stone-300 dark:border-stone-700 bg-stone-50/50 dark:bg-stone-900/30 ${className}`}
      role="region"
      aria-label={title}
    >
      <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-700 dark:text-emerald-400 mb-3 shadow-inner">
        {icon || (
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        )}
      </div>
      <h3 className="text-base font-semibold text-stone-900 dark:text-stone-100">{title}</h3>
      <p className="text-sm text-stone-600 dark:text-stone-400 max-w-sm mt-1 mb-4">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} className="bg-emerald-700 hover:bg-emerald-800 text-white shadow-sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export default EmptyState;
