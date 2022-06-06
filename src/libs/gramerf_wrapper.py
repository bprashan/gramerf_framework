#
# Imports
#
import os
import yaml
import inspect
import shutil
from src.libs.Workload import Workload
from src.libs import gramine_libs
from src.config_files.constants import *
from src.libs import utils

def read_perf_suite_config(test_instance, test_yaml_file, test_name):
    # Reading global config data.
    config_file_name = "config.yaml"
    config_file_path = os.path.join(FRAMEWORK_HOME_DIR, 'src/config_files', config_file_name)
    with open(config_file_path, "r") as config_fd:
        try:
            test_config_dict = yaml.safe_load(config_fd)
        except yaml.YAMLError as exc:
            print(exc)

    # Reading workload specific data.
    with open(test_yaml_file, "r") as test_default_fd:
        try:
            yaml_test_config = yaml.safe_load(test_default_fd)
        except yaml.YAMLError as exc:
            print(exc)

    test_config_dict.update(yaml_test_config['Default'])

    # Reading test specific data.
    if yaml_test_config.get(test_name):
        test_config_dict.update(yaml_test_config[test_name])
        test_config_dict['test_name'] = test_name

    # Reading command line overrides.
    if test_instance._config.getoption('--iterations') != 1:
        test_config_dict['iterations'] = test_instance._config.getoption('iterations')
    
    if test_instance._config.getoption('--exec_mode') != '' and test_instance._config.getoption('--exec_mode') != 'None':
        test_config_dict['exec_mode'] = test_instance._config.getoption('exec_mode').split(' ')

    print("\n-- Read the following Test Configuration Data : \n\n", test_config_dict)

    return test_config_dict

def run_test(test_instance, test_yaml_file):

    test_name = inspect.stack()[1].function

    test_config_dict = read_perf_suite_config(test_instance, test_yaml_file, test_name)
    
    test_obj = Workload(test_config_dict)
    workload_home_dir = os.path.join(FRAMEWORK_HOME_DIR, test_config_dict['workload_home_dir'])
    os.chdir(workload_home_dir)

    # Workload pre-actions if any.
    test_obj.pre_actions(test_config_dict)
        
    gramine_libs.update_manifest_file(test_config_dict)
    # Download, build and install workload.
    test_obj.setup_workload(test_config_dict)
    gramine_libs.generate_sgx_token_and_sig(test_config_dict)
    test_obj.execute_workload(test_config_dict)
    os.chdir(FRAMEWORK_HOME_DIR)
    
    test_obj.parse_performance(test_config_dict)
        

    test_obj.calculate_degradation(test_config_dict)

    return True
