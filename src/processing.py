# Copyright (C) [2025] [Aura Healthcare]
# Modificado por [André Coimbra] em [2025]
#
# https://pypi.org/project/hrv-analysis/
#
# Este programa é software livre; você pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral GNU conforme publicada pela Free Software Foundation,
# na versão 3 da licença ou (a seu critério) qualquer versão posterior.
#
# Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA;
# sem mesmo a garantia implícita de COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO FIM.
# Consulte a Licença Pública Geral GNU para mais detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU junto com este programa;
# se não, consulte <https://www.gnu.org/licenses/>.


import logging
import numpy as np

# from scipy.signal import medfilt
from config import (
    OUTLIER_THRESHOLD,
    MEDIAN_FILTER_KERNEL_SIZE,
    LOW_RRI,
    HIGH_RRI,
    POLICY,
)


# Função para detectar batimentos ectópicos
def detect_ectopic_beats(rr_intervals, threshold=1.2):
    rr_intervals = np.array(rr_intervals)
    rr_ratio = rr_intervals[1:] / rr_intervals[:-1]
    ectopic_beats = (
        np.abs(rr_ratio - 1) > threshold
    )  # Batimentos com variação > threshold
    # Adiciona 'False' no final para igualar o tamanho
    ectopic_beats = np.concatenate(([False], ectopic_beats))  # Adiciona False no início
    return ectopic_beats


# Função para detectar outliers usando IQR (Interquartile Range)
def detect_outliers(rr_intervals):
    rr_intervals = np.array(rr_intervals)
    Q1 = np.percentile(rr_intervals, 25)
    Q3 = np.percentile(rr_intervals, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = (rr_intervals < lower_bound) | (rr_intervals > upper_bound)
    return outliers


# Função para avaliar a qualidade do sinal
def evaluate_signal_quality(rr_intervals):
    logging.debug(f"Avaliando a qualidade do sinal")

    ectopic_beats = detect_ectopic_beats(rr_intervals)
    outliers = detect_outliers(rr_intervals)

    # O número de batimentos é 1 a mais do que o número de intervalos RR
    total_beats = len(rr_intervals) + 1
    # Máscara booleana que seleciona apenas os batimentos válidos
    valid_beats = np.sum(~ectopic_beats & ~outliers)
    valid_percentage = valid_beats / total_beats

    ectopic_percentage = np.sum(ectopic_beats) / total_beats
    outlier_percentage = np.sum(outliers) / total_beats

    logging.debug(f"Percentual de batimentos válidos: {valid_percentage*100:.2f}%")
    logging.debug(f"Percentual de batimentos ectópicos: {ectopic_percentage*100:.2f}%")
    logging.debug(f"Percentual de outliers: {outlier_percentage*100:.2f}%")

    return valid_percentage


def remove_outliers(rr_intervals, low_rri=LOW_RRI, high_rri=HIGH_RRI):
    """
    Function that replace RR-interval outlier by nan.

    Parameters
    ---------
    rr_intervals : list
        raw signal extracted.
    low_rri : int
        lowest RrInterval to be considered plausible.
    high_rri : int
        highest RrInterval to be considered plausible.
    verbose : bool
        Print information about deleted outliers.

    Returns
    ---------
    rr_intervals_cleaned : list
        list of RR-intervals without outliers

    References
    ----------
    .. [1] O. Inbar, A. Oten, M. Scheinowitz, A. Rotstein, R. Dlin, R.Casaburi. Normal \
    cardiopulmonary responses during incremental exercise in 20-70-yr-old men.

    .. [2] W. C. Miller, J. P. Wallace, K. E. Eggert. Predicting max HR and the HR-VO2 relationship\
    for exercise prescription in obesity.

    .. [3] H. Tanaka, K. D. Monahan, D. R. Seals. Age-predictedmaximal heart rate revisited.

    .. [4] M. Gulati, L. J. Shaw, R. A. Thisted, H. R. Black, C. N. B.Merz, M. F. Arnsdorf. Heart \
    rate response to exercise stress testing in asymptomatic women.
    """

    # Conversion RrInterval to Heart rate ==> rri (ms) =  1000 / (bpm / 60)
    # rri 2000 => bpm 30 / rri 300 => bpm 200
    rr_intervals_cleaned = [
        rri if high_rri >= rri >= low_rri else np.nan for rri in rr_intervals
    ]

    outliers_list = []
    for rri in rr_intervals:
        if high_rri >= rri >= low_rri:
            pass
        else:
            outliers_list.append(rri)

    nan_count = sum(np.isnan(rr_intervals_cleaned))
    logging.info(f"{nan_count} outlier(s) have been deleted.")
    if nan_count:
        logging.debug(f"The outlier(s) value(s) are : {outliers_list}")

    return rr_intervals_cleaned

    # def apply_median_filter(rr_intervals, kernel_size=MEDIAN_FILTER_KERNEL_SIZE):
    """Aplica filtro da mediana para suavizar os dados."""
    # smoothed = medfilt(rr_intervals, kernel_size=kernel_size)
    # logging.debug(f"Filtro de mediana aplicado (kernel size={kernel_size})")
    # return smoothed


def remove_ectopic_beats(rr_intervals=[], removing_rule=0.2):
    """
    RR-intervals differing by more than the removing_rule from the one proceeding it are removed.

    Parameters
    ---------
    rr_intervals : list
        list of RR-intervals
    removing_rule : int
        Percentage criteria of difference with previous RR-interval at which we consider
        that it is abnormal. 
    
    Returns
    ---------
    nn_intervals : list
        list of NN Interval

    References
    ----------
    .. [5] Kamath M.V., Fallen E.L.: Correction of the Heart Rate Variability Signal for Ectopics \
    and Miss- ing Beats, In: Malik M., Camm A.J.

    .. [6] Geometric Methods for Heart Rate Variability Assessment - Malik M et al
    """
    # set first element in list
    outlier_count = 0
    previous_outlier = False
    nn_intervals = [rr_intervals[0]]
    for i, rr_interval in enumerate(rr_intervals[:-1]):

        if previous_outlier:
            nn_intervals.append(rr_intervals[i + 1])
            previous_outlier = False
            continue

        if abs(rr_interval - rr_intervals[i + 1]) <= removing_rule * rr_interval:
            nn_intervals.append(rr_intervals[i + 1])
        else:
            nn_intervals.append(np.nan)
            outlier_count += 1
            previous_outlier = True

    logging.info("{} ectopic beat(s) have been deleted.".format(outlier_count))

    return nn_intervals


def interpolate_nan_values(
    rr_intervals=[],
    interpolation_method="linear",
    limit_area=None,
    limit_direction="forward",
    limit=None,
):
    """
    Function that interpolate Nan values with linear interpolation

    Parameters
    ---------
    rr_intervals : list
        RrIntervals list.
    interpolation_method : str
        Method used to interpolate Nan values of series.
    limit_area: str
        If limit is specified, consecutive NaNs will be filled with this restriction.
    limit_direction: str
        If limit is specified, consecutive NaNs will be filled in this direction.
    limit: int
        Maximum number of NaNs to fill consecutively.
    ---------
    interpolated_rr_intervals : list
        new list with outliers replaced by interpolated values.
    """
    rr_intervals = np.array(rr_intervals)

    # Handle the first NaNs (fill with the next value)
    if np.isnan(rr_intervals[0]):
        start_idx = 0
        while np.isnan(rr_intervals[start_idx]):
            start_idx += 1
        rr_intervals[0:start_idx] = rr_intervals[start_idx]

    # Interpolate NaN values (linear interpolation by default)
    for i in range(1, len(rr_intervals) - 1):
        if np.isnan(rr_intervals[i]):
            if interpolation_method == "linear":
                # Linear interpolation: find previous and next non-NaN values
                prev_value = rr_intervals[i - 1]
                next_value = rr_intervals[i + 1]
                rr_intervals[i] = (prev_value + next_value) / 2
            elif interpolation_method == "zero":
                rr_intervals[i] = rr_intervals[
                    i - 1
                ]  # Zero interpolation (forward fill)
            # Add more methods here if needed

    # Apply limit if specified
    if limit is not None:
        nan_count = 0
        for i in range(len(rr_intervals)):
            if np.isnan(rr_intervals[i]):
                nan_count += 1
                if nan_count > limit:
                    break
            else:
                nan_count = 0

    return rr_intervals.tolist()


def denoise_rr_intervals(rr_intervals, low_rri=LOW_RRI, high_rri=HIGH_RRI):
    """Pipeline de denoise."""
    logging.debug("Iniciando denoise do sinal")
    rr_intervals = rr_intervals * 1000  # Convertendo para milissegundos
    rr_intervals_without_outliers = remove_outliers(rr_intervals, low_rri, high_rri)
    interpolated_rr_intervals = interpolate_nan_values(rr_intervals_without_outliers)
    rr_intervals_without_ectopic = remove_ectopic_beats(interpolated_rr_intervals)
    rr_cleaned = interpolate_nan_values(rr_intervals_without_ectopic)
    rr_final = np.array(rr_cleaned) / 1000
    logging.debug("Denoise concluído")
    return rr_final


def truncate_rr_intervals(rr_intervals, target_duration, policy=POLICY):
    """
    Corta os intervalos RR para garantir que todos tenham a mesma duração.
    """
    logging.debug("Iniciando truncamento do sinal")

    accumulated_time = 0.0
    truncated_rr = []

    for rr in rr_intervals:
        if accumulated_time + rr > target_duration:
            break
        truncated_rr.append(rr)
        accumulated_time += rr

    logging.debug(
        f"Tamanho inicial: {len(rr_intervals)}, tamanho após truncamento: {len(truncated_rr)}"
    )
    logging.debug(
        f"Tempo acumulado após truncamento: {accumulated_time:.2f} s (limite: {target_duration:.2f} s)"
    )

    return np.array(truncated_rr)
