
# Gramerf Framework

Gramerf framework is a test automation framework to measure the performance of Gramine against different workloads.

## Description:
This project provides a common automation framework for measuring the performance of Gramine, thereby making it easy to add any feasible workload to the framework without knowing deeper details of the worklaod itself !!

Details about Gramine can be found at - [Gramine](https://github.com/gramineproject/gramine)

## Infrastructure:

- System: `Intel Xeon Processor with SGX feature enabled` or `Virtual machine with SGX feature enabled`
- Operating System: `Ubuntu 18.04 / 20.04 / 22.04`
- Architecture: `x86_64`

## Pre-requisites:
- Following system dependencies would be required before executing the framework:

    `python >= 3.6.9` `meson` `lsb-release` `python3-pip` `git` `unzip`

- Following python packages would also be required:

    `pytest` `pandas` `openpyxl` `psutil` `netifaces`

Before installing the above system dependencies and python packages, ensure that the latest version of the package list is fetched from distro's software repository, and any third-party repositories that is configured on the system by executing `sudo apt-get update`.

## Installation:

This is a pytest based project. So, we just need to clone the project as mentioned below and proceed to execute from the project folder as specified in further sections.

```bash
  git clone https://github.com/vasanth-intel/gramerf_framework.git
  cd gramerf-framework
```

## Project Structure:

```
├── baremetal_benchmarking
│   ├── config_files
│   │   ├── openvino_latency.manifest.template
│   │   ├── openvino_throughput.manifest.template
│   │   ├── python_bert.manifest.template
│   │   ├── python_packages.yaml
│   │   ├── python_resnet.manifest.template
│   │   ├── redis-server.manifest.template.exitless
│   │   ├── redis-server.manifest.template.non-exitless
│   │   └── system_packages.yaml
│   ├── gramine_libs.py
│   ├── __init__.py
│   └── workloads
│       ├── __init__.py
│       ├── openvino_workload.py
│       ├── redis_workload.py
│       └── tensorflow_workload.py
├── ci
│   ├── Jenkinsfile
│   └── lib
│       └── gramerf-groovy-lib.groovy
├── common
│   ├── config_files
│   │   ├── constants.py
│   │   ├── __init__.py
│   │   └── set_cpu_freq_scaling_governor.sh
│   ├── __init__.py
│   ├── libs
│   │   ├── gramerf_wrapper.py
│   │   ├── __init__.py
│   │   ├── utils.py
│   │   └── workload.py
│   └── perf_benchmarks
│       ├── __init__.py
│       └── memtier_benchmark.py
├── data
│   ├── ov_performance_tests.yaml
│   ├── redis_performance_tests.yaml
│   ├── tf_performance_tests.yaml
│   └── tf_serving_performance_tests.yaml
├── docker_benchmarking
│   ├── curated_apps_lib.py
│   ├── __init__.py
│   └── workloads
│       ├── __init__.py
│       ├── redis_workload.py
│       └── tf_serving_workload.py
├── tests
│   ├── __init__.py
│   ├── test_ov_performance.py
│   ├── test_redis_performance.py
│   ├── test_tf_performance.py
│   └── test_tf_serving_performance.py
├── .gitignore
├── README.md
├── conftest.py
```

## Project Setup/Dependencies:

Following points need to be checked before we execute the framework.


- Ensure the date of the system is correct.

- Framework executes many commands with `sudo`. To suppress the password prompt every time we execute a bash cmd with `sudo`, we add following line to '/etc/sodoers' by running 'sudo visudo' cmd in bash.

	`%sudo ALL=(ALL) NOPASSWD: ALL`
	
- Openvino workload dependency:

  While executing the test with model 'brain-tumor-segmentation-0001", we need to copy folders "FP16" and "FP32" at "~/Do_not_delete_gramerf_dependencies/brain-tumor-segmentation-0001". Framework ensures that these folders are copied to "gramerf_framework/gramine/examples/openvino/model/public/brain-tumor-segmentation-0001/" when this test is executed.
	
- Redis workload dependency:
	- Ensure the client details (IP address, Username, Memtier benchmark scripts and results path) are updated accordingly within the input Redis yaml data file. Client password need to be updated as 'SSHPASS' environment variable within utils.py.

	- In order to execute ssh commands on the client, install sshpass on the server where the framework is running and generate a ~/.ssh/known_hosts file using "ssh -T user@HostClientIP" (Eg: `ssh -T intel@10.66.247.185`). This generates key within the 'known_hosts' file, without which the SSH commands will fail.

## Quick Start

Gramerf framework is built using pytest framework. So, using the pytest markers it has the ability to execute the whole workload to measure the performance of Gramine against the workload or a single performance test within the workload. Following are few quick steps to execute a workload using the framework.

1. Clone Gramerf framework repository.
`git clone https://github.com/vasanth-intel/gramerf_framework.git`

2. Change directory to the above cloned framework directory.
`cd gramerf-framework`
	
3. Execute the framework using the following command.
`python3 -m pytest -s -v -m workload_name_or_test_name --ignore=gramine --disable-warnings`
		
`workload_name_or_test_name` is the marker of workload or the test as specified in the respective workload test script.

Above are the bare minimum options that need to be passed to the framework for successful execution. Below are the additional options that can be passed to customize the execution.
	
```
--perf_config: 'baremetal' or 'container' based execution. Default is 'baremetal'.
	
--build_gramine: 'package' or 'source' based installation of Gramine. Default is 'source'.
	
--commit_id: Any specific commit to be used for source based installation. If nothing is specified, framework pulls the latest Gramine commit.
	
--iterations: Number of times workload/benchmark app needs to be launched/executed. Default is 3.
	
--exec_mode: Different execution modes for the workload.
			 Default is a comma separated list with value 'native,gramine-direct,gramine-sgx'.
			 For Redis workload, this value would be 'native,gramine-direct,gramine-sgx-single-thread-non-exitless,gramine-sgx-diff-core-exitless'.
	
--encryption: Enable encryption for model/s before workload command execution. This option is currently applicable only for	Tensorflow workload.
```

## Troubleshooting:

- While executing the framework, if you face any issues with respect to invalid/expired certificates, ensure that the date on the system is correct and then re-execute the framework. If you still face the same issue, verify that valid certificates are actually installed on the system and then re-execute the framework.

- While executing the framework, if you face any issues while executing scaling governor shell script, then execute the following command on the script and then re-run the framework.
	
	`sed -i -e 's/\r$//' scriptname.sh`
