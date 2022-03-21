# These tests do not cover templates/scc/astronomer-scc-anyuid.yaml because the
# contents of that file are not included in the k8s schema we use for validating
# k8s manifests. See https://github.com/astronomer/issues/issues/3887

from tests.helm_template_generator import render_chart
import pytest
from . import supported_k8s_versions
import yaml

show_only = [
    "charts/astronomer/templates/commander/commander-role.yaml",
    "charts/astronomer/templates/houston/houston-configmap.yaml",
]

commander_expected_result = {
    "apiGroups": ["security.openshift.io"],
    "resources": ["securitycontextconstraints"],
    "verbs": ["create", "delete"],
}
### elasticsearch SecurityContextConstraint tests


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_elastic_scc_can_be_enabled(kube_version):
    """elastic SecurityContextConstraint should be present if sccEnabled and elasticsearchEnabled"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": True, "elasticsearchEnabled": True}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    houston_values = yaml.safe_load(docs[1]["data"]["production.yaml"])

    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-elastic"
        ),
        None,
    )
    assert x is not None
    assert len(docs) == 2
    assert commander_expected_result not in docs[0]["rules"]
    assert houston_values["deployments"]["helm"].get("sccEnabled") is None

@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_elastic_scc_absent_if_elastic_disabled(kube_version):
    """elastic SecurityContextConstraint should disable if elastic is disabled"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": True, "elasticsearchEnabled": False}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-elastic"
        ),
        None,
    )
    assert x is None


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_elastic_scc_absent_if_scc_disabled(kube_version):
    """elastic SecurityContextConstraint should disable if sccEnabled is False"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": False, "elasticsearchEnabled": True}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-elastic"
        ),
        None,
    )
    assert x is None


#### fluentd daemonset SecurityContextConstraintg tests


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_scc_can_be_enabled(kube_version):
    """fluentd SecurityContextConstraint should be present if sccEnabled and fluentdEnabled"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": True, "fluentdEnabled": True}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-fluentd"
        ),
        None,
    )
    assert x is not None


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_scc_absent_if_fluentd_disabled(kube_version):
    """fluentd SecurityContextConstraint should disable if fluentd is disabled"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": True, "fluentdEnabled": False}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-fluentd"
        ),
        None,
    )
    assert x is None


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_scc_absent_if_scc_disabled(kube_version):
    """fluentd SecurityContextConstraint should disable if sccEnabled is False"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": False, "fluentdEnabled": True}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-fluentd"
        ),
        None,
    )
    assert x is None


### .nodeExporterEnabled SecurityContextConstraint tests
# name: {{ .Release.Name }}-prometheus-node-exporter
@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_nodeExporter_scc_can_be_enabled(kube_version):
    """prometheus nodeExporter SecurityContextConstraint should be present if sccEnabled and nodeExporterEnabled"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": True, "nodeExporterEnabled": True}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-nodeExporter"
        ),
        None,
    )
    assert x is not None


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_nodeExporter_scc_absent_if_nodeExporter_disabled(kube_version):
    """prometheus nodeExporter SecurityContextConstraint should disable if nodeExporter is disabled"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": True, "nodeExporterEnabled": False}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-nodeExporter"
        ),
        None,
    )
    assert x is None


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_nodeExporter_scc_absent_if_scc_disabled(kube_version):
    """prometheus nodeExporter SecurityContextConstraint should disable if sccEnabled is False"""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"sccEnabled": False, "nodeExporterEnabled": True}},
        skip_schema_validation=True,  # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next(
        (
            doc
            for doc in docs
            if doc["kind"] == "SecurityContextConstraints"
            and doc["metadata"]["name"] == "RELEASE-NAME-nodeExporter"
        ),
        None,
    )
    assert x is None
