import time
import subprocess
import glob
import sys
import statistics
from common.config_files.constants import *
from docker_benchmarking import curated_apps_lib
from common.libs import utils
from common.perf_benchmarks import memtier_benchmark
from conftest import trd
import re

class MySqlWorkload:
    def __init__(self, test_config_dict):
        # MySql home dir => "~/gramerf_framework/contrib_repo/Intel-Confidential-Compute-for-X/"
        # Ideally, changing to home dir is required for bare-metal case as we build
        # the workload by downloading its source.
        # But, we are setting the workload home dir to CURATED_APPS_PATH in this
        # workload as we execute most of the workload commands from this dir.
        self.workload_home_dir = CURATED_APPS_PATH

    def get_workload_home_dir(self):
        return self.workload_home_dir

    def pull_workload_default_image(self, test_config_dict):
        workload_docker_image_name = utils.get_workload_name(test_config_dict['docker_image'])
        workload_docker_pull_cmd = f"docker pull {workload_docker_image_name}"
        print(f"\n-- Pulling MySql docker image from docker hub..\n", workload_docker_pull_cmd)
        utils.exec_shell_cmd(workload_docker_pull_cmd, None)

    def check_sgx_dirs(self, test_config_dict):
        if not 'gramine-sgx' in test_config_dict['exec_mode']:
            return
        if os.path.exists("/dev/sgx/enclave") and os.path.exists("/dev/sgx/provision"):
            utils.exec_shell_cmd("sudo chmod 777 /dev/sgx/enclave /dev/sgx/provision", None)
            return
        if not os.path.exists("/dev/sgx/enclave") and not os.path.exists("/dev/sgx_enclave"):
            raise Exception("\n-- Failure - Will not be able to run with SGX, due to absence of dev-enclave SGX folder")
        if not os.path.exists("/dev/sgx/provision") and not os.path.exists("/dev/sgx_provision"):
            raise Exception("\n-- Failure - Will not be able to run with SGX, due to absence of dev-provision SGX folder")
        utils.exec_shell_cmd("sudo mkdir /dev/sgx", None)
        utils.exec_shell_cmd("sudo cp -rf /dev/sgx_enclave /dev/sgx/enclave", None)
        utils.exec_shell_cmd("sudo cp -rf /dev/sgx_provision /dev/sgx/provision", None)
        utils.exec_shell_cmd("sudo chmod 777 /dev/sgx/enclave /dev/sgx/provision", None)

    def pre_actions(self, test_config_dict):
        os.chdir(self.get_workload_home_dir())
        utils.set_threads_cnt_env_var()
        utils.set_cpu_freq_scaling_governor()
        self.check_sgx_dirs(test_config_dict)

    def setup_workload(self, test_config_dict):
        # Pull default workload image for native run.
        self.pull_workload_default_image(test_config_dict)

        manifest_file = os.path.join(CURATED_APPS_PATH, "workloads/mysql/mysql.manifest.template")
        with open(manifest_file) as f:
            if not '2G' in f.read():
                enc_size_sed_cmd = f"sed -i 's/sgx.enclave_size = \"4G\"/sgx.enclave_size = \"2G\"/' {manifest_file}"
                utils.exec_shell_cmd(enc_size_sed_cmd, None)
        with open(manifest_file) as f:
            if not 'MALLOC_ARENA_MAX' in f.read():
                arena_sed_cmd = f"sed -i '/sys.enable_extra_runtime_domain_names_conf = true/a loader.env.MALLOC_ARENA_MAX = \"1\"' {manifest_file}"
                utils.exec_shell_cmd(arena_sed_cmd, None)

        # Create graminized image for gramine direct and sgx runs.
        print(f"\n-- Creating graminized image for SGX runs..")
        curation_output = curated_apps_lib.generate_curated_image(test_config_dict)
        decode_curation_output = curation_output.decode('utf-8')
        curation_output_result = curated_apps_lib.verify_image_creation(decode_curation_output)
        if curation_output_result == False:
            raise Exception("\n-- Failed to create the curated image!!")
        print(f"\n-- Successfully created graminized image..")

    def get_mysql_server_exec_cmd(self, tcd, e_mode, container_name):
        workload_docker_image_name = utils.get_workload_name(tcd['docker_image'])
        if e_mode == 'native':
            mysql_init_db_cmd = f"docker run --rm --net=host --name {container_name} --user $(id -u):$(id -g) \
                                    -v $PWD/workloads/mysql/test_db:/test_db \
                                    -e MYSQL_ALLOW_EMPTY_PASSWORD=true -e MYSQL_DATABASE=test_db {workload_docker_image_name} \
                                    --datadir /test_db"
        elif e_mode == 'gramine-sgx':
            if os.environ['encryption'] == '1':
                mysql_init_db_cmd = f"docker run --rm --net=host --name {container_name} --device=/dev/sgx/enclave \
                                        -v /var/run/test_db_encrypted:/var/run/test_db_encrypted \
                                        -t gsc-{workload_docker_image_name} --datadir /var/run/test_db_encrypted"
            else:
                mysql_init_db_cmd = f"docker run --rm --net=host --name {container_name} --device=/dev/sgx/enclave --user $(id -u):$(id -g) \
                                        -v $PWD/workloads/mysql/test_db:/test_db \
                                        -e MYSQL_ALLOW_EMPTY_PASSWORD=true -e MYSQL_DATABASE=test_db gsc-{workload_docker_image_name} \
                                        --datadir /test_db"
        return mysql_init_db_cmd

    def get_container_name(self, e_mode):
        if e_mode == 'native':
            return "init_native_test_db"
        elif e_mode == 'gramine-sgx':
            if os.environ['encryption'] == '1':
                return "init_sgx_enc_test_db"
            else:
                return "init_sgx_wo_enc_test_db"
        else:
            raise Exception("\n-- Invalid execution mode!!")

    def construct_sysbench_operation(self, tcd, mysql_cmd, e_mode='native', iteration=1):
        operation_cmd = ''
        if mysql_cmd == 'prepare' or mysql_cmd == 'cleanup':
            operation_cmd = f"sysbench --db-driver=mysql --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-db=test_db \
                                --time=40 --report-interval=5 {tcd['operation']} --tables=16 --table_size=100000 \
                                --threads={os.environ['CORES_COUNT']} {mysql_cmd}"
        elif mysql_cmd == 'run':
            results_dir = os.path.join(PERF_RESULTS_DIR, tcd['workload_name'], tcd['test_name'])
            output_file_name = results_dir + "/" + tcd['test_name'] + '_' + e_mode + '_' + str(iteration) + '.log'
            operation_cmd = f"sysbench --db-driver=mysql --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-db=test_db \
                                --time=40 --report-interval=5 {tcd['operation']} --tables=16 --table_size=100000 \
                                --threads={tcd['threads']} {mysql_cmd} | tee {output_file_name}"
        else:
            raise Exception("\n-- Invalid MySql operation command requested!!")
        
        return operation_cmd

    # Build the workload execution command based on execution params and execute it.
    def execute_workload(self, test_config_dict, e_mode, test_dict):
        print("\n##### In execute_workload #####\n")
        print(f"\n-- Executing {test_config_dict['test_name']} in {e_mode} mode")

        results_dir = os.path.join(PERF_RESULTS_DIR, test_config_dict['workload_name'], test_config_dict['test_name'])
        os.makedirs(results_dir, exist_ok=True)

        workload_docker_image_name = utils.get_workload_name(test_config_dict['docker_image'])
        container_name = self.get_container_name(e_mode)
        mysql_init_db_cmd = self.get_mysql_server_exec_cmd(test_config_dict, e_mode, container_name)
        print(f"\n-- Launching MySql server in {e_mode} mode..\n", mysql_init_db_cmd)

        print("\n\n", os.getcwd())
        
        process = utils.popen_subprocess(mysql_init_db_cmd)
        time.sleep(5)
        if curated_apps_lib.verify_process(test_config_dict, process, 60*10) == False:
            raise Exception(f"\n-- Failure - Couldn't launch MySql server in {e_mode} mode!!")

        # 'Prepare' and 'Cleanup' commands need to be performed only once per test.
        # Hence, not calling these commands in loop.
        prepare_op_cmd = self.construct_sysbench_operation(test_config_dict, "prepare")
        utils.exec_shell_cmd(prepare_op_cmd, None)
        time.sleep(5)

        for i in range(test_config_dict['iterations']):
            run_op_cmd = self.construct_sysbench_operation(test_config_dict, "run", e_mode, i + 1)
            run_cmd_output = utils.exec_shell_cmd(run_op_cmd)
            print(run_cmd_output)
            time.sleep(TEST_SLEEP_TIME_BW_ITERATIONS)

        cleanup_op_cmd = self.construct_sysbench_operation(test_config_dict, "cleanup")
        utils.exec_shell_cmd(cleanup_op_cmd, None)
        time.sleep(5)

        # workload cleanup
        utils.exec_shell_cmd("docker ps", None)
        print(f"\n\n-- Stopping MySql Server DB running in {e_mode} mode..\n")
        output = utils.exec_shell_cmd(f"docker stop {container_name}")
        print(output)
        
    def process_results(self, tcd):
        log_test_res_folder = os.path.join(PERF_RESULTS_DIR, tcd['workload_name'], tcd['test_name'])
        os.chdir(log_test_res_folder)
        log_files = glob.glob1(log_test_res_folder, "*.log")
        
        if len(log_files) != (len(tcd['exec_mode']) * tcd['iterations']):
            raise Exception(f"\n-- Number of test result files - {len(log_files)} is not equal to the expected number - {len(tcd['exec_mode']) * tcd['iterations']}.\n")

        global trd
        test_read_tpt_dict = {}
        test_write_tpt_dict = {}
        test_avg_lat_dict = {}
        test_95_pcnt_lat_dict = {}
        for e_mode in tcd['exec_mode']:
            test_read_tpt_dict[e_mode] = []
            test_write_tpt_dict[e_mode] = []
            test_avg_lat_dict[e_mode] = []
            test_95_pcnt_lat_dict[e_mode] = []
        
        read_throughput, write_throughput, avg_latency, percentile_95_latency = 0, 0, 0, 0
        for filename in log_files:
            with open(filename, "r") as f:
                all_results_captured = False
                for row in f.readlines():
                    row = row.split()
                    if row:
                        if "read:" in row[0]:
                            read_throughput = row[1]
                        elif "write:" in row[0]:
                            write_throughput = row[1]
                        elif "avg:" in row[0]:
                            avg_latency = row[1]
                        elif "95th" in row[0]:
                            percentile_95_latency = row[2]
                            all_results_captured = True
                            break

                if not all_results_captured:
                    if "native" in filename:
                        test_read_tpt_dict['native'].append(0)
                        test_write_tpt_dict['native'].append(0)
                        test_avg_lat_dict['native'].append(0)
                        test_95_pcnt_lat_dict['native'].append(0)
                    elif "gramine-sgx" in filename:
                        test_read_tpt_dict['gramine-sgx'].append(0)
                        test_write_tpt_dict['gramine-sgx'].append(0)
                        test_avg_lat_dict['gramine-sgx'].append(0)
                        test_95_pcnt_lat_dict['gramine-sgx'].append(0)
                    continue

                if "native" in filename:
                    test_read_tpt_dict['native'].append(float(read_throughput))
                    test_write_tpt_dict['native'].append(float(write_throughput))
                    test_avg_lat_dict['native'].append(float(avg_latency))
                    test_95_pcnt_lat_dict['native'].append(float(percentile_95_latency))
                elif "gramine-sgx" in filename:
                    test_read_tpt_dict['gramine-sgx'].append(float(read_throughput))
                    test_write_tpt_dict['gramine-sgx'].append(float(write_throughput))
                    test_avg_lat_dict['gramine-sgx'].append(float(avg_latency))
                    test_95_pcnt_lat_dict['gramine-sgx'].append(float(percentile_95_latency))
                else:
                    raise Exception(f"\n-- Incorrect results file present in test results folder.\n")

        if 'native' in tcd['exec_mode']:
            test_read_tpt_dict['native-avg'] = '{:0.3f}'.format(statistics.median(test_read_tpt_dict['native']))
            test_write_tpt_dict['native-avg'] = '{:0.3f}'.format(statistics.median(test_write_tpt_dict['native']))
            test_avg_lat_dict['native-avg'] = '{:0.3f}'.format(statistics.median(test_avg_lat_dict['native']))
            test_95_pcnt_lat_dict['native-avg'] = '{:0.3f}'.format(statistics.median(test_95_pcnt_lat_dict['native']))
            
        if 'gramine-sgx' in tcd['exec_mode']:
            test_read_tpt_dict['sgx-avg'] = '{:0.3f}'.format(statistics.median(test_read_tpt_dict['gramine-sgx']))
            test_write_tpt_dict['sgx-avg'] = '{:0.3f}'.format(statistics.median(test_write_tpt_dict['gramine-sgx']))
            test_avg_lat_dict['sgx-avg'] = '{:0.3f}'.format(statistics.median(test_avg_lat_dict['gramine-sgx']))
            test_95_pcnt_lat_dict['sgx-avg'] = '{:0.3f}'.format(statistics.median(test_95_pcnt_lat_dict['gramine-sgx']))
            if 'native' in tcd['exec_mode']:
                test_read_tpt_dict['sgx-deg'] = utils.percent_degradation(tcd, test_read_tpt_dict['native-avg'], test_read_tpt_dict['sgx-avg'], True)
                test_write_tpt_dict['sgx-deg'] = utils.percent_degradation(tcd, test_write_tpt_dict['native-avg'], test_write_tpt_dict['sgx-avg'], True)
                test_avg_lat_dict['sgx-deg'] = utils.percent_degradation(tcd, test_avg_lat_dict['native-avg'], test_avg_lat_dict['sgx-avg'])
                test_95_pcnt_lat_dict['sgx-deg'] = utils.percent_degradation(tcd, test_95_pcnt_lat_dict['native-avg'], test_95_pcnt_lat_dict['sgx-avg'])

        trd[tcd['workload_name']] = trd.get(tcd['workload_name'], {})
        trd[tcd['workload_name']].update({tcd['test_name']+'_read': test_read_tpt_dict})
        trd[tcd['workload_name']].update({tcd['test_name']+'_write': test_write_tpt_dict})
        trd[tcd['workload_name']].update({tcd['test_name']+'_avg': test_avg_lat_dict})
        trd[tcd['workload_name']].update({tcd['test_name']+'_95th_percentile': test_95_pcnt_lat_dict})

        os.chdir(self.workload_home_dir)
