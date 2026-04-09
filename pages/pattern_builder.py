"""
Patterns Builder
================
Actors as rows, timesteps as columns.
First and last columns are t_start / t_end (always present).
Intermediate timestep columns can be added and removed.
A Plotly chart below renders one smooth polyline per actor.

Dependencies:
    pip install streamlit plotly pandas
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np



# ── colour palette (one per actor row) ────────────────────────────────────────
ACTOR_COLORS = [
    "#E63946", "#2A9D8F", "#E9C46A", "#457B9D",
    "#F4A261", "#6A4C93", "#43AA8B", "#F94144",
    "#277DA1", "#90BE6D",
]

COL_ACTOR = "Actor"          # fixed first column name

# ── session-state initialisation ──────────────────────────────────────────────
def init_state():
    if "timesteps" not in st.session_state:
        # list of integer time values; first = t_start, last = t_end
        st.session_state.timesteps = [2025, 2050]

    if "df" not in st.session_state:
        t0, t1 = st.session_state.timesteps[0], st.session_state.timesteps[-1]
        st.session_state.df = pd.DataFrame({
            COL_ACTOR: ["Actor A", "Actor B"],
            str(t0):   [0.0, 5.0],
            str(t1):   [0.0, 5.0],
        })

init_state()

# ── helpers ───────────────────────────────────────────────────────────────────

def timestep_cols():
    """Return column names that represent timesteps (everything except COL_ACTOR)."""
    return [c for c in st.session_state.df.columns if c != COL_ACTOR]


def sync_df_columns():
    """
    Make sure df columns exactly match [COL_ACTOR] + [str(t) for t in timesteps].
    Adds missing columns (empty), drops removed ones.
    """
    df = st.session_state.df
    desired = [str(t) for t in st.session_state.timesteps]
    existing = timestep_cols()

    for col in desired:
        if col not in df.columns:
            df[col] = np.nan

    for col in existing:
        if col not in desired:
            df = df.drop(columns=[col])

    # reorder: actor first, then timesteps in order
    st.session_state.df = df[[COL_ACTOR] + desired]


def update_boundary_timestep(old_val, new_val, position):
    """
    Replace t_start (position=0) or t_end (position=-1) with a new integer value.
    Renames the corresponding df column and updates the timesteps list.
    Intermediate timesteps that would fall outside the new range are removed.
    """
    ts = st.session_state.timesteps
    df = st.session_state.df

    # rename df column
    old_col, new_col = str(old_val), str(new_val)
    if old_col in df.columns and old_col != new_col:
        df = df.rename(columns={old_col: new_col})
        st.session_state.df = df

    # update timesteps list
    if position == 0:
        ts[0] = new_val
        # drop intermediates that are now <= new t_start
        ts[1:-1] = [t for t in ts[1:-1] if t > new_val]
    else:
        ts[-1] = new_val
        # drop intermediates that are now >= new t_end
        ts[1:-1] = [t for t in ts[1:-1] if t < new_val]

    sync_df_columns()


def duplicate_timesteps():
    """Return list of duplicate integer timestep values, if any."""
    seen, dupes = set(), set()
    for t in st.session_state.timesteps:
        (dupes if t in seen else seen).add(t)
    return sorted(dupes)


# def build_figure():
#     """Build the Plotly figure from current df and timesteps."""
#     df         = st.session_state.df
#     timesteps  = st.session_state.timesteps
#     tcols      = timestep_cols()

#     # fine-grained x for smooth interpolated lines
#     if len(timesteps) >= 2:
#         x_fine = np.linspace(timesteps[0], timesteps[-1], 300)
#     else:
#         x_fine = np.array(timesteps)

#     fig = go.Figure()

#     for row_idx, row in df.iterrows():
#         color      = ACTOR_COLORS[row_idx % len(ACTOR_COLORS)]
#         actor_name = row[COL_ACTOR] or f"Actor {row_idx + 1}"

#         # collect defined (x, y) pairs for this actor
#         xs, ys = [], []
#         for col, t in zip(tcols, timesteps):
#             val = row[col]
#             if pd.notna(val):
#                 xs.append(t)
#                 ys.append(float(val))

#         if len(xs) == 0:
#             continue

#         if len(xs) == 1:
#             # single point — just draw a dot
#             fig.add_trace(go.Scatter(
#                 x=xs, y=ys,
#                 mode="markers",
#                 marker=dict(color=color, size=10),
#                 name=actor_name,
#             ))
#             continue

#         # interpolate across all timesteps for smooth line
#         y_interp = np.interp(x_fine, xs, ys)

#         fig.add_trace(go.Scatter(
#             x=x_fine,
#             y=y_interp,
#             mode="lines",
#             line=dict(color=color, width=2.5),
#             name=actor_name,
#             hovertemplate=f"<b>{actor_name}</b><br>t=%{{x:.1f}}<br>value=%{{y:.2f}}<extra></extra>",
#         ))

#         # start and end markers
#         fig.add_trace(go.Scatter(
#             x=[xs[0], xs[-1]],
#             y=[ys[0], ys[-1]],
#             mode="markers",
#             marker=dict(color=color, size=9, line=dict(color="white", width=1.5)),
#             showlegend=False,
#             hoverinfo="skip",
#         ))

#     fig.update_layout(
#         height=420,
#         margin=dict(l=60, r=40, t=30, b=60),
#         plot_bgcolor="#ffffff",
#         paper_bgcolor="#ffffff",
#         font=dict(color="#e0e0e0"),
#         xaxis=dict(
#             title="Time",
#             gridcolor="#2a2a2a",
#             zeroline=False,
#             tickmode="array",
#             tickvals=timesteps,
#         ),
#         yaxis=dict(title="Value", gridcolor="#2a2a2a", zeroline=False),
#         legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#444", borderwidth=1)
#     )
#     return fig


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════
st.title("Patterns Builder")

# ── time horizon inputs ───────────────────────────────────────────────────────
st.subheader("Time horizon")
h_start, h_end, h_spacer = st.columns([2, 2, 6])

with h_start:
    new_t_start = st.number_input(
        "Start year",
        value=st.session_state.timesteps[0],
        step=1,
        format="%d",
    )
    if new_t_start != st.session_state.timesteps[0]:
        if new_t_start < st.session_state.timesteps[-1]:
            update_boundary_timestep(st.session_state.timesteps[0], int(new_t_start), position=0)
            st.rerun()
        else:
            st.error("Start year must be less than end year.")

with h_end:
    new_t_end = st.number_input(
        "End year",
        value=st.session_state.timesteps[-1],
        step=1,
        format="%d",
    )
    if new_t_end != st.session_state.timesteps[-1]:
        if new_t_end > st.session_state.timesteps[0]:
            update_boundary_timestep(st.session_state.timesteps[-1], int(new_t_end), position=-1)
            st.rerun()
        else:
            st.error("End year must be greater than start year.")

st.divider()

# ── timestep toolbar ──────────────────────────────────────────────────────────
col_add_input, col_add_btn, col_remove_input, col_remove_btn, col_spacer = st.columns([2, 1, 2, 1, 4])

ts      = st.session_state.timesteps
t_start = ts[0]
t_end   = ts[-1]
default_new = (t_start + t_end) // 2   # sensible default for the input

with col_add_input:
    new_ts = st.number_input(
        "Add timestep",
        min_value=t_start + 1,
        max_value=t_end - 1,
        value=default_new,
        step=1,
        format="%d",
        key="new_timestep_input",
    )

with col_add_btn:
    st.write("")   # vertical alignment nudge
    st.write("")
    if st.button("＋ Add", use_container_width=True):
        if new_ts in ts:
            st.warning(f"Timestep {new_ts} already exists.")
        else:
            # insert in sorted position (before t_end)
            insert_at = next(i for i, t in enumerate(ts) if t > new_ts)
            ts.insert(insert_at, int(new_ts))
            sync_df_columns()
            st.rerun()

with col_remove_input:
    intermediate = ts[1:-1]
    if intermediate:
        to_remove = st.selectbox(
            "Remove timestep",
            options=intermediate,
            format_func=lambda t: f"{t}",
            label_visibility="visible",
            key="remove_select",
        )
    else:
        st.caption("No intermediate\ntimesteps yet.")
        to_remove = None

with col_remove_btn:
    st.write("")   # vertical alignment nudge
    st.write("")
    if to_remove is not None:
        if st.button("✕ Remove", use_container_width=True):
            ts.remove(to_remove)
            sync_df_columns()
            st.rerun()

# ── duplicate warning ─────────────────────────────────────────────────────────
dupes = duplicate_timesteps()
if dupes:
    st.warning(f"⚠️ Duplicate timestep values: {dupes}. Please make all timestep headers unique.")

# ── data editor ───────────────────────────────────────────────────────────────
tcols     = timestep_cols()
timesteps = st.session_state.timesteps

# build per-column config
column_config = {
    COL_ACTOR: st.column_config.TextColumn(
        "Actor",
        help="Actor name",
        width="medium",
    ),
}
for col, t in zip(tcols, timesteps):
    is_start = (t == timesteps[0])
    is_end   = (t == timesteps[-1])
    label    = f"t = {t} {'🏁' if is_end else '🚩' if is_start else ''}"
    column_config[col] = st.column_config.NumberColumn(
        label,
        help=f"Value at t={t}  (leave empty to interpolate)",
        format="%.2f",
        width="small",
    )

def save_edits():
    st.session_state.df = st.session_state.main_table["edited_rows"]  # wrong approach

# ── CORRECT approach: use a callback to merge edits immediately ───────────────
def apply_table_edits():
    edits = st.session_state.main_table
    df = st.session_state.df.copy()

    for row_idx, changes in edits.get("edited_rows", {}).items():
        for col, val in changes.items():
            df.at[row_idx, col] = val

    for row in edits.get("added_rows", []):
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    for row_idx in sorted(edits.get("deleted_rows", []), reverse=True):
        df = df.drop(index=row_idx).reset_index(drop=True)

    st.session_state.df = df


edited_df = st.data_editor(
    st.session_state.df,
    column_config=column_config,
    num_rows="dynamic",
    use_container_width=True,
    key="main_table",
    hide_index=True,
    on_change=apply_table_edits,   # ← persist immediately on every edit
)
# ── persist edits back to session state ───────────────────────────────────────
# parse column headers as new timestep values if user edited them
# (data_editor doesn't expose header editing natively, so timesteps
#  are managed via the Add/Remove buttons above — headers are display-only)
st.session_state.df = edited_df

# keep actor count in sync (data_editor handles row add/delete natively)
# ensure new rows get NaN for all timestep cols (data_editor does this)

# ── update timesteps from column headers (in case of future extension) ────────
# currently timesteps are authoritative; df columns follow them.


# ── chart ─────────────────────────────────────────────────────────────────────
st.divider()

# ── reference lines state ─────────────────────────────────────────────────────
if "ref_lines" not in st.session_state:
    st.session_state.ref_lines = pd.DataFrame({
        "Label": ["Threshold"],
        "Value": [2.5],
    })

def apply_refline_edits():
    edits = st.session_state.ref_lines_table
    df = st.session_state.ref_lines.copy()

    for row_idx, changes in edits.get("edited_rows", {}).items():
        for col, val in changes.items():
            df.at[row_idx, col] = val

    for row in edits.get("added_rows", []):
        new_row = {"Label": row.get("Label", ""), "Value": row.get("Value", None)}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    for row_idx in sorted(edits.get("deleted_rows", []), reverse=True):
        df = df.drop(index=row_idx).reset_index(drop=True)

    st.session_state.ref_lines = df


def build_figure():
    """Build the Plotly figure from current df and timesteps."""
    df         = st.session_state.df
    timesteps  = st.session_state.timesteps
    tcols      = timestep_cols()
    ref_lines  = st.session_state.ref_lines

    if len(timesteps) >= 2:
        x_fine = np.linspace(timesteps[0], timesteps[-1], 300)
    else:
        x_fine = np.array(timesteps)

    fig = go.Figure()

    for row_idx, row in df.iterrows():
        color      = ACTOR_COLORS[row_idx % len(ACTOR_COLORS)]
        actor_name = row[COL_ACTOR] or f"Actor {row_idx + 1}"

        xs, ys = [], []
        for col, t in zip(tcols, timesteps):
            val = row[col]
            if pd.notna(val):
                xs.append(t)
                ys.append(float(val))

        if len(xs) == 0:
            continue

        if len(xs) == 1:
            fig.add_trace(go.Scatter(
                x=xs, y=ys,
                mode="markers",
                marker=dict(color=color, size=10),
                name=actor_name,
            ))
            continue

        y_interp = np.interp(x_fine, xs, ys)

        fig.add_trace(go.Scatter(
            x=x_fine,
            y=y_interp,
            mode="lines",
            line=dict(color=color, width=2.5),
            name=actor_name,
            hovertemplate=f"<b>{actor_name}</b><br>t=%{{x:.1f}}<br>value=%{{y:.2f}}<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=[xs[0], xs[-1]],
            y=[ys[0], ys[-1]],
            mode="markers",
            marker=dict(color=color, size=9, line=dict(color="white", width=1.5)),
            showlegend=False,
            hoverinfo="skip",
        ))

    # ── reference lines ───────────────────────────────────────────────────────
    for _, ref_row in ref_lines.iterrows():
        label = ref_row["Label"]
        value = ref_row["Value"]
        if pd.isna(value):
            continue
        value = float(value)
        x0, x1 = timesteps[0], timesteps[-1]

        fig.add_shape(
            type="line",
            x0=x0, x1=x1,
            y0=value, y1=value,
            line=dict(color="black", width=1.5, dash="dash"),
        )
        fig.add_annotation(
            x=x1,
            y=value,
            text=f"  {label}",
            showarrow=False,
            xanchor="left",
            font=dict(color="black", size=12),
        )

    fig.update_layout(
        height=420,
        margin=dict(l=60, r=100, t=30, b=60),   # extra right margin for labels
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#e0e0e0"),
        xaxis=dict(
            title="Time",
            gridcolor="#2a2a2a",
            zerolinecolor="#2a2a2a",
            tickmode="array",
            tickvals=timesteps,
        ),
        yaxis=dict(title="Value", gridcolor="#2a2a2a", zerolinecolor="#2a2a2a"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#444", borderwidth=1)
    )
    return fig


st.plotly_chart(build_figure(), use_container_width=True)

# ── reference lines editor ────────────────────────────────────────────────────
st.subheader("Reference lines")
st.caption("Add horizontal dashed lines annotated directly in the chart.")

st.data_editor(
    st.session_state.ref_lines,
    column_config={
        "Label": st.column_config.TextColumn("Label", help="Annotation text shown in the chart", width="medium"),
        "Value": st.column_config.NumberColumn("Value", help="Y-axis value for the horizontal line", format="%.2f", width="small"),
    },
    num_rows="dynamic",
    use_container_width=False,
    key="ref_lines_table",
    hide_index=True,
    on_change=apply_refline_edits,
)