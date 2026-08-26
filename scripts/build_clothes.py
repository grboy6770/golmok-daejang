#!/usr/bin/env python3
"""자치구별 의류수거함 CSV(19개 구) → docs/data/clothes.json.

- 17개 구는 위도·경도 컬럼을 그대로 사용
- 좌표가 없는 구(구로·동대문)는 build_bins의 가로수 도로명·지번 색인 +
  Nominatim 캐시로 지오코딩
- 미제공 자치구(2026-08 기준): 도봉·노원·은평·마포·서초·중구 (+ 종로 외 미확인분)
"""
import csv
import io
import json
from pathlib import Path

from build_bins import ROOT, locate, road_index_from_trees

RAW = ROOT / "data/raw/clothes"
OUT = ROOT / "docs/data/clothes.json"
CACHE = ROOT / "data/cache/nominatim_bins.json"

LAT_KEYS = ("위도",)
LON_KEYS = ("경도",)
ADDR_KEYS = ("도로명주소", "도로명 주소", "설치장소(도로명주소)", "설치장소(도로명)",
             "소재지도로명주소", "주소", "설치장소", "위치")
JIBUN_KEYS = ("지번주소", "소재지지번주소", "설치장소(지번주소)")
DONG_KEYS = ("행정동", "법정동")

LON_RANGE = (126.7, 127.3)
LAT_RANGE = (37.4, 37.8)


def decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "cp949", "euc-kr", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("all", raw, 0, 1, "unknown encoding")


def col(header, keys):
    for k in keys:
        if k in header:
            return header.index(k)
    return None


def main() -> None:
    indexes = None  # 필요할 때만 가로수 색인 로드 (수 초 소요)
    geocache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    boxes = []
    unmatched = 0
    per_gu = {}

    for path in sorted(RAW.glob("*.csv")):
        gu = path.stem
        rows = list(csv.reader(io.StringIO(decode(path.read_bytes()))))
        header = rows[0]
        i_lat, i_lon = col(header, LAT_KEYS), col(header, LON_KEYS)
        i_addr, i_jibun = col(header, ADDR_KEYS), col(header, JIBUN_KEYS)
        i_dong = col(header, DONG_KEYS)
        got = 0
        for r in rows[1:]:
            if not any(x.strip() for x in r):
                continue
            lon = lat = None
            if i_lat is not None and i_lon is not None:
                try:
                    lat, lon = float(r[i_lat]), float(r[i_lon])
                except (ValueError, IndexError):
                    lat = lon = None
            addr = (r[i_addr].strip() if i_addr is not None and i_addr < len(r) else "")
            jibun = (r[i_jibun].strip() if i_jibun is not None and i_jibun < len(r) else "")
            if lon is None:
                # 주소 지오코딩: 도로명 → 지번 → Nominatim 캐시
                if indexes is None:
                    indexes = road_index_from_trees()
                res = None
                for cand in (addr, jibun):
                    if cand:
                        res = locate(indexes, gu, cand)
                        if res:
                            break
                if res is None:
                    g = geocache.get(f"{gu} {addr or jibun}")
                    res = (g[0], g[1], "osm") if g else None
                if res is None:
                    unmatched += 1
                    continue
                lon, lat = res[0], res[1]
            if not (LON_RANGE[0] <= lon <= LON_RANGE[1] and LAT_RANGE[0] <= lat <= LAT_RANGE[1]):
                unmatched += 1
                continue
            boxes.append({
                "lon": round(lon, 6), "lat": round(lat, 6), "gu": gu,
                "addr": addr or jibun,
                "d": (r[i_dong].strip() if i_dong is not None and i_dong < len(r) else ""),
            })
            got += 1
        per_gu[gu] = got

    OUT.write_text(json.dumps({
        "asof": "2026-08", "gu_count": len(per_gu),
        "matched": len(boxes), "unmatched": unmatched, "boxes": boxes,
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"gu={len(per_gu)} matched={len(boxes)} unmatched={unmatched}")
    print(per_gu)


if __name__ == "__main__":
    main()
