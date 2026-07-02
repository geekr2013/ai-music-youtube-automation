import fs from "node:fs";
import path from "node:path";

const slug = process.env.KAGGLE_KERNEL_SLUG;

if (!slug || !slug.includes("/")) {
  throw new Error("GitHub Variable KAGGLE_KERNEL_SLUG is required. Example: your-kaggle-name/ai-music-quality-pipeline");
}

const metadata = {
  id: slug,
  title: "AI Music Quality Pipeline",
  code_file: "quality_pipeline.py",
  language: "python",
  kernel_type: "script",
  is_private: true,
  enable_gpu: true,
  enable_internet: false,
  dataset_sources: [],
  competition_sources: [],
  kernel_sources: []
};

fs.writeFileSync(
  path.resolve("kaggle/kernel-metadata.json"),
  `${JSON.stringify(metadata, null, 2)}\n`
);

console.log(`Kaggle kernel metadata prepared: ${slug}`);
