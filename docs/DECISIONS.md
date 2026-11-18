# Engineering decisions

## 2026-11-18: Start with explainable local reports

The first release focuses on a narrow, offline report of workflow token
permissions and external workflow/action references. Existing linting and
security scanners remain complementary; this project is not positioned as a
replacement for them.

The parser does not execute workflow code or resolve remote references. This
keeps analysis deterministic and avoids turning a security report into an
execution surface. Future policy checks should consume the stable JSON report.
