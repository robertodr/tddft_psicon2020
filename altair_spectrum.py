from typing import Tuple, Dict

import pandas as pd
import altair as alt

def plot_spectrum(data: Dict,
               *,
               title: str = "",
               x_title: Tuple[str, str] = ("ω", "au"),
               y_title: Tuple[str, str] = ("ε", "L⋅mol⁻¹⋅cm⁻¹"),
               offset: int = 0):
    hover = alt.selection_single(
      fields=["x"],
      nearest=True,
      on="mouseover",
      empty="none",
      clear="mouseout"
    )

    s1 = pd.DataFrame(data["convolution"])
    lines = alt.Chart(s1).mark_line(size=1.5).encode(
       x=alt.X("x", axis=alt.Axis(title=f"{x_title[0]} [{x_title[1]}]", offset=offset)),
       y=alt.Y("y", axis=alt.Axis(title=f"{y_title[0]} [{y_title[1]}]")),
       )

    points = lines.transform_filter(hover).mark_circle()

    tooltips = alt.Chart(s1).mark_rule().encode(
      x='x:Q',
      opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
      tooltip=[alt.Tooltip("x:Q", format=".4f", title=f"{x_title[0]}"), alt.Tooltip("y:Q", format=".1f", title=f"{y_title[0]}")]
      ).add_selection(
        hover
        )

    s2 = pd.DataFrame(data["sticks"])
    sticks = alt.Chart(s2).mark_bar(size=2, opacity=0.2, color="red").encode(
        x="poles:Q",
        y="residues:Q",
        )

    # Put the layers into a chart and bind the data
    plot = alt.layer(
      lines, points, tooltips, sticks,
      ).properties(
        title=title,
        )

    return plot
