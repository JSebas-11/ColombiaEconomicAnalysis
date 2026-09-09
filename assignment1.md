## SLIDE 1 — Descripción de la BD

### Análisis de la Economía Colombiana 2018–2026

Base de datos construida a partir de información estadística oficial del Banco de la República de Colombia (BanRep), integrando diferentes fuentes y frecuencias para analizar la evolución de la economía colombiana entre enero de 2018 y 2026.

**Indicadores analizados**

* Inflación (IPC)
* Tasa Representativa del Mercado (TRM)
* Tasa de ocupación y desempleo
* Tasa de política monetaria
* Índice bursátil COLCAP
* Crecimiento del PIB real

**Fuentes**

* 6 archivos oficiales de BanRep
* 4 CSV + 2 Excel

Los datos fueron limpiados, transformados y normalizados para facilitar su análisis mediante SQL, conservando la frecuencia económica apropiada de cada indicador.

---

## SLIDE 2 — Evaluación y preparación de los datos

### Dataset mensual

* **104 observaciones × 8 variables**
* `MonthlyDate`: frecuencia mensual
* 7 variables económicas numéricas (`float64`)
* `OccupationRate`: 1 valor faltante
* `UnemploymentRate`: 1 valor faltante
* Demás variables: 0 valores faltantes

### Transformaciones principales

* TRM → promedio mensual
* Tasa de política → último valor del mes
* COLCAP → último valor del mes
* COLCAP → retorno mensual calculado

### Dataset trimestral

* **33 observaciones × 2 variables**
* `Quarter`: formato `YYYY-Q#`
* `RealGDPGrowth`: numérica (`float64`)
* 0 valores faltantes

### PIB real — estadísticas

* Promedio: **2,75%**
* Mediana: **2,33%**
* Mínimo: **−16,74%**
* Máximo: **18,27%**
* Desviación estándar: **6,02%**

### Calidad

Los datos presentan una estructura consistente y adecuada para el análisis. Los únicos valores faltantes corresponden a ocupación y desempleo, ambos en 2026.

**104 meses | 33 trimestres | 10 variables económicas**

---

## SLIDE 3 — Consultas y principales resultados

### QUERY 1 — Inflación

**¿Cómo se comportó la inflación entre 2018 y 2026?**

* 2018–2021: relativamente estable, alrededor de **2,5–3,5%**
* 2022: fuerte aceleración, promedio de **10,15%**
* 2023: máximo de **13,34%**
* 2024–2025: desinflación significativa
* 2026: permanece por encima de los niveles pre-2022

### QUERY 2 — TRM

**¿Cómo evolucionó la tasa de cambio entre 2018 y 2026?**

* 2018: **2.956 COP/USD**
* 2020: **3.693 COP/USD**
* 2022: **4.253 COP/USD**, máximo mensual de **4.927**
* 2023: máximo promedio anual de **4.328 COP/USD**
* 2024–2025: descenso gradual
* 2026: **3.541 COP/USD***

### QUERY 3 — Política monetaria

**¿Cómo respondió BanRep a la inflación?**

| Nivel de inflación | Inflación promedio | Tasa de política promedio |
| ------------------ | -----------------: | ------------------------: |
| Baja               |              1,86% |                     2,06% |
| Moderada           |              3,61% |                     4,11% |
| Alta               |              8,07% |                    10,17% |

### QUERY 4 — Mercado laboral y PIB

**¿Qué ocurrió con el empleo y el crecimiento durante COVID-19?**

* Ocupación: **58,42% → 50,43%**
* Desempleo: **10,43% → 16,67%**
* PIB: **+2,87% → −7,17%**
* Post-COVID: PIB **4,54%** y desempleo cercano al nivel pre-COVID

### QUERY 5 — Mercado bursátil

**¿Cuáles fueron los extremos del retorno mensual del COLCAP?**

* Peor retorno: **−27,48% — marzo 2020**
* Segundo gran descenso: **−17,49% — junio 2022**
* Fuerte recuperación: **+10,67% — noviembre 2020**
* Mayor retorno: **+19,67% — enero 2026**

### QUERY 6 — Relaciones

**¿Existe relación entre las variables macroeconómicas y el COLCAP?**

* Inflación ↔ Política monetaria: **0,756**
* Inflación ↔ TRM: **0,719**
* Política monetaria ↔ TRM: **0,566**
* Correlaciones con retornos del COLCAP: **≈ 0**

---

## SLIDE 4 — Análisis económico

**Fuente principal: Banco de la República de Colombia**

### Inflación y política monetaria

La economía colombiana pasó de una inflación relativamente estable a niveles de dos dígitos durante 2022–2023. El máximo de **13,34% en marzo de 2023** reflejó un período de fuertes presiones inflacionarias.

En respuesta, BanRep aumentó progresivamente la tasa de política, desde **1,75% en 2021 hasta 13,25% en 2023**, buscando reducir las presiones de demanda y conducir la inflación hacia su meta del **3%**.

### TRM y shocks económicos

La tasa de cambio experimentó fuertes movimientos durante los principales episodios de estrés económico.

* **2020:** fuerte depreciación asociada al shock de COVID-19.
* **2022:** nuevo episodio de depreciación, alcanzando un máximo de **4.926,66 COP/USD**.

Posteriormente, el peso mostró una recuperación frente al dólar, reflejada en la reducción del promedio de la TRM.

### COVID-19: actividad y empleo

La pandemia generó un deterioro simultáneo de la actividad económica y del mercado laboral. La caída del PIB estuvo acompañada por una reducción significativa de la ocupación y un aumento del desempleo.

Posteriormente, la actividad económica se recuperó y el desempleo regresó cerca de sus niveles pre-pandemia, aunque la ocupación promedio permaneció ligeramente por debajo.

### Mercado bursátil

El mayor deterioro mensual del COLCAP ocurrió en **marzo de 2020**, coincidiendo con el shock financiero internacional provocado por la pandemia.

La posterior recuperación de noviembre y diciembre de 2020 muestra la elevada volatilidad del mercado durante este período. Un segundo episodio importante de caída ocurrió en **2022**, en un contexto de mayores presiones financieras y económicas.

---

## SLIDE 5 — Conclusiones

1. **La economía colombiana atravesó dos grandes episodios de estrés:** el shock de COVID-19 y el período de inflación y depreciación de 2022–2023.

2. **La política monetaria respondió al aumento de las presiones inflacionarias**, con tasas considerablemente mayores durante los períodos de inflación alta.

3. **La actividad económica y el mercado laboral mostraron una recuperación posterior al COVID-19**, aunque algunos indicadores no regresaron completamente a sus niveles pre-pandemia.

4. **Las relaciones macroeconómicas fueron más fuertes entre inflación, política monetaria y TRM que con el mercado bursátil.** Las correlaciones casi nulas con los retornos del COLCAP indican que su comportamiento mensual depende de múltiples factores y no puede explicarse mediante estas variables por sí solas.

* 2026 corresponde a un período parcial.