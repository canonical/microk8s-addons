import pytest
import os
import platform
import sh
import yaml

from utils import (
    docker,
    get_arch,
    is_container,
    kubectl,
    kubectl_get,
    microk8s_disable,
    microk8s_enable,
    microk8s_reset,
    run_until_success,
    update_yaml_with_arch,
    wait_for_installation,
    wait_for_namespace_termination,
    wait_for_pod_state,
)
from subprocess import PIPE, STDOUT, CalledProcessError, check_call, run, check_output


class TestKnative(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping knative tests as we are under time pressure",
    )
    @pytest.mark.skip(reason="Due to https://github.com/canonical/microk8s/issues/3597")
    def test_knative(self):
        """
        Test knative
        """

        print("Enabling Knative")
        microk8s_enable("knative")
        print("Validating Knative")
        self.validate_knative()
        print("Disabling Knative")
        microk8s_disable("knative")
        wait_for_namespace_termination("knative-serving", timeout_insec=600)

    def validate_knative(self):
        """
        Validate Knative by deploying the helloworld-go app supports both amd64 and arm64
        """

        wait_for_installation()
        knative_services = [
            "activator",
            "autoscaler",
            "controller",
            "domain-mapping",
            "autoscaler-hpa",
            "domainmapping-webhook",
            "webhook",
            "net-kourier-controller",
            "3scale-kourier-gateway",
        ]
        for service in knative_services:
            wait_for_pod_state(
                "", "knative-serving", "running", label="app={}".format(service)
            )

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "knative-helloworld.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state(
            "", "default", "running", label="serving.knative.dev/service=helloworld-go"
        )
        kubectl("delete -f {}".format(manifest))
