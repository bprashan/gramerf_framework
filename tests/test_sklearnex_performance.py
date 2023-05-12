import os
import pytest
from common.libs.gramerf_wrapper import run_test

yaml_file_name = "sklearnex_performance_tests.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)


@pytest.mark.usefixtures("gramerf_setup")
class TestClass:

    # For this workload, after discussion with dev team we decided to run only two 
    # algorithms from skl_config.json as part of bi-weekly perf tests. 'kmeans' and
    # 'kd_tree_knn_clsf' are the two algorithms. Hence, we will use 'sklearnex_perf'
    # marker as the marker within Jenkins. But, we can still run other individual
    # algortihtm's tests below by using their corresponding markers.
    @pytest.mark.sklearnex_perf
    def test_sklearnex_perf_skl_config(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_dbscan
    def test_sklearnex_perf_dbscan(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_df_clsf
    def test_sklearnex_perf_df_clsf(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_df_regr
    def test_sklearnex_perf_df_regr(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_elasticnet
    def test_sklearnex_perf_elasticnet(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_kmeans
    def test_sklearnex_perf_kmeans(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_knn_clsf
    def test_sklearnex_perf_knn_clsf(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_knn_regr
    def test_sklearnex_perf_knn_regr(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_lasso
    def test_sklearnex_perf_lasso(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_linear
    def test_sklearnex_perf_linear(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_log_reg
    def test_sklearnex_perf_log_reg(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_nusvc
    def test_sklearnex_perf_nusvc(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_nusvr
    def test_sklearnex_perf_nusvr(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_pca
    def test_sklearnex_perf_pca(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_ridge
    def test_sklearnex_perf_ridge(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_svm
    def test_sklearnex_perf_svm(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_svr
    def test_sklearnex_perf_svr(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_train_test_split
    def test_sklearnex_perf_train_test_split(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.sklearnex_perf_tsne
    def test_sklearnex_perf_tsne(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result
