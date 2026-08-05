#!/usr/bin/env python3
"""
Pick one pre-made thumbnail from the rotating pool in assets/thumbnails/ and copy
it to the output path for upload.

The thumbnails are already branded ("Meditated Sleeping - Calm. Sleep. Restore."),
so nothing is drawn on top — this just rotates through the pool so consecutive
uploads don't all use the same image.

Rotation is deterministic by --index (e.g. the Sheet row number), so the pool cycles
evenly: index 0..N-1 map to each image in filename order, then wrap around. Pass
--random instead to pick one at random.

Usage:
    python select_thumbnail.py --index 5 --out thumbnail.png
    python select_thumbnail.py --random --out thumbnail.png
"""
import argparse
import glob
import os
import random
import shutil


def pool_images(pool_dir: str):
    images = sorted(glob.glob(os.path.join(pool_dir, "*.png")))
    if not images:
        raise SystemExit(f"No thumbnails found in {pool_dir}")
    return images


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pool", default="assets/thumbnails", help="folder of pre-made thumbnails")
    p.add_argument("--index", type=int, default=0, help="rotation index (e.g. the Sheet row number)")
    p.add_argument("--random", action="store_true", help="pick at random instead of by index")
    p.add_argument("--out", default="thumbnail.png")
    args = p.parse_args()

    images = pool_images(args.pool)
    chosen = random.choice(images) if args.random else images[args.index % len(images)]
    shutil.copyfile(chosen, args.out)
    print(f"Selected thumbnail {os.path.basename(chosen)} ({args.index % len(images) + 1}/{len(images)}) -> {args.out}")


if __name__ == "__main__":
    main()
