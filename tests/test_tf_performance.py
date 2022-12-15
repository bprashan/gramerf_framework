import os
import pytest
from common.libs.gramerf_wrapper import run_test

yaml_file_name = "tf_performance_tests.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)


@pytest.mark.usefixtures("gramerf_setup")
class TestClass:

    @pytest.mark.tf_perf
    @pytest.mark.tf_perf_bert
    def test_tf_perf_bert_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.tf_perf
    @pytest.mark.tf_perf_resnet
    @pytest.mark.tf_perf_resnet_bs_1
    def test_tf_perf_resnet_bs_1_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.tf_perf
    @pytest.mark.tf_perf_resnet
    @pytest.mark.tf_perf_resnet_bs_512
    def test_tf_perf_resnet_bs_512_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.tf_perf
    @pytest.mark.tf_perf_resnet
    @pytest.mark.tf_perf_resnet_bs_16
    def test_tf_perf_resnet_bs_16_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result
