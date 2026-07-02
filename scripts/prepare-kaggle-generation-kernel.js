import fs from "node:fs";
import path from "node:path";

const slug = process.env.KAGGLE_GENERATION_KERNEL_SLUG || process.env.KAGGLE_KERNEL_SLUG;

if (!slug || !slug.includes("/")) {
  throw new Error("GitHub Variable KAGGLE_GENERATION_KERNEL_SLUG is required. Example: your-kaggle-name/ai-music-video-generator");
}

const [owner, slugName] = slug.split("/");
const kaggleUsername = process.env.KAGGLE_USERNAME;

if (kaggleUsername && owner.toLowerCase() !== kaggleUsername.toLowerCase()) {
  throw new Error(`KAGGLE_GENERATION_KERNEL_SLUG owner (${owner}) must match KAGGLE_USERNAME (${kaggleUsername}).`);
}

const title = slugName
  .split("-")
  .filter(Boolean)
  .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
  .join(" ");

const metadata = {
  id: slug,
  title,
  code_file: "generate_music_video.py",
  language: "python",
  kernel_type: "script",
  is_private: true,
  enable_gpu: false,
  enable_internet: false,
  dataset_sources: [],
  competition_sources: [],
  kernel_sources: []
};

fs.writeFileSync(
  path.resolve("kaggle/kernel-metadata.json"),
  `${JSON.stringify(metadata, null, 2)}\n`
);

console.log(`Kaggle generation kernel metadata prepared: ${slug}`);
