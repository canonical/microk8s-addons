import pytest
import os
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    run_until_success,
    wait_for_installation,
    wait_for_pod_state,
)


class TestIstio(object):
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == "True",
        reason="Skipping istio and knative tests as we are under time pressure",
    )
    def test_istio(self):
        """
        Sets up and validate istio.
        """
        print("Enabling Istio")
        microk8s_enable("istio")
        print("Validating Istio")
        self.validate_istio()
        print("Disabling Istio")
        microk8s_disable("istio")

    def validate_istio(self):
        """
        Validate istio by deploying the bookinfo app.
        """
        @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
        wait_for_installation()
        istio_services = ["pilot", "egressgateway", "ingressgateway"]
        for service in istio_services:
            wait_for_pod_state(
                "", "istio-system", "running", label="istio={}".format(service)
            )

        cmd = "/snap/bin/microk8s.istioctl verify-install"
        return run_until_success(cmd, timeout_insec=900, err_out="no")
