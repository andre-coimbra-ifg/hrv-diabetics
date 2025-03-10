# Copyright (C) [2025] [Aura Healthcare]
# Modificado por [André Coimbra] em [2025]
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
from scipy.signal import medfilt
from config import (
    OUTLIER_THRESHOLD,
    MEDIAN_FILTER_KERNEL_SIZE,
    LOW_RRI,
    HIGH_RRI,
    QUALITY_THRESHOLD,
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


# Função para detectar outliers usando IQR
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
def evaluate_signal_quality(rr_intervals, threshold=QUALITY_THRESHOLD):
    logging.debug(f"Avaliando  qualidade do sinal...")

    ectopic_beats = detect_ectopic_beats(rr_intervals)
    outliers = detect_outliers(rr_intervals)

    # O número de batimentos é 1 a mais do que o número de intervalos RR
    total_beats = len(rr_intervals) + 1
    valid_beats = np.sum(~ectopic_beats & ~outliers)
    valid_percentage = valid_beats / total_beats

    ectopic_percentage = np.sum(ectopic_beats) / total_beats
    outlier_percentage = np.sum(outliers) / total_beats

    logging.debug(f"Percentual de batimentos válidos: {valid_percentage*100:.2f}%")
    logging.debug(f"Percentual de batimentos ectópicos: {ectopic_percentage*100:.2f}%")
    logging.debug(f"Percentual de outliers: {outlier_percentage*100:.2f}%")

    if valid_percentage < threshold:
        logging.warning(
            f"Sinal com baixa qualidade ({valid_percentage*100:.2f}%) e foi removido da análise!"
        )
    else:
        logging.info(
            f"Sinal tem boa qualidade ({valid_percentage*100:.2f}%) e foi incluído na análise!"
        )

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


def apply_median_filter(rr_intervals, kernel_size=MEDIAN_FILTER_KERNEL_SIZE):
    """Aplica filtro da mediana para suavizar os dados."""
    smoothed = medfilt(rr_intervals, kernel_size=kernel_size)
    logging.debug(f"Filtro de mediana aplicado (kernel size={kernel_size})")
    return smoothed


def denoise_rr_intervals(rr_intervals, low_rri=LOW_RRI, high_rri=HIGH_RRI):
    """Pipeline de denoise."""
    logging.debug("Iniciando denoise do sinal")
    rr_intervals = rr_intervals * 1000  # Convertendo para milissegundos
    rri_without_outliers = remove_outliers(
        rr_intervals=rr_intervals, low_rri=low_rri, high_rri=high_rri
    )

    logging.debug("Denoise concluído")
    return
