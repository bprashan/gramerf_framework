import os
import pytest
from common.libs.gramerf_wrapper import run_test

yaml_file_name = "ov_performance_tests.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)


@pytest.mark.usefixtures("gramerf_setup")
class TestClass:

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_bert_large
    @pytest.mark.ov_perf_bert_large_throughput
    @pytest.mark.ov_perf_bert_large_fp16_throughput
    def test_ov_perf_bert_large_fp16_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_bert_large
    @pytest.mark.ov_perf_bert_large_throughput
    @pytest.mark.ov_perf_bert_large_fp32_throughput
    def test_ov_perf_bert_large_fp32_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_bert_large
    @pytest.mark.ov_perf_bert_large_latency
    @pytest.mark.ov_perf_bert_large_fp16_latency
    def test_ov_perf_bert_large_fp16_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_bert_large
    @pytest.mark.ov_perf_bert_large_latency
    @pytest.mark.ov_perf_bert_large_fp32_latency
    def test_ov_perf_bert_large_fp32_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_bert_large
    @pytest.mark.ov_perf_bert_large_int8_throughput
    def test_ov_perf_bert_large_int8_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_bert_large
    @pytest.mark.ov_perf_bert_large_int8_latency
    def test_ov_perf_bert_large_int8_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0002
    @pytest.mark.ov_perf_brain_tumor_seg_0002_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0002_fp16_throughput
    def test_ov_perf_brain_tumor_seg_0002_fp16_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0002
    @pytest.mark.ov_perf_brain_tumor_seg_0002_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0002_fp32_throughput
    def test_ov_perf_brain_tumor_seg_0002_fp32_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0002
    @pytest.mark.ov_perf_brain_tumor_seg_0002_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0002_fp16_latency
    def test_ov_perf_brain_tumor_seg_0002_fp16_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0002
    @pytest.mark.ov_perf_brain_tumor_seg_0002_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0002_fp32_latency
    def test_ov_perf_brain_tumor_seg_0002_fp32_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_resnet
    @pytest.mark.ov_perf_resnet_throughput
    @pytest.mark.ov_perf_resnet_fp16_throughput
    def test_ov_perf_resnet_fp16_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_resnet
    @pytest.mark.ov_perf_resnet_throughput
    @pytest.mark.ov_perf_resnet_fp32_throughput
    def test_ov_perf_resnet_fp32_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_resnet
    @pytest.mark.ov_perf_resnet_latency
    @pytest.mark.ov_perf_resnet_fp16_latency
    def test_ov_perf_resnet_fp16_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_resnet
    @pytest.mark.ov_perf_resnet_latency
    @pytest.mark.ov_perf_resnet_fp32_latency
    def test_ov_perf_resnet_fp32_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_ssd_mobilenet
    @pytest.mark.ov_perf_ssd_mobilenet_throughput
    @pytest.mark.ov_perf_ssd_mobilenet_fp16_throughput
    def test_ov_perf_ssd_mobilenet_fp16_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_ssd_mobilenet
    @pytest.mark.ov_perf_ssd_mobilenet_throughput
    @pytest.mark.ov_perf_ssd_mobilenet_fp32_throughput
    def test_ov_perf_ssd_mobilenet_fp32_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_ssd_mobilenet
    @pytest.mark.ov_perf_ssd_mobilenet_latency
    @pytest.mark.ov_perf_ssd_mobilenet_fp16_latency
    def test_ov_perf_ssd_mobilenet_fp16_latency(self):
        
        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_ssd_mobilenet
    @pytest.mark.ov_perf_ssd_mobilenet_latency
    @pytest.mark.ov_perf_ssd_mobilenet_fp32_latency
    def test_ov_perf_ssd_mobilenet_fp32_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0001
    @pytest.mark.ov_perf_brain_tumor_seg_0001_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0001_fp16_throughput
    def test_ov_perf_brain_tumor_seg_0001_fp16_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0001
    @pytest.mark.ov_perf_brain_tumor_seg_0001_throughput
    @pytest.mark.ov_perf_brain_tumor_seg_0001_fp32_throughput
    def test_ov_perf_brain_tumor_seg_0001_fp32_throughput(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0001
    @pytest.mark.ov_perf_brain_tumor_seg_0001_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0001_fp16_latency
    def test_ov_perf_brain_tumor_seg_0001_fp16_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.ov_perf
    @pytest.mark.ov_perf_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0001
    @pytest.mark.ov_perf_brain_tumor_seg_0001_latency
    @pytest.mark.ov_perf_brain_tumor_seg_0001_fp32_latency
    def test_ov_perf_brain_tumor_seg_0001_fp32_latency(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result
