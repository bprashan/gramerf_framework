import time
import shutil
import glob
from common.config_files.constants import *
from baremetal_benchmarking import gramine_libs
from common.libs import utils
from common.perf_benchmarks import memtier_benchmark
from conftest import trd


class RedisWorkload:
    def __init__(self, test_config_dict):
        # Redis home dir => "~/gramerf_framework/gramine/CI-Examples/redis"
        self.workload_home_dir = os.path.join(FRAMEWORK_HOME_DIR, test_config_dict['workload_home_dir'])
        # Redis build dir => "~/gramerf_framework/gramine/CI-Examples/redis/redis-6.0.5"
        self.workload_bld_dir = os.path.join(self.workload_home_dir, "redis-6.0.5")
        self.server_ip_addr = utils.determine_host_ip_addr()
        self.command = None

    def get_workload_home_dir(self):
        return self.workload_home_dir

    def download_workload(self, test_config_dict):
        # We would not install if the installation dir already exists.
        if os.path.exists(self.workload_bld_dir):
            print("\n-- Redis already downloaded. Not fetching from source..")
            return True

        tar_file_name = os.path.basename(REDIS_DOWNLOAD_CMD.split()[1])
        untar_cmd = "tar xzf " + tar_file_name

        print("\n-- Fetching and extracting Redis workload from source..")
        utils.exec_shell_cmd(REDIS_DOWNLOAD_CMD)
        utils.exec_shell_cmd(untar_cmd)

    def build_and_install_workload(self, test_config_dict):
        print("\n###### In build_and_install_workload #####\n")

        bin_file_name = os.path.join(self.workload_bld_dir, "src", "redis-server")
        if os.path.exists(bin_file_name):
            print(f"\n-- Redis binary already built. Proceeding without building..\n")
            return

        if os.path.exists(self.workload_bld_dir):
            redis_bld_cmd = f"make -C {self.workload_bld_dir}"
            print(f"\n-- Building redis workload..\n", redis_bld_cmd)

            redis_make_log = LOGS_DIR + "/redis" + test_config_dict['test_name'] + '_make.log'
            log_fd = open(redis_make_log, "w")
            utils.exec_shell_cmd(redis_bld_cmd, log_fd)
            log_fd.close()
        else:
            raise Exception(f"\n{self.workload_bld_dir} does not exist!")
            
    def generate_manifest(self):
        manifest_cmd = "gramine-manifest -Dlog_level={} -Darch_libdir={} \
                            redis-server.manifest.template > redis-server.manifest".format(LOG_LEVEL, os.environ.get('ARCH_LIBDIR'))
        
        utils.exec_shell_cmd(manifest_cmd)

    def copy_server_binary(self):
        bin_file_name = os.path.join(self.workload_bld_dir, "src", "redis-server")
        if not os.path.exists(bin_file_name):
            raise Exception(f"\n{bin_file_name} does not exist! Please check if the binary was built successfully.")
        
        shutil.copy2(bin_file_name, self.workload_home_dir)

    def update_server_details_in_client(self, tcd):
        client_name = tcd['client_username'] + "@" + tcd['client_ip']
        client_file_path = os.path.join(tcd['client_scripts_path'], "instance_benchmark.sh")

        # Setting 'SSHPASS' env variable for ssh commands
        print(f"\n-- Updating 'SSHPASS' env-var\n")
        os.environ['SSHPASS'] = "intel@123"

        # Updating Server IP.
        host_sed_cmd = f"sed -i 's/^export HOST.*/export HOST=\"{self.server_ip_addr}\"/' {client_file_path}"
        update_server_ip_cmd = f"sshpass -e ssh {client_name} \"{host_sed_cmd}\""
        print("\n-- Updating server IP within redis client script..")
        print(update_server_ip_cmd)
        utils.exec_shell_cmd(update_server_ip_cmd)

        # Updating Server Port.
        # Client scripts are incrementing the port value and then using the result as server port.
        # Hence decreasing the port value by one to replace within the client script.
        port = tcd['baremetal_server_port'] - 1
        port_sed_cmd = f"sed -i 's/^export MASTER_START_PORT.*/export MASTER_START_PORT=\"{str(port)}\"/' {client_file_path}"
        update_server_port_cmd = f"sshpass -e ssh {client_name} \"{port_sed_cmd}\""
        print("\n-- Updating server Port within redis client script..")
        print(update_server_port_cmd)
        utils.exec_shell_cmd(update_server_port_cmd)

    def delete_old_test_results(self, tcd):
        print("\n-- Deleting older test results from client..")
        test_res_path = os.path.join(tcd['client_results_path'], tcd['test_name'])
        client_name = tcd['client_username'] + "@" + tcd['client_ip']
        test_res_del_cmd = f"sshpass -e ssh {client_name} 'rm -rf {test_res_path}'"
        print(test_res_del_cmd)
        utils.exec_shell_cmd(test_res_del_cmd)

    def pre_actions(self, test_config_dict):
        os.chdir(self.get_workload_home_dir())
        utils.set_cpu_freq_scaling_governor()
        self.update_server_details_in_client(test_config_dict)
        gramine_libs.update_manifest_file(test_config_dict)

    def setup_workload(self, test_config_dict):
        self.download_workload(test_config_dict)
        self.build_and_install_workload(test_config_dict)
        self.generate_manifest()
        self.copy_server_binary()
        self.delete_old_test_results(test_config_dict)
        gramine_libs.generate_sgx_token_and_sig(test_config_dict)

    def construct_server_workload_exec_cmd(self, test_config_dict, exec_mode = 'native'):
        redis_exec_cmd = None

        server_size = test_config_dict['server_size'] * 1024 * 1024 * 1024
        exec_bin_str = './redis-server' if exec_mode == 'native' else 'redis-server'

        tmp_exec_cmd = f"{exec_bin_str} --port {test_config_dict['baremetal_server_port']} --maxmemory {server_size} --maxmemory-policy allkeys-lru --appendonly no --protected-mode no --save '' &"
        
        if exec_mode == 'native':
            redis_exec_cmd = "numactl -C 1 " + tmp_exec_cmd
        elif exec_mode == 'gramine-direct':
            redis_exec_cmd = "numactl -C 1 gramine-direct " + tmp_exec_cmd
        elif exec_mode == 'gramine-sgx-single-thread-non-exitless':
            redis_exec_cmd = "numactl -C 1 gramine-sgx " + tmp_exec_cmd
        elif exec_mode == 'gramine-sgx-diff-core-exitless':
            redis_exec_cmd = "numactl -C 1,2 gramine-sgx " + tmp_exec_cmd
        else:
            raise Exception(f"\nInvalid execution mode specified in config yaml!")

        print("\n-- Server command name = \n", redis_exec_cmd)
        return redis_exec_cmd

    def free_redis_server_port(self, tcd):
        lsof_cmd = f"lsof -t -i:{tcd['baremetal_server_port']}"
        PID = utils.exec_shell_cmd(lsof_cmd)
        print(f"\n-- Killing server process {PID} running on port {tcd['baremetal_server_port']}")
        if PID is not None:
            kill_cmd = f"kill -9 {PID}"
            print(kill_cmd)
            utils.exec_shell_cmd(kill_cmd)

    # Default manifest specified in yaml would be 'redis-server.manifest.template.non-exitless'
    # for single thread non-exitless execution. We need to override and re-generate the 
    # manifest for multithreaded exitless configuration.
    def override_manifest_for_exitless(self, tcd):
        tcd['manifest_file'] = "redis-server.manifest.template.exitless"
        gramine_libs.update_manifest_file(tcd)
        self.generate_manifest()
        gramine_libs.generate_sgx_token_and_sig(tcd)

    # Build the workload execution command based on execution params and execute it.
    def execute_workload(self, tcd, e_mode, test_dict=None):
        print("\n##### In execute_workload #####\n")

        print(f"\n-- Executing {tcd['test_name']} in {e_mode} mode")

        if e_mode == 'gramine-sgx-diff-core-exitless':
            self.override_manifest_for_exitless(tcd)

        self.command = self.construct_server_workload_exec_cmd(tcd, e_mode)
        if self.command is None:
            raise Exception(
                f"\n-- Failure: Unable to construct command for {tcd['test_name']} Exec_mode: {e_mode}")

        # Bring up the redis server.
        utils.exec_shell_cmd(self.command, None)
        
        time.sleep(5)

        # Construct and execute memtier benchmark command within client.
        client_ssh_cmd = memtier_benchmark.construct_client_exec_cmd(tcd, e_mode)
        utils.exec_shell_cmd(client_ssh_cmd, None)
        
        time.sleep(5)

        self.free_redis_server_port(tcd)

        time.sleep(TEST_SLEEP_TIME_BW_ITERATIONS)

    def parse_csv_res_files(self, tcd):
        csv_test_res_folder = os.path.join(PERF_RESULTS_DIR, tcd['workload_name'], tcd['test_name'])
        os.chdir(csv_test_res_folder)
        csv_files = glob.glob1(csv_test_res_folder, "*.csv")
        
        if len(csv_files) != (len(tcd['exec_mode']) * tcd['iterations']):
            raise Exception(f"\n-- Number of test result files - {len(csv_files)} is not equal to the expected number - {len(tcd['exec_mode']) * tcd['iterations']}.\n")

        global trd
        test_dict_throughput = {}
        test_dict_latency = {}
        for e_mode in tcd['exec_mode']:
            test_dict_throughput[e_mode] = []
            test_dict_latency[e_mode] = []
        
        avg_latency = 0
        avg_throughput = 0
        for filename in csv_files:
            with open(filename, "r") as f:
                for row in f.readlines():
                    row = row.split()
                    if row:
                        if "Totals" in row[0]:
                            avg_latency = row[4]
                            avg_throughput = row[-1]
                            break

                if "native" in filename:
                    test_dict_latency['native'].append(float(avg_latency))
                    test_dict_throughput['native'].append(float(avg_throughput))
                elif "graphene_sgx_single_thread" in filename:
                    test_dict_latency['gramine-sgx-single-thread-non-exitless'].append(float(avg_latency))
                    test_dict_throughput['gramine-sgx-single-thread-non-exitless'].append(float(avg_throughput))
                elif "graphene_sgx_diff_core" in filename:
                    test_dict_latency['gramine-sgx-diff-core-exitless'].append(float(avg_latency))
                    test_dict_throughput['gramine-sgx-diff-core-exitless'].append(float(avg_throughput))
                else:
                    test_dict_latency['gramine-direct'].append(float(avg_latency))
                    test_dict_throughput['gramine-direct'].append(float(avg_throughput))

        if 'native' in tcd['exec_mode']:
            test_dict_latency['native-avg'] = '{:0.3f}'.format(sum(test_dict_latency['native'])/len(test_dict_latency['native']))
            test_dict_throughput['native-avg'] = '{:0.3f}'.format(sum(test_dict_throughput['native'])/len(test_dict_throughput['native']))

        if 'gramine-direct' in tcd['exec_mode']:
            test_dict_latency['direct-avg'] = '{:0.3f}'.format(
                sum(test_dict_latency['gramine-direct'])/len(test_dict_latency['gramine-direct']))
            test_dict_throughput['direct-avg'] = '{:0.3f}'.format(
                sum(test_dict_throughput['gramine-direct'])/len(test_dict_throughput['gramine-direct']))
            if 'native' in tcd['exec_mode']:
                test_dict_latency['direct-deg'] = utils.percent_degradation(tcd, test_dict_latency['native-avg'], test_dict_latency['direct-avg'])
                test_dict_throughput['direct-deg'] = utils.percent_degradation(tcd, test_dict_throughput['native-avg'], test_dict_throughput['direct-avg'], True)

        if 'gramine-sgx-single-thread-non-exitless' in tcd['exec_mode']:
            test_dict_latency['sgx-single-thread-avg'] = '{:0.3f}'.format(
                sum(test_dict_latency['gramine-sgx-single-thread-non-exitless'])/len(test_dict_latency['gramine-sgx-single-thread-non-exitless']))
            test_dict_throughput['sgx-single-thread-avg'] = '{:0.3f}'.format(
                sum(test_dict_throughput['gramine-sgx-single-thread-non-exitless'])/len(test_dict_throughput['gramine-sgx-single-thread-non-exitless']))
            if 'native' in tcd['exec_mode']:
                test_dict_latency['sgx-single-thread-deg'] = utils.percent_degradation(tcd, test_dict_latency['native-avg'], test_dict_latency['sgx-single-thread-avg'])
                test_dict_throughput['sgx-single-thread-deg'] = utils.percent_degradation(tcd, test_dict_throughput['native-avg'], test_dict_throughput['sgx-single-thread-avg'], True)

        if 'gramine-sgx-diff-core-exitless' in tcd['exec_mode']:
            test_dict_latency['sgx-diff-core-exitless-avg'] = '{:0.3f}'.format(
                sum(test_dict_latency['gramine-sgx-diff-core-exitless'])/len(test_dict_latency['gramine-sgx-diff-core-exitless']))
            test_dict_throughput['sgx-diff-core-exitless-avg'] = '{:0.3f}'.format(
                sum(test_dict_throughput['gramine-sgx-diff-core-exitless'])/len(test_dict_throughput['gramine-sgx-diff-core-exitless']))
            if 'native' in tcd['exec_mode']:
                test_dict_latency['sgx-diff-core-exitless-deg'] = utils.percent_degradation(tcd, test_dict_latency['native-avg'], test_dict_latency['sgx-diff-core-exitless-avg'])
                test_dict_throughput['sgx-diff-core-exitless-deg'] = utils.percent_degradation(tcd, test_dict_throughput['native-avg'], test_dict_throughput['sgx-diff-core-exitless-avg'], True)

        trd[tcd['workload_name']] = trd.get(tcd['workload_name'], {})
        trd[tcd['workload_name']].update({tcd['test_name']+'_latency': test_dict_latency})
        trd[tcd['workload_name']].update({tcd['test_name']+'_throughput': test_dict_throughput})

        os.chdir(self.workload_home_dir)

    def process_results(self, tcd):
        csv_res_folder = os.path.join(PERF_RESULTS_DIR, tcd['workload_name'])
        if not os.path.exists(csv_res_folder): os.makedirs(csv_res_folder)

        # Copy test results folder from client to local server results folder.
        client_res_folder = os.path.join(tcd['client_results_path'], tcd['test_name'])
        client_scp_path = tcd['client_username'] + "@" + tcd['client_ip'] + ":" + client_res_folder
        copy_client_to_server_cmd = f"sshpass -e scp -r {client_scp_path} {csv_res_folder}"
        utils.exec_shell_cmd(copy_client_to_server_cmd)

        # Parse the individual csv result files and update the global test results dict.
        self.parse_csv_res_files(tcd)
