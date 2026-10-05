import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import CropScanPage from "./CropScanPage";

function renderPage() {
  return render(<MemoryRouter><CropScanPage /></MemoryRouter>);
}

describe("CropScanPage", () => {
  it("rejects unsupported files without crashing", () => {
    renderPage();
    const input = screen.getByLabelText("Upload a crop image");
    fireEvent.change(input, { target: { files: [new File(["text"], "notes.txt", { type: "text/plain" })] } });
    expect(screen.getByRole("alert")).toHaveTextContent("Please choose a JPG, PNG, or WebP image.");
  });

  it("shows a valid image preview and analysis action", () => {
    renderPage();
    const input = screen.getByLabelText("Upload a crop image");
    fireEvent.change(input, { target: { files: [new File(["image"], "leaf.jpg", { type: "image/jpeg" })] } });
    expect(screen.getByAltText("Selected crop for scanning")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /continue to analysis/i })).toBeInTheDocument();
  });

  it("asks for a correct crop or leaf photo when validation rejects the image", async () => {
    renderPage();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ valid_image: false, message: "Please upload a proper crop or leaf photo." }),
    }));
    const input = screen.getByLabelText("Upload a crop image");
    fireEvent.change(input, { target: { files: [new File(["image"], "photo.jpg", { type: "image/jpeg" })] } });
    fireEvent.click(screen.getByRole("button", { name: /continue to analysis/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Please upload a proper crop or leaf photo.");
    vi.unstubAllGlobals();
  });
});
