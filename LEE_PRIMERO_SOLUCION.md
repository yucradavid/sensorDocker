# LEE PRIMERO - Solución al error Spark Kafka

## Tu avance está bien

Kafka está levantado y el tópico `calidad-aire-eventos` fue creado correctamente. Si Kafka UI muestra `Message Count = 0`, significa que todavía no está corriendo ningún productor/simulador enviando datos.

## Error del notebook

El error:

```txt
AnalysisException: Failed to find data source: kafka
```

significa que Spark no encontró el conector `spark-sql-kafka`. Usa el notebook corregido:

```txt
iot_air_kafka_final_corregido/bigdata-lab/notebooks/09_streaming_calidad_aire_kafka_FIXED.ipynb
```

Cópialo a:

```txt
C:\Users\User\Pictures\bogdata9ciclo\bigdata-lab\notebooks\09_streaming_calidad_aire_kafka_FIXED.ipynb
```

## Comandos Windows CMD

### 1. Copiar notebook corregido a bigdata-lab

```cmd
copy /Y "C:\Users\User\Pictures\bogdata9ciclo\iot_air_kafka_final_corregido\bigdata-lab\notebooks\09_streaming_calidad_aire_kafka_FIXED.ipynb" "C:\Users\User\Pictures\bogdata9ciclo\bigdata-lab\notebooks\09_streaming_calidad_aire_kafka_FIXED.ipynb"
```

### 2. Levantar simulador para que haya datos

```cmd
cd C:\Users\User\Pictures\bogdata9ciclo\iot_air_kafka_final_corregido\air-quality-simulator-py
docker compose -f docker-compose-dev.yml up --build
```

Debes ver JSON cada 3 segundos. Después Kafka UI debe mostrar `Message Count > 0`.

### 3. Abrir notebook correcto

Abre Jupyter desde bigdata-lab y entra a:

```txt
notebooks/09_streaming_calidad_aire_kafka_FIXED.ipynb
```

Si ya ejecutaste el notebook anterior, usa:

```txt
Kernel -> Restart Kernel
```

Luego ejecuta desde la primera celda.

## Estado esperado

- Kafka: Running
- Tópico: `calidad-aire-eventos`
- Simulador: generando JSON cada 3 segundos
- Kafka UI: Message Count mayor que 0
- Notebook FIX: ya no debe mostrar `Failed to find data source: kafka`
