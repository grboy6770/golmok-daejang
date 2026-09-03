#!/usr/bin/env python3
"""의류수거함 미매칭 주소를 Nominatim으로 지오코딩해 공용 캐시에 누적.

build_clothes.py 와 같은 판정 순서(확정 사전 → Nominatim 캐시)로 좌표를 못 얻은 주소만 골라
data/cache/nominatim_bins.json 에 추가한다 (초당 1건, 재실행 시 이어서).
완료 후 build_clothes.py 를 다시 실행하면 반영된다.
"""
import csv
import io
import json
import sys
import time

from build_bins import load_caches, lookup
from build_clothes import ADDR_KEYS, JIBUN_KEYS, LAT_KEYS, LON_KEYS, LON_RANGE, LAT_RANGE, RAW, col, decode
from geocode_bins import CACHE, query


def main() -> None:
    addrcache, geocache = load_caches()
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    todo = []
    seen = set()
    for path in sorted(RAW.glob("*.csv")):
        gu = path.stem
        rows = list(csv.reader(io.StringIO(decode(path.read_bytes()))))
        header = rows[0]
        i_lat, i_lon = col(header, LAT_KEYS), col(header, LON_KEYS)
        i_addr, i_jibun = col(header, ADDR_KEYS), col(header, JIBUN_KEYS)
        for r in rows[1:]:
            if not any(x.strip() for x in r):
                continue
            ok = False
            if i_lat is not None and i_lon is not None:
                try:
                    lat, lon = float(r[i_lat]), float(r[i_lon])
                    ok = LON_RANGE[0] <= lon <= LON_RANGE[1] and LAT_RANGE[0] <= lat <= LAT_RANGE[1]
                except (ValueError, IndexError):
                    ok = False
            if ok:
                continue
            addr = (r[i_addr].strip() if i_addr is not None and i_addr < len(r) else "")
            jibun = (r[i_jibun].strip() if i_jibun is not None and i_jibun < len(r) else "")
            # build_clothes 와 같은 키·같은 판정 순서
            key = f"{gu} {addr or jibun}".strip()
            if lookup(addrcache, geocache, key) is not None:
                continue
            if key and key != gu and key not in cache and key not in seen:
                seen.add(key)
                todo.append(key)

    print(f"조회 대상 {len(todo)}건")
    for i, key in enumerate(todo, 1):
        try:
            cache[key] = query(key)
        except Exception as e:
            print(f"중단({e}) — 진행분 저장", file=sys.stderr)
            break
        if i % 50 == 0 or i == len(todo):
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(f"  {i}/{len(todo)}")
        time.sleep(1.05)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    hit = sum(1 for k in todo if cache.get(k))
    print(f"완료: {len(todo)}건 중 성공 {hit}건")


if __name__ == "__main__":
    main()
