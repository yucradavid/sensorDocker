# ============================================================
# EXPORTACIÓN DE RESULTADOS DE UNIDAD 3 PARA AULASENSE UPEU
# Pega/ejecuta esta celda al final del notebook de Unidad 3.
# ============================================================

from pathlib import Path
import shutil
from pyspark.sql import functions as F

EXPORT_DASHBOARD_PATH = "/opt/data/calidad_aire/aulasense_dashboard_export"
Path(EXPORT_DASHBOARD_PATH).mkdir(parents=True, exist_ok=True)

print("Exportando resultados para dashboard AulaSense UPeU...")
print("Ruta:", EXPORT_DASHBOARD_PATH)


def export_csv(df, name):
    path = f"{EXPORT_DASHBOARD_PATH}/{name}"
    if Path(path).exists():
        shutil.rmtree(path, ignore_errors=True)
    df.coalesce(1).write.mode("overwrite").option("header", True).csv(path)
    print("Exportado:", path)

# 1. Serie temporal del aula
# Ajusta el nombre si tu DataFrame se llama distinto.
if "serie_ml" in globals():
    export_csv(serie_ml, "serie_temporal")
elif "serie_temporal" in globals():
    export_csv(serie_temporal, "serie_temporal")
elif "features_ready" in globals():
    export_csv(features_ready, "serie_temporal")
else:
    print("No se encontró serie_ml / serie_temporal / features_ready.")

# 2. Métricas del modelo
if "metrics_df" in globals():
    export_csv(metrics_df, "metricas_modelo")
else:
    print("No se encontró metrics_df.")

# 3. Predicciones batch históricas
if "pred_all" in globals():
    export_csv(pred_all, "predicciones_batch")
else:
    print("No se encontró pred_all.")

# 4. Acciones de última ventana
if "latest_actions" in globals() and latest_actions is not None:
    export_csv(latest_actions, "acciones_ultima_ventana")
elif "resumen_operativo" in globals():
    export_csv(resumen_operativo, "acciones_ultima_ventana")
else:
    print("No se encontró latest_actions / resumen_operativo.")

# 5. Importancia de variables
if "importancia_df" in globals():
    export_csv(importancia_df, "importancia_variables")
else:
    print("No se encontró importancia_df.")

print("Exportación terminada. Usa esta ruta en Streamlit/Grafana:", EXPORT_DASHBOARD_PATH)
