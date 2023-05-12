import time
import subprocess
import glob
import statistics
from common.config_files.constants import *
from docker_benchmarking import curated_apps_lib
from common.libs import utils
from common.perf_benchmarks import memtier_benchmark
from conftest import trd
import re

class TensorflowServingWorkload:
    def __init__(self, test_config_dict):
        # Redis home dir => "~/gramerf_framework"
        # Setting the workload home dir to framework root dir.
        # Changing to home dir is required for bare-metal case as we build
        # the workload by downloading its source.
        # In container case, we would just pull the docker image from the repo
        # and not build it. So, we do not require any workload home dir here.
        # Hence, assigning the home dir as framework dir itself and not
        # changing to it within pre-actions in container case, as we would 
        # anyways be executing from framework dir.
        self.workload_home_dir = FRAMEWORK_HOME_DIR

    def get_workload_home_dir(self):
        return self.workload_home_dir

    def pull_workload_default_image(self):
        print("Starting Process %s from %s" %(TFSERVING_HELPER_CMD, os.getcwd()))
        logged_in_user = os.getlogin()
        # The following command needs to run on tty.
        tf_serving_base_image_cmd = f"ssh -tt {logged_in_user}@localhost 'cd {CURATED_APPS_PATH} && {TFSERVING_HELPER_CMD}'"
        process = subprocess.run(tf_serving_base_image_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True, shell=True)
        if process.returncode != 0:
            print(process.stderr.strip())
            raise Exception("Failed to run command {}".format(TFSERVING_HELPER_CMD))
        print(process.stdout.strip())

    def download_and_update_tfserving_repo(self):
        print("\n-- Cloning Tensorflow serving repo...")
        output = utils.exec_shell_cmd(TFSERVING_CLONE_CMD, None)
        print(output)
        print("\n-- Update Tensorflow serving repo...")
        output = utils.exec_shell_cmd(TFSERVING_RESNET_SED_CMD)
        print(output)

    def exec_workload_perf_cmd(self, test_config_dict, test_dict, exec_mode = 'native'):
        iteration = test_config_dict['iterations']
        utils.set_no_proxy()
        for itr in range(iteration):
            output = utils.exec_shell_cmd(TFSERVING_RESNET_PERF_CMD)
            print(output)
            output = float(re.search(r"(?<=latency:).*?(?=ms)", output).group(0).strip())
            print(output)
            test_dict[exec_mode].append(output)

    def pre_actions(self, test_config_dict):
        utils.set_cpu_freq_scaling_governor()

    def setup_workload(self, test_config_dict):
        # Pull default workload image for native run.
        self.pull_workload_default_image()
        # clone the serving repo to get the latency values
        self.download_and_update_tfserving_repo()
        # Create graminized image for gramine direct and sgx runs.
        curation_output = curated_apps_lib.generate_curated_image(test_config_dict)
        decode_curation_output = curation_output.decode('utf-8')
        curation_output_result = curated_apps_lib.verify_image_creation(decode_curation_output)
        if curation_output_result == False:
            raise Exception("\n-- Failed to create the curated image!!")
    
    # Build the workload execution command based on execution params and execute it.
    def execute_workload(self, test_config_dict, e_mode, test_dict):
        print("\n##### In execute_workload #####\n")
        print(f"\n-- Executing {test_config_dict['test_name']} in {e_mode} mode")

        workload_docker_image_name = utils.get_workload_name(test_config_dict['docker_image'])
        workload_docker_arguments = test_config_dict["docker_arguments"]
        if e_mode == 'native':
            # docker run --net=host -it tf-serving-base --model_name="resnet" --model_base_path="/models/resnet"
            docker_native_cmd = f"docker run --rm --net=host -t {workload_docker_image_name} {workload_docker_arguments}"
            process = utils.popen_subprocess(docker_native_cmd)
            if curated_apps_lib.verify_process(test_config_dict, process) == False:
                raise Exception(f"\n-- Failure - Couldn't launch tf-serving in {e_mode} mode!!")
        else:
            docker_run_cmd = curated_apps_lib.get_docker_run_command(workload_docker_image_name + ' ' + workload_docker_arguments)
            result = curated_apps_lib.run_curated_image(test_config_dict,docker_run_cmd)
            if result == False:
                raise Exception(f"\n-- Failure - Couldn't launch tf-serving in {e_mode} mode!!")

        self.exec_workload_perf_cmd(test_config_dict, test_dict, e_mode)

        # workload cleanup
        if e_mode == 'native':
            output = utils.exec_shell_cmd("docker stop $(docker ps -a -q)")
            print(output)
        else:
            utils.cleanup_after_test(workload_docker_image_name)

    def update_test_results_in_global_dict(self, tcd, test_dict):
        global trd
        if 'native' in tcd['exec_mode']:
            test_dict['native-avg'] = '{:0.3f}'.format(statistics.median(test_dict['native']))

        if 'gramine-direct' in tcd['exec_mode']:
            test_dict['direct-avg'] = '{:0.3f}'.format(statistics.median(test_dict['gramine-direct']))
            if 'native' in tcd['exec_mode']:
                test_dict['direct-deg'] = utils.percent_degradation(tcd, test_dict['native-avg'], test_dict['direct-avg'])

        if 'gramine-sgx' in tcd['exec_mode']:
            test_dict['sgx-avg'] = '{:0.3f}'.format(statistics.median(test_dict['gramine-sgx']))
            if 'native' in tcd['exec_mode']:
                test_dict['sgx-deg'] = utils.percent_degradation(tcd, test_dict['native-avg'], test_dict['sgx-avg'])

        utils.write_to_csv(tcd, test_dict)

        trd[tcd['workload_name']] = trd.get(tcd['workload_name'], {})
        trd[tcd['workload_name']].update({tcd['test_name']: test_dict})