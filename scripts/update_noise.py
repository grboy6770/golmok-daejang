#!/usr/bin/env python3
"""S-DoT 소음 데이터 자동 갱신 (GitHub Actions용).

1. 데이터셋 페이지(OA-15969)에서 주간 파일 목록(seq)을 긁는다
2. 최신 N주(기본 4주) CSV + 센서 위치 xlsx를 내려받는다
3. build_noise.py 를 실행해 docs/data/noise.json 재생성

인증키 불필요. 실패 시 exit code 1 (기존 noise.json은 그대로 남는다).
"""
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
PAGE = "https://data.seoul.go.kr/dataList/OA-15969/S/1/datasetView.do"
DL = "https://datafile.seoul.go.kr/bigfile/iot/inf/nio_download.do?&useCache=false"
UA = {"User-Agent": "Mozilla/5.0 (golmok-daejang updater)"}
WEEKS = 4


def post_download(seq: str, dest: Path) -> None:
    data = urllib.parse.urlencode({"infId": "OA-15969", "seq": seq, "infSeq": "3"}).encode()
    req = urllib.request.Request(DL, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r:
        content = r.read()
    if content[:20].lstrip().startswith(b"<html"):
        raise RuntimeError(f"seq={seq}: 다운로드 거부 응답(HTML)")
    dest.write_bytes(content)
    print(f"  {dest.name}: {len(content):,} bytes")


def main() -> int:
    req = urllib.request.Request(PAGE, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    # downloadFile('20260824');">S-DoT_NATURE_2026.08.10-08.16.csv
    entries = re.findall(r"downloadFile\('(\d{8})'\);\">\s*(S-DoT_NATURE_[^<]+\.csv)", html)
    if not entries:
        print("주간 파일 목록을 찾지 못함 — 페이지 구조 변경 여부 확인 필요", file=sys.stderr)
        return 1
    entries.sort(key=lambda e: e[0], reverse=True)
    latest = entries[:WEEKS]
    print("최신 주간 파일:", [f"{s} ({n})" for s, n in latest])

    RAW.mkdir(parents=True, exist_ok=True)
    for old in RAW.glob("sdot_*.csv"):
        old.unlink()
    post_download("100000001", RAW / "sdot_loc.xlsx")
    for seq, _name in latest:
        post_download(seq, RAW / f"sdot_{seq}.csv")

    subprocess.run([sys.executable, str(ROOT / "scripts/build_noise.py")], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
