import time
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


class TestInaccel(object):
    @pytest.fixture(scope="session", autouse=True)
    def clean_up(self):
        """
        Clean up after a test
        """
        yield
        microk8s_reset()

    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping FPGA tests as we are under time pressure",
    )
    @pytest.mark.skipif(
        os.environ.get("TEST_FPGA") != "True",
        reason="Skipping FPGA because TEST_FPGA is not set",
    )
    @pytest.mark.skipif(
        platform.machine() != "x86_64",
        reason="FPGA tests are only relevant in x86 architectures",
    )
    def test_inaccel(self):
        """
        Sets up inaccel.

        """
        try:
            print("Enabling inaccel")
            microk8s_enable("inaccel")
        except CalledProcessError:
            # Failed to enable addon. Skip the test.
            print("Could not enable inaccel support")
            return
        self.validate_inaccel()
        print("Disable inaccel")
        microk8s_disable("inaccel")

    def validate_inaccel(self):
        """
        Validate inaccel by trying a vadd.
        """
        if platform.machine() != "x86_64":
            print("FPGA tests are only relevant in x86 architectures")
            return

        wait_for_pod_state(
            "", "kube-system", "running", label="app.kubernetes.io/name=fpga-operator"
        )
        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "inaccel.yaml")

        get_pod = kubectl_get("po")
        if "inaccel-vadd" in str(get_pod):
            # Cleanup
            kubectl("delete -f {}".format(manifest))
            time.sleep(10)

        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state("inaccel-vadd", "default", "terminated")
        result = kubectl("logs pod/inaccel-vadd")
        assert "PASSED" in result
