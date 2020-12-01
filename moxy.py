import psi4

from psi4.driver.procrouting.response.scf_response import tdscf_excitations
from psi4.driver.p4util import spectrum

psi4.core.set_output_file("moxy.out")

# structure from Pederson et al., CPL, submitted
moxy = psi4.geometry("""0 1
C  0.152133 -0.035800  0.485797
C -1.039475  0.615938 -0.061249
C  1.507144  0.097806 -0.148460
O -0.828215 -0.788248 -0.239431
H  0.153725 -0.249258  1.552136
H -1.863178  0.881921  0.593333
H -0.949807  1.214210 -0.962771
H  2.076806 -0.826189 -0.036671
H  2.074465  0.901788  0.325106
H  1.414895  0.315852 -1.212218
""", name="(S)-methyloxirane")

psi4.set_options({
    'save_jk': True,
})

method = 'HF'
basis = 'cc-pVDZ'
e, wfn = psi4.energy(f"{method}/{basis}", return_wfn=True, molecule=moxy)
res = tdscf_excitations(wfn, states=8, triplets="also")

from typing import Tuple, Dict

import numpy as np
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

# get poles and residues to plot OPA and ECD spectra
poles = [r["EXCITATION ENERGY"] for r in res]
opa_residues = [np.linalg.norm(r["ELECTRIC DIPOLE TRANSITION MOMENT (LEN)"])**2 for r in res]
ecd_residues = [r["ROTATORY STRENGTH (LEN)"] for r in res]

opa_spectrum = spectrum(poles=poles, residues=opa_residues, gamma=0.01, out_units="nm")
opa_plot = plot_spectrum(opa_spectrum,
                         title="OPA (Gaussian broadening)",
                         x_title=("λ", "nm"))

ecd_spectrum = spectrum(poles=poles, residues=ecd_residues, kind="ECD", gamma=0.01, out_units="nm")
ecd_plot = plot_spectrum(ecd_spectrum,
                         title="ECD (Gaussian broadening)",
                         x_title=("λ", "nm"),
                         y_title=("Δε", "L⋅mol⁻¹⋅cm⁻¹"))

(opa_plot & ecd_plot).save("moxy.html")
