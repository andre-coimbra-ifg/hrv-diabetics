import os
import logging
import numpy as np
from file_io import load_rr_intervals, save_rr_intervals
from processing import (
    denoise_rr_intervals,
    evaluate_signal_quality,
    truncate_rr_intervals,
)
from utils import list_rr_files, get_output_path
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
    min_length = float("inf")
    min_file = None

    for dir in [control_dir, test_dir]:
        files.extend(list_rr_files(dir))

    if not files:
        logging.warning(
            f"Nenhum arquivo encontrado nos diretórios '{control_dir}' e '{test_dir}'"
        )
        return

    for file in files:
        print(file)

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

                length = np.sum(rr_cleaned)
                if length < min_length:
                    min_length = length
                    min_file = file

                output_file = get_output_path(
                    file, OUTPUT_DIR, control_dir, test_dir, "_denoised.txt"
                )
                save_rr_intervals(output_file, rr_cleaned)

    for file in files:

        denoised_file = get_output_path(
            file, OUTPUT_DIR, control_dir, test_dir, "_denoised.txt"
        )

        rr_intervals = load_rr_intervals(denoised_file)
        rr_truncated = truncate_rr_intervals(rr_intervals, min_length)

        min_length_minute = (min_length / 60).round(1)
        logging.info(
            f"Shortest file is '{min_file}' with length of {min_length_minute} minutes"
        )
        dir = control_dir if control_dir in file else test_dir
        output_file = get_output_path(
            file,
            OUTPUT_DIR,
            control_dir,
            test_dir,
            f"_trunc_{min_length_minute}min.txt",
        )
        save_rr_intervals(output_file, rr_truncated)


# logging.info(f"Processamento concluído para o grupo: {group_name}")


def main():
    setup_logging()
    logging.info("Iniciando o processamento dos dados...")

    process_data(CONTROL_DIR, TEST_DIR, POLICY)

    logging.info("Processamento de todos os grupos concluído")


if __name__ == "__main__":
    main()
