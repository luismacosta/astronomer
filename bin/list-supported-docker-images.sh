#!/usr/bin/env sh
# list all the various images associated with this platform version
# the images used by the platform
# the images deployed by the chart
# various airflow images that can be theoretically be used with this chart version
(
	./bin/list-airflow-chart-images.sh;
	./bin/list-supported-airflow-images.py
	./bin/list-platform-docker-images.sh;
) | sort | uniq
