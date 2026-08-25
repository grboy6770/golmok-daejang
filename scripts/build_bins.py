#!/usr/bin/env python3
"""서울시 가로쓰레기통 설치정보 → 좌표 부여(지오코딩) → bins.json.

좌표가 없는 주소("사직로 125")를, 가로수 데이터(28만 그루)의
도로명주소↔좌표를 사전 삼아 해결한다. 외부 지오코딩 API 불필요.

매칭 규칙 (순서대로 시도):
  1. 같은 (자치구, 도로명, 건물번호) 정확 일치 → 해당 가로수들 좌표 평균
  2. 같은 (자치구, 도로명)에서 번호가 가장 가까운 두 지점 사이 선형 보간
     (번호 차이 40 이내일 때만)
  3. Nominatim 캐시(data/cache/nominatim_bins.json — geocode_bins.py 가 생성)
  4. 실패 → unmatched (bins.json에 미포함, 개수만 기록)

입력: data/raw/bins_202511.xlsx, data/raw/trees_2026.xlsx
출력: docs/data/bins.json
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
OUT = ROOT / "docs/data/bins.json"

# "사직로 125", "왕십리로 415-6", "세종대로 172(앞)" 등에서 (도로명, 본번) 추출
ADDR_RE = re.compile(r"([가-힣A-Za-z0-9·\.]+(?:대로|로|길))\s*[, ]?\s*(\d+)(?:-(\d+))?")
# "신당동 170-4", "신문로1가 141" 등 지번 (도로명과 겹치지 않게 동/가 로 한정)
JIBUN_RE = re.compile(r"([가-힣0-9]+(?:동|가))\s+(?:산\s*)?(\d+)(?:-(\d+))?")


def _finalize(acc):
    index = {}
    for key, nums in acc.items():
        pts = []
        for num, coords in nums.items():
            lon = sum(c[0] for c in coords) / len(coords)
            lat = sum(c[1] for c in coords) / len(coords)
            pts.append((num, lon, lat))
        pts.sort()
        index[key] = pts
    return index


def road_index_from_trees():
    """도로명·지번 색인 한 쌍을 만든다.

    반환: (road_index, jibun_index) — 각각 (구, 도로명|동명) -> [(번호, lon, lat)] 정렬 목록.
    번호는 본번*100+부번.
    """
    wb = openpyxl.load_workbook(RAW / "trees_2026.xlsx", read_only=True)
    road_acc = defaultdict(lambda: defaultdict(list))
    jibun_acc = defaultdict(lambda: defaultdict(list))
    for sheet in wb.sheetnames:
        for row in wb[sheet].iter_rows(min_row=4, values_only=True):
            gu, _rte, _sp, road_addr, lot_addr, lon, lat = row[:7]
            if lon is None or lat is None:
                continue
            try:
                pt = (float(lon), float(lat))
            except (TypeError, ValueError):
                continue
            gu = str(gu).strip()
            if road_addr:
                m = ADDR_RE.search(str(road_addr))
                if m:
                    num = int(m.group(2)) * 100 + int(m.group(3) or 0)
                    road_acc[(gu, m.group(1))][num].append(pt)
            if lot_addr:
                m = JIBUN_RE.search(str(lot_addr))
                if m:
                    num = int(m.group(2)) * 100 + int(m.group(3) or 0)
                    jibun_acc[(gu, m.group(1))][num].append(pt)
    return _finalize(road_acc), _finalize(jibun_acc)


def _locate_in(index, gu, name, main, sub, tol=4000):
    pts = index.get((gu, name))
    if not pts:
        return None
    target = main * 100 + sub
    exact = [(n, lon, lat) for n, lon, lat in pts if n // 100 == main]
    if exact:
        lon = sum(p[1] for p in exact) / len(exact)
        lat = sum(p[2] for p in exact) / len(exact)
        return (lon, lat, "exact")
    # 가장 가까운 번호 두 개로 보간
    below = max((p for p in pts if p[0] <= target), default=None)
    above = min((p for p in pts if p[0] >= target), default=None)
    cand = [p for p in (below, above) if p]
    if not cand:
        return None
    nearest = min(cand, key=lambda p: abs(p[0] - target))
    if abs(nearest[0] - target) > tol:  # 번호 차이 허용 한도 초과 → 신뢰 불가
        return None
    if below and above and below[0] != above[0]:
        t = (target - below[0]) / (above[0] - below[0])
        lon = below[1] + (above[1] - below[1]) * t
        lat = below[2] + (above[2] - below[2]) * t
        return (lon, lat, "interp")
    return (nearest[1], nearest[2], "nearest")


def locate(indexes, gu, addr):
    road_index, jibun_index = indexes
    m = ADDR_RE.search(addr)
    if m:
        r = _locate_in(road_index, gu, m.group(1), int(m.group(2)), int(m.group(3) or 0))
        if r:
            return r
    m = JIBUN_RE.search(addr)
    if m:
        # 지번은 번지 간 공간 연속성이 약해 허용 오차를 좁게 (본번 5)
        r = _locate_in(jibun_index, gu, m.group(1), int(m.group(2)), int(m.group(3) or 0), tol=500)
        if r:
            return (r[0], r[1], "jibun-" + r[2])
    return None


def main() -> None:
    index = road_index_from_trees()
    cache_path = ROOT / "data/cache/nominatim_bins.json"
    geocache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    wb = openpyxl.load_workbook(RAW / "bins_202511.xlsx", read_only=True)
    ws = wb[wb.sheetnames[0]]
    bins, unmatched = [], []
    methods = defaultdict(int)
    for row in ws.iter_rows(min_row=6, values_only=True):
        _no, gu, addr, detail, place, kind = (list(row) + [None] * 6)[:6]
        if not gu or not addr:
            continue
        gu, addr = str(gu).strip(), str(addr).strip()
        r = locate(index, gu, addr)
        if r is None:
            g = geocache.get(f"{gu} {addr}")
            r = (g[0], g[1], "osm") if g else None
        if r is None:
            unmatched.append(f"{gu} {addr}")
            continue
        lon, lat, how = r
        methods[how] += 1
        bins.append({
            "lon": round(lon, 6), "lat": round(lat, 6),
            "gu": gu, "addr": addr,
            "d": str(detail or "").strip(), "k": str(kind or "").strip(),
        })
    OUT.write_text(json.dumps({
        "asof": "2025-11", "total": len(bins) + len(unmatched),
        "matched": len(bins), "sensors": None, "bins": bins,
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"total={len(bins)+len(unmatched)} matched={len(bins)} "
          f"({dict(methods)}) unmatched={len(unmatched)}")
    for u in unmatched[:10]:
        print("  miss:", u)


if __name__ == "__main__":
    sys.exit(main())
