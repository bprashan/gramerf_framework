import sys
import pytest
import time
import json
import glob
import shutil
import warnings
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from common.config_files.constants import *
from common.libs import utils
from baremetal_benchmarking import gramine_libs
from conftest import trd


@pytest.mark.usefixtures("func")
class SklearnexWorkload():
    def __init__(self, test_config_dict):
        self.workload_home_dir = os.path.join(FRAMEWORK_HOME_DIR, test_config_dict['workload_home_dir'])
        os.makedirs(self.workload_home_dir, exist_ok=True)
        self.command = None

    def get_workload_home_dir(self):
        return self.workload_home_dir
        
    def download_workload(self):
        if sys.version_info < (3, 6):
            raise Exception("Please upgrade Python version to atleast 3.6 or higher before executing this workload.")

        distro, distro_version = utils.get_distro_and_version()
        if distro == 'ubuntu' and distro_version == '18.04':
            # We need to upgrade pip to latest version only on 18.04, as scikit-learn
            # is not available with older version of pip. On other distro versions, no
            # need for upgrading pip.
            print("\n-- Executing pip upgrade command..")
            utils.exec_shell_cmd(PIP_UPGRADE_CMD)
        
        if distro == 'ubuntu' and (distro_version == '20.04' or distro_version == '21.04'):
            utils.exec_shell_cmd("sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y python-is-python3", None)

        # Checking if the directory is empty or not
        if not os.listdir(self.workload_home_dir):
            print("\n-- Cloning scikit-learn benchmark..")
            utils.exec_shell_cmd(SKL_REPO_CLONE_CMD, None)

        # Deleting old data folder. Result file deletion will be taken care later.
        # Data within the 'Data' folder should be freshly taken if the version of 
        # sklearn repo is different. Data folder must be created again to avoid
        # failures later.
        #if os.path.exists("data"):
        #    shutil.rmtree("data")

        os.makedirs("results", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
    def build_and_install_workload(self):
        # Check if workload is already installed    
        if not utils.is_package_installed("scikit-learn-intelex"):
            print("\n-- Installing scikit-learn-intelex benchmark..")
            requirements_txt = os.path.join(FRAMEWORK_HOME_DIR, 'baremetal_benchmarking/config_files', "sklearnex_requirements.txt")
            utils.exec_shell_cmd("python3 -m pip install -r " + requirements_txt + " --no-cache-dir", None)
        else:
            print("\n-- Scikit-learn-intelex benchmark already installed..")
    
    def generate_manifest(self):
        entrypoint_path = utils.exec_shell_cmd("sh -c 'command -v python3'")

        manifest_cmd = "gramine-manifest -Dlog_level={} -Darch_libdir={} -Denv_user_uid={} -Denv_user_gid={} -Dentrypoint={} \
                            sklearnex.manifest.template > sklearnex.manifest".format(
            LOG_LEVEL, os.environ.get('ARCH_LIBDIR'), os.environ.get('ENV_USER_UID'), os.environ.get('ENV_USER_GID'), entrypoint_path)
        
        utils.exec_shell_cmd(manifest_cmd)

    def pre_actions(self, test_config_dict):
        os.chdir(self.get_workload_home_dir())
        utils.set_threads_cnt_env_var()
        utils.set_cpu_freq_scaling_governor()

    def delete_old_test_reports(self, tcd):
        print("\n-- Deleting old test reports..")
        report_folder = os.path.join(PERF_RESULTS_DIR, tcd['workload_name'], tcd['test_name'])
        # Deleting old xlsx report folder.
        if os.path.exists(report_folder):
            shutil.rmtree(report_folder)

        # Re-create the folder to collect the report later.
        os.makedirs(report_folder, exist_ok=True)    

    def setup_workload(self, test_config_dict):
        self.download_workload()
        gramine_libs.update_manifest_file(test_config_dict)
        self.build_and_install_workload()
        self.generate_manifest()
        self.delete_old_test_reports(test_config_dict)
        gramine_libs.generate_sgx_token_and_sig(test_config_dict)

    def copy_local_skl_config_json(self, test_config_dict):
        src_file = os.path.join(FRAMEWORK_HOME_DIR, "baremetal_benchmarking/config_files" , test_config_dict['config_name'])
        dest_file = os.path.join(FRAMEWORK_HOME_DIR, test_config_dict['workload_home_dir'] , "configs", test_config_dict['config_name'])

        shutil.copy2(src_file, dest_file)
        
    def construct_workload_exec_cmd(self, test_config_dict, exec_mode = 'native'):
        skl_exec_cmd = None
        exec_mode_cmd = 'python3' if exec_mode == 'native' else exec_mode + ' sklearnex'
        if test_config_dict['test_name'] == 'test_sklearnex_perf_skl_config':
            self.copy_local_skl_config_json(test_config_dict)
            config_file = os.path.join("configs", test_config_dict['config_name'])
        else:
            config_file = os.path.join(test_config_dict['config_dir'], test_config_dict['config_name'])
        path_obj = Path(test_config_dict['config_name'])
        res_file_name = "{0}_{1}{2}".format(path_obj.stem, exec_mode, path_obj.suffix)
        result_file = os.path.join("results", res_file_name)
        
        try: # Deleting old json results file.
            os.remove(result_file)
        except OSError:
            pass

        skl_exec_cmd = f"{exec_mode_cmd} runner.py --configs {config_file} --output-file {result_file}"
        print("\nCommand name = ", skl_exec_cmd)
        return skl_exec_cmd

    def construct_test_report_gen_cmd(self, tcd, exec_mode = 'native'):
        test_report_cmd = None
        path_obj = Path(tcd['config_name'])
        res_file_name = "{0}_{1}{2}".format(path_obj.stem, exec_mode, path_obj.suffix)
        result_file = os.path.join("results", res_file_name)
        report_file_name = "{0}_{1}{2}".format(path_obj.stem, exec_mode, ".xlsx")
        report_file = os.path.join(PERF_RESULTS_DIR, tcd['workload_name'], tcd['test_name'], report_file_name)

        if not os.path.exists(result_file):
            raise Exception(
                f"\n-- Failure: Results file {result_file} does not exist! Cannot generate report for {tcd['test_name']} Exec_mode: {exec_mode}")

        test_report_cmd = "python3 report_generator/report_generator.py --result-files " + result_file + \
                           " --report-file " + report_file + " --generation-config report_generator/default_report_gen_config.json"
        print("\nReport generate command = ", test_report_cmd)
        return test_report_cmd

    # Build the workload execution command based on execution params and execute it.
    def execute_workload(self, tcd, e_mode, test_dict=None):
        print("\n##### In execute_workload #####\n")

        print(f"\n-- Executing {tcd['test_name']} in {e_mode} mode")

        self.command = self.construct_workload_exec_cmd(tcd, e_mode)
        if self.command is None:
            raise Exception(
                f"\n-- Failure: Unable to construct command for {tcd['test_name']} Exec_mode: {e_mode}")

        # Execute the benchmark.
        cmd_output = utils.exec_shell_cmd(self.command)
        if cmd_output is not None:
            print(cmd_output)

        # Verify the output of above command execution and fail if necessary.
        if cmd_output is None or utils.verify_output(cmd_output, "Error in benchmark") is not None or \
                                utils.verify_output(cmd_output, "Error reading the CPU table") is not None:
                # Currently, issuing only warning. Above error may get fixed with later versions of benchmark repo.
                warnings.warn(f"\n-- Failure: Test workload execution failed for {tcd['test_name']} Exec_mode: {e_mode}")

        time.sleep(TEST_SLEEP_TIME_BW_ITERATIONS)

        # Generate report.
        test_report_cmd = self.construct_test_report_gen_cmd(tcd, e_mode)
        if test_report_cmd is None:
            raise Exception(
                f"\n-- Failure: Unable to construct test report command for {tcd['test_name']} Exec_mode: {e_mode}")

        utils.exec_shell_cmd(test_report_cmd)

        time.sleep(TEST_SLEEP_TIME_BW_ITERATIONS)

    def get_column_header(self, data_frame, col_index):
        # Extract all rows containing 'algorithm'
        row = data_frame.loc[data_frame[0] == 'algorithm']
        
        # Converting data frame into list of dictionaries.
        row_list = row.to_dict(orient='records')

        # Now convert the first dict entry into column list and return the
        # same to be used as column header.
        col_header = list(row_list[0].values())

        # Change the value of the last element of the column header to 'time'.
        # This is an important assignment, as all the perf time values are 
        # extracted from this column.
        col_header[col_index] = 'time'

        return col_header

    def get_training_prediction_dicts(self, report_file_name, sheetname, filter_str):
        
        data_frame = pd.read_excel(report_file_name, sheet_name=sheetname, engine='openpyxl')

        # Rename columns to indices (numbers) to get rid of 'Unnamed' columns
        # and to get the column index of column containing the string 'time'
        # in the next statement.
        data_frame.columns = range(data_frame.shape[1])

        # Get the index of column containing the string 'time[s]'.
        col_index_list = data_frame.columns[(data_frame.values=='time[s]').any(0)].to_list()

        # Retrieve the column header of the future data frame. This cannot be performed
        # later since all 'Nan' entries will be filtered in the next statement and we will
        # not be able to get the column header after the next statement.
        col_header = self.get_column_header(data_frame, col_index_list[0])

        # Delete all blank rows of the filtered dataframe.
        data_frame = data_frame.replace(r'^\s*$', np.nan, regex=True)
        data_frame.dropna(axis=0, how='any', inplace=True)

        # Extract all rows containing 'training'/'prediction' within first column.
        filtered_df = data_frame.loc[data_frame[1] == filter_str]
        
        # Retain and rename only required columns and ignore the rest.
        filtered_df = filtered_df.iloc[:,4:col_index_list[0]+1]
        filtered_df.columns = col_header[4:col_index_list[0]+1] # Renaming with the column header extracted earlier.
        
        # Convert the data frame into a dictionary. By passing 'orient' parameter with
        # 'records' value, we are converting each row within the dataframe into a dictionary.
        # We can later access the dict elements like below.
        # training_dict[0]['data_type'], training_dict[0]['time']..
        filtered_dict = filtered_df.to_dict(orient='records')

        return filtered_dict

    # Search for the existence of super dict row within sub dict.
    # If found, calculate degradation and update the same within 
    # sub dict and return True.
    # Return False if not found.
    def check_row_presence(self, tr_pd_dict, super_dict_row, sub_index):
        # Remove 'time : value' key value pair entries/column from sub dict
        # and copy the other key values to a temp dict, so that searching the super 
        # row within sub dict becomes easy.
        temp_dict = [{key : val for key, val in sub.items() if key != 'time'} for sub in tr_pd_dict[sub_index]]
        temp_super_row = super_dict_row.copy() # Making a shallow copy so that original super dict row is not changed.
        del temp_super_row['time'] # Removing 'time : value' column.
        try:
            found_index = temp_dict.index(temp_super_row)
            return found_index
        except ValueError:
            return -1

    def calculate_degradation(self, tcd, tr_pd_dict, algo, e_mode):
        # This method will be called for both 'gramine-direct' and 'gramine-sgx' only
        # when 'native' is part of execution mode list.
        dict_index = algo + "_" + e_mode # Index/name of either direct or sgx dicts within training/prediciton dicts
        native_index = algo + "_native" # Index/name of native dict within training/prediciton dicts
        if len(tr_pd_dict[native_index]) > len(tr_pd_dict[dict_index]):
            super_index = native_index
            sub_index = dict_index
        else:
            super_index = dict_index
            sub_index = native_index
        for i in range(len(tr_pd_dict[super_index])):
            # Find the existence of super dict row within sub dict and retrieve the matching index. 
            found_index = self.check_row_presence(tr_pd_dict, tr_pd_dict[super_index][i], sub_index)
            if found_index != -1:
                # Super dict row entry found in sub dict. Hence, calculate the degradation
                # in the correspoding index (found_index) entry of the sub dict.
                tr_pd_dict[dict_index][found_index][e_mode+"-deg"] = utils.percent_degradation(tcd, tr_pd_dict[native_index][i]['time'],
                                                                                                    tr_pd_dict[dict_index][found_index]['time'])
            else:
                # Super dict row entry not found in sub dict. So, insert the
                # row entry at the right position of sub dict and mark the
                # degradation with 'NA' as sub dict data is unavailable.  
                # This is a failure case in Gramine, which should be escalated.
                temp_super_row = tr_pd_dict[super_index][i].copy()
                tr_pd_dict[sub_index].insert(i, temp_super_row)
                tr_pd_dict[sub_index][i]["time"] = 'NA'
                tr_pd_dict[sub_index][i][e_mode+"-deg"] = 'NA'

    # This method is used to re-structure the training/predcition dictionaries (which have
    # the degradation data already computed) to match the dataframe column structure 
    # while creating the final report.
    def format_dict(self, tcd, algo, test_dict):
        formatted_dict = defaultdict(dict)
        temp_dict = {}
        if 'native' in tcd['exec_mode']:
            dict_index = algo + "_native"
        elif 'gramine-direct' in tcd['exec_mode']:
            dict_index = algo + "_gramine-direct"
        elif 'gramine-sgx' in tcd['exec_mode']:
            dict_index = algo + "_gramine-sgx"
        if test_dict.get(dict_index) != None:
            temp_dict = dict(enumerate(test_dict[dict_index]))

        if 'native' in tcd['exec_mode'] and temp_dict:
            for i in range(len(temp_dict)):
                formatted_dict[i] = (temp_dict[i])
                if 'gramine-direct' in tcd['exec_mode']:
                    dict_index = algo + "_gramine-direct"
                    if test_dict.get(dict_index) != None:
                        formatted_dict[i]['gramine-direct'] = test_dict[dict_index][i]['time']
                        if test_dict[dict_index][i].get('gramine-direct-deg') != None:
                            formatted_dict[i]['gramine-direct-deg'] = test_dict[dict_index][i]['gramine-direct-deg']
                if 'gramine-sgx' in tcd['exec_mode']:
                    dict_index = algo + "_gramine-sgx"
                    if test_dict.get(dict_index) != None:
                        formatted_dict[i]['gramine-sgx'] = test_dict[dict_index][i]['time']
                        if test_dict[dict_index][i].get('gramine-sgx-deg') != None:
                            formatted_dict[i]['gramine-sgx-deg'] = test_dict[dict_index][i]['gramine-sgx-deg']
            # We are done with all formatting for all modes if 'native' is present in exec mode.
            # So, return the final formatted dict without further processing.
            return formatted_dict

        if 'gramine-direct' in tcd['exec_mode']:
            # Case where only 'gramine-direct' is present in execution mode. Hence, no need to copy deg data.
            if test_dict.get(dict_index) != None:
                for i in range(len(temp_dict)):
                    formatted_dict[i] = (temp_dict[i])
                    dict_index = algo + "_gramine-direct"
                    formatted_dict[i]['gramine-direct'] = test_dict[dict_index][i]['time']

        if 'gramine-sgx' in tcd['exec_mode']:
            # Case where only 'gramine-sgx' is present in execution mode. Hence, no need to copy deg data.
            if test_dict.get(dict_index) != None:
                for i in range(len(temp_dict)):
                    formatted_dict[i] = (temp_dict[i])
                    dict_index = algo + "_gramine-sgx"
                    formatted_dict[i]['gramine-sgx'] = test_dict[dict_index][i]['time']

        return formatted_dict

    def calc_deg_for_individual_algo(self, tcd, test_dict_training, test_dict_prediction, algo):
        if 'native' in tcd['exec_mode'] and 'gramine-direct' in tcd['exec_mode']:
            filename = tcd['config_name'].split('.')[0] + '_gramine-direct.xlsx'
            xlsx_file = pd.ExcelFile(filename, engine='openpyxl')
            sheet_names = [sheet for sheet in xlsx_file.sheet_names if sheet.lower().startswith(algo)]
            if len(sheet_names) != 0:
                # We are not calculating degradations if the algo is not present in the workload generated report.
                # This is a failure condition and is handled/reported in the earlier flow.
                # All those corresponding gramine-direct entries are reported as blanks in the final report.
                self.calculate_degradation(tcd, test_dict_training, algo, 'gramine-direct')
                self.calculate_degradation(tcd, test_dict_prediction, algo, 'gramine-direct')

        if 'native' in tcd['exec_mode'] and 'gramine-sgx' in tcd['exec_mode']:
            filename = tcd['config_name'].split('.')[0] + '_gramine-sgx.xlsx'
            xlsx_file = pd.ExcelFile(filename, engine='openpyxl')
            sheet_names = [sheet for sheet in xlsx_file.sheet_names if sheet.lower().startswith(algo)]
            if len(sheet_names) != 0:
                # We are not calculating degradations if the algo is not present in the workload generated report.
                # This is a failure condition and is handled/reported in the earlier flow.
                # All those corresponding gramine-sgx entries are reported as blanks in the final report.
                self.calculate_degradation(tcd, test_dict_training, algo, 'gramine-sgx')
                self.calculate_degradation(tcd, test_dict_prediction, algo, 'gramine-sgx')

# =======================================================
# The results from different report (.xlsx) files are 
# parsed and collected in the following two training and
# prediction nested dictionaries in the below format.
# =======================================================
# training
# 	algo_native
# 		datatype1 rows1 col1 native1
#       datatype2 rows2 col2 native2
# 	algo_gramine-sgx
# 		datatype1 rows1 col1 gramine-sgx1 sgx-deg1
# 		datatype2 rows2 col2 gramine-sgx2 sgx-deg2
# 	algo_gramine-direct
# 		datatype1 rows1 col1 gramine-direct1 direct-deg1
# 		datatype2 rows2 col2 gramine-direct2 direct-deg2
# =======================================================
# prediction
# 	algo_native
# 		datatype1 rows1 col1 native1
#       datatype2 rows2 col2 native2
# 	algo_gramine-sgx
# 		datatype1 rows1 col1 gramine-sgx1 sgx-deg1
# 		datatype2 rows2 col2 gramine-sgx2 sgx-deg2
# 	algo_gramine-direct
# 		datatype1 rows1 col1 gramine-direct1 direct-deg1
# 		datatype2 rows2 col2 gramine-direct2 direct-deg2
# =======================================================
    def process_results(self, tcd):
        xlsx_test_rep_folder = os.path.join(PERF_RESULTS_DIR, tcd['workload_name'], tcd['test_name'])
        os.chdir(xlsx_test_rep_folder)
        xlsx_files = glob.glob1(xlsx_test_rep_folder, "*.xlsx")
        
        if len(xlsx_files) != (len(tcd['exec_mode'])):
            raise Exception(f"\n-- Number of test report files - {len(xlsx_files)} is not equal to the expected number - {len(tcd['exec_mode'])}.\n")

        global trd
        test_dict_training = {}
        test_dict_prediction = {}

        # We are converting the config file name into list to simplify the 
        # code further below which works well for both cases where a config 
        # has either 1 algorithm or multiple algorithms.
        if 'algorithms' in tcd:
            # Case where a config has multiple algos.
            algo_list = tcd['algorithms'].split(',')
        else:
            algo_list = [tcd['config_name'].split('.')[0]]
        for filename in xlsx_files:
            if "native" in filename:
                e_mode = 'native'
            elif "gramine-direct" in filename:
                e_mode = 'gramine-direct'
            elif "gramine-sgx" in filename:
                e_mode = 'gramine-sgx'
            
            xlsx_file = pd.ExcelFile(filename, engine='openpyxl')
            for i in range(len(algo_list)):
                sheet_names = [sheet for sheet in xlsx_file.sheet_names if sheet.lower().startswith(algo_list[i])]
                if len(sheet_names) == 0:
                    warnings.warn(f"\n-- Failure: Worksheet not present with name '{algo_list[i]}' algorithm!!\n")
                    continue
                dict_index = algo_list[i] + "_" + e_mode
                test_dict_training[dict_index] = self.get_training_prediction_dicts(filename, sheet_names[0], 'training')
                if algo_list[i] == 'pca':
                    test_dict_prediction[dict_index] = self.get_training_prediction_dicts(filename, sheet_names[0], 'transformation')
                else:
                    test_dict_prediction[dict_index] = self.get_training_prediction_dicts(filename, sheet_names[0], 'prediction')

        trd[tcd['workload_name']] = trd.get(tcd['workload_name'], {})
        for i in range(len(algo_list)):
            self.calc_deg_for_individual_algo(tcd, test_dict_training, test_dict_prediction, algo_list[i])
            formatted_training_dict = self.format_dict(tcd, algo_list[i], test_dict_training)
            formatted_prediction_dict = self.format_dict(tcd, algo_list[i], test_dict_prediction)

            trd[tcd['workload_name']].update({tcd['test_name']+'_training_'+algo_list[i]: formatted_training_dict})
            trd[tcd['workload_name']].update({tcd['test_name']+'_prediction_'+algo_list[i]: formatted_prediction_dict})

        os.chdir(self.workload_home_dir)
