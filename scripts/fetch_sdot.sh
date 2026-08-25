#!/bin/sh
# S-DoT 원본 파일 다운로드 (서울 열린데이터광장 OA-15969, 인증키 불필요)
# 사용: scripts/fetch_sdot.sh [주간파일 seq ...]
#   seq 목록은 데이터셋 페이지의 파일 목록에서 확인 (예: 20260824 = 2026.08.10~08.16 주간)
#   기본값: 최근 4주 (2026-08 기준)
set -e
cd "$(dirname "$0")/../data/raw"
URL="https://datafile.seoul.go.kr/bigfile/iot/inf/nio_download.do?&useCache=false"

# 센서 설치 위치 (항상 갱신)
curl -s --max-time 60 -X POST "$URL" -d "infId=OA-15969&seq=100000001&infSeq=3" -o sdot_loc.xlsx

SEQS="${*:-20260824 20260817 20260810 20260803}"
for seq in $SEQS; do
  echo "download sdot_$seq.csv ..."
  curl -s --max-time 300 -X POST "$URL" -d "infId=OA-15969&seq=$seq&infSeq=3" -o "sdot_$seq.csv"
  ls -la "sdot_$seq.csv"
done
