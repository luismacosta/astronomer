from tests.chart_tests.helm_template_generator import render_chart
import pytest
from tests import supported_k8s_versions
import jmespath


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_daemonset(kube_version):
    """Test that helm renders a volume mount for private ca certificates for fluentd daemonset when private-ca-certificates are enabled."""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"privateCaCerts": ["private-root-ca"]}},
        show_only=["charts/fluentd/templates/fluentd-daemonset.yaml"],
    )

    search_result = jmespath.search(
        "spec.template.spec.containers[*].volumeMounts[?name == 'private-root-ca']",
        docs[0],
    )
    expected_result = [
        [
            {
                "mountPath": "/usr/local/share/ca-certificates/private-root-ca.pem",
                "name": "private-root-ca",
                "subPath": "cert.pem",
            }
        ]
    ]
    assert search_result == expected_result


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_clusterrolebinding(kube_version):
    """Test that helm renders a good ClusterRoleBinding template for fluentd when rbacEnabled=True."""
    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"rbacEnabled": True}},
        show_only=["charts/fluentd/templates/fluentd-clusterrolebinding.yaml"],
    )

    assert len(docs) == 1
    doc = docs[0]
    assert doc["kind"] == "ClusterRoleBinding"
    assert doc["apiVersion"] == "rbac.authorization.k8s.io/v1"
    assert doc["metadata"]["name"] == "release-name-fluentd"
    assert len(doc["roleRef"]) > 0
    assert len(doc["subjects"]) > 0

    docs = render_chart(
        kube_version=kube_version,
        values={"global": {"rbacEnabled": False}},
        show_only=["charts/fluentd/templates/fluentd-clusterrolebinding.yaml"],
    )

    assert len(docs) == 0


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_configmap_manual_namespaces_enabled(kube_version):
    """Test that when namespace Pools is disabled, and manualNamespaces is enabled, helm renders fluentd configmap targeting all namespaces."""
    doc = render_chart(
        kube_version=kube_version,
        values={
            "global": {
                "manualNamespaceNamesEnabled": True,
                "features": {
                    "namespacePools": {
                        "enabled": False,
                    }
                },
            }
        },
        show_only=["charts/fluentd/templates/fluentd-configmap.yaml"],
    )[0]

    expected_rule = "key $.kubernetes.namespace_name\n    # fluentd should gather logs from all namespaces if manualNamespaceNamesEnabled is enabled"
    assert expected_rule in doc["data"]["output.conf"]


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_configmap_manual_namespaces_and_namespacepools_disabled(kube_version):
    """Test that when namespace Pools and manualNamespaceNamesEnabled are disabled, helm renders a default fluentd configmap looking at an environment variable"""
    doc = render_chart(
        kube_version=kube_version,
        values={
            "global": {
                "manualNamespaceNamesEnabled": False,
                "features": {
                    "namespacePools": {
                        "enabled": False,
                    }
                },
            }
        },
        show_only=["charts/fluentd/templates/fluentd-configmap.yaml"],
    )[0]

    expected_rule = (
        'key $.kubernetes.namespace_labels.platform\n    pattern "release-name"'
    )
    assert expected_rule in doc["data"]["output.conf"]


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_pod_securityContextOverride(kube_version):
    """Test that helm renders a container securityContext when securityContext is enabled."""

    docs = render_chart(
        kube_version=kube_version,
        values={"fluentd": {"pod": {"securityContext": {"runAsUser": 9999}}}},
        show_only=["charts/fluentd/templates/fluentd-daemonset.yaml"],
    )

    pod_search_result = jmespath.search(
        "spec.template.spec",
        docs[0],
    )
    # the pod container should report a default user of 9999
    assert pod_search_result["securityContext"]["runAsUser"] == 9999


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_container_securityContextOverride(kube_version):
    """Test that helm renders a container securityContext when securityContext is enabled."""

    docs = render_chart(
        kube_version=kube_version,
        values={
            "fluentd": {
                "container": {
                    "securityContext": {
                        "runAsUser": 8888,
                        "seLinuxOptions": {"type": "spc_t"},
                    }
                }
            }
        },
        show_only=["charts/fluentd/templates/fluentd-daemonset.yaml"],
    )

    container_search_result = jmespath.search(
        "spec.template.spec.containers[?name == 'fluentd']",
        docs[0],
    )
    # the fluentd container should now report running as user 8888
    assert container_search_result[0]["securityContext"]["runAsUser"] == 8888


@pytest.mark.parametrize(
    "kube_version",
    supported_k8s_versions,
)
def test_fluentd_securityContext_empty_by_default(kube_version):
    """Test that no securityContext is present by default on pod or container"""

    docs = render_chart(
        kube_version=kube_version,
        values={},
        show_only=["charts/fluentd/templates/fluentd-daemonset.yaml"],
    )

    container_search_result = jmespath.search(
        "spec.template.spec.containers[?name == 'fluentd']",
        docs[0],
    )
    pod_search_result = jmespath.search(
        "spec.template.spec",
        docs[0],
    )
    # the securityContext should be present but empty by default
    assert not pod_search_result["securityContext"].keys()
    # the securityContext should be present but empty by default
    assert not container_search_result[0]["securityContext"].keys()
