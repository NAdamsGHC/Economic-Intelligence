"""
End-to-end build for the Gateshead Business Map.

Run locally or from the monthly GitHub Action:
    python build.py            # fetch (if needed) -> pipeline -> render
    python build.py --render   # re-render only (reuse cached dashboard_data.json)

No API keys / secrets required: every source is free and public.
"""
import sys

def main():
    if "--render" in sys.argv:
        import render
        render.main()
        return
    import fetch_ch, pipeline, render
    fetch_ch.main()      # warm the Companies House bulk download (idempotent cache)
    pipeline.main()      # fetch + enrich + score -> .cache/dashboard_data.json
    render.main()        # -> business-industry-trade/gateshead-business-map.html

if __name__ == "__main__":
    main()
