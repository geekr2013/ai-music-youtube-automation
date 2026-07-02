import fs from "node:fs";
import path from "node:path";

const slug = process.env.KAGGLE_GENERATION_KERNEL_SLUG || process.env.KAGGLE_KERNEL_SLUG;

if (!slug || !slug.includes("/")) {
  throw new Error("GitHub Variable KAGGLE_GENERATION_KERNEL_SLUG is required. Example: your-kaggle-name/ai-music-video-generator");
}

const metadata = {
  id: slug,
  title: "AI Music Video Generator",
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
