#!/usr/bin/env bash

[ "$#" == 3 ] || { echo "ERROR: Must give exactly two arguments: <image_to_scan> <ignore_file> <trivy_image_scan_result_dir>" ; exit 1 ; }
[ -f /etc/os-release ] && cat /etc/os-release

GIT_ROOT="$(git -C "${0%/*}" rev-parse --show-toplevel)"
scan_target="$1"
ignore_file="$2"
trivy_result_dir="$3"

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
elif [ "${exit_code}" -gt 0 ]; then
  echo "Storing code scanning result"
  mv "${GIT_ROOT}/trivy-output.txt" "${GIT_ROOT}/${trivy_result_dir}/trivy-output-${scan_target}.sarif"
  exit 0
fi

exit "${exit_code}"
