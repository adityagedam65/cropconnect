import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(__dirname, "../public");
const sourceIcon = path.join(publicDir, "icon.svg");

if (!existsSync(sourceIcon)) {
  // Clear error beats a cryptic sharp/ENOENT stack trace in CI.
  console.error(`ERROR: Source icon not found at ${sourceIcon}`);
  console.error("Run this script from the cropconnect-frontend directory.");
  process.exit(1);
}

const targets = [
  ["icon-192.png", 192],
  ["icon-512.png", 512],
  ["apple-touch-icon.png", 180],
];

await Promise.all(
  targets.map(([filename, size]) =>
    sharp(sourceIcon)
      .resize(size, size)
      .png()
      .toFile(path.join(publicDir, filename)),
  ),
);

console.log("Generated PWA icons from public/icon.svg");
