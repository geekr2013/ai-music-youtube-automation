import fs from "node:fs";
import path from "node:path";

const outputDir = path.resolve("kaggle-output");
const metadataPath = path.join(outputDir, "metadata.json");

if (!fs.existsSync(metadataPath)) {
  throw new Error("Kaggle output metadata.json was not found.");
}

const metadata = JSON.parse(fs.readFileSync(metadataPath, "utf8"));
const videoFile = path.join(outputDir, metadata.videoFile || "final_video.mp4");
const thumbnailFile = path.join(outputDir, metadata.thumbnailFile || "thumbnail.jpg");

if (!fs.existsSync(videoFile)) {
  throw new Error(`Generated video file was not found: ${videoFile}`);
}

if (!fs.existsSync(thumbnailFile)) {
  throw new Error(`Generated thumbnail file was not found: ${thumbnailFile}`);
}

fs.mkdirSync("content/videos", { recursive: true });
fs.mkdirSync("content/thumbnails", { recursive: true });
fs.mkdirSync("content/metadata", { recursive: true });

const safeId = metadata.id || new Date().toISOString().replace(/[:.]/g, "-");
const targetVideo = `content/videos/${safeId}.mp4`;
const targetThumbnail = `content/thumbnails/${safeId}.jpg`;

fs.copyFileSync(videoFile, targetVideo);
fs.copyFileSync(thumbnailFile, targetThumbnail);

const queue = [
  {
    id: safeId,
    status: "ready",
    videoFile: targetVideo,
    thumbnailFile: targetThumbnail,
    videoUrl: "",
    thumbnailUrl: "",
    title: metadata.title,
    description: metadata.description,
    tags: metadata.tags || [],
    categoryId: metadata.categoryId || "10",
    language: metadata.language || "en",
    madeForKids: false,
    containsSyntheticMedia: true
  }
];

fs.writeFileSync("content/metadata/upload_queue.json", `${JSON.stringify(queue, null, 2)}\n`);
console.log(`Prepared generated upload: ${metadata.title}`);
