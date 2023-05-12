import os
import pytest
from common.libs.gramerf_wrapper import run_test

yaml_file_name = "tf_serving_performance_tests.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)


@pytest.mark.usefixtures("gramerf_setup")
class TestClass:

    @pytest.mark.tf_serving_perf
    @pytest.mark.tf_serving_perf_resnet
    def test_tf_serving_perf_resnet_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

