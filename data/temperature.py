import pandas as pd
import json
import webbrowser

# === Step 1: Load & clean data ===
df = pd.read_csv("data/GlobalTemperatures.csv")

# Ensure numeric and sorted properly
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
df["Monthly_Anomaly"] = pd.to_numeric(df["Monthly_Anomaly"], errors="coerce")
df = df.dropna(subset=["Year", "Month", "Monthly_Anomaly"])
df = df.sort_values(["Year", "Month"])

# === Step 2: Convert to JSON ===
json_data = df[["Year", "Month", "Monthly_Anomaly"]].to_dict(orient="records")
json_str = json.dumps(json_data)

# === Step 3: Create HTML ===
html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://cdn.amcharts.com/lib/5/index.js"></script>
  <script src="https://cdn.amcharts.com/lib/5/xy.js"></script>
  <script src="https://cdn.amcharts.com/lib/5/themes/Animated.js"></script>
  <title>Global Temperature Anomalies Animation</title>
  <style>
    html, body {{ width: 100%; height: 100%; margin: 0; background: #fefefe; }}
    #chartdiv {{ width: 100%; height: 100%; }}
  </style>
</head>
<body>
  <div id="chartdiv"></div>
  <script>
  am5.ready(function() {{
    var root = am5.Root.new("chartdiv");
    root.setThemes([am5themes_Animated.new(root)]);

    var chart = root.container.children.push(
      am5xy.XYChart.new(root, {{
        panX: true,
        panY: false,
        wheelX: "panX",
        wheelY: "zoomX",
        layout: root.verticalLayout
      }})
    );

    var xAxis = chart.xAxes.push(
      am5xy.ValueAxis.new(root, {{
        renderer: am5xy.AxisRendererX.new(root, {{}}),
        min: 1,
        max: 12,
        strictMinMax: true,
        title: am5.Label.new(root, {{ text: "Month" }})
      }})
    );

    var yAxis = chart.yAxes.push(
      am5xy.ValueAxis.new(root, {{
        renderer: am5xy.AxisRendererY.new(root, {{}}),
        title: am5.Label.new(root, {{ text: "Temperature Anomaly (°C)" }})
      }})
    );

    // --- Injected Data ---
    const data = {json_str};

    // Group by year
    const grouped = {{}};
    data.forEach(d => {{
      if (!grouped[d.Year]) grouped[d.Year] = [];
      grouped[d.Year].push(d);
    }});

    // Color scale (yellow → orange → red)
    function colorForValue(v) {{
      const scale = Math.min(Math.max((v + 0.5) / 1.5, 0), 1);
      const r = Math.round(255 * scale);
      const g = Math.round(255 * (1 - scale) * 0.8);
      return `rgb(${{r}},${{g}},0)`;
    }}

    // Add line series per year with animation
    const years = Object.keys(grouped).sort((a,b)=>a-b);
    let delay = 0;
    years.forEach(year => {{
      const series = chart.series.push(
        am5xy.LineSeries.new(root, {{
          name: year,
          xAxis: xAxis,
          yAxis: yAxis,
          valueXField: "Month",
          valueYField: "Monthly_Anomaly",
          stroke: am5.color(colorForValue(grouped[year][0].Monthly_Anomaly)),
          tooltip: am5.Tooltip.new(root, {{
            labelText: "{{name}}\\nMonth: {{valueX}}\\nAnomaly: {{valueY}}"
          }})
        }})
      );

      series.data.setAll(grouped[year]);
      series.appear(1200, delay);
      delay += 250; // 0.25s delay between each year's draw
    }});

    chart.appear(1000, 100);
  }});
  </script>
</body>
</html>
"""

# === Step 4: Write to file ===
output_path = "temperature_anomalies_amcharts.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# === Step 5: Open in browser ===
webbrowser.open(output_path)
print(f"✅ Visualization saved and opened: {output_path}")
