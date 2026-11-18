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
class ReusableWorkflowUse:
    job: str
    reference: str


@dataclass(frozen=True)
class WorkflowReport:
    path: str
    workflow_permissions: dict[str, str]
    job_permissions: dict[str, dict[str, str]]
    jobs_without_explicit_permissions: list[str]
    actions: list[ActionUse]
    reusable_workflows: list[ReusableWorkflowUse]

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "workflow_permissions": self.workflow_permissions,
            "job_permissions": self.job_permissions,
            "jobs_without_explicit_permissions": self.jobs_without_explicit_permissions,
            "actions": [asdict(action) for action in self.actions],
            "reusable_workflows": [asdict(workflow) for workflow in self.reusable_workflows],
        }


def _load_workflow(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise TypeError(f"{path} must contain a YAML mapping")
    if True in document and "on" not in document:
        document["on"] = document.pop(True)
    return document


def _parse_permissions(value: Any, path: Path, scope: str) -> dict[str, str]:
    if value is None:
        return {}
    if value == "read-all":
        return {"*": "read"}
    if value == "write-all":
        return {"*": "write"}
    if isinstance(value, dict):
        return {str(key): str(level) for key, level in value.items()}
    raise TypeError(f"{path} has invalid {scope} permissions")


def analyze_workflow(path: Path) -> WorkflowReport:
    document = _load_workflow(path)
    workflow_permissions = _parse_permissions(
        document.get("permissions"), path, "workflow-level"
    )

    jobs = document.get("jobs")
    if not isinstance(jobs, dict):
        raise TypeError(f"{path} has a jobs value that is not a mapping")

    actions: list[ActionUse] = []
    reusable_workflows: list[ReusableWorkflowUse] = []
    job_permissions: dict[str, dict[str, str]] = {}
    missing_permissions: list[str] = []
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            raise TypeError(f"{path} has a job value that is not a mapping")
        if "permissions" not in job:
            missing_permissions.append(str(job_name))
        else:
            job_permissions[str(job_name)] = _parse_permissions(
                job.get("permissions"), path, f"job {job_name!r}"
            )
        if "uses" in job:
            reusable_workflows.append(
                ReusableWorkflowUse(job=str(job_name), reference=str(job["uses"]))
            )
        steps = job.get("steps")
        if steps is None:
            steps = []
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
        job_permissions=job_permissions,
        jobs_without_explicit_permissions=missing_permissions,
        actions=actions,
        reusable_workflows=reusable_workflows,
    )

