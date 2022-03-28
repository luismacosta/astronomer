#!/usr/bin/env bash
# this script lists all docker images associated with the airflow chart referenced in .Values.astronomer.airflowChartVersion
set -e
set -u
#AIRFLOW_CHART_VERSION=$(cat charts/astronomer/values.yaml | python -c 'import yaml,sys;print(yaml.safe_load(sys.stdin)["airflowChartVersion"])')
AIRFLOW_CHART_VERSION=$(cat charts/astronomer/values.yaml | yq eval '.airflowChartVersion' - )
#echo "Found airflow chart version ${AIRFLOW_CHART_VERSION}"
helm_chart_index=$(curl -L https://helm.astronomer.io 2>/dev/null)
helm_chart_index_json=$(echo -e "$helm_chart_index"|yq eval -o json)
embedded_airflow_chart_url=$(echo -e "$helm_chart_index_json"|jq '.entries.airflow'|jq ".[] | select(.version == \"${AIRFLOW_CHART_VERSION}\").urls[0]" -r)
# airflow executor must be set to CeleryExecutor or similar to get the redis image to show up when templating
embedded_airflow_chart_images=$(helm template "$embedded_airflow_chart_url" \
	--set airflow.executor=CeleryExecutor \
	--set airflow.flower.enabled=true \
	--set airflow.redis.enabled=true \
	--set airflow.pgbouncer.enabled=true \
	--set airflow.dags.gitSync.enabled=true \
	--set airflow.postgresql.enabled=false \
	| grep 'image: '|cut -d ':' -f 2-|sed 's/^[ \t]*//;s/[ \t]*$//'|sort|uniq)
echo -e "$embedded_airflow_chart_images"
