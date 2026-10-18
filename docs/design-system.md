# CropConnect: Design System & Frontend Architecture (Layer 6)

## 1. Style Direction & Philosophy
CropConnect breaks away from generic, clinical SaaS templates by adopting an agricultural-inspired organic aesthetic:
- **Warm Canvas**: Eggshell & parchment whites (`#FDFBF7`, `#F7F4EB`) evoking soil and harvest paper.
- **Forest & Field Accents**: Deep pine and emerald greens (`#1B4332`, `#2D6A4F`, `#40916C`) indicating healthy plant life and irrigation.
- **Alert & Soil Warmth**: Clay terracottas, amber rusts (`#B45309`, `#DC2626`), and soft grain overlays.
- **Typography Pairing**: Editorial serif headlines (`Fraunces` / `DM Serif Display`) paired with crisp, highly legible sans-serif data tables (`DM Sans`).

---

## 2. Token Architecture

### Color Palette Tokens
| Token | Light Value | Dark Value | Usage |
|---|---|---|---|
| `bg-canvas` | `#FDFBF7` | `#0F1411` | Application background |
| `bg-surface` | `#FFFFFF` | `#1A221E` | Card & container surface |
| `text-primary` | `#1A201C` | `#F4F6F4` | Primary high-contrast text |
| `text-muted` | `#5A665E` | `#9BA9A0` | Secondary descriptions |
| `primary-green` | `#2D6A4F` | `#40916C` | Buttons, active navigation, healthy metrics |
| `accent-amber` | `#D97706` | `#F59E0B` | Low moisture warning, pending sync |
| `accent-red` | `#DC2626` | `#EF4444` | Sensor disconnect, pump failure |
| `border-subtle`| `#E5E0D4` | `#28332C` | Card borders and divider lines |

### Radii Scale
- `rounded-sm`: 4px (tags, tooltips)
- `rounded-md`: 8px (form inputs, default buttons)
- `rounded-xl`: 14px (cards, widgets)
- `rounded-2xl`: 20px (modals, dialog sheets)

---

## 3. Base Component Catalog (`cropconnect-frontend/src/components/ui/`)
1. **Button** (`button.jsx`): Variants: `default`, `secondary`, `outline`, `destructive`, `ghost`. States: default, hover, focus-visible, active, disabled, loading.
2. **Input** (`input.jsx`): Semantic text/password inputs with visible focus rings and inline error support.
3. **Select** (`select.jsx`): Accessible dropdown selector with chevron indicator.
4. **Modal** (`modal.jsx`): Accessible dialog with backdrop blur, Escape key listener, and focus trapping.
5. **Toast** (`Toaster` via Sonner): Contextual feedback toasts (`toast.success`, `toast.error`, `toast.info`).
6. **Table** (`table.jsx`): Responsive time-series data table for sensor logs and mandi prices.
7. **Skeleton** (`skeleton.jsx`): Shimmering placeholder animations preventing layout shift.
8. **EmptyState** (`empty-state.jsx`): Friendly empty state featuring illustrative icon, helpful guidance, and clear primary CTA.
9. **ErrorState** (`error-state.jsx`): Clear error banner with actionable retry button.

---

## 4. The 4 Data-Driven States (Layer 6b)
Every data view in CropConnect implements all four lifecycle states:
1. **Loading State**: Content-shaped Skeletons rendering immediate structural layout while network requests resolve.
2. **Empty State**: Replaces blank cards with an explicit description of why no data is present and an action button to initiate data flow (e.g. "Connect ESP32").
3. **Error State**: Displays a contextual, non-technical explanation accompanied by a "Try Again" retry handler.
4. **Success State**: Clean presentation of live telemetry, pump status, or AI diagnostic output.

---

## 5. Responsive & Accessibility Standards (WCAG 2.1 AA)
- **Mobile First**: Tested and fully interactive down to 375px mobile viewport widths.
- **Form Controls**: Every form element has explicit `<label htmlFor="...">` associations.
- **Keyboard Navigation**: All interactive elements are reachable via `Tab`, with visible `focus-visible:ring-2` focus rings.
- **Color Contrast**: 4.5:1 minimum contrast ratio for body text; 3:1 for large display headlines.
- **ARIA & Roles**: Modals declare `role="dialog"` with `aria-modal="true"`; error states declare `role="alert"`.

---

## 6. Living Showcase (`/design`)
A dedicated design catalog is available at route **`/design`**, presenting all base components across every state.
