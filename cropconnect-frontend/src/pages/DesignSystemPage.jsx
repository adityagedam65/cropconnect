import React, { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

export default function DesignSystemPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [selectedRole, setSelectedRole] = useState("Owner");

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-[#1A201C] p-6 sm:p-12 font-sans selection:bg-emerald-200">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <header className="border-b border-stone-200 pb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 mb-2">
            Layer 6: Frontend & Design System
          </div>
          <h1 className="text-3xl sm:text-4xl font-serif font-bold text-stone-900 tracking-tight">
            CropConnect Design System
          </h1>
          <p className="text-stone-600 mt-2 max-w-2xl">
            Living component catalog and state showcase. All components adhere to the 4 data-driven states
            (loading, empty, error, success) and WCAG 2.1 AA accessibility standards.
          </p>
        </header>

        {/* 1. Buttons */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold font-serif text-stone-800 border-b border-stone-200 pb-2">
            1. Buttons & Variants
          </h2>
          <div className="flex flex-wrap gap-4 items-center">
            <Button onClick={() => toast.success("Default action clicked")}>Default Button</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="ghost">Ghost</Button>
            <Button disabled>Disabled</Button>
            <Button size="sm">Small</Button>
            <Button size="lg">Large</Button>
          </div>
        </section>

        {/* 2. Inputs & Select */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold font-serif text-stone-800 border-b border-stone-200 pb-2">
            2. Form Controls (Input & Select)
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl">
            <div>
              <label htmlFor="design-input" className="block text-xs font-semibold text-stone-700 uppercase tracking-wider mb-1.5">
                Farm Name (Text Input)
              </label>
              <Input
                id="design-input"
                placeholder="e.g. Green Valley Farm"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="design-select" className="block text-xs font-semibold text-stone-700 uppercase tracking-wider mb-1.5">
                User Role (Select)
              </label>
              <Select
                id="design-select"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                <option value="Owner">Owner (Full admin + tenant management)</option>
                <option value="Admin">Admin (Farm ops & controls)</option>
                <option value="Member">Member (Telemetry & crop planning)</option>
                <option value="Viewer">Viewer (Read-only)</option>
              </Select>
            </div>
          </div>
        </section>

        {/* 3. The 4 Data-Driven States */}
        <section className="space-y-6">
          <h2 className="text-xl font-bold font-serif text-stone-800 border-b border-stone-200 pb-2">
            3. Four Data-Driven States (Layer 6b)
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Loading State with Skeletons */}
            <div className="p-6 rounded-xl border border-stone-200 bg-white space-y-3">
              <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider">State 1: Loading</span>
              <div className="space-y-2">
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <div className="pt-2 flex gap-2">
                  <Skeleton className="h-9 w-24" />
                  <Skeleton className="h-9 w-24" />
                </div>
              </div>
            </div>

            {/* Empty State */}
            <div className="p-6 rounded-xl border border-stone-200 bg-white">
              <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider block mb-2">State 2: Empty</span>
              <EmptyState
                title="No telemetry logged yet"
                description="Power on your ESP32 device with SIM800L module to stream field moisture."
                actionLabel="Connect Device"
                onAction={() => toast.info("Opening ESP32 setup flow")}
              />
            </div>

            {/* Error State with Retry */}
            <div className="p-6 rounded-xl border border-stone-200 bg-white">
              <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider block mb-2">State 3: Error</span>
              <ErrorState
                title="Failed to fetch Mandi rates"
                message="Data.gov.in API timed out. Your connection or API rate limit may be impacted."
                onRetry={() => toast.success("Retrying mandi query...")}
              />
            </div>

            {/* Success State */}
            <div className="p-6 rounded-xl border border-stone-200 bg-white">
              <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider block mb-2">State 4: Success</span>
              <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-200 flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0">
                  ✓
                </div>
                <div>
                  <h4 className="text-sm font-bold text-emerald-900">Pump Cycle Completed</h4>
                  <p className="text-xs text-emerald-700 mt-0.5">
                    Field 2 pump automatically turned OFF after reaching 42% target soil moisture.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 4. Table Component */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold font-serif text-stone-800 border-b border-stone-200 pb-2">
            4. Data Table
          </h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Sensor Channel</TableHead>
                <TableHead>Field Location</TableHead>
                <TableHead>Moisture (%)</TableHead>
                <TableHead>Temperature (°C)</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Zone 1 — Wheat</TableCell>
                <TableCell>North Acre</TableCell>
                <TableCell>38%</TableCell>
                <TableCell>24.5°C</TableCell>
                <TableCell><span className="px-2 py-0.5 text-xs rounded-full bg-emerald-100 text-emerald-800 font-medium">Optimal</span></TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Zone 2 — Mustard</TableCell>
                <TableCell>South Plot</TableCell>
                <TableCell>19%</TableCell>
                <TableCell>28.1°C</TableCell>
                <TableCell><span className="px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-800 font-medium">Needs Irrigation</span></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </section>

        {/* 5. Modal Dialog & Toasts */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold font-serif text-stone-800 border-b border-stone-200 pb-2">
            5. Modal Dialog & Toasts
          </h2>
          <div className="flex gap-4">
            <Button onClick={() => setModalOpen(true)}>Open Test Modal</Button>
            <Button variant="outline" onClick={() => toast.info("Triggered sample sonner notification")}>
              Trigger Toast Notification
            </Button>
          </div>

          <Modal
            isOpen={modalOpen}
            onClose={() => setModalOpen(false)}
            title="Configure Pump Schedule"
            description="Set automated irrigation thresholds for Zone 1 based on live soil moisture."
            footer={
              <>
                <Button variant="outline" onClick={() => setModalOpen(false)}>Cancel</Button>
                <Button onClick={() => { setModalOpen(false); toast.success("Schedule saved successfully"); }}>
                  Save Schedule
                </Button>
              </>
            }
          >
            <p className="text-sm text-stone-600">
              When moisture drops below 25%, the pump will automatically trigger via the ESP32 relay command queue.
            </p>
          </Modal>
        </section>
      </div>
    </div>
  );
}
