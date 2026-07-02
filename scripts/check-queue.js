import fs from "node:fs";
import path from "node:path";

const queuePath = path.resolve("content/metadata/upload_queue.json");

if (!fs.existsSync(queuePath)) {
  throw new Error("upload_queue.json file is missing.");
}

const queue = JSON.parse(fs.readFileSync(queuePath, "utf8"));
const ready = queue.filter((item) => item.status === "ready");

if (ready.length === 0) {
  throw new Error("No ready video found in upload queue.");
}

const next = ready[0];
const missing = [next.videoFile, next.thumbnailFile].filter((file) => !fs.existsSync(path.resolve(file)));

if (missing.length > 0) {
  throw new Error(`Missing upload file(s): ${missing.join(", ")}`);
}

console.log(`Next upload target: ${next.title}`);
