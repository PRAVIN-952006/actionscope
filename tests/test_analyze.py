from pathlib import Path

from actionscope.analyze import analyze_workflow


def test_analyzes_permissions_and_actions(tmp_path: Path) -> None:
    workflow = tmp_path / "ci.yml"
    workflow.write_text(
        """
name: CI
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - run: python -m pytest
  release:
    permissions:
      contents: write
    runs-on: ubuntu-latest
    steps:
      - uses: softprops/action-gh-release@v2
""",
        encoding="utf-8",
    )

    report = analyze_workflow(workflow)

    assert report.workflow_permissions == {"contents": "read"}
    assert report.jobs_without_explicit_permissions == ["test"]
    assert [action.reference for action in report.actions] == [
        "actions/checkout@v4",
        "softprops/action-gh-release@v2",
    ]


def test_accepts_read_all_permissions(tmp_path: Path) -> None:
    workflow = tmp_path / "ci.yml"
    workflow.write_text("permissions: read-all\njobs: {}\n", encoding="utf-8")

    assert analyze_workflow(workflow).workflow_permissions == {"*": "read"}

