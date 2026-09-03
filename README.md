<div align="center">

<img src="docs/assets/mascot.png" width="110" alt="골목대장 마스코트 — 골목 고양이">

# 골목대장

**서울 골목 사정을 다 꿰고 있는 지도**

골목 소음 🔉 쓰레기통·의류수거함 🗑️

[**👉 지도 열어보기**](https://grboy6770.github.io/golmok-daejang/)

[![소음 데이터 주간 갱신](https://github.com/grboy6770/golmok-daejang/actions/workflows/update-noise.yml/badge.svg)](https://github.com/grboy6770/golmok-daejang/actions/workflows/update-noise.yml)
![data](https://img.shields.io/badge/데이터-서울%20열린데이터광장%20·%20공공데이터포털-e8b40c)
![stack](https://img.shields.io/badge/서버-없음%20(정적%20페이지)-2b2926)

<img src="docs/assets/bins.png" width="820" alt="서울 쓰레기통과 의류수거함 지도 전경">

</div>

---

골목대장은 동네를 꽉 잡고 있는 그 아이 이름이면서, 골목 데이터를 적어두는 대장(臺帳)이기도 합니다.
서울시가 공개한 데이터를 지도 한 장에 켜켜이 쌓는 개인 프로젝트예요. 누군가 쓸지도 몰라서 만들었습니다.

## 뭘 볼 수 있나요

### 🔉 소음 편 — "조용한 동네 찾기"

서울 곳곳의 도시 센서(S-DoT) 936개가 잰 소음을 **시간대별 평균**으로 보여줍니다.
슬라이더를 새벽 3시로 돌리면 도시가 초록색(조용)으로 변하고, 저녁 6시로 돌리면
대로변이 빨갛게 달아오르는 걸 볼 수 있어요. 데이터는 매주 화요일에 자동으로 갱신됩니다.

<img src="docs/assets/noise.png" width="820" alt="시간대별 소음 지도">

### 🗑️ 쓰레기통 편 — "버릴 곳 찾기"

길에서 쓰레기통 찾아 헤맨 적 있다면. **가로쓰레기통 6천여 개**와 **의류수거함 9천여 개**의
위치를 표시합니다. 점을 탭하면 "정독도서관 앞, 일반쓰레기" 같은 설명이 나옵니다.

<img src="docs/assets/bins.png" width="820" alt="쓰레기통과 의류수거함 지도">

### 🍂 은행나무 편 — 내렸습니다 (2026-09-03)

처음 공개할 때는 서울 가로수 중 은행나무(암나무) 위치로 "가을 은행 냄새 구간"을 보여주는 편이 있었습니다.
다음 이유로 내렸습니다.

- 원본 데이터 「서울시 가로수 위치 정보」(열린데이터광장 OA-22904)는 **공공누리 제4유형**(출처표시·비상업·변경금지)입니다.
- 2026-09-03 서울시(열린데이터광장 → 원천부서) 회신: 광장에 올린 자료는 시민 열람용이며, 변형·2차적 저작물 작성은 허용되지 않고,
  연구·활용 목적이면 정보공개청구 등으로 따로 받아야 한다는 판단이었습니다.
- 그래서 2026-09-03에 은행나무 편(지도 레이어), 가공 파일 `docs/data/ginkgo.json`·`docs/data/summary.json`,
  화면 캡처 2장, 원본 엑셀을 지우고, 이들이 들어 있던 git 이력도 다시 썼습니다.
  다만 GitHub 쪽 캐시나 포크(복제본)에는 옛 커밋이 당분간 남아 있을 수 있습니다. 추가 삭제 요청은 따로 검토 중입니다.

**남아 있는 것(밝혀 둡니다)**

- 쓰레기통·의류수거함 주소를 좌표로 바꿀 때 쓴 주소→좌표 사전 `data/cache/addr_coords.json`은 그대로 있습니다.
  12,667건 중 **최소 11,863건**(최대 11,953건)이 예전에 가로수 위치를 평균·보간해서 계산한 값입니다.
  범위로 적는 이유: 옛 스크립트가 가로수 색인을 먼저 보고 그 다음에 OpenStreetMap 결과를 봤기 때문에,
  두 값이 다 있는 주소 90건은 어느 쪽이 쓰였는지 파일만 봐서는 가릴 수 없습니다.
- 그 좌표가 들어간 `docs/data/bins.json`(주소 3,648건 중 **최소 3,243건**, 최대 3,328건)과 `docs/data/clothes.json`에서 원본 CSV에 좌표가 없어 주소로 찾은 행(868행 — 구로구·동대문구 전체와 서대문·영등포·중랑구 일부)도 그대로입니다.
- 이 사전은 이번 정리(2026-09-03)에서 기존 결과물과 어긋나지 않도록 4건을 추가하고 1,199건을 갱신했습니다.
  갱신된 값의 출처도 같은 가로수 위치입니다(이동 거리 중앙값 21m, 최대 909m).
- 이 파일들에는 주소와 점 좌표만 있고 나무 정보(수종·노선·개체)는 없습니다. 다른 지오코딩 서비스로 다시 계산하지 않았고,
  이 잔여를 그대로 두기로 한 것은 운영자의 결정입니다.

## 데이터는 어디서 왔나요

| 데이터 | 출처 | 규모 | 갱신 |
|--------|------|------|------|
| 소음 (S-DoT) | [서울 열린데이터광장 OA-15969](https://data.seoul.go.kr/dataList/OA-15969/S/1/datasetView.do) | 센서 936개 × 4주 | **매주 자동** (GitHub Actions) |
| 가로쓰레기통 | [서울 열린데이터광장 OA-15069](https://data.seoul.go.kr/dataList/OA-15069/F/1/datasetView.do) | 6,849개 | 연 1회 |
| 의류수거함 | 공공데이터포털 자치구별 파일 19종 | 9,362개 | 자치구별 상이 |

## 어떻게 만들었나요

서버 없이 정적 페이지 하나로 돌아갑니다. 파이프라인은 전부 이 저장소 안에 있어요.

```
공공데이터 (xlsx/csv)
   │  scripts/build_*.py        ← 전처리·집계·지오코딩
   ▼
docs/data/*.json                ← 정적 데이터 (repo에 커밋)
   │
   ▼
docs/index.html                 ← MapLibre GL + OpenFreeMap 벡터 타일
   │
   ▼
GitHub Pages                    ← 호스팅 (유지비 0원)
```

재미있었던 문제 하나: 쓰레기통·의류수거함 자료에는 좌표 없이 주소만 있는 게 많습니다.
유료 지오코딩 API 대신 **주소→좌표 사전**(`data/cache/addr_coords.json` — 이전 빌드에서 서울시 가로수 위치를
평균·보간해 확정한 값, 자세한 내용은 위 은행나무 편 안내 참조)과 OpenStreetMap Nominatim으로 채웠습니다.
결과: 쓰레기통 91%, 의류수거함 99% 매칭.

## 직접 돌려보기

```bash
git clone https://github.com/grboy6770/golmok-daejang.git
cd golmok-daejang

# 그냥 보기 (데이터는 이미 repo에 들어 있음)
cd docs && python3 -m http.server 8000
# → http://localhost:8000

# 데이터를 처음부터 다시 만들고 싶다면 (openpyxl 필요)
scripts/fetch_sdot.sh              # 소음 원본 내려받기 (주당 50MB)
python3 scripts/build_noise.py     # 소음 집계
python3 scripts/build_bins.py      # 쓰레기통 지오코딩
python3 scripts/build_clothes.py   # 의류수거함
```

## 솔직한 한계

- 쓰레기통·의류수거함 위치는 주소를 좌표로 바꾼 값이라 실제와 수십 미터 차이가 날 수 있습니다
- 의류수거함은 도봉·노원·은평·마포·서초·중구 데이터가 아직 공개되지 않았습니다
- 소음 센서가 없는 골목은 표시되지 않습니다

## 출처 표시

- 데이터: 소음 — 서울 열린데이터광장 OA-15969 (공공누리 제1유형, 출처표시) · 가로쓰레기통 — 서울 열린데이터광장 OA-15069 (이용제한 없음) · 의류수거함 — 공공데이터포털 자치구 파일 (이용제한 없음)
- 지도: [OpenFreeMap](https://openfreemap.org) · © OpenMapTiles · © OpenStreetMap contributors
- 지오코딩 일부: © OpenStreetMap contributors (Nominatim)

본 프로젝트는 비상업 개인 프로젝트입니다. 데이터 오류를 발견하면 이슈로 알려주세요 — 지도편달 부탁드립니다. 🙇
