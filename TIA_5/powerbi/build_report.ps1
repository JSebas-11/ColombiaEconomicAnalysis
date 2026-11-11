# Genera las 3 páginas del informe ColombiaMacro.pbip (formato PBIR), en español.
# Ejecutar con Power BI Desktop cerrado:
#   powershell -ExecutionPolicy Bypass -File TIA_5\powerbi\build_report.ps1
# Reemplaza todas las páginas de ColombiaMacro.Report\definition\pages: los cambios hechos a mano en Desktop se pierden.
# Este archivo debe guardarse como UTF-8 con BOM para que Windows PowerShell 5.1 lea bien las tildes.

$ErrorActionPreference = 'Stop'
$Root = Join-Path $PSScriptRoot 'ColombiaMacro.Report\definition'
$PagesDir = Join-Path $Root 'pages'
$VC = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json'
$PG = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'
$PM = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json'

# Paleta (DASHBOARD_SPEC sección 4): cada variable conserva su color en todo el informe.
$C = @{ Policy = '#2a78d6'; Inflation = '#eb6834'; InflationLight = '#f5b89a'; Trm = '#008300'; Colcap = '#6250d6'
        Unemployment = '#e34948'; Ink = '#0b0b0b'; Ink2 = '#52514e'; Box = '#f0efec' }
$M = '_Measures'

# ---------- expresiones ----------
function Lit([string]$v) { [ordered]@{ expr = [ordered]@{ Literal = [ordered]@{ Value = $v } } } }
function LitStr([string]$s) { Lit ("'" + $s.Replace("'", "''") + "'") }
function LitBool([bool]$b) { if ($b) { Lit 'true' } else { Lit 'false' } }
function LitNum($n) { Lit ("{0}D" -f $n) }
function Color([string]$hex) { [ordered]@{ solid = [ordered]@{ color = (LitStr $hex) } } }
function ColField([string]$table, [string]$col) {
  [ordered]@{ Column = [ordered]@{ Expression = [ordered]@{ SourceRef = [ordered]@{ Entity = $table } }; Property = $col } }
}
function MeasureField([string]$measure) {
  [ordered]@{ Measure = [ordered]@{ Expression = [ordered]@{ SourceRef = [ordered]@{ Entity = $M } }; Property = $measure } }
}
function ColorByMeasure([string]$measure) { [ordered]@{ solid = [ordered]@{ color = [ordered]@{ expr = (MeasureField $measure) } } } }
$AllPoints = [ordered]@{ data = @([ordered]@{ dataViewWildcard = [ordered]@{ matchingOption = 1 } }) }

# Proyección: 'Tabla.Columna' para una columna, nombre simple para una medida de _Measures. Nombre visible opcional.
function Proj([string]$ref, [string]$display = $null, [bool]$active = $false) {
  if ($ref.Contains('.')) { $t, $c = $ref.Split('.', 2); $f = ColField $t $c; $qr = $ref; $native = $c }
  else { $f = MeasureField $ref; $qr = "$M.$ref"; $native = $ref }
  $p = [ordered]@{ field = $f; queryRef = $qr; nativeQueryRef = $native }
  if ($display) { $p.displayName = $display }
  if ($active) { $p.active = $true }
  $p
}
function Role { param([object[]]$projections) [ordered]@{ projections = @($projections) } }
function Prop([hashtable]$props, $selector = $null) {
  $o = [ordered]@{ properties = $props }
  if ($selector) { $o.selector = $selector }
  $o
}
function SortBy([string]$ref, [string]$dir = 'Ascending') {
  $f = if ($ref.Contains('.')) { $t, $c = $ref.Split('.', 2); ColField $t $c } else { MeasureField $ref }
  [ordered]@{ sort = @([ordered]@{ field = $f; direction = $dir }) }
}
function TitleObj([string]$text, [string]$subtitle = $null) {
  $o = [ordered]@{ title = @(Prop @{ show = (LitBool $true); text = (LitStr $text); fontSize = (LitNum 11) }) }
  # Sin subtítulo explícito se apaga, para que Power BI no genere uno automático en inglés ("X by Y").
  $o.subTitle = if ($subtitle) { @(Prop @{ show = (LitBool $true); text = (LitStr $subtitle) }) } else { @(Prop @{ show = (LitBool $false) }) }
  $o
}
function NoTitle { [ordered]@{ title = @(Prop @{ show = (LitBool $false) }) } }

# ---------- páginas y contenedores ----------
$script:page = $null; $script:z = 0
$pages = [System.Collections.ArrayList]::new()
function New-Page([string]$name, [string]$display) {
  $script:page = [ordered]@{ name = $name; display = $display; visuals = [System.Collections.ArrayList]::new() }
  $script:z = 1000
}
function Save-Page { [void]$pages.Add($script:page) }
function Add-Visual([string]$name, [double]$x, [double]$y, [double]$w, [double]$h, $visual) {
  $script:z += 100
  [void]$script:page.visuals.Add([ordered]@{
    '$schema' = $VC; name = $name
    position = [ordered]@{ x = $x; y = $y; z = $script:z; height = $h; width = $w; tabOrder = $script:z }
    visual = $visual
  })
}

# ---------- visuales ----------
function Run([string]$t, [int]$s = 11, [bool]$b = $false, [string]$c = $C.Ink, [string]$f = 'Segoe UI') {
  $st = [ordered]@{ fontFamily = $f; fontSize = "${s}pt"; color = $c }
  if ($b) { $st.fontWeight = 'bold' }
  [ordered]@{ value = $t; textStyle = $st }
}
function Para([object[]]$runs, [string]$align = $null) {
  $p = [ordered]@{ textRuns = @($runs) }
  if ($align) { $p.horizontalTextAlignment = $align }
  $p
}
function TextBox([object[]]$paras, [string]$bg = $null) {
  $v = [ordered]@{ visualType = 'textbox'; objects = [ordered]@{ general = @(Prop @{ paragraphs = @($paras) }) } }
  if ($bg) { $v.visualContainerObjects = [ordered]@{ background = @(Prop @{ show = (LitBool $true); color = (Color $bg); transparency = (LitNum 0) }) } }
  $v.drillFilterOtherVisuals = $true
  $v
}
function Shape([string]$shapeType, [string]$fill) {
  [ordered]@{
    visualType = 'basicShape'
    objects = [ordered]@{
      general = @(Prop @{ shapeType = (LitStr $shapeType) })
      fill = @(Prop @{ fillColor = (Color $fill); transparency = (LitNum 0) })
      line = @(Prop @{ lineColor = (Color $fill); transparency = (LitNum 100); weight = (LitNum 0) })
    }
    drillFilterOtherVisuals = $true
  }
}
# Gráfico de líneas sobre DimDate[Date]; $names son los nombres de la leyenda.
function LineChart([string[]]$measures, [string[]]$names, [string[]]$colors, [string]$title, [string]$axisTitle, [string]$subtitle) {
  $dp = @(for ($i = 0; $i -lt $measures.Count; $i++) { Prop @{ fill = (Color $colors[$i]) } ([ordered]@{ metadata = "$M.$($measures[$i])" }) })
  $projs = @(for ($i = 0; $i -lt $measures.Count; $i++) { Proj $measures[$i] $names[$i] })
  [ordered]@{
    visualType = 'lineChart'
    query = [ordered]@{
      queryState = [ordered]@{ Category = (Role @(Proj 'DimDate.Date' 'Mes' -active $true)); Y = (Role $projs) }
      sortDefinition = (SortBy 'DimDate.Date')
    }
    objects = [ordered]@{
      dataPoint = $dp
      legend = @(Prop @{ show = (LitBool ($measures.Count -gt 1)); position = (LitStr 'Top') })
      valueAxis = @(Prop @{ showAxisTitle = (LitBool $true); titleText = (LitStr $axisTitle) })
      categoryAxis = @(Prop @{ showAxisTitle = (LitBool $false) })
    }
    visualContainerObjects = (TitleObj $title $subtitle)
    drillFilterOtherVisuals = $true
  }
}
# Columnas (clusteredColumnChart) o barras horizontales (clusteredBarChart). $colorMeasure colorea cada punto con una medida que devuelve un hex.
function Bars([string]$type, [string]$categoryRef, [string]$categoryName, [string[]]$measures, [string[]]$names, [string[]]$colors,
              [string]$title, [string]$axisTitle, [string]$subtitle = $null, [bool]$labels = $false, [string]$colorMeasure = $null) {
  $dp = if ($colorMeasure) { @(Prop @{ fill = (ColorByMeasure $colorMeasure) } $AllPoints) }
        else { @(for ($i = 0; $i -lt $measures.Count; $i++) { Prop @{ fill = (Color $colors[$i]) } ([ordered]@{ metadata = "$M.$($measures[$i])" }) }) }
  $projs = @(for ($i = 0; $i -lt $measures.Count; $i++) { Proj $measures[$i] $names[$i] })
  $objs = [ordered]@{
    dataPoint = $dp
    legend = @(Prop @{ show = (LitBool ($measures.Count -gt 1)); position = (LitStr 'Top') })
    valueAxis = @(Prop @{ showAxisTitle = (LitBool ([bool]$axisTitle)); titleText = (LitStr $axisTitle) })
    categoryAxis = @(Prop @{ showAxisTitle = (LitBool $false) })
  }
  if ($labels) { $objs.labels = @(Prop @{ show = (LitBool $true); labelDisplayUnits = (LitNum 1) }) }
  [ordered]@{
    visualType = $type
    query = [ordered]@{
      queryState = [ordered]@{ Category = (Role @(Proj $categoryRef $categoryName -active $true)); Y = (Role $projs) }
      sortDefinition = (SortBy $categoryRef)
    }
    objects = $objs
    visualContainerObjects = (TitleObj $title $subtitle)
    drillFilterOtherVisuals = $true
  }
}
# Tabla. $cols: arreglo de @(ref, nombre visible).
function Table([object[]]$cols, [string]$title, [string]$sortRef) {
  [ordered]@{
    visualType = 'tableEx'
    query = [ordered]@{ queryState = [ordered]@{ Values = (Role @($cols | ForEach-Object { Proj $_[0] $_[1] })) }; sortDefinition = (SortBy $sortRef) }
    objects = [ordered]@{
      values = @(Prop @{ wordWrap = (LitBool $true); fontSize = (LitNum 9) })
      columnHeaders = @(Prop @{ wordWrap = (LitBool $true); fontSize = (LitNum 9) })
      total = @(Prop @{ totals = (LitBool $false) })
    }
    visualContainerObjects = (TitleObj $title)
    drillFilterOtherVisuals = $true
  }
}
function Card([string]$measure, [string]$title, [string]$label, [int]$size = 34) {
  [ordered]@{
    visualType = 'card'
    query = [ordered]@{ queryState = [ordered]@{ Values = (Role @(Proj $measure $label)) } }
    objects = [ordered]@{
      labels = @(Prop @{ fontSize = (LitNum $size); color = (Color $C.Ink); labelDisplayUnits = (LitNum 1) })
      categoryLabels = @(Prop @{ show = (LitBool $true); fontSize = (LitNum 9) })
    }
    visualContainerObjects = (TitleObj $title)
    drillFilterOtherVisuals = $true
  }
}
function Slicer([string]$ref, [string]$display, [string]$group) {
  [ordered]@{
    visualType = 'slicer'
    query = [ordered]@{ queryState = [ordered]@{ Values = (Role @(Proj $ref $display -active $true)) }; sortDefinition = (SortBy $ref) }
    objects = [ordered]@{
      data = @(Prop @{ mode = (LitStr 'Dropdown') })
      selection = @(Prop @{ selectAllCheckboxEnabled = (LitBool $true); singleSelect = (LitBool $false) })
    }
    syncGroup = [ordered]@{ groupName = $group; fieldChanges = $true; filterChanges = $true }
    drillFilterOtherVisuals = $true
  }
}

# ---------- elementos comunes ----------
$W = 1280; $H = 720; $L = 24; $FW = 1232; $LW = 604; $RX = 652
function Header([int]$n, [string]$part, [string]$title) {
  Add-Visual 'hdr_part' $L 10 700 26 (TextBox @(Para @(Run ("PARTE $n · " + $part.ToUpper()) 9 $false $C.Ink2)))
  Add-Visual 'hdr_num' ($W - 24 - 120) 10 120 26 (TextBox @(Para @(Run "0$n / 03" 9 $false $C.Ink2) 'right'))
  Add-Visual 'hdr_title' $L 32 980 44 (TextBox @(Para @(Run $title 20 $false $C.Ink 'Segoe UI Semibold')))
}
function SectionLabel([string]$name, [double]$x, [double]$y, [double]$w, [string]$text) {
  Add-Visual $name $x $y $w 22 (TextBox @(Para @(Run $text.ToUpper() 9 $true $C.Ink2)))
}
# Recuadro gris con barra de acento. Si una línea empieza con "Etiqueta: ", la etiqueta va en negrita.
function NoteBox([string]$name, [double]$x, [double]$y, [double]$w, [double]$h, [string]$label, [string[]]$lines, [int]$size = 10) {
  $paras = @(Para @(Run $label 9 $true $C.Ink2))
  foreach ($line in $lines) {
    $i = $line.IndexOf(': ')
    if ($i -gt 0 -and $i -lt 14) { $paras += Para @((Run ($line.Substring(0, $i + 2)) $size $true), (Run ($line.Substring($i + 2)) $size)) }
    else { $paras += Para @(Run $line $size) }
  }
  Add-Visual $name $x $y $w $h (TextBox $paras $C.Box)
  Add-Visual "${name}_bar" $x $y 4 $h (Shape 'rectangle' $C.Ink)
}

# =====================================================================
# 1 Resumen (contexto: 20 puntos)
# =====================================================================
New-Page 'overview' '1 Resumen'
Header 1 'Resumen' 'La inflación anticipa las tasas; el COLCAP se mueve por eventos'
Add-Visual 'context' $L 84 $LW 214 (TextBox @(
  (Para @(Run 'LA DECISIÓN' 9 $true $C.Ink2)),
  (Para @(Run 'El comité de inversiones de una gestora de activos colombiana debe decidir cómo ajustar su exposición a renta fija, acciones colombianas y dólares a lo largo del ciclo macroeconómico.' 12)),
  (Para @(Run ' ' 6)),
  (Para @(Run 'LOS DATOS' 9 $true $C.Ink2)),
  (Para @(Run ('Siete indicadores macroeconómicos de Colombia: inflación, tasa de política monetaria, tasa de cambio (TRM), índice accionario COLCAP, desempleo, tasa de ocupación y crecimiento real del PIB. ' +
    'Fuente: estadísticas del Banco de la República. Periodo: enero de 2008 a julio de 2026, 223 meses y 74 trimestres.') 11))))
Add-Visual 'questions' $L 306 $LW 150 (TextBox @(
  (Para @(Run 'CUATRO PREGUNTAS' 9 $true $C.Ink2)),
  (Para @(Run '1.  ¿La tasa de política sigue a la inflación? ¿Con cuánto rezago?' 12)),
  (Para @(Run '2.  ¿El peso y el COLCAP se mueven juntos?' 12)),
  (Para @(Run '3.  ¿Qué tan fuerte golpeó el COVID al empleo y qué tan rápido se recuperó?' 12)),
  (Para @(Run '4.  ¿Cómo cambiaron las condiciones dentro de cada gobierno?' 12))))
$kpis = @(
  @('Inflation Latest', 'INFLACIÓN (% ANUAL)', $C.Inflation), @('Policy Rate Latest', 'TASA DE POLÍTICA (%)', $C.Policy),
  @('TRM Latest', 'TRM (COP POR USD)', $C.Trm), @('COLCAP Latest', 'COLCAP (PUNTOS)', $C.Colcap))
$kw = ($LW - 12) / 2; $kh = 180
for ($i = 0; $i -lt 4; $i++) {
  $k = $kpis[$i]; $x = $RX + ($i % 2) * ($kw + 12); $y = 84 + [math]::Floor($i / 2) * ($kh + 12)
  Add-Visual "kpi$i" $x $y $kw $kh (Card $k[0] $k[1] 'Julio de 2026')
  Add-Visual "kpi${i}_bar" $x $y $kw 4 (Shape 'rectangle' $k[2])
}
NoteBox 'recommendation' $L 476 $FW 124 'RECOMENDACIÓN AL COMITÉ' @(
  'Renta fija: usar la inflación como señal temprana. La tasa de política sigue más de cerca a la inflación unos seis meses después.',
  'Dólar: decidir la exposición por separado de las acciones. El peso y el COLCAP casi no se mueven juntos.',
  'Acciones: dimensionar las posiciones para resistir choques, no intentar anticiparlos con datos macro. Los meses extremos del COLCAP respondieron a eventos.') 13
Add-Visual 'footer' $L 676 $FW 24 (TextBox @(Para @(Run 'La página 2 muestra cómo se verificaron los datos. La página 3 responde las cuatro preguntas.' 9 $false $C.Ink2)))
Save-Page

# =====================================================================
# 2 Calidad de datos (faltantes: 20, atípicos: 20, estadística descriptiva)
# =====================================================================
New-Page 'quality' '2 Calidad de datos'
Header 2 'Calidad de datos' 'Los datos están completos y los extremos son eventos reales'
# Una sola tabla por variable: faltantes, atípicos y estadística descriptiva.
Add-Visual 'summary' $L 84 $FW 262 (Table @(
  @('DimSeries.Serie', 'Serie'), @('DimSeries.Unidad', 'Unidad'), @('Empty Cells', 'Vacíos'), @('Outliers', 'Atípicos (IQR)'),
  @('Mean', 'Media'), @('Median', 'Mediana'), @('Std Dev', 'Desv. estándar'), @('Minimum', 'Mínimo'), @('Maximum', 'Máximo')) `
  'Resumen por variable, enero de 2008 a julio de 2026: 1 vacío y 50 atípicos' 'DimSeries.Serie')
NoteBox 'missing_note' $L 358 $LW 150 'DATOS FALTANTES: IDENTIFICAR, EXPLICAR, ACTUAR' @(
  'Identificar: 1 de 1561 celdas mensuales está vacía (0.06%), el rendimiento del COLCAP de enero de 2008. El PIB no tiene vacíos.',
  'Causa: un rendimiento necesita el mes anterior, que es previo al índice. Los vacíos más antiguos son fechas de inicio de cada serie.',
  'Acción: no se imputa. Rellenar un valor que no puede existir sería inventar datos.',
  'Impacto: los rendimientos tienen 222 observaciones en lugar de 223 y se excluye la historia anterior a 2008.')
Add-Visual 'returns' $RX 358 $LW 334 (Bars 'clusteredColumnChart' 'DimDate.Date' 'Mes' @('COLCAP Monthly Return') @('Rendimiento mensual') @($C.Colcap) `
  'Atípicos con la regla IQR: rendimiento mensual del COLCAP' '% mensual' -subtitle 'En negro: meses fuera de 1.5 × IQR, cada uno ligado a un evento' -colorMeasure 'Return Color')
NoteBox 'outlier_note' $L 518 $LW 174 'DATOS ATÍPICOS: INVESTIGAR Y DECIDIR' @(
  'Investigar: se concentran en episodios conocidos: la crisis de 2008, la caída por el COVID (COLCAP −27.48%, desempleo 21.97%), la venta masiva por las elecciones de 2022, el pico de inflación de 2022-23 (13.34%) y los máximos históricos de enero de 2026.',
  '¿Errores? Ninguno. Los extremos del mercado y del PIB coinciden con reportes de prensa y del DANE.',
  'Decisión: se conservan los 50. Eliminarlos subestimaría el riesgo y borraría los episodios que son el objeto del análisis.',
  'Impacto: los promedios siguen siendo sensibles a los extremos; por eso la mediana se muestra junto a la media.')
Save-Page

# =====================================================================
# 3 Hallazgos (gráficos e interpretación: 25 puntos)
# =====================================================================
New-Page 'story' '3 Hallazgos'
Header 3 'Hallazgos' 'Las tasas siguen a la inflación; los mercados, a los eventos'
Add-Visual 'slc_term' 1036 26 220 52 (Slicer 'DimDate.Gobierno' 'Gobierno' 'TermSync')
$GW = 610; $GH = 300; $GX2 = $L + $GW + 12; $GY2 = 84 + $GH + 12
Add-Visual 'q1_rates' $L 84 $GW $GH (LineChart @('Inflation YoY', 'Policy Rate') @('Inflación anual', 'Tasa de política') @($C.Inflation, $C.Policy) `
  'P1. La tasa de política sigue a la inflación, con rezago' '% anual' 'Correlación: 0.80 en el mismo mes y 0.88 seis meses después')
Add-Visual 'q2_markets' $GX2 84 $GW $GH (LineChart @('TRM Rebased', 'COLCAP Rebased') @('TRM', 'COLCAP') @($C.Trm, $C.Colcap) `
  'P2. Peso (TRM) y COLCAP casi no se mueven juntos' 'índice, enero de 2008 = 100' 'Correlación de −0.14: dólar y acciones son decisiones separadas')
Add-Visual 'q3_jobs' $L $GY2 $GW $GH (LineChart @('Unemployment Rate') @('Desempleo') @($C.Unemployment) `
  'P3. El COVID disparó el desempleo, que se recuperó para 2023' '% de la fuerza laboral' 'Pico de 21.97% (mayo de 2020); en 2023 volvió cerca del nivel de 2019')
Add-Visual 'q4_terms' $GX2 $GY2 $GW $GH (Bars 'clusteredColumnChart' 'DimDate.Gobierno' 'Gobierno' @('Inflation Start', 'Inflation End') @('Primer mes', 'Último mes') `
  @($C.InflationLight, $C.Inflation) 'P4. Inflación al inicio y al final de cada gobierno' '% anual' `
  -subtitle 'Duque: de 3.10% a 10.21%. Petro: de 10.84% a 6.03%' -labels $true)
Save-Page

# ---------- escritura ----------
$enc = [System.Text.UTF8Encoding]::new($false)
function Write-Json($obj, [string]$path) {
  New-Item -ItemType Directory -Force (Split-Path $path) | Out-Null
  [System.IO.File]::WriteAllText($path, (ConvertTo-Json -InputObject $obj -Depth 100), $enc)
}
Get-ChildItem $PagesDir -Directory | Remove-Item -Recurse -Force
foreach ($p in $pages) {
  $dir = Join-Path $PagesDir $p.name
  Write-Json ([ordered]@{ '$schema' = $PG; name = $p.name; displayName = $p.display; displayOption = 'FitToPage'; height = $H; width = $W }) (Join-Path $dir 'page.json')
  $names = @{}
  foreach ($v in $p.visuals) {
    if ($names.ContainsKey($v.name)) { throw "Nombre de visual duplicado $($v.name) en $($p.name)" }
    $names[$v.name] = 1
    Write-Json $v (Join-Path $dir "visuals\$($v.name)\visual.json")
  }
}
Write-Json ([ordered]@{ '$schema' = $PM; pageOrder = @($pages | ForEach-Object { $_.name }); activePageName = $pages[0].name }) (Join-Path $PagesDir 'pages.json')
"Escritas $($pages.Count) páginas, $(($pages | ForEach-Object { $_.visuals.Count } | Measure-Object -Sum).Sum) visuales."
