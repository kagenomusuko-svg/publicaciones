#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY_ROOT))

from maquetacion.build_book import build, ensure_seal, md  # noqa: E402


def strip_part_marker(raw: str) -> str:
    return re.sub(r'^\s*\*Parte\s+[IVXLCDM]+\s+[—-]\s+[^*]+\*\s*\n+', '', raw, count=1, flags=re.I)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--output', default='afrodita-areia/sobre-la-pasion/build/afrodita-areia-vol-i-sobre-la-pasion.pdf')
    args = parser.parse_args()
    build(
        Path(args.root).resolve(),
        Path(args.output).resolve(),
        REPOSITORY_ROOT / 'maquetacion' / 'estilo-libro-6x9.css',
    )


if __name__ == '__main__':
    main()
