import os
import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestPortainer(object):
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_portainer(self):
        """
        Sets up and validates Portainer.
        """
        print("Enabling Portainer")
        microk8s_enable("portainer")
        print("Validating Portainer")
        self.validate_portainer()
        print("Disabling Portainer")
        microk8s_disable("portainer")

    def validate_portainer(self):
        """
        Validate portainer
        """
        wait_for_pod_state(
            "", "portainer", "running", label="app.kubernetes.io/name=portainer"
        )
