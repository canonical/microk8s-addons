import os
import pytest
import platform

from utils import (
    microk8s_disable,
    microk8s_enable,
    wait_for_pod_state,
)


class TestGoPaddleLite(object):
    @pytest.mark.skipif(
        os.environ.get("UNDER_TIME_PRESSURE") == None,
        reason="Skipping test, expected to be tested when under time pressure",
    )
    @pytest.mark.skipif(
        platform.machine() == "s390x",
        reason="gopaddle tests are only relevant in x86 and arm64 architectures",
    )
    def test_gopaddle_lite(self):
        """
        Sets up and validates gopaddle.
        """
        print("Enabling gopaddle")
        microk8s_enable("gopaddle")
        print("Validating gopaddle")
        self.validate_gopaddle_lite()
        print("Disabling gopaddle")
        microk8s_disable("gopaddle")

    def validate_gopaddle_lite(self):
        """
        Validate gopaddle
        """
        wait_for_pod_state("", "gopaddle", "running", label="released-by=gopaddle")
