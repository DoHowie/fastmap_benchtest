#!/usr/bin/env python3
import argparse, time, numpy as np
from pathlib import Path

from fastmap import (
    load_map, load_scen, build_graph,
    FastMap,
)
from fastmap.search import improved_astar_with_fastmap

# ──────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("map");  ap.add_argument("scen")
    ap.add_argument("-k", type=int, default=10, help="FastMap dims")
    ap.add_argument("-n", type=int, default=None, help="# scen lines (all)")
    ap.add_argument("-t", "--thresh", type=float, default=0.5,
                    help="flag rows where |err| > THRESH")
    args = ap.parse_args()

    # ── build graph & FastMap embedding ───────────────────────────────
    grid, _, _ = load_map(args.map)
    G, W       = build_graph(grid)
    emb        = FastMap(G.copy(), K=args.k).compute_embeddings()

    # ── read scenario lines (keep raw for echo) ───────────────────────
    scen_raw  = Path(args.scen).read_text().splitlines()[1:]  # skip header
    if args.n:  scen_raw = scen_raw[: args.n]

    rows, bad = [], []
    t0 = time.time()

    for idx, line in enumerate(scen_raw):
        _, _, w, _, sx, sy, gx, gy, opt = line.split()
        w   = int(w)
        s   = int(sy) * w + int(sx)
        g   = int(gy) * w + int(gx)
        opt = float(opt)

        dist = improved_astar_with_fastmap(G, s, g, emb, W)
        err  = dist - opt

        rows.append((idx, dist, opt, err))
        if abs(err) > args.thresh:
            bad.append((idx, err, line.strip()))

    t1 = time.time()

    # ── full per-case table ───────────────────────────────────────────
    print(f"{'Case':>4} | {'dist':>10} | {'optimal':>10} | {'err':>10}")
    print("-" * 48)
    for idx, d, opt, err in rows:
        print(f"{idx:4d} | {d:10.6f} | {opt:10.6f} | {err:10.6f}")

    # ── summary stats ─────────────────────────────────────────────────
    abs_err = [abs(r[3]) for r in rows]
    print("\n--- SUMMARY ---")
    print(f"{len(rows)} cases | mean|err|={np.mean(abs_err):.3e} "
          f"| max|err|={np.max(abs_err):.3e} | {t1-t0:.2f}s")

    # ── problematic rows ──────────────────────────────────────────────
    if bad:
        print(f"\nCases with |err| > {args.thresh}: {len(bad)}\n")
        print(f"{'Idx':>4} | {'err':>10} |  Raw .scen line")
        print("-" * 90)
        for idx, e, raw in bad:
            print(f"{idx:4d} | {e:10.6f} | {raw}")

if __name__ == "__main__":
    main()
