import os

CONTROL_DIR = "../data/control"
TEST_DIR = "../data/diabetic"

POLICY = "early"  # "early", "late", "best"

CLIP_START_LENGHT = 10  # Amount of entries (RR) to clip from the start of the data

QUALITY_THRESHOLD = 0.9  # Threshold for quality of the data

# THRESHOLDS IN MILLISECONDS
LOW_RRI = 300
HIGH_RRI = 2000

# Diretório base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretórios de saída
OUTPUT_DIR = os.path.join(BASE_DIR, "../data/output")
DENOISED_OUTPUT_DIR = os.path.join(BASE_DIR, "../data/output/denoised")
TRUNCATED_OUTPUT_DIR = os.path.join(BASE_DIR, "../data/output/truncated")

# Parâmetros para processamento
OUTLIER_THRESHOLD = 3
MEDIAN_FILTER_KERNEL_SIZE = 5

# Configurações de logging
LOG_FILE = os.path.join(BASE_DIR, "../data/logs/rr_processing.log")
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

control_basename = os.path.basename(CONTROL_DIR)
test_basename = os.path.basename(TEST_DIR)

# Criação de diretórios se não existirem
os.makedirs(OUTPUT_DIR, exist_ok=True)
for directory in [DENOISED_OUTPUT_DIR, TRUNCATED_OUTPUT_DIR]:
    os.makedirs(os.path.join(directory, control_basename), exist_ok=True)
    os.makedirs(os.path.join(directory, test_basename), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
