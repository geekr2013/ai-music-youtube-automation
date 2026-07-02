# AI Music YouTube Automation

무료 한도 중심으로 AI 음악 채널 운영을 자동화하는 MVP입니다.

## 포함된 기능

- GitHub Actions로 주 3회 자동 실행
- Kaggle에서 음악, 배경 이미지 여러 장, 영상 자동 생성
- YouTube Data API로 자동 업로드
- 제목, 설명, 해시태그, 썸네일 자동 생성
- 업로드 후 생성 파일 정리

## 기본 운영 방식

1. GitHub Actions가 화/목/토 21:23 KST에 실행됩니다.
2. Kaggle이 10대/20대 취향의 전자음악 계열 콘셉트를 고릅니다.
3. 오리지널 음악, 여러 장의 배경 이미지, 최종 영상을 생성합니다.
4. GitHub Actions가 생성 결과를 받아 YouTube에 업로드합니다.
5. 업로드가 끝나면 임시 영상/이미지 파일을 정리합니다.

## 핵심 워크플로

- `Generate and Upload AI Music Video`: 정기 자동 생성 + 업로드
- `YouTube Manual Upload`: 직접 준비한 영상이 있을 때만 수동 업로드
- `Kaggle Quality Pipeline`: 품질 점검용 수동 실행

## GitHub에 넣을 비밀값

YouTube Secrets:

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

Kaggle Secrets:

- `KAGGLE_USERNAME`
- `KAGGLE_KEY`

GitHub Variables:

- `DEFAULT_PRIVACY_STATUS`: 처음에는 `private` 추천
- `REQUIRE_SYNTHETIC_MEDIA_DISCLOSURE`: `true` 추천
- `KAGGLE_GENERATION_KERNEL_SLUG`: 예시 `your-kaggle-name/ai-music-video-generator`

## 품질 전략

현재 버전은 무료 MVP입니다. 외부 유료 플랫폼 없이 전체 자동화 흐름을 검증하는 것이 목적입니다. 채널 반응이 확인되면 음악 생성부만 더 좋은 모델 또는 서비스로 교체할 수 있습니다.

## 주의

YouTube API 프로젝트가 검증되지 않은 경우, API 업로드 영상이 비공개로 제한될 수 있습니다. 처음에는 자동 비공개 업로드 후 YouTube Studio에서 직접 공개/예약 공개하는 방식을 추천합니다.
