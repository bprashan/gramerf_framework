import sys
import time
import re
from common.config_files.constants import *
from common.libs import utils
from conftest import trd


class TensorflowWorkload():
    def __init__(self, test_config_dict):
        self.workload_home_dir = os.path.join(FRAMEWORK_HOME_DIR, test_config_dict['workload_home_dir'])
        os.makedirs(self.workload_home_dir, exist_ok=True)
        self.command = None
        
    def download_workload(self, test_config_dict):
        if sys.version_info < (3, 6):
            raise Exception("Please upgrade Python version to atleast 3.6 or higher before executing this workload.")

        print("\n-- Executing pip upgrade command..")
        utils.exec_shell_cmd(PIP_UPGRADE_CMD)
        
        print("\n-- Installing Tensorflow..")
        utils.exec_shell_cmd(TENSORFLOW_INSTALL_CMD)

    def download_bert_models(self):
        if not os.path.exists('./models'):
            utils.exec_shell_cmd(TF_BERT_INTEL_AI_MODELS_CLONE_CMD, None)
        
        os.makedirs('./data', exist_ok=True)

        dataset_folder_name = TF_BERT_DATASET_UNZIP_CMD.split()[1].split('.')[0]
        if not os.path.exists(dataset_folder_name):
            print("\n-- Downloading BERT dataset models..")
            utils.exec_shell_cmd(TF_BERT_DATASET_WGET_CMD, None)
            utils.exec_shell_cmd(TF_BERT_DATASET_UNZIP_CMD, None)
            utils.exec_shell_cmd(TF_BERT_SQUAAD_DATASET_WGET_CMD, None)
        
        checkpoints_folder_name = TF_BERT_CHECKPOINTS_UNZIP_CMD.split()[1].split('.')[0]
        if not os.path.exists(checkpoints_folder_name):
            print("\n-- Downloading BERT checkpoints models..")
            utils.exec_shell_cmd(TF_BERT_CHECKPOINTS_WGET_CMD, None)
            utils.exec_shell_cmd(TF_BERT_CHECKPOINTS_UNZIP_CMD, None)
            utils.exec_shell_cmd(TF_BERT_FP32_MODEL_WGET_CMD, None)

        print("\n-- Required BERT models downloaded / already present..")

    def download_resnet_models(self):
        if not os.path.exists('./models'):
            print("\n-- Downloading RESNET Intel_AI models..")
            utils.exec_shell_cmd(TF_RESNET_INTEL_AI_MODELS_CLONE_CMD, None)

        resnet_inte8_model_name = os.path.basename(TF_RESNET_INT8_MODEL_WGET_CMD.split()[1])
        if not os.path.exists(resnet_inte8_model_name):
            print("\n-- Downloading RESNET Pretrained model..")
            utils.exec_shell_cmd(TF_RESNET_INT8_MODEL_WGET_CMD, None)

        print("\n-- Required RESNET models downloaded / already present..")

    def build_and_install_workload(self, test_config_dict):
        print("\n###### In build_and_install_workload #####\n")

        if test_config_dict['model_name'] == 'bert':
            self.download_bert_models()
        elif test_config_dict['model_name'] == 'resnet':
            self.download_resnet_models()
        else:
            raise Exception("Unknown tensorflow model. Please check the test yaml file.")

    def generate_manifest(self):
        entrypoint_path = utils.exec_shell_cmd("sh -c 'command -v python3'")
        pythondist_path = os.path.expanduser('~/.local/lib/python') + '%d.%d' % sys.version_info[:2] + "/site-packages"

        manifest_cmd = "gramine-manifest -Dlog_level={} -Darch_libdir={} -Dentrypoint={} -Dpythondistpath={} \
                            python.manifest.template > python.manifest".format(
            LOG_LEVEL, os.environ.get('ARCH_LIBDIR'), entrypoint_path, pythondist_path)
        
        utils.exec_shell_cmd(manifest_cmd)

    def install_mimalloc(self):
        if os.path.exists(MIMALLOC_INSTALL_PATH):
            print("\n-- Library 'mimalloc' already exists.. Returning without rebuilding.\n")
            return

        print("\n-- Setting up mimalloc for Openvino..\n", MIMALLOC_CLONE_CMD)
        utils.exec_shell_cmd(MIMALLOC_CLONE_CMD)
        mimalloc_dir = os.path.join(self.workload_home_dir, 'mimalloc')
        os.chdir(mimalloc_dir)
        mimalloc_make_dir_path = os.path.join(mimalloc_dir, 'out/release')
        os.makedirs(mimalloc_make_dir_path, exist_ok=True)
        os.chdir(mimalloc_make_dir_path)

        utils.exec_shell_cmd("cmake ../..")
        utils.exec_shell_cmd("make")
        utils.exec_shell_cmd("sudo make install")

        os.chdir(self.workload_home_dir)

        if not os.path.exists(MIMALLOC_INSTALL_PATH):
            raise Exception(f"\n-- Library {MIMALLOC_INSTALL_PATH} not generated/installed.\n")

    def pre_actions(self, test_config_dict):
        utils.set_threads_cnt_env_var()
        utils.set_cpu_freq_scaling_governor()
        if test_config_dict['model_name'] == 'bert':
            self.install_mimalloc()

    def setup_workload(self, test_config_dict):
        self.download_workload(test_config_dict)
        self.build_and_install_workload(test_config_dict)
        self.generate_manifest()

    def construct_workload_exec_cmd(self, test_config_dict, exec_mode = 'native', iteration=1):
        tf_exec_cmd = None
        exec_mode_cmd = 'python3' if exec_mode == 'native' else exec_mode + ' python'
        taskset_str = f"0-{int(os.environ['CORES_PER_SOCKET']) - 1} "
        output_file_name = LOGS_DIR + "/" + test_config_dict['test_name'] + '_' + exec_mode + '_' + str(iteration) + '.log'

        print("\nOutput file name = ", output_file_name)
        if test_config_dict['model_name'] == 'bert':
            tf_exec_cmd = "OMP_NUM_THREADS=" + os.environ['CORES_PER_SOCKET'] + " KMP_AFFINITY=granularity=fine,verbose,compact,1,0" + \
                            " taskset -c " + taskset_str + exec_mode_cmd + \
                            " models/models/language_modeling/tensorflow/bert_large/inference/run_squad.py" + \
                            " --init_checkpoint=data/bert_large_checkpoints/model.ckpt-3649" + \
                            " --vocab_file=data/wwm_uncased_L-24_H-1024_A-16/vocab.txt" + \
                            " --bert_config_file=data/wwm_uncased_L-24_H-1024_A-16/bert_config.json" + \
                            " --predict_file=data/wwm_uncased_L-24_H-1024_A-16/dev-v1.1.json" + \
                            " --precision=int8" + \
                            " --output_dir=output/bert-squad-output" + \
                            " --predict_batch_size=" + str(test_config_dict['batch_size']) + \
                            " --experimental_gelu=True" + \
                            " --optimized_softmax=True" + \
                            " --input_graph=data/fp32_bert_squad.pb" + \
                            " --do_predict=True --mode=benchmark" + \
                            " --inter_op_parallelism_threads=1" + \
                            " --intra_op_parallelism_threads=" + os.environ['CORES_PER_SOCKET'] + " | tee " + output_file_name

            os.environ['LD_PRELOAD'] = MIMALLOC_INSTALL_PATH if exec_mode == 'native' else ''

        elif test_config_dict['model_name'] == 'resnet':
            tf_exec_cmd = "OMP_NUM_THREADS=" + os.environ['CORES_PER_SOCKET'] + " KMP_AFFINITY=granularity=fine,verbose,compact,1,0" + \
                            " taskset -c " + taskset_str + exec_mode_cmd + \
                            " models/models/image_recognition/tensorflow/resnet50v1_5/inference/eval_image_classifier_inference.py" + \
                            " --input-graph=resnet50v1_5_int8_pretrained_model.pb" + \
                            " --num-inter-threads=1" + \
                            " --num-intra-threads=" + os.environ['CORES_PER_SOCKET'] + \
                            " --batch-size=" + str(test_config_dict['batch_size']) + \
                            " --warmup-steps=50" + \
                            " --steps=500 | tee " + output_file_name

            os.environ['LD_PRELOAD'] = TCMALLOC_INSTALL_PATH if exec_mode == 'native' else ''

        else:
            raise Exception("\n-- Failure: Internal error! Non-existent tensorflow model..")

        print("\nCommand name = ", tf_exec_cmd)
        return tf_exec_cmd

    @staticmethod
    def get_metric_value(test_config_dict, test_file_name):
        with open(test_file_name, 'r') as test_fd:
            for line in test_fd:
                if re.search(test_config_dict['metric'], line, re.IGNORECASE) is not None:
                    throughput = re.findall('\d+\.\d+', line)
                    return round(float(throughput[0]),3)

    # Build the workload execution command based on execution params and execute it.
    def execute_workload(self, tcd):
        print("\n##### In execute_workload #####\n")
        test_dict = {}
        global trd

        for e_mode in tcd['exec_mode']:
            print(f"\n-- Executing {tcd['test_name']} in {e_mode} mode")
            test_dict[e_mode] = []
            for j in range(tcd['iterations']):
                self.command = self.construct_workload_exec_cmd(tcd, e_mode, j + 1)

                if self.command is None:
                    raise Exception(
                        f"\n-- Failure: Unable to construct command for {tcd['test_name']} Exec_mode: {e_mode}")

                cmd_output = utils.exec_shell_cmd(self.command)
                print(cmd_output)
                if cmd_output is None or utils.verify_output(cmd_output, tcd['metric']) is None:
                    raise Exception(
                        f"\n-- Failure: Test workload execution failed for {tcd['test_name']} Exec_mode: {e_mode}")

                test_file_name = LOGS_DIR + '/' + tcd['test_name'] + '_' + e_mode + '_' + str(j+1) + '.log'
                if not os.path.exists(test_file_name):
                    raise Exception(f"\nFailure: File {test_file_name} does not exist for parsing performance..")
                metric_val = float(self.get_metric_value(tcd, test_file_name))
                test_dict[e_mode].append(metric_val)
                
                time.sleep(TEST_SLEEP_TIME_BW_ITERATIONS)

        if 'native' in tcd['exec_mode']:
            test_dict['native-avg'] = '{:0.3f}'.format(sum(test_dict['native'])/len(test_dict['native']))

        if 'gramine-direct' in tcd['exec_mode']:
            test_dict['direct-avg'] = '{:0.3f}'.format(
                sum(test_dict['gramine-direct'])/len(test_dict['gramine-direct']))
            if 'native' in tcd['exec_mode']:
                test_dict['direct-deg'] = utils.percent_degradation(test_dict['native-avg'], test_dict['direct-avg'])

        if 'gramine-sgx' in tcd['exec_mode']:
            test_dict['sgx-avg'] = '{:0.3f}'.format(sum(test_dict['gramine-sgx'])/len(test_dict['gramine-sgx']))
            if 'native' in tcd['exec_mode']:
                test_dict['sgx-deg'] = utils.percent_degradation(test_dict['native-avg'], test_dict['sgx-avg'])

        utils.write_to_csv(tcd, test_dict)

        trd[tcd['workload_name']] = trd.get(tcd['workload_name'], {})
        trd[tcd['workload_name']].update({tcd['test_name']: test_dict})
