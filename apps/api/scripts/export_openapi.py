"""Dump the FastAPI app's OpenAPI schema to JSON.

Used by `npm run generate:types` at the repo root to keep
`packages/shared`'s TypeScript DTOs generated from this schema instead of
hand-maintained, so the frontend cannot silently drift from the API.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from prisma_api.main import app


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openapi.json")
    schema = app.openapi()
    destination.write_text(json.dumps(schema, indent=2) + "\n")
    print(f"wrote {destination}")


if __name__ == "__main__":
    main()
