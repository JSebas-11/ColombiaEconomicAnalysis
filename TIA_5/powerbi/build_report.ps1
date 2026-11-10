# Generates the 7 report pages of ColombiaMacro.pbip as PBIR files from DASHBOARD_SPEC.md.
# Run with Power BI Desktop closed:  powershell -ExecutionPolicy Bypass -File TIA_5\powerbi\build_report.ps1
# It replaces every page in ColombiaMacro.Report\definition\pages. Hand edits made in Desktop are lost on rerun.

$ErrorActionPreference = 'Stop'
$Root = Join-Path $PSScriptRoot 'ColombiaMacro.Report\definition'
$PagesDir = Join-Path $Root 'pages'
$VC = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json'
$PG = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'
$PM = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json'

# Non-ASCII characters built from code points, so this file stays ASCII for Windows PowerShell 5.1.
$DOT = [string][char]0x00B7; $NDASH = [string][char]0x2013; $BUL = [string][char]0x2022; $MINUS = [string][char]0x2212

# Palette (spec section 4)
$C = @{ Policy = '#2a78d6'; Inflation = '#eb6834'; Gdp = '#1baf7a'; Occupation = '#e87ba4'; Trm = '#008300'
        Colcap = '#6250d6'; Unemployment = '#e34948'; Ink = '#0b0b0b'; Ink2 = '#52514e'; Box = '#f0efec'; Rule = '#c9c8c2' }
$M = '_Measures'

# ---------- expression helpers ----------
function Lit([string]$v) { [ordered]@{ expr = [ordered]@{ Literal = [ordered]@{ Value = $v } } } }
function LitStr([string]$s) { Lit ("'" + $s.Replace("'", "''") + "'") }
function LitBool([bool]$b) { if ($b) { Lit 'true' } else { Lit 'false' } }
function LitNum($n) { Lit ("{0}D" -f $n) }
function Color([string]$hex) { [ordered]@{ solid = [ordered]@{ color = (LitStr $hex) } } }
function ColorByMeasure([string]$measure) {
  [ordered]@{ solid = [ordered]@{ color = [ordered]@{ expr = (MeasureField $measure) } } }
}
function ColField([string]$table, [string]$col) {
  [ordered]@{ Column = [ordered]@{ Expression = [ordered]@{ SourceRef = [ordered]@{ Entity = $table } }; Property = $col } }
}
function MeasureField([string]$measure) {
  [ordered]@{ Measure = [ordered]@{ Expression = [ordered]@{ SourceRef = [ordered]@{ Entity = $M } }; Property = $measure } }
}
# Projection: 'Table.Column' for a column, plain name for a measure in _Measures. Optional display name.
function Proj([string]$ref, [string]$display = $null, [bool]$active = $false) {
  if ($ref.Contains('.')) {
    $t, $c = $ref.Split('.', 2); $f = ColField $t $c; $qr = $ref; $native = $c
  } else {
    $f = MeasureField $ref; $qr = "$M.$ref"; $native = $ref
  }
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
# Categorical visual-level filter: Table.Column in (values)
function FilterIn([string]$ref, [string[]]$values, [string]$name) {
  $t, $c = $ref.Split('.', 2)
  # Values is a list of single-item lists; ArrayList avoids PowerShell flattening a lone inner array.
  $vals = [System.Collections.ArrayList]::new()
  foreach ($v in $values) {
    $inner = [System.Collections.ArrayList]::new()
    [void]$inner.Add([ordered]@{ Literal = [ordered]@{ Value = "'" + $v + "'" } })
    [void]$vals.Add($inner)
  }
  [ordered]@{
    name = $name; field = (ColField $t $c); type = 'Categorical'
    filter = [ordered]@{
      Version = 2
      From = @([ordered]@{ Name = 'f'; Entity = $t; Type = 0 })
      Where = @([ordered]@{ Condition = [ordered]@{ In = [ordered]@{
        Expressions = @([ordered]@{ Column = [ordered]@{ Expression = [ordered]@{ SourceRef = [ordered]@{ Source = 'f' } }; Property = $c } })
        Values = $vals } } })
    }
    howCreated = 'User'
  }
}
function FilterEqNum([string]$ref, [int]$value, [string]$name) {
  $t, $c = $ref.Split('.', 2)
  [ordered]@{
    name = $name; field = (ColField $t $c); type = 'Advanced'
    filter = [ordered]@{
      Version = 2
      From = @([ordered]@{ Name = 'f'; Entity = $t; Type = 0 })
      Where = @([ordered]@{ Condition = [ordered]@{ Comparison = [ordered]@{
        ComparisonKind = 0
        Left = [ordered]@{ Column = [ordered]@{ Expression = [ordered]@{ SourceRef = [ordered]@{ Source = 'f' } }; Property = $c } }
        Right = [ordered]@{ Literal = [ordered]@{ Value = "${value}L" } } } } })
    }
    howCreated = 'User'
  }
}
function TitleObj([string]$text, [string]$subtitle = $null) {
  $o = [ordered]@{ title = @(Prop @{ show = (LitBool $true); text = (LitStr $text); fontSize = (LitNum 11) }) }
  if ($subtitle) { $o.subTitle = @(Prop @{ show = (LitBool $true); text = (LitStr $subtitle) }) }
  $o
}
function NoTitle { [ordered]@{ title = @(Prop @{ show = (LitBool $false) }) } }

# ---------- page / visual containers ----------
$script:page = $null; $script:z = 0
# Backup mode: pages are hidden in view mode, prefixed "Backup", and headers say BACKUP.
$script:backup = $false
function New-Page([string]$name, [string]$display) {
  if ($script:backup) { $name = "b_$name"; $display = "Backup $display" }
  $script:page = [ordered]@{ name = $name; display = $display; hidden = $script:backup; visuals = [System.Collections.ArrayList]::new() }
  $script:z = 1000
}
function Add-Visual([string]$name, [double]$x, [double]$y, [double]$w, [double]$h, $visual, $filters = $null) {
  $script:z += 100
  $vc = [ordered]@{
    '$schema' = $VC; name = $name
    position = [ordered]@{ x = $x; y = $y; z = $script:z; height = $h; width = $w; tabOrder = $script:z }
    visual = $visual
  }
  if ($filters) { $vc.filterConfig = [ordered]@{ filters = @($filters) } }
  [void]$script:page.visuals.Add($vc)
}

# ---------- visual builders ----------
# Text box. Paragraphs: array of arrays of runs; a run is @{ t = text; s = size; b = bold; c = color; f = font }.
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
  $v = [ordered]@{
    visualType = 'textbox'
    objects = [ordered]@{ general = @(Prop @{ paragraphs = @($paras) }) }
  }
  if ($bg) {
    $v.visualContainerObjects = [ordered]@{ background = @(Prop @{ show = (LitBool $true); color = (Color $bg); transparency = (LitNum 0) }) }
  }
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
function LineChart([string[]]$measures, [string[]]$colors, [string]$title, [string]$axisTitle, [string]$subtitle = $null) {
  $dp = @(for ($i = 0; $i -lt $measures.Count; $i++) {
    Prop @{ fill = (Color $colors[$i]) } ([ordered]@{ metadata = "$M.$($measures[$i])" })
  })
  [ordered]@{
    visualType = 'lineChart'
    query = [ordered]@{
      queryState = [ordered]@{
        Category = (Role @(Proj 'DimDate.Date' -active $true))
        Y = (Role @($measures | ForEach-Object { Proj $_ }))
      }
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
# Column chart. $colorMeasure colors each column by a measure returning a hex code; otherwise one fixed color.
function ColumnChart([string]$categoryRef, [string]$measure, [string]$title, [string]$axisTitle, [string]$color = $null, [string]$colorMeasure = $null, [bool]$labels = $false) {
  $fill = if ($colorMeasure) {
    Prop @{ fill = (ColorByMeasure $colorMeasure) } ([ordered]@{ data = @([ordered]@{ dataViewWildcard = [ordered]@{ matchingOption = 1 } }) })
  } else { Prop @{ fill = (Color $color) } }
  $objs = [ordered]@{
    dataPoint = @($fill)
    legend = @(Prop @{ show = (LitBool $false) })
    valueAxis = @(Prop @{ showAxisTitle = (LitBool $true); titleText = (LitStr $axisTitle) })
    categoryAxis = @(Prop @{ showAxisTitle = (LitBool $false) })
  }
  if ($labels) { $objs.labels = @(Prop @{ show = (LitBool $true) }) }
  [ordered]@{
    visualType = 'clusteredColumnChart'
    query = [ordered]@{
      queryState = [ordered]@{
        Category = (Role @(Proj $categoryRef -active $true))
        Y = (Role @(Proj $measure))
      }
      sortDefinition = (SortBy $categoryRef)
    }
    objects = $objs
    visualContainerObjects = (TitleObj $title)
    drillFilterOtherVisuals = $true
  }
}
# Column or bar chart with one or more measures, each with a fixed color, optional display names and subtitle.
# $type: clusteredColumnChart or clusteredBarChart (horizontal).
function Bars([string]$type, [string]$categoryRef, [string[]]$measures, [string[]]$colors, [string]$title, [string]$axisTitle,
              [string]$subtitle = $null, [string[]]$names = $null, [bool]$labels = $false, [string]$colorMeasure = $null) {
  $dp = if ($colorMeasure) {
    @(Prop @{ fill = (ColorByMeasure $colorMeasure) } ([ordered]@{ data = @([ordered]@{ dataViewWildcard = [ordered]@{ matchingOption = 1 } }) }))
  } else {
    @(for ($i = 0; $i -lt $measures.Count; $i++) {
      Prop @{ fill = (Color $colors[$i]) } ([ordered]@{ metadata = "$M.$($measures[$i])" })
    })
  }
  $projs = @(for ($i = 0; $i -lt $measures.Count; $i++) { if ($names) { Proj $measures[$i] $names[$i] } else { Proj $measures[$i] } })
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
      queryState = [ordered]@{
        Category = (Role @(Proj $categoryRef -active $true))
        Y = (Role $projs)
      }
      sortDefinition = (SortBy $categoryRef)
    }
    objects = $objs
    visualContainerObjects = (TitleObj $title $subtitle)
    drillFilterOtherVisuals = $true
  }
}
# Table. $cols: array of @(ref, displayName).
function Table([object[]]$cols, [string]$title, [string]$sortRef = $null) {
  $q = [ordered]@{ queryState = [ordered]@{ Values = (Role @($cols | ForEach-Object { Proj $_[0] $_[1] })) } }
  if ($sortRef) { $q.sortDefinition = (SortBy $sortRef) }
  [ordered]@{
    visualType = 'tableEx'
    query = $q
    objects = [ordered]@{
      values = @(Prop @{ wordWrap = (LitBool $true); fontSize = (LitNum 9) })
      columnHeaders = @(Prop @{ wordWrap = (LitBool $true); fontSize = (LitNum 9) })
      total = @(Prop @{ totals = (LitBool $false) })
    }
    visualContainerObjects = (TitleObj $title)
    drillFilterOtherVisuals = $true
  }
}
# Card: one measure, optional category label under the value.
function Card([string]$measure, [string]$title, [string]$label = $null, [int]$size = 24, [string]$color = $C.Ink) {
  $vco = if ($title) { TitleObj $title } else { NoTitle }
  [ordered]@{
    visualType = 'card'
    query = [ordered]@{ queryState = [ordered]@{ Values = (Role @(Proj $measure $label)) } }
    objects = [ordered]@{
      labels = @(Prop @{ fontSize = (LitNum $size); color = (Color $color); labelDisplayUnits = (LitNum 1) })
      categoryLabels = @(Prop @{ show = (LitBool ([bool]$label)); fontSize = (LitNum 9) })
    }
    visualContainerObjects = $vco
    drillFilterOtherVisuals = $true
  }
}
function Slicer([string]$ref, [string]$display, [string]$mode, [string]$group) {
  $objs = [ordered]@{ data = @(Prop @{ mode = (LitStr $mode) }) }
  if ($mode -ne 'Between') { $objs.selection = @(Prop @{ selectAllCheckboxEnabled = (LitBool $true); singleSelect = (LitBool $false) }) }
  [ordered]@{
    visualType = 'slicer'
    query = [ordered]@{
      queryState = [ordered]@{ Values = (Role @(Proj $ref $display -active $true)) }
      sortDefinition = (SortBy $ref)
    }
    objects = $objs
    syncGroup = [ordered]@{ groupName = $group; fieldChanges = $true; filterChanges = $true }
    drillFilterOtherVisuals = $true
  }
}

# ---------- shared page furniture ----------
$W = 1280; $H = 720; $L = 24; $CW = 1016; $RX = 1060; $RW = 196
function Header([int]$n, [string]$total, [string]$part, [string]$title) {
  $label = if ($script:backup) { "BACKUP $DOT " + $part.ToUpper() } else { "PART $n $DOT " + $part.ToUpper() }
  $num = if ($script:backup) { "B$n" } else { "0$n / $total" }
  Add-Visual 'hdr_part' $L 10 700 26 (TextBox @(Para @(Run $label 9 $false $C.Ink2)))
  Add-Visual 'hdr_num' ($W - 24 - 120) 10 120 26 (TextBox @(Para @(Run $num 9 $false $C.Ink2) 'right'))
  Add-Visual 'hdr_title' $L 32 960 44 (TextBox @(Para @(Run $title 20 $false $C.Ink 'Segoe UI Semibold')))
}
function Furniture([int]$n, [string]$part, [string]$title) {
  Header $n '07' $part $title
  Add-Visual 'slc_term' $RX 84 $RW 200 (Slicer 'DimDate.TermLabel' 'Presidential term' 'Basic' 'TermSync')
  Add-Visual 'slc_date' $RX 292 $RW 92 (Slicer 'DimDate.Date' 'Months' 'Between' 'DateSync')
}
# Takeaway box with ink accent bar. $label defaults to KEY TAKEAWAY.
function Takeaway([string[]]$lines, [string]$label = 'KEY TAKEAWAY', [double]$y = 590, [double]$h = 110, [double]$x = $L, [double]$w = $CW, [int]$size = 11) {
  $paras = @(Para @(Run $label 9 $true $C.Ink2))
  $paras += @($lines | ForEach-Object { Para @(Run $_ $size) })
  Add-Visual 'takeaway' $x $y $w $h (TextBox $paras $C.Box)
  Add-Visual 'takeaway_bar' $x $y 4 $h (Shape 'rectangle' $C.Ink)
}
function SideNote([string]$name, [string]$label, [string[]]$lines, [double]$y = 396, [double]$h = 304) {
  $paras = @(Para @(Run $label 9 $true $C.Ink2))
  $paras += @($lines | ForEach-Object { Para @(Run $_ 9) })
  Add-Visual $name $RX $y $RW $h (TextBox $paras $C.Box)
  Add-Visual "${name}_bar" $RX $y 4 $h (Shape 'rectangle' $C.Ink)
}
function SectionLabel([string]$name, [double]$x, [double]$y, [double]$w, [string]$text) {
  Add-Visual $name $x $y $w 22 (TextBox @(Para @(Run $text.ToUpper() 9 $true $C.Ink2)))
}
# Grey note box with ink accent bar anywhere on the page. Lines starting with "Label:" get the label in bold.
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
function CoverageMatrix([string]$title = $null) {
  [ordered]@{
    visualType = 'pivotTable'
    query = [ordered]@{ queryState = [ordered]@{
      Rows = (Role @(Proj 'DimSeries.SeriesKey' 'Series' -active $true))
      Columns = (Role @(Proj 'CoverageByYear.Year' 'Year' -active $true))
      Values = (Role @(Proj 'Coverage %' 'Coverage %')) } }
    objects = [ordered]@{
      values = @(
        (Prop @{ fontSize = (LitNum 8) }),
        (Prop @{ backColor = (ColorByMeasure 'Coverage Color'); fontColor = (ColorByMeasure 'Coverage Font Color') } ([ordered]@{ data = @([ordered]@{ dataViewWildcard = [ordered]@{ matchingOption = 1 } }); metadata = "$M.Coverage %" })))
      columnHeaders = @(Prop @{ fontSize = (LitNum 8) })
      rowHeaders = @(Prop @{ fontSize = (LitNum 8) })
      subTotals = @(Prop @{ rowSubtotals = (LitBool $false); columnSubtotals = (LitBool $false) })
    }
    visualContainerObjects = $(if ($title) { TitleObj $title } else { NoTitle })
    drillFilterOtherVisuals = $true
  }
}

$pages = [System.Collections.ArrayList]::new()
function Save-Page { [void]$pages.Add($script:page) }

# =====================================================================
# PRESENTATION PAGES (3): one per presenter
# =====================================================================
$LW = 604; $RXX = 652   # left/right half widths and right half x

# ---------------- 1 Overview ----------------
New-Page 'overview' '1 Overview'
Header 1 '03' 'Overview' 'Inflation leads rates, COLCAP moves on events'
Add-Visual 'context' $L 84 $LW 176 (TextBox @(
  (Para @(Run 'THE DECISION' 9 $true $C.Ink2)),
  (Para @(Run "A Colombian asset manager's investment committee must decide how to adjust exposure to fixed income, Colombian equities and US dollars as the macro cycle turns." 12)),
  (Para @(Run ' ' 6)),
  (Para @(Run 'THE DATA' 9 $true $C.Ink2)),
  (Para @(Run ("Seven Colombian macro indicators: inflation, policy rate, exchange rate (TRM), the COLCAP stock index, unemployment, occupation and real GDP growth. " +
    "Source: Banco de la Rep$([char]0x00FA)blica statistics. Window: January 2008 to July 2026, 223 months and 74 quarters.") 11))))
Add-Visual 'questions' $L 270 $LW 160 (TextBox @(
  (Para @(Run 'FOUR QUESTIONS' 9 $true $C.Ink2)),
  (Para @(Run '1.  Does the policy rate follow inflation, and with what delay?' 12)),
  (Para @(Run '2.  Do the peso and COLCAP move together?' 12)),
  (Para @(Run '3.  How hard did COVID hit jobs, and how fast did they recover?' 12)),
  (Para @(Run '4.  How did conditions change within each presidential term?' 12))))
$kpi4 = @(
  @('Inflation Latest', 'INFLATION (% YoY)', $C.Inflation), @('Policy Rate Latest', 'POLICY RATE (%)', $C.Policy),
  @('TRM Latest', 'TRM (COP PER USD)', $C.Trm), @('COLCAP Latest', 'COLCAP (POINTS)', $C.Colcap))
$kw4 = ($LW - 12) / 2; $kh4 = 166
for ($i = 0; $i -lt 4; $i++) {
  $k = $kpi4[$i]; $x = $RXX + ($i % 2) * ($kw4 + 12); $y = 84 + [math]::Floor($i / 2) * ($kh4 + 12)
  Add-Visual "kpi$i" $x $y $kw4 $kh4 (Card $k[0] $k[1] 'July 2026' 34 $C.Ink)
  Add-Visual "kpi${i}_bar" $x $y $kw4 4 (Shape 'rectangle' $k[2])
}
Takeaway @(
  "$BUL  Fixed income: use inflation as the early signal. The policy rate tracks inflation most closely about six months later.",
  "$BUL  USD: decide it separately from equities. The peso and COLCAP barely move together.",
  "$BUL  Equities: size positions for shocks instead of timing them with macro data. The extreme COLCAP months were event-driven.") 'RECOMMENDATION TO THE COMMITTEE' 450 150 $L 1232 13
Add-Visual 'footer' $L 676 1232 24 (TextBox @(Para @(Run 'Page 2 shows how the data was checked. Page 3 answers the four questions.' 9 $false $C.Ink2)))
Save-Page

# ---------------- 2 Data Quality ----------------
New-Page 'quality' '2 Data Quality'
Header 2 '03' 'Data quality' 'The data is complete, and the extremes are real events'
SectionLabel 'lbl_missing' $L 80 $LW 'Missing data'
Add-Visual 'coverage' $L 102 $LW 186 (CoverageMatrix 'Coverage by year, % of expected periods: every gap is before 2008')
NoteBox 'missing_note' $L 296 $LW 132 'MISSING DATA: IDENTIFY, EXPLAIN, ACT' @(
  'Identify: 1 of 1,561 monthly cells is empty (0.06%), the January 2008 COLCAP return. GDP has none.',
  'Why: a return needs the previous month, which predates the index. Older gaps are series start dates.',
  'Action: no imputation. Filling a value that cannot exist would invent data.',
  'Impact: returns have 222 observations instead of 223, and pre-2008 history is left out.')
SectionLabel 'lbl_stats' $L 438 $LW 'Descriptive statistics'
Add-Visual 'stats' $L 460 $LW 232 (Table @(
  @('DimSeries.SeriesKey', 'Series'), @('DimSeries.Unit', 'Unit'), @('Mean', 'Mean'), @('Median', 'Median'),
  @('Std Dev', 'Std dev'), @('Minimum', 'Min'), @('Maximum', 'Max')) 'Inflation and policy rate means sit above their medians, pulled up by 2022-23' 'DimSeries.SeriesKey')
SectionLabel 'lbl_outliers' $RXX 80 $LW 'Outliers: IQR rule, 1.5 x IQR beyond the quartiles'
Add-Visual 'outlier_bars' $RXX 102 $LW 186 (Bars 'clusteredBarChart' 'DimSeries.SeriesKey' @('Outliers') @($C.Ink) 'Outliers per variable: 50 in total' '' -labels $true)
Add-Visual 'returns' $RXX 296 $LW 190 (Bars 'clusteredColumnChart' 'DimDate.Date' @('COLCAP Monthly Return') @($C.Colcap) 'COLCAP monthly return' '% per month' -subtitle 'Black months fall outside the fences, and each matches a documented event' -colorMeasure 'Return Color')
NoteBox 'outlier_note' $RXX 494 $LW 198 'OUTLIERS: INVESTIGATE AND DECIDE' @(
  ("Investigate: they cluster in known episodes: the 2008 crisis, the COVID crash (COLCAP $($MINUS)27.48%, unemployment 21.97%), the 2022 election sell-off, the 2022-23 inflation peak (13.34%) and record highs in January 2026."),
  'Errors? None found. Market and GDP extremes match press and DANE reports.',
  'Decision: keep all 50. Removing them would understate risk and erase the episodes the analysis is about.',
  'Impact: averages stay sensitive to extremes, so the median is shown next to the mean.')
Save-Page

# ---------------- 3 Macro Story ----------------
New-Page 'story' '3 Macro Story'
Header 3 '03' 'Macro story' 'Rates follow inflation; markets follow events'
Add-Visual 'slc_term' 1036 26 220 52 (Slicer 'DimDate.TermLabel' 'Presidential term' 'Dropdown' 'TermSync')
$GW = 610; $GH = 300; $GX2 = $L + $GW + 12; $GY2 = 84 + $GH + 12
Add-Visual 'q1_rates' $L 84 $GW $GH (LineChart @('Inflation YoY', 'Policy Rate') @($C.Inflation, $C.Policy) 'Q1. Inflation and the policy rate' '% per year' `
  'Correlation 0.80 in the same month and 0.88 six months later: the rate reacts with a delay')
Add-Visual 'q2_markets' $GX2 84 $GW $GH (LineChart @('TRM Rebased', 'COLCAP Rebased') @($C.Trm, $C.Colcap) 'Q2. Peso (TRM) and COLCAP, January 2008 = 100' 'index' `
  "Correlation $($MINUS)0.14: they barely move together, so USD and equity exposure are separate decisions")
Add-Visual 'q3_jobs' $L $GY2 $GW $GH (LineChart @('Unemployment Rate') @($C.Unemployment) 'Q3. Unemployment rate' '% of labor force' `
  'COVID peak of 21.97% in May 2020, back near the 2019 average (10.89%) by 2023 (10.17%)')
Add-Visual 'q4_terms' $GX2 $GY2 $GW $GH (Bars 'clusteredColumnChart' 'DimDate.TermLabel' @('Inflation Start', 'Inflation End') @('#f5b89a', $C.Inflation) `
  'Q4. Inflation in the first and last month of each term' '% YoY' -subtitle ("Duque: 3.10% to 10.21%. Petro: 10.84% to 6.03%. Term averages alone hide this") `
  -names @('First month', 'Last month') -labels $true)
Save-Page

# =====================================================================
# BACKUP PAGES (hidden in view mode): the detailed 7-page build, for Q&A
# =====================================================================
$script:backup = $true

# ================= Page 1: Overview =================
New-Page 'p1_overview' '1 Overview'
Furniture 1 'Overview' 'Inflation leads rates, COLCAP moves on events'
Add-Visual 'decision' $L 80 $CW 64 (TextBox @(
  (Para @(Run 'THE DECISION' 9 $true $C.Ink2)),
  (Para @(Run ("A Colombian asset manager's investment committee must decide how to adjust exposure to fixed income, Colombian equities and USD across the macro cycle. " +
    "Data: Banco de la Rep$([char]0x00FA)blica statistics, January 2008 to July 2026.") 11))))
$kpis = @(
  @('Inflation Latest', 'Inflation Window Avg', 'INFLATION', '% YoY', $C.Inflation),
  @('Policy Rate Latest', 'Policy Rate Window Avg', 'POLICY RATE', '%', $C.Policy),
  @('TRM Latest', 'TRM Window Avg', 'TRM', 'COP per USD', $C.Trm),
  @('Unemployment Latest', 'Unemployment Window Avg', 'UNEMPLOYMENT', '%', $C.Unemployment),
  @('GDP Growth Latest', 'GDP Growth Window Avg', 'REAL GDP GROWTH', '% YoY', $C.Gdp),
  @('COLCAP Latest', 'COLCAP Window Avg', 'COLCAP', 'points', $C.Colcap))
$kw = ($CW - 5 * 12) / 6
for ($i = 0; $i -lt 6; $i++) {
  $k = $kpis[$i]; $x = $L + $i * ($kw + 12)
  Add-Visual "kpi${i}_latest" $x 156 $kw 112 (Card $k[0] ("$($k[2]) ($($k[3]))") 'Latest month in selection' 24 $C.Ink)
  Add-Visual "kpi${i}_avg" $x 270 $kw 64 (Card $k[1] $null "2008$($NDASH)2026 average" 14 $C.Ink2)
  Add-Visual "kpi${i}_bar" $x 156 $kw 4 (Shape 'rectangle' $k[4])
}
Add-Visual 'questions' $L 348 $CW 230 (TextBox @(
  (Para @(Run 'FOUR QUESTIONS FOR THE COMMITTEE' 9 $true $C.Ink2)),
  (Para @(Run "1.  Does the policy rate follow inflation, and with what delay?  (page 4)" 12)),
  (Para @(Run "2.  Do the peso and COLCAP move together, or are they separate decisions?  (page 5)" 12)),
  (Para @(Run "3.  How hard did COVID hit jobs and output, and how fast did they recover?  (page 6)" 12)),
  (Para @(Run "4.  How did conditions differ across presidential terms?  (page 7)" 12)),
  (Para @(Run ' ' 6)),
  (Para @(Run ("Pages 2 and 3 show how the data was checked first: one empty cell in 1,561, and 50 outliers kept because they are real events.") 10 $false $C.Ink2))))
Takeaway @(
  "$BUL  Use inflation as an early signal for the rate cycle and fixed income positioning. The policy rate tracks inflation most closely about six months later.",
  "$BUL  Decide USD exposure separately from COLCAP exposure. The two barely move together.",
  "$BUL  Size equity positions for shocks rather than timing them with macro levels. Extreme COLCAP months are event-driven.") 'RECOMMENDATION'
Save-Page

# ================= Page 2: Data Quality =================
New-Page 'p2_quality' '2 Data Quality'
Furniture 2 'Data quality' 'January 2008 is the first month every series exists'
SectionLabel 'lbl_obs' $L 78 $CW 'Observations in the window: 223 months, 74 quarters'
$series = @(
  @('Inflation YoY', 'Inflation'), @('Policy Rate', 'Policy Rate'), @('TRM', 'TRM'), @('COLCAP', 'COLCAP'),
  @('COLCAP Monthly Return', 'Returns'), @('Unemployment Rate', 'Unemployment'), @('Occupation Rate', 'Occupation'),
  @('Real GDP Growth', 'GDP (quarters)'))
$cw2 = ($CW - 7 * 8) / 8
for ($i = 0; $i -lt 8; $i++) {
  $s = $series[$i]
  Add-Visual "obs$i" ($L + $i * ($cw2 + 8)) 100 $cw2 70 (Card 'Observations' $s[1] $null 20 $C.Ink) (FilterIn 'DimSeries.SeriesKey' @($s[0]) "f_obs$i")
}
SectionLabel 'lbl_cov' $L 178 $CW 'Missing data: coverage by year, % of expected periods'
Add-Visual 'coverage' $L 198 $CW 160 ([ordered]@{
  visualType = 'pivotTable'
  query = [ordered]@{ queryState = [ordered]@{
    Rows = (Role @(Proj 'DimSeries.SeriesKey' 'Series' -active $true))
    Columns = (Role @(Proj 'CoverageByYear.Year' 'Year' -active $true))
    Values = (Role @(Proj 'Coverage %' 'Coverage %')) } }
  objects = [ordered]@{
    values = @(
      (Prop @{ fontSize = (LitNum 8) }),
      (Prop @{ backColor = (ColorByMeasure 'Coverage Color'); fontColor = (ColorByMeasure 'Coverage Font Color') } ([ordered]@{ data = @([ordered]@{ dataViewWildcard = [ordered]@{ matchingOption = 1 } }); metadata = "$M.Coverage %" })))
    columnHeaders = @(Prop @{ fontSize = (LitNum 8) })
    rowHeaders = @(Prop @{ fontSize = (LitNum 8) })
    subTotals = @(Prop @{ rowSubtotals = (LitBool $false); columnSubtotals = (LitBool $false) })
  }
  visualContainerObjects = (NoTitle)
  drillFilterOtherVisuals = $true
})
Add-Visual 'missing' $L 366 560 216 (Table @(
  @('MissingDataSummary.SeriesKey', 'Series'), @('MissingDataSummary.FirstAvailable', 'First available'),
  @('MissingDataSummary.ObservedInWindow', 'Observed'), @('MissingDataSummary.EmptyInWindow', 'Empty'),
  @('MissingDataSummary.PreWindowGap', 'Before 2008'), @('MissingDataSummary.TreatmentInWindow', 'Treatment in window')) 'Missing data and treatment')
Add-Visual 'stats' ($L + 568) 366 ($CW - 568) 216 (Table @(
  @('DimSeries.SeriesKey', 'Series'), @('DimSeries.Unit', 'Unit'), @('Observations', 'Obs'), @('Mean', 'Mean'),
  @('Median', 'Median'), @('Std Dev', 'Std dev'), @('Minimum', 'Min'), @('Maximum', 'Max')) 'Descriptive statistics in the selection' 'DimSeries.SeriesKey')
Takeaway @(
  ("Earlier gaps come from when each series began, not from lost records. Starting in January 2008 leaves 1 of 1,561 monthly cells empty (0.06%), the first COLCAP return, which cannot exist without a prior month. " +
   "Nothing was imputed, because filling it would invent data. The impact is one fewer observation for returns and the loss of pre-2008 history. " +
   "Inflation and the policy rate have means above their medians (4.93% vs 3.97% and 6.11% vs 4.50%), pulled up by the 2022-23 cycle."))
Save-Page

# ================= Page 3: Outliers =================
New-Page 'p3_outliers' '3 Outliers'
Furniture 3 'Outliers' 'Extreme values are real events, with no entry errors found'
Add-Visual 'count_m' 880 30 80 46 (TextBox @((Para @(Run '43' 22 $false $C.Ink 'Segoe UI Semibold') 'center'), (Para @(Run 'MONTHLY' 8 $true $C.Ink2) 'center')))
Add-Visual 'count_q' 960 30 90 46 (TextBox @((Para @(Run '7' 22 $false $C.Ink 'Segoe UI Semibold') 'center'), (Para @(Run 'GDP QUARTERS' 8 $true $C.Ink2) 'center')))
# Event timeline
Add-Visual 'tl_line' ($L + 60) 91 ($CW - 120) 2 (Shape 'rectangle' $C.Rule)
$events = @(
  @('2008', 'Global financial crisis', 'COLCAP fell 18.98% in October.'),
  @('2020', 'COVID crash', 'COLCAP fell 27.48% in March, then rose 14.3% in December.'),
  @("2020$($NDASH)21", 'Labor shock', 'Unemployment peaked at 21.97% in May 2020. GDP fell 16.74% in Q2 2020.'),
  @('2022', 'Election-month sell-off', 'COLCAP fell 17.49% in June.'),
  @("2022$($NDASH)23", 'Inflation episode', '14 months above the upper fence, peaking at 13.34% in March 2023.'),
  @('2026', 'Record highs', 'COLCAP rose 19.67% in January, with 5 months above the fence.'))
$ew = $CW / 6
for ($i = 0; $i -lt 6; $i++) {
  $e = $events[$i]; $cx = $L + $i * $ew + $ew / 2
  Add-Visual "tl_dot$i" ($cx - 6) 86 12 12 (Shape 'oval' $C.Ink)
  Add-Visual "tl_txt$i" ($cx - $ew / 2 + 4) 100 ($ew - 8) 72 (TextBox @(
    (Para @(Run "$($e[0]) $DOT $($e[1])" 9 $true) 'center'),
    (Para @(Run $e[2] 8 $false $C.Ink2) 'center')))
}
Add-Visual 'fences' $L 178 420 196 (Table @(
  @('DimSeries.SeriesKey', 'Series'), @('DimSeries.Q1', 'Q1'), @('DimSeries.Q3', 'Q3'), @('DimSeries.IQR', 'IQR'),
  @('DimSeries.LowerFence', 'Lower fence'), @('DimSeries.UpperFence', 'Upper fence'), @('DimSeries.OutlierCount', 'Outliers')) 'IQR fences (1.5x), full window' 'DimSeries.SeriesKey')
Add-Visual 'outlier_list' $L 382 420 200 (Table @(
  @('FactOutliers.SeriesKey', 'Series'), @('FactOutliers.Period', 'Period'), @('FactOutliers.Value', 'Value'),
  @('FactOutliers.Direction', 'Direction'), @('FactOutliers.Classification', 'Event'), @('FactOutliers.Treatment', 'Treatment')) 'Every flagged observation' 'FactOutliers.Period')
$small = @(
  @('Inflation YoY', 'Inflation YoY (%)'), @('Unemployment Rate', 'Unemployment rate (%)'), @('Occupation Rate', 'Occupation rate (%)'),
  @('COLCAP', 'COLCAP (points)'), @('COLCAP Monthly Return', 'COLCAP monthly return (%)'), @('Real GDP Growth', 'Real GDP growth (% YoY)'))
$sw = (588 - 16) / 3; $sh = (402 - 8) / 2
for ($i = 0; $i -lt 6; $i++) {
  $s = $small[$i]; $col = $i % 3; $row = [math]::Floor($i / 3)
  $chart = ColumnChart 'DimDate.Date' 'Series Value' $s[1] '' -colorMeasure 'Outlier Color'
  $chart.objects.valueAxis = @(Prop @{ showAxisTitle = (LitBool $false) })
  Add-Visual "sm$i" (452 + $col * ($sw + 8)) (178 + $row * ($sh + 8)) $sw $sh $chart (FilterIn 'DimSeries.SeriesKey' @($s[0]) "f_sm$i")
}
SideNote 'treatment' 'TREATMENT DECISION' @(
  '1. Not removed automatically. The IQR rule flags candidates, not errors.',
  '2. Matched to documented events. The market and GDP extremes were cross-checked against press and DANE reports.',
  '3. Kept, because they record real episodes. Removing them would understate volatility and erase what the analysis is about.',
  ' ',
  'Black columns mark outliers.')
Takeaway @(
  ("The IQR rule (1.5x) flags 50 observations that cluster in a few episodes: the 2008 crisis, COVID, the 2022 election and the 2022-23 inflation cycle. " +
   "COLCAP's five level outliers in 2026 are new highs on a rising index, not anomalies. Because they stay in, averages remain sensitive to extremes, so the median is shown beside the mean throughout."))
Save-Page

# ================= Page 4: Inflation and Rates =================
New-Page 'p4_rates' '4 Inflation and Rates'
Furniture 4 'Inflation and rates' 'The policy rate follows inflation by about six months'
Add-Visual 'rates_line' $L 80 $CW 254 (LineChart @('Inflation YoY', 'Policy Rate') @($C.Inflation, $C.Policy) 'Inflation and policy rate' '% per year')
Add-Visual 'real_rate' $L 342 640 240 (ColumnChart 'DimDate.Date' 'Real Policy Rate' 'Real policy rate (policy rate minus inflation)' 'percentage points' -colorMeasure 'Real Rate Color')
Add-Visual 'lag_corr' ($L + 648) 342 ($CW - 648) 240 (Table @(
  @('CorrelationSummary.LagMonths', 'Rate lag (months)'), @('CorrelationSummary.Correlation', 'Correlation'),
  @('CorrelationSummary.PairedObservations', 'Observations')) 'Inflation vs policy rate N months later' 'CorrelationSummary.LagMonths') @(
  (FilterIn 'CorrelationSummary.VariableX' @('Inflation YoY') 'f_x'), (FilterIn 'CorrelationSummary.VariableY' @('Policy Rate') 'f_y'))
Takeaway @(
  ("Correlation rises from 0.80 in the same month to 0.88 six months later. In 2022, inflation averaged 10.15% against a 7.46% policy rate, a negative real rate. " +
   "By 2024 it was 6.63% against 11.33%. This is consistent with a central bank reacting with a delay, but correlation between trending series doesn't prove cause."))
Save-Page

# ================= Page 5: FX and Markets =================
New-Page 'p5_markets' '5 FX and Markets'
Furniture 5 'FX and markets' 'The peso and COLCAP are separate decisions'
Add-Visual 'rebased' $L 80 500 250 (LineChart @('TRM Rebased', 'COLCAP Rebased') @($C.Trm, $C.Colcap) 'TRM and COLCAP, rebased' 'index' 'January 2008 = 100')
Add-Visual 'returns' ($L + 508) 80 ($CW - 508) 250 (ColumnChart 'DimDate.Date' 'COLCAP Monthly Return' 'COLCAP monthly return (black = outside the IQR fences)' '% per month' -colorMeasure 'Return Color')
Add-Visual 'scatter' $L 338 500 244 ([ordered]@{
  visualType = 'scatterChart'
  query = [ordered]@{ queryState = [ordered]@{
    Category = (Role @(Proj 'DimDate.Date' 'Month' -active $true))
    X = (Role @(Proj 'Inflation YoY'))
    Y = (Role @(Proj 'COLCAP Monthly Return')) } }
  objects = [ordered]@{
    dataPoint = @(Prop @{ fill = (Color $C.Colcap) })
    valueAxis = @(Prop @{ showAxisTitle = (LitBool $true); titleText = (LitStr 'COLCAP monthly return (%)') })
    categoryAxis = @(Prop @{ showAxisTitle = (LitBool $true); titleText = (LitStr 'Inflation YoY (%)') })
  }
  visualContainerObjects = (TitleObj 'Monthly return vs inflation, one dot per month')
  drillFilterOtherVisuals = $true
})
Add-Visual 'market_corr' ($L + 508) 338 ($CW - 508) 244 (Table @(
  @('CorrelationSummary.VariableX', 'Variable'), @('CorrelationSummary.VariableY', 'Against'),
  @('CorrelationSummary.Correlation', 'Correlation')) 'Same-month correlations, full window' 'CorrelationSummary.VariableX') @(
  (FilterIn 'CorrelationSummary.VariableY' @('Inflation YoY', 'COLCAP', 'COLCAP Monthly Return') 'f_y'),
  (FilterEqNum 'CorrelationSummary.LagMonths' 0 'f_lag'))
Takeaway @(
  ("TRM moves moderately with inflation (0.58) but barely with COLCAP ($($MINUS)0.14). Monthly returns show almost no same-month correlation with inflation ($($MINUS)0.05) or the policy rate (0.03). " +
   "The five extreme months are tied to events: the 2008 crisis, the COVID crash, the vaccine rally, the sell-off around the 2022 election, and the record highs of January 2026."))
Save-Page

# ================= Page 6: Real Economy =================
New-Page 'p6_real' '6 Real Economy'
Furniture 6 'Real economy' 'COVID hit hard, and unemployment was back near its 2019 level by 2023'
Add-Visual 'unemp' $L 80 500 250 (LineChart @('Unemployment Rate') @($C.Unemployment) 'Unemployment rate' '% of labor force')
Add-Visual 'unemp_note' ($L + 300) 84 190 22 (TextBox @(Para @(Run 'Peak 21.97%, May 2020' 9 $true $C.Unemployment) 'right'))
Add-Visual 'occup' ($L + 508) 80 ($CW - 508) 250 (LineChart @('Occupation Rate') @($C.Occupation) 'Occupation rate' '% of working-age population')
Add-Visual 'occup_note' ($L + 508 + 300) 84 200 22 (TextBox @(Para @(Run 'Trough 42.50%, April 2020' 9 $true $C.Ink) 'right'))
Add-Visual 'gdp' $L 338 $CW 244 (ColumnChart 'FactQuarterly.QuarterLabel' 'GDP Growth' 'Real GDP growth by quarter (year over year, never interpolated)' '% YoY' -color $C.Gdp)
Add-Visual 'gdp_note' ($L + $CW - 330) 342 320 22 (TextBox @(Para @(Run "Q2 2020: $($MINUS)16.74%  $DOT  Q2 2021: +18.27%" 9 $true $C.Ink) 'right'))
Takeaway @(
  ("Unemployment averaged 10.89% in 2019, 16.67% in 2020 and 10.17% in 2023, peaking at 21.97% in May 2020. Occupation fell to 42.50% in April 2020. " +
   "GDP growth is year-over-year: $($MINUS)16.74% in Q2 2020, then +18.27% in Q2 2021, a rebound measured against a collapsed base."))
Save-Page

# ================= Page 7: Presidential Terms =================
New-Page 'p7_terms' '7 Presidential Terms'
Furniture 7 'Presidential terms' 'Macro conditions by term, shaped by more than the president'
Add-Visual 'term_table' $L 80 $CW 200 (Table @(
  @('DimDate.TermLabel', 'Term'), @('Inflation YoY', 'Inflation Avg'), @('Inflation Start', 'Inflation Start'), @('Inflation End', 'Inflation End'),
  @('Policy Rate', 'Policy Rate Avg'), @('TRM Change %', 'TRM Change'), @('COLCAP Change %', 'COLCAP Change'),
  @('Unemployment Rate', 'Unemployment Avg'), @('GDP Growth', 'GDP Growth Avg')) 'Term comparison: averages, plus start and end values' 'DimDate.TermLabel')
Add-Visual 'term_trm' $L 288 500 294 (ColumnChart 'DimDate.TermLabel' 'TRM Change %' 'TRM change over the term (+ = weaker peso)' '% change' -color $C.Trm -labels $true)
Add-Visual 'term_colcap' ($L + 508) 288 ($CW - 508) 294 (ColumnChart 'DimDate.TermLabel' 'COLCAP Change %' 'COLCAP change over the term' '% change' -color $C.Colcap -labels $true)
SideNote 'footer' 'HOW TO READ THIS PAGE' @(
  'Terms describe when conditions occurred, not who caused them.',
  ('Banco de la Rep' + [char]0x00FA + 'blica sets the policy rate independently, and global shocks fall inside several terms.'),
  'Uribe II covers January 2008 to July 2010 only.',
  'Months are assigned to the incoming president from August.')
Takeaway @(
  ("Averages hide direction. Inflation averaged a mild 4.01% under Duque but rose from 3.10% to 10.21%, then averaged 7.97% under Petro while falling from 10.84% to 6.03%. " +
   "Unemployment was highest under Duque (13.07%), mostly due to COVID. The peso weakened most in Santos II (+52.0% TRM), during the oil price collapse."))
Save-Page

# ---------- write files ----------
$enc = [System.Text.UTF8Encoding]::new($false)
function Write-Json($obj, [string]$path) {
  New-Item -ItemType Directory -Force (Split-Path $path) | Out-Null
  [System.IO.File]::WriteAllText($path, (ConvertTo-Json -InputObject $obj -Depth 100), $enc)
}
Get-ChildItem $PagesDir -Directory | Remove-Item -Recurse -Force
foreach ($p in $pages) {
  $dir = Join-Path $PagesDir $p.name
  $pj = [ordered]@{ '$schema' = $PG; name = $p.name; displayName = $p.display; displayOption = 'FitToPage'; height = $H; width = $W }
  if ($p.hidden) { $pj.visibility = 'HiddenInViewMode' }
  Write-Json $pj (Join-Path $dir 'page.json')
  $names = @{}
  foreach ($v in $p.visuals) {
    if ($names.ContainsKey($v.name)) { throw "Duplicate visual name $($v.name) on $($p.name)" }
    $names[$v.name] = 1
    Write-Json $v (Join-Path $dir "visuals\$($v.name)\visual.json")
  }
}
Write-Json ([ordered]@{ '$schema' = $PM; pageOrder = @($pages | ForEach-Object { $_.name }); activePageName = $pages[0].name }) (Join-Path $PagesDir 'pages.json')
"Wrote $($pages.Count) pages, $(($pages | ForEach-Object { $_.visuals.Count } | Measure-Object -Sum).Sum) visuals."
