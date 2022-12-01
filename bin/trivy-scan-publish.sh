#!/usr/bin/env bash

[ "$#" == 1 ] || {
  echo "ERROR: Must give exactly one argument: <trivy_image_scan_result_dir>"
  exit 1
}
[ -f /etc/os-release ] && cat /etc/os-release

GIT_REPO_NAME=$(basename -s .git "$(git config --get remote.origin.url)")
GIT_ROOT="$(git -C "${0%/*}" rev-parse --show-toplevel)"
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_COMMIT_SHA=$(git rev-parse HEAD)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_STR=$(date -u +"%Y-%m-%d")

trivy_result_dir="$1"

set +exo pipefail

echo "Merging scan results to single file"

# Sarif Tools Copy Ref: https://github.com/microsoft/sarif-tools#copy
sarif copy --output "${GIT_ROOT}/final.sarif" "${GIT_ROOT}/${trivy_result_dir}"

sarif_base64=$(gzip -c "${GIT_ROOT}/final.sarif" | base64 -w0)

echo "Publishing the Trivy scan result to Github Security - Code Scanning"

# Github Upload Sarif Ref: https://docs.github.com/en/rest/code-scanning?apiVersion=2022-11-28#upload-an-analysis-as-sarif-data
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/astronomer/astronomer/code-scanning/sarifs \
  -d '{"commit_sha":'"\"${GIT_COMMIT_SHA}\""',"ref":'"\"refs/heads/${GIT_BRANCH}\""',"started_at":'"\"${TIMESTAMP}\""',"sarif":'"\"${sarif_base64}\""'}'

# Sarif Tools Copy Ref: https://github.com/microsoft/sarif-tools#csv
sarif csv --output "${GIT_ROOT}/astronomer_vul_${DATE_STR}.csv" "${GIT_ROOT}/final.sarif"

# Upload File Ref: https://api.slack.com/methods/files.upload#arg_file
curl -F file=@"${GIT_ROOT}/astronomer_vul_${DATE_STR}.csv" -F "initial_comment=Trivy Vulnerability Scan Report for repo ${GIT_REPO_NAME} of branch ${GIT_BRANCH}. " -F channels=C03HS1H9G1E -H "Authorization: Bearer $SLACK_ACCESS_TOKEN" https://slack.com/api/files.upload

exit $?
