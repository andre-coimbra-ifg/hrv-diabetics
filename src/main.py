import os
import logging
from file_io import load_rr_intervals, save_rr_intervals
from processing import denoise_rr_intervals, evaluate_signal_quality
from utils import list_rr_files
from config import (
    OUTPUT_DIR,
    CONTROL_DIR,
    TEST_DIR,
    POLICY,
    LOW_RRI,
    HIGH_RRI,
    CLIP_START_LENGHT,
    QUALITY_THRESHOLD,
)
from logging_config import setup_logging


def process_data(control_dir, test_dir, policy="early_valid"):

    logging.debug(
        f"Iniciando o processamento dos diretórios: '{control_dir}' e '{test_dir}'"
    )

    files = []

    for dir in [control_dir, test_dir]:
        files.extend(list_rr_files(dir))

    if not files:
        logging.warning(
            f"Nenhum arquivo encontrado nos diretórios '{control_dir}' e '{test_dir}'"
        )
        return

    for file in files:
        rr_intervals = load_rr_intervals(file)

        if rr_intervals is not None:
            logging.info(f"Removendo os {CLIP_START_LENGHT} primeiros RRis do arquivo")
            rr_intervals = rr_intervals[CLIP_START_LENGHT:]
            if evaluate_signal_quality(rr_intervals) < QUALITY_THRESHOLD:
                files.remove(file)
                continue
            else:
                rr_cleaned = denoise_rr_intervals(rr_intervals, LOW_RRI, HIGH_RRI)
                # output_file = os.path.join(output_dir, os.path.basename(file))
                # save_rr_intervals(output_file, rr_cleaned)

    # logging.info(f"Processamento concluído para o grupo: {group_name}")


def main():
    setup_logging()
    logging.info("Iniciando o processamento dos dados...")

    process_data(CONTROL_DIR, TEST_DIR, POLICY)

    logging.info("Processamento de todos os grupos concluído")


if __name__ == "__main__":
    main()
