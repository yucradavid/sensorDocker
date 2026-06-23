from __future__ import annotations

from fastapi import FastAPI

from utils_data import get_data_dir, read_csv_logical, classify_iaq, recommend_action

app = FastAPI(
    title="AulaSense UPeU API",
    description="API local para consultar estado predictivo de calidad de aire en aulas UPeU.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "AulaSense UPeU API", "data_dir": str(get_data_dir())}


@app.get("/predicciones/latest")
def latest_predictions():
    acciones = read_csv_logical("acciones_ultima_ventana")
    if acciones.empty:
        return {"status": "sin_datos", "message": "No se encontraron acciones exportadas."}
    return {"status": "ok", "records": acciones.to_dict(orient="records")}


@app.get("/aulas/estado")
def classroom_state():
    serie = read_csv_logical("serie_temporal")
    acciones = read_csv_logical("acciones_ultima_ventana")

    response = {"status": "ok", "aula": "Aula UPeU", "estado_actual": {}, "predicciones": []}

    if not serie.empty:
        last = serie.tail(1).iloc[0]
        iaq = last.get("iaq_promedio", last.get("iaq", None))
        response["aula"] = str(last.get("estacion", "Aula UPeU"))
        response["estado_actual"] = {
            "iaq": None if iaq is None else float(iaq),
            "estado": classify_iaq(iaq),
            "accion": recommend_action(iaq),
            "eco2": None if last.get("eco2_promedio", None) is None else float(last.get("eco2_promedio")),
            "voc": None if last.get("voc_promedio", None) is None else float(last.get("voc_promedio")),
        }

    if not acciones.empty:
        response["predicciones"] = acciones.to_dict(orient="records")

    return response


@app.get("/decision")
def decision():
    acciones = read_csv_logical("acciones_ultima_ventana")
    if acciones.empty:
        return {"status": "sin_datos", "accion": "Sin recomendación"}

    # Priorizar la acción más crítica si existen varias predicciones.
    prioridad = {
        "Alerta + extractor/purificador": 4,
        "Encender purificador/extractor": 3,
        "Ventilación preventiva": 2,
        "Monitoreo normal": 1,
    }

    records = acciones.to_dict(orient="records")
    best = max(records, key=lambda r: prioridad.get(str(r.get("accion_recomendada", "")), 0))
    return {"status": "ok", "decision_principal": best, "predicciones": records}
