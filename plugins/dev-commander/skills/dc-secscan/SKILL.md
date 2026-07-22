---
name: dc-secscan
description: Security scanning for Dev Commander. Use when the user runs /dc:scan or asks to check for vulnerable dependencies or committed secrets. Runs the project's stack-native dependency scanner and a secret scan, writes a report under .dev-commander/security/, and supplies the scan step dc-ci embeds in the pipeline.
---

# dc-secscan

Runs security scans on demand and reports. It never fixes anything: it
finds and recommends, and a dependency upgrade becomes a /dc:plan
follow-up.

## Stack detection

Infer the stack from project files: `pyproject.toml` present means python,
`package.json` means node-ts, `go.mod` means go. If none or more than one
is present, ask the user which stack rather than guessing.

## /dc:scan

1. Detect the stack.
2. Run the dependency scanner for the stack and the universal secret scan:
   - python: `pip-audit` (against the installed environment or the
     exported requirements).
   - node-ts: `npm audit --audit-level=high`.
   - go: `govulncheck ./...`.
   - secrets, all stacks: `gitleaks detect` over the repository.
3. If a scanner is not installed, report the install command (for example
   `pip install pip-audit`,
   `go install golang.org/x/vuln/cmd/govulncheck@latest`, or the gitleaks
   release page) and continue with the scanners that are available. Never
   crash on a missing tool.
4. Write a report to `.dev-commander/security/NNNN-<slug>.md`, where NNNN is
   the next zero-padded sequence number, with: the scanners that ran,
   findings grouped by severity (the vulnerable package, or the file and
   line for a secret, plus the advisory reference), and a verdict — clean,
   or issues found.
5. Severity and the gate: a high or critical dependency vulnerability, or
   any committed secret, is a gating finding; lower-severity dependency
   findings are informational. Scanners without a severity threshold
   (pip-audit, govulncheck) report every known vulnerability; treat those
   as gating.
6. Never edit dependencies or code. Recommend the fix (a version bump, a
   removed secret) and let the user decide, or open a /dc:plan for it.

## The CI scan step

dc-secscan is the single source of truth for how to scan each stack. dc-ci
embeds the dependency-scan commands from step 2 verbatim; for secret
scanning it runs the official gitleaks GitHub Action, the same gitleaks
engine as the local `gitleaks detect`. Local scans and the pipeline check
the same things.
