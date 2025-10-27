import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="D a t a   V i s u a l i z a t i o n s", layout="centered")

# Custom CSS to center the title

st.markdown(
    """
    <style>
    /* Centered title */
    .centered-title {
        text-align: center;
        color: #0b3d91;
        font-weight: bold;
        font-family: 'Old Standard TT', serif; /* default page font */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Use st.markdown to create an h1 heading with the custom class
st.markdown("<h1 class='centered-title'>Data Visualizations</h1>", unsafe_allow_html=True)
@st.cache_data
def load_data():
    df = pd.read_csv("data/GlobalTemperatures.csv")
    df = df[["Year", "Month", "Monthly_Anomaly"]].dropna()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df["Monthly_Anomaly"] = pd.to_numeric(df["Monthly_Anomaly"], errors="coerce")
    df = df.sort_values(["Year", "Month"])
    return df

df = load_data()
json_data = df.to_dict(orient="records")
json_str = json.dumps(json_data)

amcharts_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.amcharts.com/lib/5/index.js"></script>
<script src="https://cdn.amcharts.com/lib/5/xy.js"></script>
<script src="https://cdn.amcharts.com/lib/5/themes/Animated.js"></script>

<style>
html, body {{
    width: 100%;
    height: 100%;
    margin: 0;
    font-family: 'Old Standard TT', serif; /* default page font */
    color: #033e3e; /* default text color */
}}

.centered-title{{
    font-family: 'UnifrakturCook', serif;  /* NYT-like title font */
}}

.title {{
        font-family: 'Old Standard TT', serif; /* default page font */
        font-size: 36px;
        font-weight: 700;
        text-align: center;
        margin-top: 10px;
        color: #000000;
        transition: color 0.5s ease, text-shadow 0.5s ease;
}}

.subtitle {{
        font-family: 'Old Standard TT', serif; /* readable serif for subtitles */
        font-size: 18px;
        text-align: center;
        color: #1b7f4f;
        margin-bottom: 10px;
}}

    /* amCharts labels font */
.amcharts-label {{
        font-family: 'Old Standard TT', serif !important;
}}

#chartdiv {{
    width: 100%;
    height: 700px;
}}

.stButton>button {{
    background-color: #1b7f4f;
    color: white;
    border-radius: 8px;
}}
</style>
</head>
<body>
<div class="title" id="chartTitle">
  Global Temperature Anomaly in <span id="yearSpan">1850</span>
</div>
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
            min: 1, max: 12, strictMinMax: true,
            title: am5.Label.new(root, {{ text: "Month" }})
        }})
    );

    var yAxis = chart.yAxes.push(
        am5xy.ValueAxis.new(root, {{
            renderer: am5xy.AxisRendererY.new(root, {{}}),
            title: am5.Label.new(root, {{ text: "Temperature Anomaly (°C)" }})
        }})
    );

    const data = {json_str};
    const grouped = {{}};
    data.forEach(d => {{
        if (!grouped[d.Year]) grouped[d.Year] = [];
        grouped[d.Year].push(d);
    }});

    const years = Object.keys(grouped).sort((a,b)=>a-b);

    function colorForValue(v) {{
        const min = -0.5, max = 1.0;
        const t = Math.min(Math.max((v - min)/(max-min),0),1);
        const r = 255;
        const g = Math.round(200*(1 - t*0.9));
        const b = 0;
        return `rgb(${{r}},${{g}},${{b}})`;
    }}

    // --- create all series invisible first ---
    const seriesList = [];
    years.forEach(year => {{
        const avgAnomaly = grouped[year].reduce((a,b)=>a+b.Monthly_Anomaly,0)/grouped[year].length;
        const yearColor = colorForValue(avgAnomaly);

        const series = chart.series.push(
            am5xy.LineSeries.new(root, {{
                name: year,
                xAxis: xAxis,
                yAxis: yAxis,
                valueXField: "Month",
                valueYField: "Monthly_Anomaly",
                stroke: am5.color(yearColor),
                tooltip: am5.Tooltip.new(root, {{
                    labelText: "{{name}}\\nMonth: {{valueX}}\\nAnomaly: {{valueY}}"
                }})
            }})
        );
        series.data.setAll(grouped[year]);
        series.set("visible", false);  // initially hidden
        seriesList.push({{series: series, color: yearColor, year: year}});
    }});

    // --- sequential animation function ---
let idx = 0;

    function animateNext() {{
        if (idx >= seriesList.length) {{
            chart.set("interactivityEnabled", true);
            addFinalPoint(); // draw final point after all years
            return;
        }}

        const current = seriesList[idx];
        const series = current.series;
        const color = current.color;
        const year = current.year;

        const yearSpan = document.getElementById("yearSpan");
        yearSpan.innerText = year;
        yearSpan.style.color = color;
        yearSpan.style.textShadow = "0 0 10px " + color + ",0 0 20px " + color;

        series.set("visible", true);
        series.appear(250); // faster line animation
        idx++;
        setTimeout(animateNext, 75); // faster next year
    }}

function addFinalPoint() {{
    // Separate series for the bullet marker
    var finalSeries = chart.series.push(
        am5xy.LineSeries.new(root, {{
            xAxis: xAxis,
            yAxis: yAxis,
            valueXField: "Month",
            valueYField: "Monthly_Anomaly",
            strokeOpacity: 0 // invisible line
        }})
    );

    finalSeries.data.setAll([
        {{ Month: 9, Monthly_Anomaly: 1.8 }},
        {{ Month: 9, Monthly_Anomaly: 1.8 }} // duplicate for bullet rendering
    ]);

    // Create bullet with circle + label
        finalSeries.bullets.push(function() {{
            var container = am5.Container.new(root, {{
                width: 50,
                height: 50
            }});

            // Circle
            var circle = am5.Circle.new(root, {{
                radius: 10,
                fill: am5.color(0xffcc00), // bright yellow
                stroke: am5.color(0xffffff),
                strokeWidth: 2
            }});
            container.children.push(circle);

            // Label
            var label = am5.Label.new(root, {{
                text: "September 2023",
                centerX: am5.p50,
                centerY: am5.p50,  // position above the circle
                dy: -10,            // fine-tune vertical offset
                fill: am5.color(0x000000),
                fontSize: 14,
                fontWeight: "700"
            }});
            container.children.push(label);

            return am5.Bullet.new(root, {{
                sprite: container
            }});
        }});

        finalSeries.appear(500);
    }}


    animateNext();
    chart.appear(1000, 100);
}});
</script>
</body>
</html>
"""

st.components.v1.html(amcharts_html, height=500, width=700, scrolling=False)

st.markdown(
    "<p style='text-align:center; font-size:10px; color: #555555;'>Data source: Berkeley Earth Land</p>",
    unsafe_allow_html=True
)
