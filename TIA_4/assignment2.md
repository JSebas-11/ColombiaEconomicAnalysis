## Analisis del contexto

### Objetivo

Analizar la evolución de los principales indicadores macroeconómicos y financieros de Colombia a lo largo del tiempo, con el propósito de identificar tendencias, variaciones y posibles relaciones entre la inflación, la tasa de cambio, el mercado laboral, la política monetaria, el mercado bursátil y el crecimiento económico.

### Qué representa esta información?

La información representa el comportamiento de diferentes variables económicas y financieras de Colombia a lo largo del tiempo. Incluye indicadores mensuales, como la inflación, la tasa de cambio representativa del mercado (TRM), las tasas de ocupación y desempleo, la tasa de política monetaria y el índice COLCAP, así como el crecimiento trimestral del PIB real.

En conjunto, estos indicadores permiten describir las condiciones económicas del país, observar cambios en el costo de vida, el mercado laboral y los mercados financieros, y explorar posibles patrones entre estas variables.

### De dónde proviene?

Los datos provienen de estadísticas sobre la economía colombiana, recopiladas por el Banco de la República de Colombia (BanRepo).

Los datos originales se encontraban en conjuntos independientes, por lo cual fueron organizados en dos archivos de análisis: uno con periodicidad mensual y otro con periodicidad trimestral. Con el fin de facilitar los análisis y comparaciones temporales entre los indicadores.

### Qué organizaciones podrían beneficiarse de este análisis?

- Entidades financieras: Para monitorear las condiciones macroeconómicas y evaluar el entorno en el que desarrollan sus operaciones.
- Empresas e inversionistas: Para comprender las variaciones económicas y financieras que pueden influir en sus decisiones.
- Entidades gubernamentales: Para estudiar la evolución de los indicadores nacionales.
- Investigadores y estudiantes: Para identificar tendencias y explorar relaciones entre variables macroeconómicas y financieras.

### Preguntas clave del análisis

- Cómo ha evolucionado la economía colombiana durante el período analizado, considerando variaciones y tendencias de sus principales indicadores?
- Qué fluctuaciones, comportamientos atípicos y cambios significativos se han presentado en los indicadores analizados, y en qué períodos se han concentrado?
- Qué patrones y posibles relaciones pueden identificarse entre la inflación, la tasa de cambio, la política monetaria y el comportamiento del mercado bursátil colombiano?
- Cómo han variado las condiciones del mercado laboral y el crecimiento económico durante el período de estudio, y qué tendencias se pueden observar en su comportamiento?
- Qué indicadores presentan mayor variabilidad y cuáles muestran un comportamiento mas estable a lo largo del período analizado?
- Qué información aportan los patrones identificados para comprender las condiciones económicas y financieras de Colombia?

---

## Revisión de tipos de datos

### Datos originales

| Dataset                    | Columna                     | Tipo original | Tipo requerido |
| -------------------------- | --------------------------- | ------------- | -------------- |
| ConsumerPriceIndex         | Fecha (Mes Año)             | `str`         | `date`         |
| ConsumerPriceIndex         | Indice                      | `float`       | `float`        |
| ConsumerPriceIndex         | Variación mensual (%)       | `float`       | `float`        |
| ConsumerPriceIndex         | Variación anual (%)         | `float`       | `float`        |
| ConsumerPriceIndex         | Variación año corrido (%)   | `float`       | `float`        |
| ConsumerPriceIndex         | Orden_División              | `float`       | `float`        |
| ConsumerPriceIndex         | División del gasto          | `str`         | `str`          |
| COP_TRM                    | Periodo (Mes Dia Año)       | `str`         | `date`         |
| COP_TRM                    | Tasa Representativa mercado | `float`       | `float`        |
| GDP                        | Fecha (Dia Mes Año)         | `str`         | `date`         |
| GDP                        | Crecimiento PIB trimestral  | `str`         | `float`        |
| OccupationAndUnemployement | Metodologia                 | `str`         | `str`          |
| OccupationAndUnemployement | Cobertura geografica        | `str`         | `str`          |
| OccupationAndUnemployement | Fecha (Mes Año)             | `str`         | `date`         |
| OccupationAndUnemployement | Tasa de ocupación           | `float`       | `float`        |
| OccupationAndUnemployement | Tasa de desempleo           | `float`       | `float`        |
| Policy_rate                | Fecha (Dia Mes Año)         | `datetime`    | `date`         |
| Policy_rate                | Tasa de política monetaria  | `float`       | `float`        |
| Stock_market_colcap        | Fecha (Dia Mes Año)         | `str`         | `date`         |
| Stock_market_colcap        | Nombre del índice           | `str`         | `str`          |
| Stock_market_colcap        | Indice                      | `float`       | `float`        |
| Stock_market_colcap        | Variación absoluta          | `float`       | `float`        |
| Stock_market_colcap        | Variación porcentual        | `float`       | `float`        |

### Datos consolidados

| Dataset             | Columna          | Tipo original | Tipo requerido |
| ------------------- | ---------------- | ------------- | -------------- |
| Economics_monthly   | MonthlyDate      | `str`         | `str`          |
| Economics_monthly   | InflationYOY     | `float`       | `float`        |
| Economics_monthly   | TRMAvg           | `float`       | `float`        |
| Economics_monthly   | OccupationRate   | `float`       | `float`        |
| Economics_monthly   | UnemploymentRate | `float`       | `float`        |
| Economics_monthly   | PolicyRate       | `float`       | `float`        |
| Economics_monthly   | ColcapIndex      | `float`       | `float`        |
| Economics_monthly   | MonthlyReturn    | `float`       | `float`        |
| Economics_quarterly | Quarter          | `str`         | `str`          |
| Economics_quarterly | RealGDPGrowth    | `float`       | `float`        |

*Nota:* `MonthlyDate` y `Quarter` pueden conservarse como cadenas ya que siguen un formato estandarizado y se interpretan correctamente durante el análisis para operaciones temporales, conversiones, ordenamiento cronológico y visualización.

---

## Análisis de datos faltantes

### Datos originales

**ConsumerPriceIndex**

| Columna                   | Datos faltantes |
| ------------------------- | --------------- |
| Fecha (Mes Año)           | 0               |
| Indice                    | 0               |
| Variación mensual (%)     | 13              |
| Variación anual (%)       | 134             |
| Variación año corrido (%) | 13              |
| Orden_División            | 1116            |
| División del gasto        | 0               |

Los valores faltantes en las columnas de variación mensual, anual y año corrido se concentran principalmente en registros cuya categoría de `División del gasto` es distinta de `Total` y en períodos anteriores a enero de 1956.

Por su parte, los 1116 valores faltantes de `Orden_División` se encuentran en las categorías distintas de `Total`. Este patrón es debido a la clasificación de las divisiones del gasto, ya que estas son consolidadas en la categoria `Total`.

**COP_TRM**

No se identificaron datos faltantes en las columnas `Periodo (Mes Dia Año)` y `Tasa Representativa mercado`.

**GDP**

No se identificaron datos faltantes en las columnas `Fecha (Dia Mes Año)` y `Crecimiento PIB trimestral`.

**OccupationAndUnemployement**

No se identificaron datos faltantes en las columnas `Metodologia`, `Cobertura geografica`, `Fecha (Mes Año)`, `Tasa de ocupación` y `Tasa de desempleo`.

**Policy_rate**

No se identificaron datos faltantes en las columnas `Fecha (Dia Mes Año)` y `Tasa de política monetaria`.

**Stock_market_colcap**

No se identificaron datos faltantes en las columnas `Fecha (Dia Mes Año)`, `Nombre del índice`, `Indice`, `Variación absoluta` y `Variación porcentual`.

### Datos consolidados

**Economics_monthly**

| Columna          | Datos faltantes |
| ---------------- | --------------- |
| MonthlyDate      | 0               |
| InflationYOY     | 12              |
| TRMAvg           | 448             |
| OccupationRate   | 559             |
| UnemploymentRate | 559             |
| PolicyRate       | 537             |
| ColcapIndex      | 642             |
| MonthlyReturn    | 643             |

Los valores faltantes presentan patrones temporales asociados con la cobertura histórica de los indicadores:

- COLCAP (`ColcapIndex` y `MonthlyReturn`): Los valores faltantes se concentran en los años anteriores a 2008. Esto es debido a la cobertura histórica del índice, cuya creacion fue en el año 2008.

- Mercado laboral (`OccupationRate` y `UnemploymentRate`): Los valores faltantes se concentran en períodos anteriores a 2001. Esto esta relacionado con los cambios en las encuestas y metodologías de medición del mercado laboral, incluida la implementación de la Gran Encuesta Integrada de Hogares (GEIH) entre los años 2000 y 2006.

- Tasa de política monetaria (`PolicyRate`): Los valores faltantes se concentran en períodos anteriores a 1999. Aunque el Banco de la República publica información relacionada con la política monetaria desde años anteriores, la serie utilizada proporciona datos desde 1999.

- Tasa de cambio (`TRMAvg`): Los valores faltantes se concentran en períodos anteriores a 1991, lo que coincide con el establecimiento de la TRM como referencia oficial en diciembre de ese año.

- Inflación (`InflationYOY`): Los 12 valores faltantes se concentran en períodos anteriores al inicio de la cobertura utilizada para esta variable, alrededor de 1955. Este patrón se refleja con las fechas y categorías de la fuente original del índice de precios al consumidor.

Estos patrones sugieren que una parte importante de los valores faltantes puede responder a diferencias en la cobertura temporal de las series.

El estudio se concentra principalmente en el período comprendido entre 2002 y 2026. Dentro de este intervalo, la información presenta una cobertura consistente para los indicadores considerados, con excepciones en los datos de COLCAP previos a 2008 y los indicadores laborales de 2026.

**Economics_quarterly**

No se identificaron datos faltantes en las columnas `Quarter` y `RealGDPGrowth`.

---

## Análisis de variables categóricas

| Dataset                    | Columna              | Inconsistencias    | Datos unicos |
| -------------------------- | -------------------- | ------------------ | ------------ |
| ConsumerPriceIndex         | División del gasto   | No inconsistencias | 13           |
| OccupationAndUnemployement | Metodología          | No inconsistencias | 1            |
| OccupationAndUnemployement | Cobertura geográfica | No inconsistencias | 3            |
| Stock_market_colcap        | Nombre del índice    | No inconsistencias | 1            |

---

## Medidas estadísticas

**Economics_monthly**

| Variable         | Total | Media   | Mediana | Dev.Std | Min    | Max     |
| ---------------- | ----- | ------: | -------:|-------: | -----: | ------: |
| InflationYOY     | 854   | 13.36   | 9.54    | 9.19    | -0.87  | 41.65   |
| TRMAvg           | 418   | 2378.34 | 2278.97 | 1037.17 | 630.41 | 4926.66 |
| OccupationRate   | 307   | 58.14   | 58.38   | 2.83    | 42.50  | 64.01   |
| UnemploymentRate | 307   | 11.55   | 11.16   | 2.46    | 7.02   | 21.97   |
| PolicyRate       | 329   | 6.95    | 6.25    | 3.45    | 1.75   | 19.00   |
| ColcapIndex      | 224   | 1456.59 | 1440.03 | 300.77  | 788.73 | 2474.76 |
| MonthlyReturn    | 223   | 0.57    | 0.85    | 5.31    | -27.48 | 19.67   |

**Economics_quarterly**

| Variable      | Total | Media  | Mediana | Dev.Std | Min    | Max     |
| ------------- | ----- | -----: | -------:|-------: | -----: | ------: |
| RealGDPGrowth | 82.0  | 3.56   | 3.14    | 4.21    | -16.74 | 18.27   |

- InflationYOY: La media (13,36%) supera la mediana (9,54%), lo que indica que los periodos de inflación 
elevada aumentan el promedio. El mínimo negativo refleja episodios de deflación.

- TRMAvg: La desviación estándar de 1.037,17 evidencia una alta variación histórica de la tasa de cambio, 
influida por cambios económicos y externos.

- OccupationRate: El promedio de 58,14% y la desviación estándar de 2,83 muestran una ocupación relativamente 
estable en general, aunque el mínimo de 42,50% refleja una caída significativa, especialmente asociada con la pandemia de COVID-19.

- UnemploymentRate: La media de 11,55% y el máximo de 21,97% reflejan dificultades 
laborales, agravadas durante la pandemia.

- PolicyRate: La tasa promedio fue de 6,95%, con valores entre 1,75% y 19%, mostrando cambios importantes en la 
política monetaria frente a distintas condiciones económicas.

- ColcapIndex: La desviación estándar de 300,77 indica variaciones relevantes en el nivel del mercado bursátil colombiano. 
Sin embargo, su tendencia histórica también influye en esta medida.

- MonthlyReturn: La media positiva de 0,57% contrasta con una desviación estándar de 5,31 y un mínimo de -27,48%, 
evidenciando rendimientos variables y caídas fuertes durante episodios de crisis.

- RealGDPGrowth: El crecimiento promedio del PIB fue de 3,56%, pero el mínimo de -16,74% y el máximo de 18,27% reflejan 
la fuerte contracción económica y posterior recuperación alrededor de la pandemia.

**Conclusión** 

Los datos muestran una economía colombiana marcada por cambios en inflación, tasa de cambio, empleo y mercados financieros. 
La pandemia de COVID-19 fue un evento excepcional que afectó especialmente el empleo y el PIB. Además, los distintos tamaños 
de muestra indican que las variables tienen diferente cobertura histórica, por lo que sus resultados deben interpretarse teniendo 
en cuenta los periodos disponibles.

--- 

## Identificación, análisis y tratamiento de valores atípicos

Para identificar posibles valores atípicos se aplicó el método del rango intercuartílico (IQR) 
a los indicadores económicos mensuales y trimestrales. 
Se identificaron 30 observaciones potencialmente atípicas en las variables mensuales y cinco 
en el crecimiento trimestral del PIB. 

**Análisis de los resultados**

En el mercado laboral, las tasas de ocupación registraron valores inusualmente bajos durante varios 
meses de 2020 y 2021, mientras que la tasa de desempleo alcanzó valores elevados durante abril y 
julio de 2020. 
Estos comportamientos son consistentes con el impacto de la pandemia de COVID-19 sobre el empleo 
y la actividad económica. La observación de desempleo de enero de 2002 también requiere revisión, 
dado el contexto histórico del mercado laboral colombiano.

La tasa de cambio presentó un valor atípico en noviembre de 2022, cuando la TRM promedio alcanzó 
COP 4.926,66 por dólar. Este resultado es compatible con la elevada volatilidad cambiaria 
observada durante ese período. 
Asimismo, los valores de la tasa de política monetaria de abril a junio de 1999 reflejan un entorno 
de tasas de interés elevadas durante la crisis económica colombiana de finales de los años noventa.

En el mercado bursátil, se identificaron rendimientos mensuales extremos en octubre de 2008, marzo y 
diciembre de 2020, junio de 2022 y enero de 2026. 
Los registros de 2008 y marzo de 2020 coinciden temporalmente con importantes episodios de turbulencia 
financiera internacional. 
Los niveles elevados del COLCAP registrados en 2026 también pueden reflejar cambios en el nivel del 
índice y no necesariamente errores de registro.

En cuanto al crecimiento trimestral del PIB, los valores negativos de 2020 coinciden con la contracción 
económica asociada a la pandemia, mientras que los valores positivos de 2021 son compatibles con la 
recuperación posterior. 
El crecimiento registrado en el segundo trimestre de 2022 también se considera una observación que 
debe analizarse dentro de su contexto económico. 
La interpretación definitiva depende de confirmar la definición de crecimiento utilizada en la fuente.

**Decisiones de tratamiento y justificación**

No se eliminarán las observaciones identificadas mediante el método IQR. Ya que los valores representan 
acontecimientos económicos reales, y aportan información relevante sobre la variabilidad y los cambios 
experimentados por la economía colombiana.

Esta estrategia permite preservar la información histórica y evita reducir artificialmente 
la volatilidad de los indicadores. 
Como resultado, las medidas estadísticas y los análisis posteriores representarán de manera 
más fiel los comportamientos observados, incluidos los episodios económicos excepcionales.