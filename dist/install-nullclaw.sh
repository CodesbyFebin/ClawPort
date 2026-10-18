#!/bin/sh
# ClawPort: pinned upstream NullClaw binary; no root access required.
set -eu
[ "$(uname -s)" = Linux ] || { echo "This installer supports Linux only." >&2; exit 1; }
case "$(uname -m)" in
  aarch64|arm64) asset_url='https://github.com/nullclaw/nullclaw/releases/download/v2026.5.29/nullclaw-linux-aarch64.bin'; expected_sha='87d4a19c39dd199f6d5f45b3c80e566d4349d0a291e6cc4ac8f573e2fecfa152' ;;
  x86_64|amd64) asset_url='https://github.com/nullclaw/nullclaw/releases/download/v2026.5.29/nullclaw-linux-x86_64.bin'; expected_sha='966c524d3816531371e8657ffc84c40f47d94db89f6c70e816adce983e6d1f0a' ;;
  *) echo "Unsupported processor. See upstream releases." >&2; exit 1 ;;
esac
command -v curl >/dev/null || { echo "curl is required." >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "sha256sum is required." >&2; exit 1; }
install_dir="${HOME}/.local/bin"
[ ! -e "$install_dir/nullclaw" ] || { echo "NullClaw already exists; refusing to overwrite." >&2; exit 1; }
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
curl --fail --location --proto '=https' --tlsv1.2 "$asset_url" -o "$work_dir/nullclaw"
printf '%s  %s\n' "$expected_sha" "$work_dir/nullclaw" | sha256sum -c -
mkdir -p "$install_dir"
chmod 755 "$work_dir/nullclaw"
# A hard link avoids overwriting a concurrently created destination.
cp "$work_dir/nullclaw" "$install_dir/.nullclaw-$$"
ln "$install_dir/.nullclaw-$$" "$install_dir/nullclaw" || { rm -f "$install_dir/.nullclaw-$$"; exit 1; }
rm "$install_dir/.nullclaw-$$"
printf 'Installed NullClaw at %s/nullclaw\nFollow https://github.com/nullclaw/nullclaw for configuration.\n' "$install_dir"
