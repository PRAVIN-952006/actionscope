from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from .analyze import analyze_workflow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path, help="Path to a GitHub Actions workflow YAML file")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON")
    args = parser.parse_args(argv)
    try:
        report = analyze_workflow(args.workflow)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"actionscope: {error}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"Workflow: {report.path}")
        print("Declared workflow permissions:")
        for name, level in report.workflow_permissions.items():
            print(f"  - {name}: {level}")
        if report.jobs_without_explicit_permissions:
            print("Jobs without explicit permissions:")
            for job in report.jobs_without_explicit_permissions:
                print(f"  - {job}")
        print("Referenced actions:")
        for action in report.actions:
            print(f"  - {action.job}/{action.step}: {action.reference}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

