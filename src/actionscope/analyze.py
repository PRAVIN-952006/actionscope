from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ActionUse:
    job: str
    step: str
    reference: str


@dataclass(frozen=True)
class WorkflowReport:
    path: str
    workflow_permissions: dict[str, str]
    jobs_without_explicit_permissions: list[str]
    actions: list[ActionUse]

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "workflow_permissions": self.workflow_permissions,
            "jobs_without_explicit_permissions": self.jobs_without_explicit_permissions,
            "actions": [asdict(action) for action in self.actions],
        }


def _load_workflow(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle) or {}
    if True in document and "on" not in document:
        document["on"] = document.pop(True)
    if not isinstance(document, dict):
        raise TypeError(f"{path} must contain a YAML mapping")
    return document


def analyze_workflow(path: Path) -> WorkflowReport:
    document = _load_workflow(path)
    permissions = document.get("permissions") or {}
    if permissions == "read-all":
        workflow_permissions = {"*": "read"}
    elif permissions == "write-all":
        workflow_permissions = {"*": "write"}
    elif isinstance(permissions, dict):
        workflow_permissions = {str(key): str(value) for key, value in permissions.items()}
    else:
        workflow_permissions = {}

    jobs = document.get("jobs") or {}
    if not isinstance(jobs, dict):
        raise TypeError(f"{path} has a jobs value that is not a mapping")

    actions: list[ActionUse] = []
    missing_permissions: list[str] = []
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        if "permissions" not in job:
            missing_permissions.append(str(job_name))
        steps = job.get("steps") or []
        if not isinstance(steps, list):
            continue
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict) or "uses" not in step:
                continue
            actions.append(
                ActionUse(
                    job=str(job_name),
                    step=str(step.get("name") or f"step-{index}"),
                    reference=str(step["uses"]),
                )
            )

    return WorkflowReport(
        path=str(path),
        workflow_permissions=workflow_permissions,
        jobs_without_explicit_permissions=missing_permissions,
        actions=actions,
    )

