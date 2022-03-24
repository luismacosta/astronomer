#!/usr/bin/env python3

# Reads directory created by scan-docker-images-in-release.sh and prints
# summary output of images that have security results that require
# attention.

# usage guidance:
# set SCAN_RESULTS_DIRECTORY to temp directory outputted by scan-docker-images-in-release.sh

from os import getenv, path, listdir
from sys import exit
import json

# VIP customer assumes unknown is unacceptable
costs = {"UNKNOWN": 7, "CRITICAL": 10, "HIGH": 8, "MEDIUM": 5, "LOW": 2}


def cost_by_severity(a):
    severity = a["Severity"]
    cost = costs[severity]
    return cost


def crosstab_scan_file(filename, image_vulnerabilities, cve_results):
    with open(filename, "r") as f:
        data = json.load(f)
    print(f"Evaluating {filename}")
    artifact_name = data["ArtifactName"]
    for result in data["Results"]:
        if "Vulnerabilities" in result:
            vulnerabilities = result["Vulnerabilities"]
            for vulnerability in vulnerabilities:
                vulnerability_id = vulnerability["VulnerabilityID"]
                # print(vulnerability["VulnerabilityID"])
                # print(vulnerability["Severity"])
                # print(vulnerability["PkgName"])
                # if "PrimaryURL" in vulnerability:
                #    print(vulnerability["PrimaryURL"])
                if vulnerability_id not in cve_results:
                    cve_results[vulnerability_id] = {
                        "artifacts": [],
                        "vulnerability": vulnerability,
                        "targets": [],
                    }
                cve_result = cve_results[vulnerability_id]
                # some vulnerabilities have multiple targets in the same image so only add it once
                if artifact_name not in cve_result["artifacts"]:
                    cve_result["artifacts"].append(artifact_name)
                cve_result["targets"].append(result["Target"])
                if artifact_name not in image_vulnerabilities:
                    image_vulnerabilities[artifact_name] = []
                image_vulnerabilities[artifact_name] += vulnerabilities

        # vulnerabilities = result["Vulnerabilities"]
        # print(vulnerabilities)


if not getenv("SCAN_RESULTS_DIRECTORY"):
    print("SCAN_RESULTS_DIRECTORY environment variable must be set")
    exit(2)
else:
    results_directory = getenv("SCAN_RESULTS_DIRECTORY")

image_vulnerabilities = {}
cve_results = {}
for filename in listdir(results_directory):
    filename = path.join(results_directory, filename)
    # checking if it is a file
    if path.isfile(filename):
        if filename.endswith(".json"):
            crosstab_scan_file(filename, image_vulnerabilities, cve_results)

# print("### SUMMARY")
# for artifact_name in image_vulnerabilities:
#     vulnerabilities = image_vulnerabilities[artifact_name]
#     sorted_vulnerabilities = sorted(vulnerabilities, key=cost_by_severity, reverse=True)
#     print(artifact_name)
#     for vulnerability in sorted_vulnerabilities:
#         print(vulnerability["VulnerabilityID"], vulnerability["Severity"])


print("### BY CVE")
print("### SUMMARY")
sorted_most_severe_cve_results = sorted(
    cve_results,
    key=lambda cve_identifier: costs[
        cve_results[cve_identifier]["vulnerability"]["Severity"]
    ],
)

for cve_identifier in sorted_most_severe_cve_results:
    cve_info = cve_results[cve_identifier]
    vulnerability = cve_info["vulnerability"]
    print(vulnerability["Severity"], cve_info["artifacts"])
    # sorted_vulnerabilities = sorted(vulnerabilities, key=cost_by_severity
    # , reverse = True)
    # print(artifact_name)
    # for vulnerability in sorted_vulnerabilities:
    #    print(vulnerability["VulnerabilityID"], vulnerability["Severity"])

print("### ")
print("### MOST SEVERE FROM EACH IMAGE")
print("### ")
most_severe_vulnerabilities = {}
for artifact_name, vulnerabilities in image_vulnerabilities.items():
    sorted_vulnerabilities = sorted(vulnerabilities, key=cost_by_severity, reverse=True)
    vulnerability = sorted_vulnerabilities[0]
    most_severe_vulnerabilities[artifact_name] = vulnerability
# print them out ordered by severity
sorted_most_severe_vulnerabilities = sorted(
    most_severe_vulnerabilities,
    key=lambda x: cost_by_severity(most_severe_vulnerabilities[x]),
)
for artifact_name in sorted_most_severe_vulnerabilities:
    vulnerability = most_severe_vulnerabilities[artifact_name]
    print(artifact_name, vulnerability["VulnerabilityID"], vulnerability["Severity"])

# OK now decide if this was a good scan or bad scan and throw a posix error return type if not good
if cve_results:
    vulnerabilities = [result["vulnerability"] for result in cve_results.values()]
    sorted_vulnerabilities = sorted(vulnerabilities, key=cost_by_severity)
    most_severe_overall = sorted_vulnerabilities[-1]["Severity"]
    print(f"Most severe vulnerability identified {most_severe_overall}")
    if costs[most_severe_overall] > costs["MEDIUM"]:
        print(
            "Recommending action to remediate all vulnerabilities higher than MEDIUM."
        )
        exit(2)
else:
    print("No vulnerabilities detected.")
