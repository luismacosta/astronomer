from tests.helm_template_generator import render_chart
import pytest
import jmespath

from . import supported_k8s_versions

@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_elastic_scc_can_be_enabled(kube_version):
    """elastic SecurityContextConstraint should be present if sccEnabled and elasticsearchEnabled"""
    docs = render_chart(
	kube_version=kube_version,
	values={"global": {"sccEnabled": True, "elasticsearchEnabled": True}},
	skip_schema_validation=True, # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next((doc for doc in docs if doc["kind"] == "SecurityContextConstraints" and doc["metadata"]["name"] == "RELEASE-NAME-elastic"), None)
    assert(x is not None)

@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_elastic_scc_absent_if_elastic_disabled(kube_version):
    """elastic SecurityContextConstraint should disable if elastic is disabled"""
    docs = render_chart(
	kube_version=kube_version,
	values={"global": {"sccEnabled": True, "elasticsearchEnabled": False}},
	skip_schema_validation=True, # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next((doc for doc in docs if doc["kind"] == "SecurityContextConstraints" and doc["metadata"]["name"] == "RELEASE-NAME-elastic"), None)
    assert(x is None)

@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_elastic_scc_absent_if_scc_disabled(kube_version):
    """elastic SecurityContextConstraint should disable if elastic is disabled"""
    docs = render_chart(
	kube_version=kube_version,
	values={"global": {"sccEnabled": False, "elasticsearchEnabled": True}},
	skip_schema_validation=True, # apparently no schema for SecurityContextConstraints in the normal spot
    )
    # there should be lots of image hits
    assert len(docs) > 50
    x = next((doc for doc in docs if doc["kind"] == "SecurityContextConstraints" and doc["metadata"]["name"] == "RELEASE-NAME-elastic"), None)
    assert(x is None)
