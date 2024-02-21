import os
import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestEasyHAProxy(object):
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_easyhaproxy(self):
        """
        Disabling conflicting addons
        """
        microk8s_disable("ingress")
        microk8s_disable("traefik")

        """
        Sets up and validates easyhaproxy.
        """
        print("Enabling easyhaproxy")
        microk8s_enable("easyhaproxy")
        print("Validating easyhaproxy")
        self.validate_easyhaproxy()
        print("Disabling easyhaproxy")
        microk8s_disable("easyhaproxy")

    def validate_easyhaproxy(self):
        """
        Validate easyhaproxy
        """
        wait_for_pod_state(
            "", "easyhaproxy", "running", label="app.kubernetes.io/name=easyhaproxy"
        )
