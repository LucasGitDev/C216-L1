from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
XML_REPORT_PATH = REPORTS_DIR / "last-test-results.xml"
MARKDOWN_REPORT_PATH = REPORTS_DIR / "last-test-report.md"
TEXT_REPORT_PATH = REPORTS_DIR / "last-test-output.txt"


@dataclass(slots=True)
class TestCaseResult:
    name: str
    classname: str
    status: str
    duration_seconds: float
    message: str | None = None


@dataclass(slots=True)
class TestSummary:
    tests: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    duration_seconds: float = 0.0
    suites: int = 0
    cases: list[TestCaseResult] | None = None


def run_pytest(pytest_args: list[str]) -> subprocess.CompletedProcess[str]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--junitxml",
        str(XML_REPORT_PATH),
        *pytest_args,
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_summary(xml_report_path: Path) -> TestSummary:
    if not xml_report_path.exists():
        return TestSummary(cases=[])

    tree = ET.parse(xml_report_path)
    root = tree.getroot()

    if root.tag == "testsuites":
        suites = len(root.findall("testsuite"))
        suite_nodes = root.findall("testsuite")
        tests = sum(int(suite.attrib.get("tests", 0)) for suite in suite_nodes)
        failures = sum(int(suite.attrib.get("failures", 0)) for suite in suite_nodes)
        errors = sum(int(suite.attrib.get("errors", 0)) for suite in suite_nodes)
        skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suite_nodes)
        duration_seconds = sum(float(suite.attrib.get("time", 0.0)) for suite in suite_nodes)
    else:
        tests = int(root.attrib.get("tests", 0))
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        skipped = int(root.attrib.get("skipped", 0))
        duration_seconds = float(root.attrib.get("time", 0.0))
        suites = 1
        suite_nodes = [root]

    cases: list[TestCaseResult] = []

    for suite in suite_nodes:
        for case in suite.findall("testcase"):
            status = "passed"
            message = None

            if (failure := case.find("failure")) is not None:
                status = "failed"
                message = failure.attrib.get("message") or (failure.text or "").strip() or None
            elif (error := case.find("error")) is not None:
                status = "error"
                message = error.attrib.get("message") or (error.text or "").strip() or None
            elif (skipped_node := case.find("skipped")) is not None:
                status = "skipped"
                message = skipped_node.attrib.get("message") or (skipped_node.text or "").strip() or None

            cases.append(
                TestCaseResult(
                    name=case.attrib.get("name", "<unknown>"),
                    classname=case.attrib.get("classname", ""),
                    status=status,
                    duration_seconds=float(case.attrib.get("time", 0.0)),
                    message=message,
                )
            )

    return TestSummary(
        tests=tests,
        failures=failures,
        errors=errors,
        skipped=skipped,
        duration_seconds=duration_seconds,
        suites=suites,
        cases=cases,
    )


def build_markdown_report(
    *,
    command: list[str],
    completed: subprocess.CompletedProcess[str],
    summary: TestSummary,
) -> str:
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    command_text = shlex.join(
        [
            sys.executable,
            "-m",
            "pytest",
            "--junitxml",
            str(XML_REPORT_PATH.relative_to(ROOT)),
            *command[5:],
        ]
    )
    cases = summary.cases or []
    passed_count = sum(1 for case in cases if case.status == "passed")
    failing_cases = [case for case in cases if case.status in {"failed", "error"}]
    skipped_cases = [case for case in cases if case.status == "skipped"]
    result_label = "passed" if completed.returncode == 0 else "failed"

    lines = [
        "# Last Test Report",
        "",
        f"- Generated at (UTC): `{generated_at}`",
        f"- Command: `{command_text}`",
        f"- Exit code: `{completed.returncode}`",
        f"- Result: `{result_label}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Test suites | {summary.suites} |",
        f"| Tests collected | {summary.tests} |",
        f"| Passed | {passed_count} |",
        f"| Failed | {summary.failures} |",
        f"| Errors | {summary.errors} |",
        f"| Skipped | {summary.skipped} |",
        f"| Duration (s) | {summary.duration_seconds:.3f} |",
        "",
    ]

    if failing_cases:
        lines.extend(["## Failing Cases", ""])
        for case in failing_cases:
            location = f"{case.classname}::{case.name}" if case.classname else case.name
            lines.append(f"- `{location}`: {case.message or case.status}")
        lines.append("")

    if skipped_cases:
        lines.extend(["## Skipped Cases", ""])
        for case in skipped_cases:
            location = f"{case.classname}::{case.name}" if case.classname else case.name
            lines.append(f"- `{location}`: {case.message or 'skipped'}")
        lines.append("")

    if cases:
        lines.extend(["## Test Cases", ""])
        for case in cases:
            location = f"{case.classname}::{case.name}" if case.classname else case.name
            lines.append(f"- `{location}` [{case.status}] ({case.duration_seconds:.3f}s)")
        lines.append("")

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()

    lines.extend(["## Console Output", "", "```text"])
    if stdout:
        lines.append(stdout)
    if stderr:
        if stdout:
            lines.append("")
            lines.append("[stderr]")
        lines.append(stderr)
    if not stdout and not stderr:
        lines.append("<no output>")
    lines.extend(["```", ""])

    return "\n".join(lines)


def persist_console_output(completed: subprocess.CompletedProcess[str]) -> None:
    sections: list[str] = []
    if completed.stdout:
        sections.append("[stdout]\n" + completed.stdout.rstrip())
    if completed.stderr:
        sections.append("[stderr]\n" + completed.stderr.rstrip())

    TEXT_REPORT_PATH.write_text("\n\n".join(sections) + ("\n" if sections else ""), encoding="utf-8")


def main() -> int:
    pytest_args = sys.argv[1:]
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--junitxml",
        str(XML_REPORT_PATH),
        *pytest_args,
    ]

    completed = run_pytest(pytest_args)
    summary = parse_summary(XML_REPORT_PATH)
    persist_console_output(completed)
    MARKDOWN_REPORT_PATH.write_text(
        build_markdown_report(command=command, completed=completed, summary=summary),
        encoding="utf-8",
    )

    sys.stdout.write(completed.stdout)
    if completed.stderr:
        sys.stderr.write(completed.stderr)

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
