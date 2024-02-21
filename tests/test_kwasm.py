import pytest
import os
import platform

from utils import (
    kubectl,
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestKwasm(object):
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    @pytest.mark.skipif(
        os.environ.get("STRICT") == "yes",
        reason="Skipping kwasm tests in strict confinement as they are expected to fail",
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_kwasm(self):
        """
        Sets up and validates kwasm.
        """
        print("Enabling kwasm")
        microk8s_enable("kwasm")
        print("Validating kwasm")
        self.validate_kwasm()
        print("Disabling kwasm")
        microk8s_disable("kwasm")

    def validate_kwasm(self):
        """
        Validate kwasm
        """
        wait_for_pod_state(
            "", "kwasm-system", "running", label="app.kubernetes.io/name=kwasm-operator"
        )

        here = os.path.dirname(os.path.abspath(__file__))
        manifest = os.path.join(here, "templates", "wasm-job.yaml")
        kubectl("apply -f {}".format(manifest))
        wait_for_pod_state(
            "", "default", "terminated", "Completed", label="job-name=wasm-test"
        )
        kubectl("delete -f {}".format(manifest))
        print("kwasm is up and running")
