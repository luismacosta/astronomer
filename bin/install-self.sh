#!/usr/bin/env bash
# shellcheck disable=SC1091
set -euo pipefail
set -x

# The path to the working directory - the root of the repo
GIT_ROOT="$(git -C "${0%/*}" rev-parse --show-toplevel)"
HELM_CHART_PATH=${HELM_CHART_PATH:-$GIT_ROOT}
RELEASE_NAME="${RELEASE_NAME:-astronomer}"
NAMESPACE="${NAMESPACE:-astronomer}"
HELM_TIMEOUT=${HELM_TIMEOUT:-800}
CONFIG_FILE=$GIT_ROOT/configs/local.yaml

echo "Deploying Astronomer..."

set +e
set -x

# Fail fast for helm syntax errors
helm template astronomer "$GIT_ROOT" -f "$CONFIG_FILE"  >/dev/null && echo "Helm template parsed successfully"

# shellcheck disable=SC2086
#if ! helm install \
if ! helm upgrade -i \
  --namespace "$NAMESPACE" \
  "$RELEASE_NAME" \
  -f "$CONFIG_FILE" \
  $HELM_CHART_PATH --debug # cannot be quoted because it may contain a glob

then
  echo "Helm chart failed to install"
  exit 1
else
  helm history -n "$NAMESPACE" "$RELEASE_NAME"
fi
