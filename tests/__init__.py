from pathlib import Path
import shutil

import git
import subprocess
from tempfile import NamedTemporaryFile
from pathlib import Path
import platform

uname_map = {
    "Linux": "linux",
    "Windows": "windows",
    "Darwin": "darwin",
    "x86_64": "amd64",
    "i386": "386",
    "i686": "386",
    "x86": "386",
    "aarch64": "arm64",
    "armv5": "armv5",
    "armv6": "armv6",
    "armv7": "armv7",
    "arm64": "arm64",
}

# The top-level path of this repository
git_repo = git.Repo(__file__, search_parent_directories=True)
git_root_dir = Path(git_repo.git.rev_parse("--show-toplevel"))

# This should match the major.minor version list in .circleci/generate_circleci_config.py
# Patch version should always be 0
supported_k8s_versions = ["1.19.0", "1.20.0", "1.21.0", "1.22.0", "1.23.0"]


def validate_prometheus_config(config):
    """Takes the contents of a prometheus configuration file and validates it using promtool."""

    promtool = shutil.which("promtool")
    if not promtool:
        machine = uname_map[platform.machine()]
        system = uname_map[platform.system()]
        url = f"https://github.com/prometheus/prometheus/releases/download/v2.37.1/prometheus-2.37.1.{system}-{machine}.tar.gz"
        print(
            f"promtool command not found. Attempting to download from {url} (NOT IMPLEMENTED)"
        )

    # https://github.com/prometheus/prometheus/releases
    with NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(config.encode())
        tmp_file.flush()
        res = subprocess.check_output(
            f"{promtool} check config {tmp_file.name}".split()
        )
        breakpoint()
        print("Fin")


def get_containers_by_name(doc, include_init_containers=False):
    """Given a single doc, return all the containers by name.

    doc must be a valid spec for a pod manager. (EG: ds, sts)
    """

    c_by_name = {c["name"]: c for c in doc["spec"]["template"]["spec"]["containers"]}

    if include_init_containers and doc["spec"]["template"]["spec"].get(
        "initContainers"
    ):
        c_by_name |= {
            c["name"]: c for c in doc["spec"]["template"]["spec"].get("initContainers")
        }

    return c_by_name
