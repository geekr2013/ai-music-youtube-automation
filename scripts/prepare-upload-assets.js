import fs from "node:fs";
import path from "node:path";
import { pipeline } from "node:stream/promises";

const queuePath = path.resolve("content/metadata/upload_queue.json");
const queue = JSON.parse(fs.readFileSync(queuePath, "utf8"));
const item = queue.find((entry) => entry.status === "ready");

if (!item) {
  throw new Error("No ready video found in upload queue.");
}

async function downloadIfNeeded(url, targetFile) {
  if (!url || fs.existsSync(targetFile)) {
    return;
  }

  fs.mkdirSync(path.dirname(targetFile), { recursive: true });

  const response = await fetch(url);
  if (!response.ok || !response.body) {
    throw new Error(`Failed to download ${url}: ${response.status} ${response.statusText}`);
  }

  await pipeline(response.body, fs.createWriteStream(targetFile));
}

await downloadIfNeeded(item.videoUrl, path.resolve(item.videoFile));
await downloadIfNeeded(item.thumbnailUrl, path.resolve(item.thumbnailFile));

console.log(`Assets prepared for: ${item.title}`);
