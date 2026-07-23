#!/bin/sh
# Verify the prerequisites for building and installing Dev Commander.
#
# Idempotent verification only: this script checks that the required tools are
# present, it never installs anything. Run it before `make install`. Exits 0
# when every prerequisite is present, 1 otherwise.
#
# The required set defaults to python3, pdm, git, and claude. Override it with
# DC_REQUIRED_COMMANDS (space-separated) mainly for testing.

set -u

MIN_PYTHON="3.12"
missing=0

report_ok()      { echo "  ok      $1"; }
report_missing() { echo "  missing $1 - $2"; missing=1; }

have() { command -v "$1" >/dev/null 2>&1; }

check_command() {
    if have "$1"; then
        report_ok "$1"
    else
        report_missing "$1" "$2"
    fi
}

check_python() {
    if ! have python3; then
        report_missing python3 "install Python ${MIN_PYTHON}+ from https://www.python.org"
        return
    fi
    version=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null)
    if python3 -c 'import sys; raise SystemExit(0 if sys.version_info[:2] >= (3, 12) else 1)' 2>/dev/null; then
        report_ok "python3 (${version})"
    else
        report_missing python3 "found ${version}, need ${MIN_PYTHON}+"
    fi
}

echo "Dev Commander prerequisite check"
echo

for cmd in ${DC_REQUIRED_COMMANDS:-python3 pdm git claude}; do
    case "$cmd" in
        python3) check_python ;;
        pdm)     check_command pdm "install with: pipx install pdm (https://pdm-project.org)" ;;
        git)     check_command git "install git from https://git-scm.com" ;;
        claude)  check_command claude "install the Claude Code CLI from https://claude.com/claude-code" ;;
        *)       check_command "$cmd" "required command not found on PATH" ;;
    esac
done

echo
if [ "$missing" -eq 0 ]; then
    echo "All prerequisites present. Run: make install"
    exit 0
fi
echo "Some prerequisites are missing. Install them and re-run ./bootstrap.sh"
exit 1
