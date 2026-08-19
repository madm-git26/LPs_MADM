"""Every change the agent makes, written down before it is forgotten.

Two artefacts per run:

* ``.audit/events-YYYY-MM-DD.jsonl`` - append-only, one line per decision,
  including the ones that were blocked or sent for approval.  This is what the
  daily report is built from and what answers "why did spend move on Tuesday".
* ``.audit/runs/<run_id>.json`` - the undo plan for that run, so
  ``scripts/rollback.py --run-id <id>`` can put the account back.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


@dataclass
class AuditRecord:
    run_id: str
    timestamp: str
    customer_id: str
    action: str
    entity: str
    verdict: str
    rule: str
    message: str
    entity_count: int = 1
    before: Any = None
    after: Any = None
    reason: str = ""
    applied: bool = False
    validated: bool = False
    resource_names: list[str] = field(default_factory=list)
    undo: dict[str, Any] | None = None
    error: str = ""

    def line(self) -> str:
        return json.dumps(asdict(self), default=str)


class AuditLog:
    def __init__(self, directory: str | os.PathLike = ".audit"):
        self.dir = Path(directory)
        self.runs_dir = self.dir / "runs"

    # -- runs --------------------------------------------------------------

    def start_run(self, label: str = "run") -> str:
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        slug = "".join(ch if ch.isalnum() else "-" for ch in label).strip("-").lower()[:32]
        return f"{stamp}-{slug or 'run'}-{uuid.uuid4().hex[:4]}"

    def _events_path(self, when: _dt.date | None = None) -> Path:
        day = (when or _dt.date.today()).isoformat()
        return self.dir / f"events-{day}.jsonl"

    # -- writing -----------------------------------------------------------

    def write(self, record: AuditRecord) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with self._events_path().open("a", encoding="utf-8") as handle:
            handle.write(record.line() + "\n")

    def write_run(self, run_id: str, records: Iterable[AuditRecord],
                  meta: dict[str, Any] | None = None) -> Path:
        records = list(records)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        path = self.runs_dir / f"{run_id}.json"
        path.write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "created": _dt.datetime.now().isoformat(timespec="seconds"),
                    "meta": meta or {},
                    "records": [asdict(r) for r in records],
                },
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        return path

    # -- reading -----------------------------------------------------------

    def read_day(self, when: _dt.date | None = None) -> list[dict[str, Any]]:
        path = self._events_path(when)
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

    def ops_today(self, customer_id: str) -> int:
        """How many entities the agent has already touched today, for the cap."""
        return sum(
            row.get("entity_count", 1)
            for row in self.read_day()
            if row.get("customer_id") == str(customer_id) and row.get("applied")
        )

    def read_run(self, run_id: str) -> dict[str, Any]:
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"No audit run {run_id!r} under {self.runs_dir}")
        return json.loads(path.read_text(encoding="utf-8"))

    def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.runs_dir.exists():
            return []
        paths = sorted(self.runs_dir.glob("*.json"), reverse=True)[:limit]
        out = []
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            applied = [r for r in data["records"] if r.get("applied")]
            out.append({
                "run_id": data["run_id"],
                "created": data["created"],
                "applied": len(applied),
                "total": len(data["records"]),
                "meta": data.get("meta", {}),
            })
        return out
