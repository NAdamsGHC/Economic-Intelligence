"""Cache-warm the Companies House bulk file (long-pole download). Idempotent."""
import sys, requests
import config as C

def main():
    for d in C.companies_house_candidate_dates():
        url = C.CH_ONEFILE_URL.format(date=d)
        dest = C.CACHE_DIR / f"ch-{d}.zip"
        if dest.exists() and dest.stat().st_size > 4e8:
            print(f"cached {dest} ({dest.stat().st_size/1e6:,.0f} MB)", flush=True)
            return
        try:
            with requests.get(url, stream=True, timeout=120, headers=C.HTTP_HEADERS) as r:
                if r.status_code != 200:
                    print(f"{d}: HTTP {r.status_code}", flush=True); continue
                total = int(r.headers.get("content-length", 0))
                tmp = dest.with_suffix(".part")
                got = 0; mark = 0
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk); got += len(chunk)
                        if got - mark >= 50 * (1 << 20):
                            mark = got
                            print(f"  {got/1e6:,.0f}/{total/1e6:,.0f} MB", flush=True)
                tmp.rename(dest)
                print(f"done {dest} ({got/1e6:,.0f} MB)", flush=True)
                return
        except Exception as e:
            print(f"{d}: ERR {e}", flush=True)
    print("FAILED: no CH file downloaded", flush=True); sys.exit(1)

if __name__ == "__main__":
    main()
