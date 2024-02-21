import os
import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_installation,
    wait_for_pod_state,
)


class TestOsmEdge(object):
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    @pytest.mark.skipif(platform.machine() == "s390x", reason="Not available on s390x")
    def test_osm_edge(self):
        """
        Sets up and validate osm-edge

        """
        print("Enabling osm-edge")
        microk8s_enable("osm-edge")
        print("Validate osm-edge installation")
        self.validate_osm_edge()
        print("Disabling osm-edge")
        microk8s_disable("osm-edge")

    def validate_osm_edge(self):
        """
        Validate osm-edge
        """
        wait_for_installation()
        wait_for_pod_state(
            "",
            "osm-system",
            "running",
            label="app=osm-controller",
            timeout_insec=300,
        )
        print("osm-edge controller up and running")
        wait_for_pod_state(
            "",
            "osm-system",
            "running",
            label="app=osm-injector",
            timeout_insec=300,
        )
        print("osm-edge proxy injector up and running.")
