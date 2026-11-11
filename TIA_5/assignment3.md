# TIA 5: Guía de presentación

**Dashboard:** `TIA_5/powerbi/ColombiaMacro.pbip`, 3 páginas. **Tiempo:** 7 minutos como máximo.
El docente elige quién presenta qué, así que **los tres deben saber todo**.

## Reparto (intercambiable)

| Página | Mensaje en una frase |
| --- | --- |
| 1 Resumen | Quién decide, con qué datos y qué preguntas |
| 2 Calidad de datos | Los datos son confiables: 1 vacío, 50 atípicos reales |
| 3 Hallazgos, P1 y P2 | Tasas siguen a la inflación; dólar y acciones van por separado |
| 3 Hallazgos, P3 y P4 | COVID y gobiernos; luego la recomendación (volver a página 1) |

## Página 1: Resumen (Contexto, 20 pts)

- **Problema:** el comité de inversiones de una gestora de activos decide cuánto invertir en **renta fija, acciones colombianas y dólares**.
- **Datos:** 7 indicadores del **Banco de la República**: inflación, tasa de política, TRM, COLCAP, desempleo, ocupación, PIB real. Periodo: enero de 2008 a julio de 2026 (223 meses, 74 trimestres).
- **Cada variable responde a una decisión:** la inflación y la tasa responden a renta fija, la TRM a dólares, el COLCAP a acciones.
- **4 preguntas:** ¿la tasa sigue a la inflación?, ¿peso y COLCAP se mueven juntos?, ¿cuánto golpeó el COVID al empleo?, ¿qué cambió en cada gobierno?
- **Tarjetas (julio de 2026):** inflación 6.03%, tasa de política 12.00%, TRM 3,268.95, COLCAP 2,392.10.

## Página 2: Calidad de datos (Faltantes 20 pts + Atípicos 20 pts + Estadística descriptiva)

**Datos faltantes: identificar, causa, acción, impacto**
- **Identificar:** 1 de 1561 celdas mensuales está vacía (0.06%), el rendimiento del COLCAP de enero de 2008. Ver la columna "Vacíos" de la tabla.
- **Causa:** un rendimiento necesita el mes anterior, y el índice nace en enero de 2008. Los vacíos más antiguos son fechas de inicio de cada serie, por eso la ventana empieza en 2008.
- **Acción:** **no se imputa**. Rellenar un dato que no puede existir es inventarlo.
- **Impacto:** 222 rendimientos en vez de 223, y se pierde la historia anterior a 2008.

**Datos atípicos: método, investigación, decisión, impacto**
- **Método estadístico + gráfico:** regla IQR (1.5 × IQR fuera de Q1–Q3). Se encontraron **50**: 43 mensuales y 7 trimestres de PIB. En el gráfico, los meses en negro son los atípicos.
- **Investigación:** coinciden con eventos documentados en prensa y en el DANE. **No hay errores de digitación.**
  - Crisis de 2008: COLCAP −18.98% en octubre.
  - COVID: COLCAP −27.48% en marzo de 2020; desempleo de 21.97% en mayo de 2020; PIB −16.74% en el segundo trimestre de 2020.
  - Elecciones de 2022: COLCAP −17.49% en junio.
  - Inflación de 2022-23: pico de 13.34% en marzo de 2023.
  - Máximos históricos: COLCAP +19.67% en enero de 2026.
- **Decisión:** **se conservan los 50**. Eliminarlos subestimaría el riesgo y borraría los episodios que se están analizando.
- **Impacto:** la media es sensible a los extremos, por eso se muestra la **mediana** al lado. Ejemplos: inflación 4.93% de media frente a 3.97% de mediana; tasa de política 6.11% frente a 4.50%.

## Página 3: Hallazgos (Gráficos e interpretación, 25 pts)

| Gráfico | Qué decir | Clic |
| --- | --- | --- |
| P1. Inflación y tasa de política | La correlación sube de 0.80 en el mismo mes a **0.88 seis meses después**: el Banco de la República reacciona con rezago. En 2022 la tasa real fue negativa (10.15% de inflación con 7.46% de tasa); en 2024, 6.63% con 11.33%. | Duque + Petro |
| P2. TRM y COLCAP (enero de 2008 = 100) | Correlación de **−0.14**: casi independientes. La TRM sí acompaña a la inflación (0.58). | Uribe II |
| P3. Desempleo | Promedio de 10.89% en 2019, **21.97% en el pico** (mayo de 2020) y 10.17% en 2023: se recuperó. | Duque |
| P4. Inflación al inicio y al final de cada gobierno | El promedio engaña. Con Duque fue de 3.10% a **10.21%**; con Petro, de 10.84% a **6.03%**. | Todos |

**Aclarar siempre:** los gobiernos indican *cuándo* pasó algo, no *quién lo causó*. El Banco de la República es independiente y hubo choques globales.

## Cierre: recomendación (volver a la página 1)

1. **Renta fija:** usar la inflación como señal temprana; la tasa la sigue unos 6 meses después.
2. **Dólar:** decidirlo por separado de las acciones; casi no se mueven juntos.
3. **Acciones:** dimensionar las posiciones para resistir choques; los extremos del COLCAP vienen de eventos, no de datos macro.

## Rúbrica: dónde se cumple cada criterio

| Criterio (pts) | Lo que pide "Excelente" | Dónde |
| --- | --- | --- |
| Contexto (20) | Problema de negocio claro; preguntas alineadas con los datos | Página 1: decisión, datos, fuente, 4 preguntas |
| Faltantes (20) | Identificar, causa, estrategia justificada, impacto | Página 2: columna "Vacíos" y recuadro de faltantes |
| Atípicos (20) | Método gráfico/estadístico, investigar, justificar el tratamiento | Página 2: columna "Atípicos (IQR)", gráfico en negro, recuadro de atípicos |
| Gráficos (25) | Precisos, variados, claros, bien interpretados | Página 3: 4 gráficos con títulos, ejes, unidades, leyendas y un hallazgo cada uno |
| Tiempo (15) | Dentro del tiempo; claro y conciso | Ensayar con cronómetro: **7:00 máximo** |
| Bonus (+0.3) | Dashboard **todo en inglés** | **No aplica:** el dashboard está en español |

## Preguntas probables

- **¿Por qué no imputaron?** Es un solo dato y no puede existir: un rendimiento sin mes previo. Imputarlo sería inventarlo, y el impacto es mínimo.
- **¿Por qué desde 2008?** Es el primer mes en que existen todas las series, porque el COLCAP nace ese mes.
- **¿Por qué hay más atípicos que en el TIA 4?** El TIA 4 usó la historia completa. El IQR depende de la ventana: con otra ventana, cambian los límites.
- **¿Por qué el IQR marca el COLCAP en 2026?** Es un nivel con tendencia, así que los nuevos máximos salen como atípicos. Por eso se analizan los rendimientos.
- **¿Qué impulsó el +19.67% de enero de 2026?** Fue un alza amplia (Cementos Argos, Cibest, Mineros, Ecopetrol, ISA), con un volumen 84% mayor. Los analistas la asocian a las expectativas por las elecciones de 2026. No hay una causa única documentada.
- **¿La correlación inflación–tasa es causal?** No lo prueba. Es consistente con un banco central que reacciona con rezago.
- **¿Por qué el PIB no es mensual?** El DANE lo publica por trimestre, y no se interpola.
- **¿Culpan a los presidentes?** No. El periodo de gobierno solo ubica en el tiempo, y desde agosto el mes se asigna al presidente entrante.
- **¿Por qué un comité de inversiones?** Es la organización que usaría estos datos: cada variable responde a una decisión de inversión.

## Antes de presentar

- [ ] Abrir el `.pbip`, hacer **Refresh** y revisar las 3 páginas.
- [ ] Exportar a PDF (**File > Export > PDF**) como respaldo si falla la demo en vivo.
- [ ] Ensayar con cronómetro, rotando quién presenta cada página.
- [ ] Practicar los 4 clics del filtro "Gobierno" en la página 3, y volver a "All" al terminar.
