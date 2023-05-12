import os

FRAMEWORK_HOME_DIR = os.getcwd()
GRAMINE_HOME_DIR = FRAMEWORK_HOME_DIR + "/gramine"
LOGS_DIR = FRAMEWORK_HOME_DIR + "/logs"
PERF_RESULTS_DIR = FRAMEWORK_HOME_DIR + "/results"
HTTP_PROXY = "http://proxy-dmz.intel.com:911/"
HTTPS_PROXY = "http://proxy-dmz.intel.com:912/"
NO_PROXY = "10.0.0.0/8,192.168.0.0./16,localhost,127.0.0.0/8,134.134.0.0/16"
SYSTEM_PACKAGES_FILE = "system_packages.yaml"
PYTHON_PACKAGES_FILE = "python_packages.yaml"
PKG_INSTALL_WAIT_TIME = 25
TEST_SLEEP_TIME_BW_ITERATIONS = 15
BUILD_TYPE = "release"
BUILD_PREFIX = FRAMEWORK_HOME_DIR + "/gramine_install/usr"

# Commands constants
GRAMINE_CLONE_CMD = "git clone https://github.com/gramineproject/gramine.git"

GRAMINE_1_4_CLONE = "RUN git clone --depth 1 --branch v1.4 https://github.com/gramineproject/gramine.git"
DEPTH_STR = "--depth 1 --branch v1.4 "

EXAMPLES_REPO_CLONE_CMD = "git clone https://github.com/gramineproject/examples.git"

MIMALLOC_CLONE_CMD = "git clone -b v1.7.6 https://github.com/microsoft/mimalloc.git"

REDIS_DOWNLOAD_CMD = "wget https://github.com/antirez/redis/archive/6.0.5.tar.gz"

MEMCACHED_DOWNLOAD_CMD = "wget https://memcached.org/files/memcached-1.5.21.tar.gz"

MIMALLOC_INSTALL_PATH = "/usr/local/lib/libmimalloc.so.1.7"

TCMALLOC_INSTALL_PATH = "/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4"

BUILD_TYPE_PREFIX_STRING = "--prefix=" + BUILD_PREFIX + " --buildtype=" + BUILD_TYPE

GRAMINE_SGX_SED_CMD = "sed -i \"/uname/ a '/usr/src/linux-headers-@0@/arch/x86/include/uapi'.format(run_command('uname', '-r').stdout().split('-generic')[0].strip()),\" meson.build"

GRAMINE_BUILD_MESON_CMD = "meson setup build/ --werror " + \
                        BUILD_TYPE_PREFIX_STRING + \
                        " -Ddirect=enabled -Dsgx=enabled > " + \
                        LOGS_DIR + "/gramine_build_meson_cmd_output.txt"

GRAMINE_NINJA_BUILD_CMD = "ninja -vC build > " + LOGS_DIR + "/gramine_ninja_build_cmd_output.txt"

GRAMINE_NINJA_INSTALL_CMD = "ninja -vC build install > " + LOGS_DIR + "/gramine_ninja_install_cmd_output.txt"

PYTHONPATH_CMD = "gramine/scripts/get-python-platlib.py " + BUILD_PREFIX

GRAMINE_SGX_GEN_PRIVATE_KEY_CMD = "gramine-sgx-gen-private-key -f"

APT_UPDATE_CMD = "sudo apt-get update"

APT_FIX_BROKEN_CMD = "sudo apt --fix-broken install -y"

SYS_PACKAGES_CMD = "sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y "

# -U option is to install the latest package (if upgrade is available).
PYTHON_PACKAGES_CMD = "python3 -m pip install -U "

PIP_UPGRADE_CMD = "python3 -m pip install --upgrade pip"

TENSORFLOW_INSTALL_CMD = "python3 -m pip install intel-tensorflow-avx512==2.4.0 --no-cache-dir"

TF_BERT_INTEL_AI_MODELS_CLONE_CMD = "git clone https://github.com/IntelAI/models.git"

TF_BERT_DATASET_WGET_CMD = "wget https://storage.googleapis.com/bert_models/2019_05_30/wwm_uncased_L-24_H-1024_A-16.zip -P data/"
TF_BERT_DATASET_UNZIP_CMD = "unzip data/wwm_uncased_L-24_H-1024_A-16.zip -d data"
TF_BERT_SQUAAD_DATASET_WGET_CMD = "wget https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json -P data/wwm_uncased_L-24_H-1024_A-16"

TF_BERT_CHECKPOINTS_WGET_CMD = "wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/bert_large_checkpoints.zip -P data/"
TF_BERT_CHECKPOINTS_UNZIP_CMD = "unzip data/bert_large_checkpoints.zip -d data"
TF_BERT_FP32_MODEL_WGET_CMD = "wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v2_4_0/fp32_bert_squad.pb -P data/"

TF_RESNET_INTEL_AI_MODELS_CLONE_CMD = "git clone https://github.com/IntelAI/models.git"
TF_RESNET_INT8_MODEL_WGET_CMD = "wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/resnet50v1_5_int8_pretrained_model.pb"

TF_BERT_FP32_MODEL_NAME = os.path.basename(TF_BERT_FP32_MODEL_WGET_CMD.split()[1])
TF_RESNET_INT8_MODEL_NAME = os.path.basename(TF_RESNET_INT8_MODEL_WGET_CMD.split()[1])

SKL_REPO_CLONE_CMD = "git clone https://github.com/IntelPython/scikit-learn_bench.git ."

LOG_LEVEL = "error"

REPO_PATH             = os.path.join(os.getcwd(), "contrib_repo")
ORIG_CURATED_PATH     = os.path.join(os.getcwd(), "orig_contrib_repo")
CONTRIB_GIT_CMD       = "git clone -b master https://github.com/gramineproject/contrib.git orig_contrib_repo"
CURATED_PATH          = "Intel-Confidential-Compute-for-X"
CURATED_APPS_PATH     = os.path.join(REPO_PATH, CURATED_PATH)
VERIFIER_TEMPLATE      = "verifier.dockerfile.template"
ORIG_BASE_PATH         = os.path.join(ORIG_CURATED_PATH, CURATED_PATH)
VERIFIER_DOCKERFILE    = os.path.join(ORIG_BASE_PATH, "verifier", VERIFIER_TEMPLATE)

WORKLOADS_PATH         = os.path.join(CURATED_APPS_PATH, "workloads")
TFSERVING_HELPER_PATH    = os.path.join(WORKLOADS_PATH, "tensorflow-serving", "base_image_helper")
TFSERVING_HELPER_CMD     = f"bash {TFSERVING_HELPER_PATH}/helper.sh"
TFSERVING_CLONE_CMD      = "git clone https://github.com/tensorflow/serving.git"
TFSERVING_RESNET_SED_CMD = "sed -i 's/MODEL_ACCEPT_JPG = False/MODEL_ACCEPT_JPG = True/g' serving/tensorflow_serving/example/resnet_client.py"
TFSERVING_RESNET_PERF_CMD = "python3 serving/tensorflow_serving/example/resnet_client.py"

CURATION_SCRIPT        = os.path.join(ORIG_BASE_PATH, "util", "curation_script.sh")
MYSQL_TESTDB_PATH      = os.path.join(CURATED_APPS_PATH, "workloads/mysql/test_db")
MYSQL_INIT_FOLDER_PATH = os.path.join(MYSQL_TESTDB_PATH, "mysql")
MYSQL_CREATE_TESTDB_CMD = f"mkdir -p {MYSQL_TESTDB_PATH}"
MYSQL_INIT_DB_CMD      = f"docker run --rm --net=host --name init_test_db --user $(id -u):$(id -g) \
                            -v $PWD/workloads/mysql/test_db:/test_db \
                            -e MYSQL_ALLOW_EMPTY_PASSWORD=true -e MYSQL_DATABASE=test_db mysql:8.0.32-debian \
                            --datadir /test_db"
STOP_TEST_DB_CMD      = f"docker stop init_test_db"
MYSQL_TEST_ENCRYPTION_KEY    = f"dd if=/dev/urandom bs=16 count=1 > workloads/mysql/base_image_helper/encryption_key"
CLEANUP_ENCRYPTED_DB   = f"sudo rm -rf /var/run/test_db_encrypted"
MYSQL_ENCRYPT_DB_CMD         = f"sudo gramine-sgx-pf-crypt encrypt -w workloads/mysql/base_image_helper/encryption_key \
                            -i workloads/mysql/test_db -o /var/run/test_db_encrypted"
MYSQL_CLIENT_INSTALL_CMD = f"sudo apt-get -y install mysql-client"
MYSQL_CLIENT_CMD       = f"printf 'SELECT User FROM mysql.user;\nexit' > input.txt | mysql -h 127.0.0.1 -uroot < input.txt"

MARIADB_TESTDB_PATH      = os.path.join(CURATED_APPS_PATH, "workloads/mariadb/test_db")
MARIADB_INIT_FOLDER_PATH = os.path.join(MARIADB_TESTDB_PATH, "mariadb")
MARIADB_CREATE_TESTDB_CMD = f"mkdir -p {MARIADB_TESTDB_PATH}"
MARIADB_INIT_DB_CMD      = f"docker run --rm --net=host --name init_test_db \
                            -v $PWD/workloads/mariadb/test_db:/test_db \
                            -e MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=true -e MARIADB_DATABASE=test_db mariadb:10.7 \
                            --datadir /test_db "
MARIADB_TEST_ENCRYPTION_KEY    = f"dd if=/dev/urandom bs=16 count=1 > workloads/mariadb/base_image_helper/encryption_key"
MARIADB_ENCRYPT_DB_CMD   = f"sudo gramine-sgx-pf-crypt encrypt -w workloads/mariadb/base_image_helper/encryption_key \
                            -i workloads/mariadb/test_db -o /var/run/test_db_encrypted"
MARIADB_CHMOD         = f"sudo chown -R $USER:$USER $PWD/workloads/mariadb/test_db"
MYSQL_TESTDB_VERIFY   = f"/usr/sbin/mysqld: ready for connections"
MARIADB_TESTDB_VERIFY = f"mariadbd: ready for connections"