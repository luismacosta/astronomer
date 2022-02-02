#!/usr/bin/env bash
# lists all images used by this platform
# slightly tweaked from make show-docker-images because the version
# ported from the make file didn't immediately work and to remove
# the first column so it only shows the image name now and not the
# http address of the image - does anyone need that for anything?
helm template . \
	--set global.baseDomain=foo.com \
	--set global.blackboxExporterEnabled=True \
	--set global.kedaEnabled=True \
	--set global.postgresqlEnabled=True \
	--set global.postgresqlEnabled=True \
	--set global.prometheusPostgresExporterEnabled=True \
	--set global.pspEnabled=True \
	--set global.veleroEnabled=True \
	2>/dev/null \
	 | grep 'image: '|cut -d ':' -f 2-|sed 's/^[ \t]*//;s/[ \t]*$//'|sed 's/"//g'|sort|uniq
