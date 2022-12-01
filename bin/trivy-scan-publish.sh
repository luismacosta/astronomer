#!/usr/bin/env bash

[ "$#" == 1 ] || {
  echo "ERROR: Must give exactly one argument: <trivy_image_scan_result_dir>"
  exit 1
}
[ -f /etc/os-release ] && cat /etc/os-release

GIT_ROOT="$(git -C "${0%/*}" rev-parse --show-toplevel)"
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_COMMIT_SHA=$(git rev-parse HEAD)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

trivy_result_dir="$1"

set +exo pipefail
set -o xtrace

echo "Merging scan results to single file"
sarif copy --output "${GIT_ROOT}/final.sarif" "${GIT_ROOT}/${trivy_result_dir}"

echo "Publishing the Trivy scan result to Github Security - Code Scanning"
sarif_base64=$(gzip -c "${GIT_ROOT}/final.sarif" | base64 -w0)
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/astronomer/astronomer/code-scanning/sarifs \
  -d '{"commit_sha":'"\"${GIT_COMMIT_SHA}\""',"ref":'"\"refs/heads/${GIT_BRANCH}\""',"started_at":'"\"${TIMESTAMP}\""',"sarif":'"\"${sarif_base64}\""'}'

sarif csv --output "${GIT_ROOT}/report.csv" "${GIT_ROOT}/final.sarif"

curl -F file=@"${GIT_ROOT}/final.sarif" -F "initial_comment=Example upload" -F channels=C03HS1H9G1E -H "Authorization: Bearer $SLACK_ACCESS_TOKEN" https://slack.com/api/files.upload

exit $?
