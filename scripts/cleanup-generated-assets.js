import fs from "node:fs";
import path from "node:path";

const targets = [
  "kaggle-output",
  "content/videos",
  "content/thumbnails"
];

for (const target of targets) {
  const resolved = path.resolve(target);
  if (!fs.existsSync(resolved)) {
    continue;
  }

  for (const entry of fs.readdirSync(resolved)) {
    if (entry === ".gitkeep") {
      continue;
    }
    fs.rmSync(path.join(resolved, entry), { recursive: true, force: true });
  }
}

const queuePath = "content/metadata/upload_queue.json";
if (fs.existsSync(queuePath)) {
  fs.writeFileSync(queuePath, "[]\n");
}

console.log("Generated assets cleaned up after upload.");
