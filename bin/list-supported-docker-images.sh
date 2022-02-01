#!/usr/bin/env sh
# list all the various images associated with this platform version
# the images used by the platform
# the images deployed by the chart
# the airflow images supported for use with this airflow chart
(
	./bin/list-airflow-chart-images.sh;
	./bin/list-supported-airflow-images.py
	./bin/list-platform-docker-images.sh;
) | sort | uniq
