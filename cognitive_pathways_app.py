import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np

# Fixes applied:
# - page_icon added (🧠)
# - load_data() wrapped in try/except + st.stop()
# - Font changed from DM Sans to Inter (portfolio-wide consistency)
# - Background changed from #F5F4F0 to #f4f5f7
# - visibility:hidden replaced with display:none !important

st.set_page_config(
    page_title="Cognitive Pathways Explorer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f4f5f7;
    color: #1A1A1A;
}
.stApp { background-color: #f4f5f7; }

/* FIX: use display:none instead of visibility:hidden to avoid layout shift */
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stToolbar"],
#MainMenu, footer { display: none !important; }

.block-container { padding: 2.5rem 3rem 4rem 3rem; max-width: 1300px; }

.hero {
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #D8D5CE;
}
.hero-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
    margin-bottom: 0.4rem;
}
.hero-sub {
    font-size: 0.88rem;
    color: #6b7280;
    font-weight: 400;
    font-style: italic;
}

.metric-row { display: flex; gap: 1rem; margin-bottom: 2rem; }
.metric-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    flex: 1;
    border: 1px solid #e5e7eb;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
    border-radius: 12px 12px 0 0;
}
.metric-card.forward  { --accent: #3D7EFF; }
.metric-card.crossref { --accent: #FF9500; }
.metric-card.loopback { --accent: #FF3B30; }
.metric-card.total    { --accent: #34C759; }

.metric-value {
    font-size: 2.2rem;
    font-weight: 600;
    color: #111827;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9ca3af;
}
.metric-sub {
    font-size: 0.78rem;
    color: #d1d5db;
    margin-top: 0.2rem;
    font-family: 'JetBrains Mono', monospace;
}

.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

.panel {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stSelectbox label { display: none; }
div[data-baseweb="select"] {
    border-radius: 10px !important;
    font-size: 0.85rem;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
}

.pill {
    display: inline-block;
    background: #f3f4f6;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 500;
    color: #6b7280;
    margin-right: 0.4rem;
    letter-spacing: 0.04em;
}
.pill.blue   { background: #eff6ff; color: #2563eb; }
.pill.orange { background: #fff7ed; color: #d97706; }
.pill.red    { background: #fef2f2; color: #dc2626; }
.pill.green  { background: #f0fdf4; color: #16a34a; }

.insight {
    background: #f9fafb;
    border-left: 3px solid #e5e7eb;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #6b7280;
    font-style: italic;
    margin-top: 1rem;
}

.cf-banner {
    background: #111827;
    border-radius: 12px;
    padding: 0.9rem 1.25rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.cf-banner-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    white-space: nowrap;
}
.cf-banner-title {
    font-size: 0.82rem;
    color: #e5e7eb;
    font-weight: 400;
}
.cf-banner-divider {
    width: 1px;
    height: 28px;
    background: #374151;
    flex-shrink: 0;
}
.cf-banner-role {
    font-size: 0.72rem;
    color: #FF9500;
    font-weight: 600;
    letter-spacing: 0.04em;
    white-space: nowrap;
}

.theory-chain {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.2rem 0 1.8rem 0;
    flex-wrap: wrap;
}
.chain-node {
    background: #FFFFFF;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.45rem 0.9rem;
    font-size: 0.75rem;
    color: #4b5563;
    font-weight: 500;
}
.chain-node.active {
    background: #111827;
    border-color: #111827;
    color: #FFFFFF;
}
.chain-arrow { color: #d1d5db; font-size: 0.8rem; }
.chain-sub {
    font-size: 0.65rem;
    color: #9ca3af;
    display: block;
    font-weight: 400;
    margin-top: 0.15rem;
}
</style>
""", unsafe_allow_html=True)

# ── matplotlib theme ───────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':        'sans-serif',
    'axes.spines.top':    False,
    'axes.spines.right':  False,
    'axes.spines.left':   False,
    'axes.grid':          True,
    'grid.color':         '#f3f4f6',
    'grid.linewidth':     0.8,
    'axes.facecolor':     '#FFFFFF',
    'figure.facecolor':   '#FFFFFF',
    'axes.edgecolor':     '#e5e7eb',
    'xtick.color':        '#9ca3af',
    'ytick.color':        '#9ca3af',
    'xtick.labelsize':    8,
    'ytick.labelsize':    8,
    'axes.labelcolor':    '#9ca3af',
    'axes.labelsize':     8.5,
})

COLORS = {
    'forward':         '#3D7EFF',
    'cross_reference': '#FF9500',
    'loopback':        '#FF3B30',
    'hesitation':      '#FF3B30',
    'no_hesitation':   '#34C759',
    'node_default':    '#111827',
    'edge_forward':    '#3D7EFF',
    'edge_loopback':   '#FF3B30',
    'edge_crossref':   '#FF9500',
}

# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_excel("cognitive_pathways_synthetic_data.xlsx")

# FIX: wrap in try/except so missing file doesn't silently crash the app
try:
    df = load_data()
except Exception as e:
    st.error(f"Data loading error: {e}")
    st.stop()

# ── Hero ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-label">HCI Research · Regulated Work Environments</div>
  <div class="hero-title">Cognitive Pathways Explorer</div>
  <div class="hero-sub">Empirical layer for <em>Document Judgment: Cognitive Friction and Responsibility in Procedural Documentation</em></div>
</div>

<div class="cf-banner">
  <div class="cf-banner-label">Companion paper</div>
  <div class="cf-banner-divider"></div>
  <div class="cf-banner-title">Document Judgment: Cognitive Friction and Responsibility in Procedural Documentation</div>
  <div class="cf-banner-divider"></div>
  <div class="cf-banner-role">↑ Theory &amp; framework</div>
</div>

<div class="theory-chain">
  <div class="chain-node">Procedural Structure<span class="chain-sub">SOP / documentation</span></div>
  <div class="chain-arrow">→</div>
  <div class="chain-node active">Cognitive Pathways<span class="chain-sub">this project · empirical</span></div>
  <div class="chain-arrow">→</div>
  <div class="chain-node">Mismatch detected<span class="chain-sub">loopback · hesitation</span></div>
  <div class="chain-arrow">→</div>
  <div class="chain-node">Cognitive Friction<span class="chain-sub">CF paper · theory</span></div>
</div>
""", unsafe_allow_html=True)

# ── Metrics ────────────────────────────────────────────────────────────────
total         = len(df)
forward_n     = (df["action_type"] == "forward").sum()
crossref_n    = (df["action_type"] == "cross_reference").sum()
loopback_n    = (df["action_type"] == "loopback").sum()
hesitation_rate = round(df["hesitation_flag"].mean() * 100, 1)

st.markdown(f"""
<div class="metric-row">
  <div class="metric-card total">
    <div class="metric-value">{total}</div>
    <div class="metric-label">Total Transitions</div>
    <div class="metric-sub">{df['session_id'].nunique()} sessions · {df['user_id'].nunique()} users</div>
  </div>
  <div class="metric-card forward">
    <div class="metric-value">{forward_n}</div>
    <div class="metric-label">Forward</div>
    <div class="metric-sub">{round(forward_n/total*100,1)}% of all transitions</div>
  </div>
  <div class="metric-card crossref">
    <div class="metric-value">{crossref_n}</div>
    <div class="metric-label">Cross-reference</div>
    <div class="metric-sub">{round(crossref_n/total*100,1)}% of all transitions</div>
  </div>
  <div class="metric-card loopback">
    <div class="metric-value">{loopback_n}</div>
    <div class="metric-label">Loopback</div>
    <div class="metric-sub">{hesitation_rate}% hesitation rate</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Filter ─────────────────────────────────────────────────────────────────
col_filter, col_spacer = st.columns([2, 5])
with col_filter:
    session_list = ["All sessions"] + sorted(df["session_id"].unique().tolist())
    selected     = st.selectbox("Session", session_list)

fdf = df.copy() if selected == "All sessions" else df[df["session_id"] == selected].copy()

st.markdown("<div class='section-header'>Behavioural patterns — CF mechanisms</div>", unsafe_allow_html=True)

# ── Row 1: Action distribution + Hesitation by node ───────────────────────
col1, col2 = st.columns(2)

with col1:
    action_counts    = fdf["action_type"].value_counts()
    action_color_map = {
        'forward':         COLORS['forward'],
        'cross_reference': COLORS['cross_reference'],
        'loopback':        COLORS['loopback'],
    }
    bar_colors = [action_color_map.get(a, '#d1d5db') for a in action_counts.index]

    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.barh(
        [a.replace('_', ' ').title() for a in action_counts.index],
        action_counts.values,
        color=bar_colors, height=0.5, edgecolor='none'
    )
    for bar, val in zip(bars, action_counts.values):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2,
                str(val), va='center', ha='left', fontsize=8.5,
                color='#6b7280', fontfamily='monospace')
    ax.set_xlabel("Count")
    ax.set_title("Action Type Distribution", fontsize=9, color='#4b5563', pad=10, loc='left')
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('#e5e7eb')
    ax.set_xlim(0, action_counts.max() * 1.18)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("""
    <div class="insight">
    <strong style="color:#3D7EFF">Forward</strong> = procedural compliance.
    <strong style="color:#FF9500">Cross-reference</strong> = working memory overload — the procedure forces the reader to hold multiple documents simultaneously.
    <strong style="color:#FF3B30">Loopback</strong> = interpretation failure — a signal that procedural language did not resolve the judgment demand.
    These are the three surface signatures of cognitive friction.
    </div>""", unsafe_allow_html=True)

with col2:
    hes_by_node = (
        fdf.groupby("to_node")["hesitation_flag"]
        .agg(['sum', 'count'])
        .assign(rate=lambda x: x['sum'] / x['count'] * 100)
        .sort_values('rate', ascending=True)
    )

    cmap_vals  = hes_by_node['rate'].values
    norm       = plt.Normalize(cmap_vals.min(), cmap_vals.max())
    bar_colors2 = plt.cm.RdYlGn_r(norm(cmap_vals))

    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.barh(
        hes_by_node.index,
        hes_by_node['rate'],
        color=bar_colors2, height=0.5, edgecolor='none'
    )
    for bar, val in zip(bars, hes_by_node['rate']):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2,
                f"{val:.0f}%", va='center', ha='left', fontsize=8,
                color='#6b7280', fontfamily='monospace')
    ax.set_xlabel("Hesitation rate (%)")
    ax.set_title("Hesitation Rate by Node", fontsize=9, color='#4b5563', pad=10, loc='left')
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('#e5e7eb')
    ax.set_xlim(0, hes_by_node['rate'].max() * 1.2)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("""
    <div class="insight">
    Hesitation concentrations are not random — they cluster at nodes where procedural text
    requires active interpretation rather than execution. This is the CF paper's core claim
    made measurable: <em>interpretation cost accumulates where language structure and cognitive
    expectation diverge.</em>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>Network structure — friction topology</div>", unsafe_allow_html=True)

# ── Row 2: Network graph ───────────────────────────────────────────────────
col3, col4 = st.columns([3, 2])

with col3:
    G = nx.DiGraph()
    edge_actions = {}
    for _, row in fdf.iterrows():
        src, dst, act = row["from_node"], row["to_node"], row["action_type"]
        if G.has_edge(src, dst):
            G[src][dst]["weight"] += 1
        else:
            G.add_edge(src, dst, weight=1, action=act)
            edge_actions[(src, dst)] = act

    node_order = [
        'Start', 'Check SOP', 'Review Terminology', 'Interpret Step',
        'Check Prior Record', 'Execute Step', 'Verify Result',
        'Document Entry', 'Final Review', 'End'
    ]
    existing_nodes = list(G.nodes())
    ordered   = [nd for nd in node_order if nd in existing_nodes]
    unordered = [nd for nd in existing_nodes if nd not in ordered]
    all_ordered = ordered + unordered

    pos = {}
    for i, nd in enumerate(all_ordered):
        angle    = 2 * np.pi * i / len(all_ordered)
        pos[nd]  = (np.cos(angle) * 2.2, np.sin(angle) * 1.6)

    edge_colors = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        act = edge_actions.get((u, v), 'forward')
        edge_colors.append(COLORS.get(act, '#d1d5db'))
        edge_widths.append(0.8 + data['weight'] * 0.25)

    node_hesitation = fdf.groupby("to_node")["hesitation_flag"].mean().to_dict()
    node_colors = []
    for nd in G.nodes():
        rate = node_hesitation.get(nd, 0)
        if rate > 0.4:
            node_colors.append('#FF3B30')
        elif rate > 0.2:
            node_colors.append('#FF9500')
        else:
            node_colors.append('#3D7EFF')

    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#f9fafb')

    nx.draw_networkx_edges(G, pos, ax=ax,
        edge_color=edge_colors, width=edge_widths, alpha=0.7,
        arrows=True, arrowsize=12,
        connectionstyle='arc3,rad=0.08',
        min_source_margin=18, min_target_margin=18,
    )
    nx.draw_networkx_nodes(G, pos, ax=ax,
        node_color=node_colors, node_size=1600, alpha=0.92,
    )
    nx.draw_networkx_labels(G, pos, ax=ax,
        font_size=6.5, font_color='white', font_weight='500',
    )

    legend_elements = [
        mpatches.Patch(color=COLORS['forward'],         label='Forward'),
        mpatches.Patch(color=COLORS['cross_reference'], label='Cross-reference'),
        mpatches.Patch(color=COLORS['loopback'],        label='Loopback'),
    ]
    ax.legend(handles=legend_elements, loc='lower left',
              frameon=True, framealpha=0.9,
              fontsize=7.5, facecolor='white', edgecolor='#e5e7eb')
    ax.set_title("Cognitive Pathways Network", fontsize=9.5, color='#4b5563',
                 pad=12, loc='left', fontweight='600')
    ax.axis('off')
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

with col4:
    fig, ax = plt.subplots(figsize=(4.5, 2.5))
    ax.hist(fdf["time_spent_sec"], bins=20,
            color='#3D7EFF', alpha=0.8, edgecolor='none')
    ax.set_xlabel("Time per step (sec)")
    ax.set_title("Time Distribution", fontsize=9, color='#4b5563', pad=8, loc='left')
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('#e5e7eb')
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("<br>", unsafe_allow_html=True)

    total_f = len(fdf)
    hes_n   = fdf["hesitation_flag"].sum()
    int_n   = fdf["interruption_flag"].sum()

    st.markdown(f"""
    <div style="background:#f9fafb; border-radius:12px; padding:1rem;
                border:1px solid #e5e7eb; box-shadow:0 1px 3px rgba(0,0,0,.04);">
      <div class="metric-label" style="margin-bottom:0.8rem;">Cognitive load summary</div>
      <div style="margin-bottom:0.6rem;">
        <span class="pill red">Hesitation</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.9rem;">
          {hes_n} events · {round(hes_n/total_f*100,1)}%
        </span>
      </div>
      <div style="margin-bottom:0.6rem;">
        <span class="pill orange">Interruption</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.9rem;">
          {int_n} events · {round(int_n/total_f*100,1)}%
        </span>
      </div>
      <div>
        <span class="pill">Avg time/step</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.9rem;">
          {round(fdf['time_spent_sec'].mean(),1)}s
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight" style="margin-top:0.8rem;">
    Node colour = hesitation rate.
    <span style="color:#FF3B30">●</span> high &nbsp;
    <span style="color:#FF9500">●</span> mid &nbsp;
    <span style="color:#3D7EFF">●</span> low
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>Research argument</div>", unsafe_allow_html=True)

_crossref  = int(crossref_n)
_loopback  = int(loopback_n)
_hes_rate  = round(df['hesitation_flag'].mean() * 100, 1)

arg_html = (
    '<div style="background:#FFFFFF; border-radius:12px; padding:1.5rem 2rem;'
    ' border:1px solid #e5e7eb; box-shadow:0 1px 3px rgba(0,0,0,.05);">'
    '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:1.5rem;">'

    '<div>'
    '<div class="metric-label" style="margin-bottom:0.6rem; color:#3D7EFF;">Working memory overload</div>'
    '<div style="font-family:\'JetBrains Mono\',monospace; font-size:1.4rem; color:#111827; margin-bottom:0.3rem;">'
    + str(_crossref) +
    '</div>'
    '<div style="font-size:0.8rem; color:#6b7280;">cross-reference transitions — '
    'each one a moment where the procedure forces the reader outside the current document '
    'to resolve a judgment demand.</div>'
    '</div>'

    '<div>'
    '<div class="metric-label" style="margin-bottom:0.6rem; color:#FF3B30;">Interpretation failure</div>'
    '<div style="font-family:\'JetBrains Mono\',monospace; font-size:1.4rem; color:#111827; margin-bottom:0.3rem;">'
    + str(_loopback) +
    '</div>'
    '<div style="font-size:0.8rem; color:#6b7280;">loopback transitions — '
    'each one a return to a prior step after the procedure failed to resolve the cognitive '
    'demand it created. The structure required re-reading, not execution.</div>'
    '</div>'

    '<div>'
    '<div class="metric-label" style="margin-bottom:0.6rem; color:#FF9500;">Friction concentration</div>'
    '<div style="font-family:\'JetBrains Mono\',monospace; font-size:1.4rem; color:#111827; margin-bottom:0.3rem;">'
    + str(_hes_rate) + '%' +
    '</div>'
    '<div style="font-size:0.8rem; color:#6b7280;">of all transitions flagged as hesitation — '
    'not distributed evenly, but concentrated at specific nodes where procedural language '
    'places the highest interpretation burden.</div>'
    '</div>'

    '</div>'
    '<div style="margin-top:1.25rem; padding-top:1.25rem; border-top:1px solid #f3f4f6;'
    ' font-size:0.85rem; color:#6b7280; font-style:italic; line-height:1.6;">'
    'This project operationalizes cognitive friction by reconstructing reasoning pathways '
    'and identifying where procedural structure conflicts with actual cognitive flow. '
    'The network graph makes the CF paper\'s theoretical claim empirically observable: '
    'friction is not a feature of individual users — it is a structural property of how '
    'documentation is written.'
    '</div>'
    '</div>'
)
st.markdown(arg_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>Transition matrix</div>", unsafe_allow_html=True)

tm = pd.crosstab(fdf["from_node"], fdf["to_node"])
st.dataframe(tm, use_container_width=True)

with st.expander("View raw data"):
    st.dataframe(
        fdf.style.apply(
            lambda col: ['background-color: #fef2f2' if v == 1 else '' for v in col]
            if col.name in ['hesitation_flag', 'interruption_flag'] else [''] * len(col),
            axis=0
        ),
        use_container_width=True
    )

st.caption("Synthetic dataset only · Prototype for portfolio demonstration")
