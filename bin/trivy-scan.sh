#!/usr/bin/env bash

[ "$#" == 2 ] || { echo "ERROR: Must give exactly two arguments: <image_to_scan> <ignore_file>" ; exit 1 ; }
[ -f /etc/os-release ] && cat /etc/os-release

GIT_ROOT="$(git -C "${0%/*}" rev-parse --show-toplevel)"
scan_target="$1"
ignore_file="$2"

set +exo pipefail

trivy \
  --cache-dir /tmp/workspace/trivy-cache \
  image \
  -s HIGH,CRITICAL \
  --ignorefile "${GIT_ROOT}/${ignore_file}" \
  --ignore-unfixed \
  --exit-code 1 \
  --no-progress \
  -f sarif \
  "${scan_target}" > "${GIT_ROOT}/trivy-output.txt"
exit_code=$?

cat "${GIT_ROOT}/trivy-output.txt"

# Trivy cannot detect vulnerabilities not installed by package managers (EG: busybox, buildroot, make install):
# - https://github.com/aquasecurity/trivy/issues/481 2020-04-30
if grep -q -i 'OS is not detected' trivy-output.txt ; then
  echo "Skipping trivy scan because of unsupported OS"
  exit 0
else
  sarif_base64=$(gzip -c "${GIT_ROOT}/trivy-output.txt" | base64)
  curl \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    https://api.github.com/repos/astronomer/astronomer/code-scanning/sarifs \
    -d '{"commit_sha":"4b6472266afd7b471e86085a6659e8c7f2b119da","ref":"refs/heads/master","sarif":"${sarif_base64}"}'
fi

exit "${exit_code}"
