import pytest
import platform
import os


from utils import (
    is_container,
    microk8s_enable,
    microk8s_disable,
    microk8s_reset,
    wait_for_installation,
    wait_for_pod_state,
)


class TestKubearmor(object):
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason=(
            "Skipping kubearmor tests in strict confinement as they are expected to fail"
        ),
    )
    @pytest.mark.skipif(
        is_container(), reason="Kubearmor tests are skipped in containers"
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_kubearmor(self):
        """
        Sets up and validates kubearmor.
        """
        print("Enabling Kubearmor")
        microk8s_enable("kubearmor")
        print("Validating Kubearmor")
        self.validate_kubearmor()
        print("Disabling Kubearmor")
        microk8s_disable("kubearmor")
        microk8s_reset()

    def validate_kubearmor(self):
        """
        Validate kubearmor by applying policy to nginx container.
        """

        wait_for_installation()
        kubearmor_pods = [
            "kubearmor-controller",
            "kubearmor",
            "kubearmor-relay",
        ]
        for pod in kubearmor_pods:
            wait_for_pod_state(
                "", "kube-system", "running", label="kubearmor-app={}".format(pod)
            )

        print("Kubearmor testing passed.")
