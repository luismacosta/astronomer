#!/usr/bin/env dash
# this script analyzes platform images from a chart and scans them with trivy
# and then captures output to a directory for later analysis
# see analyze-docker-image-scan-results.sh

image_list=$(./bin/list-supported-docker-images.sh)

echo "Writing combined process output to annotated file at ${combined_error_file}"
i=0
echo "Scanning platform images from helm chart."
scratch_dir=$(mktemp -d)
combined_error_file=${scratch_dir}/errors.txt
set -x
for image_name in ${image_list}; do
  json_scratch_file=${scratch_dir}/$i.json
  image_list_file=${scratch_dir}/image_list.txt
  echo "- ${image_name} writing to $json_scratch_file"
  echo "#START_STDOUT  ${image_name}" >> ${combined_error_file}
  (trivy image --format json -o ${json_scratch_file} $image_name ) >> ${combined_error_file}
  # couldnt hurt to save a copy of the images we scanned
  echo "$image_list" > $image_list_file
  i=$((i+1))
done
echo "#IMAGE_COUNT ${i}" >> ${combined_error_file}
echo "Wrote to combined error file ${combined_error_file}"
echo "Wrote to json files to ${scratch_dir}"
