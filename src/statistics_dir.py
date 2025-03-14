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
        "Diretório": directory,
        "Número de Arquivos": num_files,
        "Maior Duração (min)": round(max_duration / 60, 2),
        "Arquivo com Maior Duração": os.path.basename(
            max(files_stats, key=lambda x: files_stats[x]["duration"])
        ),
        "Menor Duração (min)": round(min_duration / 60, 2),
        "Arquivo com Menor Duração": os.path.basename(
            min(files_stats, key=lambda x: files_stats[x]["duration"])
        ),
        "Duração Média (min)": round(mean_duration / 60, 2),
        "Limite de Qualidade (%)": round(QUALITY_THRESHOLD * 100, 1),
        "Qualidade Média (%)": round(mean_quality * 100, 2),
        "Arquivos Abaixo do Limite": below_threshold,
        "Arquivos Acima do Limite": above_threshold,
    }

    return stats


def generate_section_lines(group_name, metrics, report):
    """
    Gera as linhas formatadas para uma seção de um grupo (Control ou Test).

    Args:
        group_name (str): Nome do grupo (Control ou Test).
        metrics (list): Lista das métricas a serem exibidas.
        report (dict): Dicionário com as estatísticas para cada grupo.

    Returns:
        str: Linhas formatadas para a seção.
    """
    lines = [f"{'-'*10} GRUPO: {group_name.upper()} {'-'*10}"]
    lines.extend([f"{metric}: {report[group_name][metric]}" for metric in metrics])
    return "\n".join(lines)


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

    report = {"Controle": control_stats, "Teste": test_stats}

    metrics = list(report["Controle"].keys())

    # Gerar a seção do Grupo de Controle
    control_section = generate_section_lines("Controle", metrics, report)

    # Gerar a seção do Grupo de Teste
    test_section = generate_section_lines("Teste", metrics, report)

    # Exibir no console
    print(f"\n{'='*15} INFORMAÇÕES BÁSICAS SOBRE OS GRUPOS {'='*15}")
    print(control_section)
    print(test_section)

    # Salvar em arquivo
    with open(output_file, "w") as f:
        f.write(f"{'='*15} INFORMAÇÕES BÁSICAS SOBRE OS GRUPOS {'='*15}\n\n")
        f.write(control_section + "\n\n")
        f.write(test_section + "\n")

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

    # Gerar linhas formatadas para o relatório
    # Cabeçalho do relatório
    lines = [
        f"{'='*10} RELATÓRIO DE DURAÇÃO DOS ARQUIVOS {'='*10}\n",
        "-> Os arquivos estão organizados em ordem crescente de duração.\n",
        "Formato: X.Nome do Arquivo | Duração (min)",
    ]

    # Função para formatar as linhas dos arquivos com contagem regressiva
    def format_group_lines(group_name, files):
        lines.append(f"\n\nGRUPO: {group_name.upper()}:")
        total_files = len(files)
        for i, (file, duration) in zip(range(total_files, 0, -1), files):
            lines.append(f"   {i}. {file} | {duration}")

    # Adicionar os arquivos dos grupos "Controle" e "Diabéticos"
    format_group_lines("Controle", control_files)
    format_group_lines("Diabéticos", test_files)

    # Exibir no console
    print("\n".join(lines))

    # Salvar em arquivo
    with open(output_file, "w") as f:
        f.write("\n".join(lines))
    logging.info(f"Relatório de duração salvo em: {output_file}")
