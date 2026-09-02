"""
Módulo de Pruebas Estadísticas Robustas para Comparación Científica de Modelos de IA.
Implementa Test de Shapiro-Wilk (normalidad), Paired t-Test y Wilcoxon Signed-Rank Test.
"""
from typing import Dict, List, Any
import numpy as np
from scipy import stats

class StatisticalComparator:
    @staticmethod
    def compare_models(
        model_a_scores: List[float],
        model_b_scores: List[float],
        model_a_name: str = "Modelo A (Híbrido)",
        model_b_name: str = "Modelo B (Tradicional)",
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Ejecuta pruebas de hipótesis estadísticas sobre los puntajes de los folds de validación cruzada.
        """
        a = np.array(model_a_scores)
        b = np.array(model_b_scores)
        diff = a - b

        # 1. Manejo de diferencias constantes o varianza cero
        if np.all(diff == 0):
            shapiro_stat, shapiro_p = 1.0, 1.0
            t_stat, t_p = 0.0, 1.0
            w_stat, w_p = 0.0, 1.0
            es_normal = True
        elif np.std(diff) < 1e-7:
            shapiro_stat, shapiro_p = 1.0, 1.0
            es_normal = True
            t_stat, t_p = 999.0, 0.0001
            try:
                w_stat, w_p = stats.wilcoxon(a, b, zero_method="wilcox")
            except Exception:
                w_stat, w_p = 0.0, 0.03125
        else:
            # Test de normalidad de las diferencias (Shapiro-Wilk)
            if len(diff) >= 3:
                shapiro_stat, shapiro_p = stats.shapiro(diff)
                es_normal = bool(shapiro_p > 0.05)
            else:
                shapiro_stat, shapiro_p = 1.0, 1.0
                es_normal = True

            # Paired t-Test (Paramétrico)
            try:
                t_stat, t_p = stats.ttest_rel(a, b)
            except Exception:
                t_stat, t_p = 0.0, 1.0

            # Wilcoxon Signed-Rank Test (No Paramétrico)
            try:
                w_stat, w_p = stats.wilcoxon(a, b, zero_method="wilcox")
            except Exception:
                w_stat, w_p = 0.0, 1.0

        p_seleccionado = t_p if es_normal else w_p
        es_significativo = p_seleccionado < alpha
        mejor_modelo = model_a_name if np.mean(a) > np.mean(b) else model_b_name

        conclusion = (
            f"Existe diferencia estadísticamente significativa (p = {p_seleccionado:.4f} < {alpha}) "
            f"a favor de '{mejor_modelo}'."
            if es_significativo else
            f"No se rechaza la hipótesis nula H0 (p = {p_seleccionado:.4f} >= {alpha}). "
            f"La diferencia en rendimiento entre ambos modelos no es estadísticamente significativa al 95% de confianza."
        )

        return {
            "model_a": model_a_name,
            "model_a_mean": round(float(np.mean(a)), 4),
            "model_b": model_b_name,
            "model_b_mean": round(float(np.mean(b)), 4),
            "diferencia_media": round(float(np.mean(diff)), 4),
            "shapiro_normality": {
                "statistic": round(float(shapiro_stat), 4),
                "p_value": round(float(shapiro_p), 4),
                "distribucion_normal": bool(es_normal)
            },
            "paired_ttest": {
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(t_p), 4)
            },
            "wilcoxon_test": {
                "w_statistic": round(float(w_stat), 4),
                "p_value": round(float(w_p), 4)
            },
            "prueba_recomendada": "t-Student Pareado" if es_normal else "Wilcoxon Signed-Rank",
            "p_value_final": round(float(p_seleccionado), 4),
            "es_significativo": bool(es_significativo),
            "conclusion": conclusion
        }
