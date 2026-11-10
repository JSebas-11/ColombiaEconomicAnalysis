## SLIDE 1

### Descripcion BD

Base de datos construida a partir de información estadística oficial del Banco de la República de Colombia (BanRep), integrando diferentes fuentes y frecuencias para analizar la evolución de la economía colombiana entre enero de 2018 y 2026.

- Indicadores analizados:
    - Inflación (IPC)
    - Tasa Representativa del Mercado (TRM)
    - Tasa de ocupación y desempleo
    - Tasa de política monetaria
    - Índice bursátil COLCAP
    - Crecimiento del PIB real

- Fuentes originales: 6 archivos de BanRep -> 4 archivos CSV + 2 archivos Excel

Los datos fueron limpiados, transformados y normalizados para facilitar su análisis mediante consultas SQL, conservando la frecuencia económica apropiada de cada indicador.

---

## SLIDE 2 (Evaluación y preparación de los datos)

### Dataset mensual

- 104 observaciones y 8 variables.
- MonthlyDate: variable temporal con frecuencia mensual (period[M]).
- Las 7 variables económicas restantes son numéricas (float64).
- Valores faltantes: OccupationRate y UnemploymentRate presentan 1 valor faltante cada una; las demás variables no presentan valores faltantes.
- Las variables fueron normalizadas a frecuencia mensual mediante transformaciones apropiadas: promedio mensual para TRM, último valor del mes para tasa de política y COLCAP, y retorno mensual calculado para COLCAP.

### Dataset trimestral

- 33 observaciones y 2 variables.
- Quarter: variable temporal categórica en formato YYYY-Q#.
- RealGDPGrowth: variable numérica (float64).
- No presenta valores faltantes.

### PIB real — estadísticas principales

- Promedio: 2,75 %
- Mediana: 2,33 %
- Mínimo: −16,74 %
- Máximo: 18,27 %
- Desviación estándar: 6,02 %

### Conclusión de calidad

Los datasets presentan una estructura consistente y adecuada para el análisis. Los únicos valores faltantes identificados corresponden a las tasas de ocupación y desempleo del 2026, por lo que deberán ser considerados durante las consultas y el análisis.

### Vista general

104 meses | 33 trimestres | 10 variables económicas

- Valores faltantes
    - 6 variables mensuales: 0 faltantes
    - Ocupación: 1 faltante
    - Desempleo: 1 faltante
    - PIB: 0 faltantes

- Tipos de datos
    -Period[M] → fecha mensual
    -YYYY-Q# → trimestre
    -float64 → variables numéricas