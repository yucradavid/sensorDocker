# Contrato de evento: calidad_aire.actualizada

Topic Kafka: `calidad-aire-eventos`

## Evento ejemplo

```json
{
  "tipoEvento": "calidad_aire.actualizada",
  "idLectura": 1,
  "id_sensor": "sensor-simulado-bme680",
  "estacion": "Grupo 2 - Sensor Simulado",
  "temperatura": 21.4,
  "humedad": 45.8,
  "presion": 1012.3,
  "altura": 3825.0,
  "gas": 48.2,
  "iaq": 86.1,
  "eco2": 554.9,
  "voc": 6.3,
  "calidad_aire": "Excelente",
  "riesgo_aire": "BAJO",
  "origen": "python-sensor-simulator",
  "fechaHora": "2026-05-24T18:30:00",
  "timestamp": 1779647400000
}
```

## Campos

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| tipoEvento | string | Tipo de evento | calidad_aire.actualizada |
| idLectura | integer | Secuencia de lectura | 1 |
| id_sensor | string | Identificador del sensor | sensor-simulado-bme680 |
| estacion | string | Nombre de estación | Grupo 2 - Sensor Simulado |
| temperatura | double | Temperatura en °C | 21.4 |
| humedad | double | Humedad relativa (%) | 45.8 |
| presion | double | Presión en hPa | 1012.3 |
| altura | double | Altura estimada en msnm | 3825.0 |
| gas | double | Resistencia de gas en KOhms | 48.2 |
| iaq | double | Índice de calidad de aire 0-500 | 86.1 |
| eco2 | double | CO2 equivalente estimado ppm | 554.9 |
| voc | double | VOC estimado | 6.3 |
| calidad_aire | string | Excelente, Buena o Pobre | Excelente |
| riesgo_aire | string | BAJO, MEDIO, ALTO | BAJO |
| origen | string | Productor del evento | python-sensor-simulator |
| fechaHora | string | Fecha ISO del productor | 2026-05-24T18:30:00 |
| timestamp | long | Epoch milisegundos del evento | 1779647400000 |
