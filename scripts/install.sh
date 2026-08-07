#!/usr/bin/env bash
#
# Alfr3d installer for macOS / Linux
# https://github.com/NewSoulOnTheBlock/alfr3d
#
# One-liner (after this file is hosted publicly):
#   curl -fsSL https://YOUR_DOMAIN/install.sh | bash
#
# GitHub raw (works today once pushed to main):
#   curl -fsSL https://raw.githubusercontent.com/NewSoulOnTheBlock/alfr3d/main/scripts/install.sh | bash
#
# Options via environment variables:
#   ALFR3D_REPO=https://github.com/NewSoulOnTheBlock/alfr3d.git
#   ALFR3D_REF=main
#   ALFR3D_INSTALL_DIR=$HOME/.alfr3d/app
#   ALFR3D_BIN_DIR=$HOME/.alfr3d/bin
#   ALFR3D_SKIP_DEPS=1
#

set -euo pipefail

REPO="${ALFR3D_REPO:-https://github.com/NewSoulOnTheBlock/alfr3d.git}"
REF="${ALFR3D_REF:-main}"
INSTALL_DIR="${ALFR3D_INSTALL_DIR:-$HOME/.alfr3d/app}"
BIN_DIR="${ALFR3D_BIN_DIR:-$HOME/.alfr3d/bin}"
SKIP_DEPS="${ALFR3D_SKIP_DEPS:-0}"

step() { printf '  %s\n' "$*" >&2; }
title() { printf '\n%s\n' "$*" >&2; }
ok() { printf '%s\n' "$*" >&2; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

pick_python() {
  local candidate ver
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      ver="$("$candidate" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null || true)"
      if [[ -n "$ver" ]]; then
        local major minor
        major="${ver%%.*}"
        minor="${ver#*.}"
        if (( major > 3 )) || { (( major == 3 )) && (( minor >= 9 )); }; then
          printf '%s\n' "$candidate"
          return 0
        fi
      fi
    fi
  done
  return 1
}

ensure_git() {
  if command -v git >/dev/null 2>&1; then
    return 0
  fi
  die "git is required. Install git, then re-run this installer."
}

ensure_python() {
  if PY="$(pick_python)"; then
    step "Python found: $PY ($("$PY" -c 'import sys; print(sys.version.split()[0])'))"
    printf '%s\n' "$PY"
    return 0
  fi
  die "Python 3.9+ is required. Install it, then re-run this installer."
}

install_or_update_repo() {
  mkdir -p "$(dirname "$INSTALL_DIR")"
  if [[ -d "$INSTALL_DIR/.git" ]]; then
    step "Updating existing install at $INSTALL_DIR ..."
    git -C "$INSTALL_DIR" fetch --tags --force origin || true
    git -C "$INSTALL_DIR" checkout "$REF"
    git -C "$INSTALL_DIR" pull --ff-only origin "$REF" || true
  else
    if [[ -e "$INSTALL_DIR" ]]; then
      step "Removing incomplete install directory..."
      rm -rf "$INSTALL_DIR"
    fi
    step "Cloning $REPO ($REF) ..."
    if ! git clone --depth 1 --branch "$REF" "$REPO" "$INSTALL_DIR"; then
      git clone "$REPO" "$INSTALL_DIR"
      git -C "$INSTALL_DIR" checkout "$REF"
    fi
  fi
}

install_python_package() {
  local py="$1"
  step "Installing Alfr3d package (editable)..."
  "$py" -m pip install --upgrade pip setuptools wheel
  if [[ "$SKIP_DEPS" != "1" ]]; then
    if [[ -f "$INSTALL_DIR/requirements-core.txt" ]]; then
      step "Installing core dependencies (lean install)..."
      "$py" -m pip install -r "$INSTALL_DIR/requirements-core.txt"
    elif [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
      step "Installing product dependencies (this may take a few minutes)..."
      "$py" -m pip install -r "$INSTALL_DIR/requirements.txt"
    fi
  fi
  "$py" -m pip install -e "$INSTALL_DIR"
}

write_shim() {
  local py="$1"
  mkdir -p "$BIN_DIR"
  local scripts
  scripts="$("$py" -c 'import sysconfig; print(sysconfig.get_path("scripts"))')"
  local shim="$BIN_DIR/alfr3d"

  if [[ -x "$scripts/alfr3d" ]]; then
    cat >"$shim" <<EOF
#!/usr/bin/env bash
exec "$scripts/alfr3d" "\$@"
EOF
  else
    cat >"$shim" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="$INSTALL_DIR\${PYTHONPATH:+:\$PYTHONPATH}"
exec "$py" -m cli "\$@"
EOF
  fi
  chmod +x "$shim"
  step "Shim written to $shim"
}

ensure_path() {
  local dir="$1"
  local rc=""
  case "${SHELL:-}" in
    */zsh) rc="$HOME/.zshrc" ;;
    */bash) rc="$HOME/.bashrc" ;;
    *) rc="$HOME/.profile" ;;
  esac

  if ! echo ":$PATH:" | grep -q ":$dir:"; then
    export PATH="$dir:$PATH"
  fi

  if [[ -f "$rc" ]] && grep -q 'alfr3d/bin' "$rc" 2>/dev/null; then
    step "PATH already configured in $rc"
    return 0
  fi

  {
    echo ""
    echo "# Alfr3d CLI"
    echo "export PATH=\"$dir:\$PATH\""
  } >>"$rc"
  step "Added $dir to PATH in $rc (open a new shell to apply)."
}

ensure_config() {
  if [[ ! -f "$INSTALL_DIR/config.json" && -f "$INSTALL_DIR/config-template.json" ]]; then
    cp "$INSTALL_DIR/config-template.json" "$INSTALL_DIR/config.json"
    step "Created config.json from product template."
  fi
}

main() {
  title "Alfr3d installer"
  step "Repo: $REPO"
  step "Ref:  $REF"
  step "Dir:  $INSTALL_DIR"
  echo >&2

  ensure_git
  need_cmd curl
  PY="$(ensure_python)"
  install_or_update_repo
  install_python_package "$PY"
  write_shim "$PY"
  ensure_path "$BIN_DIR"
  ensure_config

  echo >&2
  ok "Alfr3d installed."
  echo >&2
  echo "Next steps:" >&2
  echo "  1. Open a new terminal (so PATH updates apply)" >&2
  echo "  2. Run setup (API keys + why you're here):" >&2
  echo "       alfr3d setup" >&2
  echo "  3. Talk to Alfr3d:" >&2
  echo "       alfr3d chat" >&2
  echo "  4. Or start the full service:" >&2
  echo "       alfr3d start" >&2
  echo >&2
}

main "$@"
