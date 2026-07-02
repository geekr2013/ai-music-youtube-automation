# YouTube Auto Upload Setup

목표: GitHub가 매주 화/목/토 밤 9시 17분(KST)에 자동으로 다음 영상을 YouTube에 업로드합니다.

## 현재 구성

- 실행 시간: 매주 화, 목, 토 21:17 KST
- 업로드 대상: `content/metadata/upload_queue.json`에서 `status`가 `ready`인 첫 번째 영상
- 영상 파일 위치: `content/videos`
- 썸네일 위치: `content/thumbnails`
- 기본 공개 상태: `private`

## 왜 기본값이 private인가요?

YouTube 공식 문서 기준, 검증되지 않은 API 프로젝트로 업로드한 영상은 비공개로 제한될 수 있습니다. 완전 자동 공개 업로드를 안정적으로 쓰려면 Google API 프로젝트 검증이 필요할 수 있습니다.

그래서 MVP는 다음 순서가 안전합니다.

1. 자동 업로드는 private로 진행
2. YouTube Studio에서 품질 확인
3. 문제가 없으면 직접 공개 또는 예약 공개
4. 채널 운영이 안정화되면 Google API 검증 후 public/scheduled 자동화로 전환

## GitHub에 넣어야 하는 값

GitHub 저장소의 Settings > Secrets and variables > Actions에 아래 값을 넣습니다.

Secrets:

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Variables:

- `DEFAULT_PRIVACY_STATUS`: 처음에는 `private` 추천
- `REQUIRE_SYNTHETIC_MEDIA_DISCLOSURE`: `true` 추천

## YouTube refresh token 발급 개념

이미 Client ID와 Client Secret을 만들었다면 다음 단계는 refresh token 발급입니다.

refresh token은 GitHub Actions가 사용자 대신 YouTube 업로드 권한을 계속 사용할 수 있게 해주는 장기 토큰입니다.

발급할 때 필요한 권한 범위는 아래입니다.

```text
https://www.googleapis.com/auth/youtube.upload
```

## 업로드 파일

예시:

- `content/videos/glow-up-late.mp4`
- `content/thumbnails/glow-up-late.jpg`

그리고 `content/metadata/upload_queue.json`에 제목, 설명, 해시태그, 카테고리, 언어를 적습니다.

## 참고

- YouTube Data API videos.insert: https://developers.google.com/youtube/v3/docs/videos/insert
- GitHub Actions schedule: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
