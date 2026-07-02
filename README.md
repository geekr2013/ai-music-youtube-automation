# AI Music YouTube Automation

무료 한도 중심으로 AI 음악 채널 운영을 자동화하는 MVP입니다.

## 포함된 기능

- GitHub Actions로 주 3회 자동 실행
- YouTube Data API로 영상 업로드
- 제목, 설명, 해시태그, 썸네일 자동 적용
- Kaggle Notebook 선택 연동으로 품질 점검/배치 작업 보조

## 기본 운영 방식

1. 음악과 이미지는 무료 도구로 제작합니다.
2. 완성 영상은 `content/videos`에 넣습니다.
3. 썸네일은 `content/thumbnails`에 넣습니다.
4. `content/metadata/upload_queue.json`에서 `status`를 `ready`로 둡니다.
5. GitHub Actions가 화/목/토 21:17 KST에 자동 업로드합니다.

## GitHub에 넣을 비밀값

YouTube Secrets:

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Kaggle Secrets, 선택사항:

- `KAGGLE_USERNAME`
- `KAGGLE_KEY`

GitHub Variables:

- `DEFAULT_PRIVACY_STATUS`: 처음에는 `private` 추천
- `REQUIRE_SYNTHETIC_MEDIA_DISCLOSURE`: `true` 추천
- `KAGGLE_KERNEL_SLUG`: 예시 `your-kaggle-name/ai-music-quality-pipeline`

## 주의

YouTube API 프로젝트가 검증되지 않은 경우, API 업로드 영상이 비공개로 제한될 수 있습니다. 처음에는 자동 비공개 업로드 후 YouTube Studio에서 직접 공개/예약 공개하는 방식을 추천합니다.
