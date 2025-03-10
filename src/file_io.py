import numpy as np
import logging


def load_rr_intervals(file_path):
    """Carrega os intervalos RR de um arquivo."""
    try:
        logging.debug(f"Carregando arquivo: {file_path}")
        data = np.loadtxt(file_path, dtype=float, delimiter=" ", encoding="ISO-8859-1")
        logging.debug(f"Arquivo carregado com sucesso: {file_path}")

        # Se os dados tiverem apenas uma coluna, retorna diretamente
        if data.ndim == 1:  # Caso em que há apenas uma coluna
            logging.debug(f"Arquivo possui apenas uma coluna.")
            return data

        else:
            # Se houver duas colunas, retorna apenas a segunda (intervalos RR)
            logging.debug(f"Arquivo possui duas colunas.")
            return data[:, 1]  # Retorna a segunda coluna (intervalos RR)

    except Exception as e:
        logging.error(f"Erro ao carregar arquivo {file_path}: {e}")
        return None


def save_rr_intervals(file_path, data):
    """Salva os intervalos RR processados em um arquivo."""
    try:
        logging.debug(f"Salvando arquivo: {file_path}")
        np.savetxt(file_path, data, fmt="%.6f")
        logging.debug(f"Arquivo salvo com sucesso: {file_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar arquivo {file_path}: {e}")
