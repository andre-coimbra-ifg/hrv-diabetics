import os
import logging


def list_rr_files(directory):
    """Lista todos os arquivos RR em um diretório."""
    files = [
        os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".txt")
    ]
    logging.info(f"{len(files)} arquivo(s) encontrado(s) em {directory}")
    return files
