import os
import pytest
import time
import subprocess
import sys
from common.config_files.constants import *
from common.libs.gramerf_wrapper import run_test
from common.libs import utils

yaml_file_name = "mysql_performance_tests.yaml"
tests_yaml_path = os.path.join(os.getcwd(), 'data', yaml_file_name)


def init_db(workload_name):
    docker_output = ''
    output = None
    init_result = False
    timeout = time.time() + 60*10
    try:
        os.makedirs(eval(workload_name.upper()+"_TESTDB_PATH"), exist_ok=True)
        process = subprocess.Popen(eval(workload_name.upper()+"_INIT_DB_CMD"), cwd=CURATED_APPS_PATH, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        print(f"Initializing {workload_name.upper()} DB")
        while True:
            if process.poll() is not None and output == '':
                break
            output = process.stderr.readline()
            print(output)
            if output:
                docker_output += output
                if (docker_output.count(eval(workload_name.upper()+"_TESTDB_VERIFY")) == 2):
                    print(f"{workload_name.upper()} DB is initialized\n")
                    init_result = True
                    break
                elif time.time() > timeout:
                    break
    finally:
        process.stdout.close()
        process.stderr.close()
        utils.kill(process.pid)
    if init_result:
        utils.exec_shell_cmd(STOP_TEST_DB_CMD)
        if "mariadb" in workload_name:
            utils.exec_shell_cmd(MARIADB_CHMOD)
    return init_result


def encrypt_db(workload_name):
    output = utils.popen_subprocess(eval(workload_name.upper()+"_TEST_ENCRYPTION_KEY"), CURATED_APPS_PATH)
    output = utils.popen_subprocess(CLEANUP_ENCRYPTED_DB, CURATED_APPS_PATH)
    encryption_output = utils.popen_subprocess(eval(workload_name.upper()+"_ENCRYPT_DB_CMD"), CURATED_APPS_PATH)


@pytest.fixture(scope="session")
def execute_workload_setup():
    init_result = init_db("mysql")
    if init_result == False:
        sys.exit("DB initialization failed")
    # Generate encryption key and encrypt MySql/MariaDB database.
    encrypt_db("mysql")


@pytest.mark.usefixtures("execute_workload_setup")
@pytest.mark.usefixtures("gramerf_setup")
class TestClass:

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_only
    @pytest.mark.mysql_perf_read_only_1_threads
    def test_mysql_perf_read_only_1_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_only
    @pytest.mark.mysql_perf_read_only_8_threads
    def test_mysql_perf_read_only_8_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_only
    @pytest.mark.mysql_perf_read_only_16_threads
    def test_mysql_perf_read_only_16_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_only
    @pytest.mark.mysql_perf_read_only_32_threads
    def test_mysql_perf_read_only_32_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_only
    @pytest.mark.mysql_perf_read_only_64_threads
    def test_mysql_perf_read_only_64_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_write_only
    @pytest.mark.mysql_perf_write_only_1_threads
    def test_mysql_perf_write_only_1_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_write_only
    @pytest.mark.mysql_perf_write_only_8_threads
    def test_mysql_perf_write_only_8_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_write_only
    @pytest.mark.mysql_perf_write_only_16_threads
    def test_mysql_perf_write_only_16_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_write_only
    @pytest.mark.mysql_perf_write_only_32_threads
    def test_mysql_perf_write_only_32_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_write_only
    @pytest.mark.mysql_perf_write_only_64_threads
    def test_mysql_perf_write_only_64_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_write
    @pytest.mark.mysql_perf_read_write_1_threads
    def test_mysql_perf_read_write_1_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_write
    @pytest.mark.mysql_perf_read_write_8_threads
    def test_mysql_perf_read_write_8_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_write
    @pytest.mark.mysql_perf_read_write_16_threads
    def test_mysql_perf_read_write_16_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_write
    @pytest.mark.mysql_perf_read_write_32_threads
    def test_mysql_perf_read_write_32_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result

    @pytest.mark.mysql_perf
    @pytest.mark.mysql_perf_read_write
    @pytest.mark.mysql_perf_read_write_64_threads
    def test_mysql_perf_read_write_64_threads(self):

        test_result = run_test(self, tests_yaml_path)
        assert test_result
