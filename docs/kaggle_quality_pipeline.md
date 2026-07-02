# Kaggle Quality Pipeline

Kaggle은 무료 GPU/Notebook을 제공하므로, 고품질 제작을 위한 보조 작업에 사용할 수 있습니다.

## 추천 사용처

- 완성 전 WAV 음원의 길이/샘플레이트/채널 점검
- 여러 곡의 품질 리포트 생성
- 향후 무료 오픈소스 모델을 이용한 시각화, 마스터링 보조, 자막 생성 실험

## 추천하지 않는 사용처

- 저작권 출처가 불명확한 모델로 상업용 음악을 대량 생성
- 유명 아티스트 목소리/스타일 모방
- YouTube 업로드까지 Kaggle에서 직접 처리

## Kaggle에서 해야 할 일

1. Kaggle 로그인
2. 오른쪽 위 프로필 아이콘 클릭
3. Settings로 이동
4. API 섹션에서 `Create New Token` 클릭
5. `kaggle.json` 파일 다운로드
6. 파일 안의 `username`, `key` 값을 GitHub Secrets에 입력

GitHub Secrets:

- `KAGGLE_USERNAME`
- `KAGGLE_KEY`

GitHub Variables:

- `KAGGLE_KERNEL_SLUG`: 예시 `your-kaggle-name/ai-music-quality-pipeline`

## 실행 방법

GitHub Actions에서 `Kaggle Quality Pipeline`을 수동 실행하면 Kaggle Notebook이 실행되고 결과가 GitHub Actions artifact로 저장됩니다.

## 운영 판단

초기 MVP에서는 YouTube 자동 업로드가 우선입니다. Kaggle은 품질 점검과 배치 처리 보조로만 사용하고, 채널 반응이 확인된 뒤 기능을 늘리는 것이 안전합니다.
