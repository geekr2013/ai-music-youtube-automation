import fs from "node:fs";
import path from "node:path";
import { google } from "googleapis";

const queuePath = path.resolve("content/metadata/upload_queue.json");
const queue = JSON.parse(fs.readFileSync(queuePath, "utf8"));
const item = queue.find((entry) => entry.status === "ready");

if (!item) {
  throw new Error("No ready video found in upload queue.");
}

const requiredSecrets = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"];
for (const key of requiredSecrets) {
  if (!process.env[key]) {
    throw new Error(`GitHub Secret ${key} is required.`);
  }
}

const oauth2Client = new google.auth.OAuth2(
  process.env.YOUTUBE_CLIENT_ID,
  process.env.YOUTUBE_CLIENT_SECRET,
  "urn:ietf:wg:oauth:2.0:oob"
);

oauth2Client.setCredentials({
  refresh_token: process.env.YOUTUBE_REFRESH_TOKEN
});

const youtube = google.youtube({
  version: "v3",
  auth: oauth2Client
});

const videoPath = path.resolve(item.videoFile);
const thumbnailPath = path.resolve(item.thumbnailFile);
const privacyStatus = process.env.DEFAULT_PRIVACY_STATUS || "private";
const discloseSynthetic = process.env.REQUIRE_SYNTHETIC_MEDIA_DISCLOSURE !== "false";

const upload = await youtube.videos.insert({
  part: ["snippet", "status"],
  notifySubscribers: true,
  requestBody: {
    snippet: {
      title: item.title,
      description: item.description,
      tags: item.tags || [],
      categoryId: item.categoryId || "10",
      defaultLanguage: item.language || "en"
    },
    status: {
      privacyStatus,
      selfDeclaredMadeForKids: Boolean(item.madeForKids),
      containsSyntheticMedia: discloseSynthetic ? Boolean(item.containsSyntheticMedia) : undefined
    }
  },
  media: {
    body: fs.createReadStream(videoPath)
  }
});

const videoId = upload.data.id;

if (!videoId) {
  throw new Error("YouTube upload finished, but no videoId was returned.");
}

if (fs.existsSync(thumbnailPath)) {
  await youtube.thumbnails.set({
    videoId,
    media: {
      body: fs.createReadStream(thumbnailPath)
    }
  });
}

item.status = "uploaded";
item.youtubeVideoId = videoId;
item.uploadedAt = new Date().toISOString();
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

console.log(`Upload complete: https://www.youtube.com/watch?v=${videoId}`);
