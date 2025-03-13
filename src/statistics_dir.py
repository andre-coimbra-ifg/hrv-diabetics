from tabulate import tabulate
import os
import numpy as np
import logging
from config import QUALITY_THRESHOLD
from processing import evaluate_signal_quality
from utils import list_rr_files
from file_io import load_rr_intervals


def evaluate_directory_statistics(directory):
    """
    Avalia estatísticas gerais dos arquivos de um diretório.

    Args:
        directory (str): Caminho do diretório a ser avaliado.

    Returns:
        dict: Estatísticas sobre o diretório.
    """
    files_stats = {}  # Alterado para usar o nome do arquivo como chave
    num_files = 0

    # Percorre os arquivos do diretório
    for file in list_rr_files(directory):
        num_files += 1

        # Lê os valores dos intervalos RR
        rr_intervals = load_rr_intervals(file)
        duration = np.sum(rr_intervals)  # Soma total em segundos
        quality = evaluate_signal_quality(rr_intervals)

        # Armazenando as informações dentro de files_stats usando o nome do arquivo como chave
        files_stats[file] = {"duration": duration, "quality": quality}

    if num_files == 0:
        logging.warning(f"Nenhum arquivo encontrado em {directory}")
        return None

    # Estatísticas básicas
    durations = [stats["duration"] for stats in files_stats.values()]
    max_duration = np.max(durations)
    min_duration = np.min(durations)
    mean_duration = np.mean(durations)

    qualities = [stats["quality"] for stats in files_stats.values()]
    mean_quality = np.mean(qualities)
    below_threshold = sum(q < QUALITY_THRESHOLD for q in qualities)
    above_threshold = len(qualities) - below_threshold

    stats = {
        "Directory": directory,
        "Number of Files": num_files,
        "Max Duration (min)": round(max_duration / 60, 2),
        "File Max Duration": os.path.basename(
            max(files_stats, key=lambda x: files_stats[x]["duration"])
        ),
        "Min Duration (min)": round(min_duration / 60, 2),
        "File Min Duration": os.path.basename(
            min(files_stats, key=lambda x: files_stats[x]["duration"])
        ),
        "Mean Duration (min)": round(mean_duration / 60, 2),
        "Quality Threshold (%)": round(QUALITY_THRESHOLD * 100, 1),
        "Mean Quality (%)": round(mean_quality * 100, 2),
        "Files Below Threshold": below_threshold,
        "Files Above Threshold": above_threshold,
    }

    return stats


def generate_statistics_report(control_dir, test_dir, output_file):
    """
    Gera um relatório consolidado das estatísticas dos diretórios.

    Args:
        control_dir (str): Caminho para o diretório de controle.
        test_dir (str): Caminho para o diretório de teste.
        output_file (str): Arquivo para salvar o relatório.
    """
    control_stats = evaluate_directory_statistics(control_dir)
    test_stats = evaluate_directory_statistics(test_dir)

    if control_stats is None and test_stats is None:
        logging.warning("Nenhuma estatística foi gerada — arquivos ausentes.")
        return

    report = {"Control": control_stats, "Test": test_stats}

    # Exibe a tabela no console
    print(f"\n{'='*30} INFORMAÇÕES BÁSICAS {'='*30}")

    # Obter todas as métricas
    metrics = list(report["Control"].keys())

    # Criar uma tabela reorganizada
    table = [
        [metric, report["Control"][metric], report["Test"][metric]]
        for metric in metrics
    ]

    # Exibir a tabela formatada
    table_string = tabulate(
        table,
        headers=["Info", "Control Group", "Test Group"],
        tablefmt="grid",
        colalign=("left", "center", "center"),
    )

    print(table_string)

    # Salva em arquivo
    with open(output_file, "w") as f:
        f.write(f"{'='*29} INFORMAÇÕES BÁSICAS {'='*29}\n\n")
        f.write(table_string)

    logging.info(f"Relatório salvo em: {output_file}")


def list_files_by_duration(directory):
    """
    Lista os arquivos de RRi ordenados pela duração em ordem crescente.

    Args:
        directory (str): Caminho para o diretório contendo os arquivos de RRi.

    Returns:
        list: Lista de tuplas (nome_arquivo, duração_em_minutos), ordenada por duração.
    """
    files = list_rr_files(directory)
    if not files:
        logging.warning(f"Nenhum arquivo encontrado em {directory}")
        return []

    file_durations = []

    for file in files:
        try:
            rr_intervals = load_rr_intervals(file)  # Carrega os intervalos RR
            duration = np.sum(rr_intervals) / 60  # Converte para minutos
            file_durations.append((os.path.basename(file), round(duration, 2)))
        except Exception as e:
            logging.error(f"Erro ao processar {file}: {e}")

    # Ordena pela duração (em minutos) em ordem crescente
    file_durations.sort(key=lambda x: x[1])

    return file_durations


def generate_duration_file_report(control_dir, test_dir, output_file):
    """
    Gera um relatório detalhado com todos os arquivos e seus tempos em minutos,
    separados por grupos (controle e teste), organizados em ordem crescente.

    Args:
        control_dir (str): Caminho para o diretório de controle.
        test_dir (str): Caminho para o diretório de teste.
        output_file (str): Arquivo para salvar o relatório.
    """

    control_files = list_files_by_duration(control_dir)
    test_files = list_files_by_duration(test_dir)

    # Gerar tabela formatada
    table = []
    table.append(["Grupo", "Nome do Arquivo", "Duração (min)"])

    for file, duration in control_files:
        table.append(["Controle", file, duration])

    for file, duration in test_files:
        table.append(["Diabéticos", file, duration])

    table_string = tabulate(
        table, headers="firstrow", tablefmt="grid", colalign=("left", "left", "center")
    )

    # Exibir no console
    print(f"\n{'='*30} DURATION FILE REPORT {'='*30}")
    print(table_string)

    # Salvar em arquivo
    with open(output_file, "w") as f:
        f.write(f"{'='*29} DURATION FILE REPORT {'='*29}\n\n")
        f.write(table_string)

    logging.info(f"Relatório de duração salvo em: {output_file}")
