import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

# Title
ax.text(7, 9.5, 'AI-Powered Intelligent Shopping Advisor',
        ha='center', va='center', fontsize=16, fontweight='bold', color='#2c3e50')
ax.text(7, 9.1, 'Multi-Agent System Architecture using LangGraph',
        ha='center', va='center', fontsize=11, color='#7f8c8d')

# Box drawing helper
def draw_box(ax, x, y, w, h, label, sublabel, color, text_color='white'):
    box = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                   boxstyle="round,pad=0.1",
                                   linewidth=2,
                                   edgecolor=color,
                                   facecolor=color)
    ax.add_patch(box)
    ax.text(x, y + 0.15, label, ha='center', va='center',
            fontsize=10, fontweight='bold', color=text_color)
    ax.text(x, y - 0.2, sublabel, ha='center', va='center',
            fontsize=8, color=text_color, alpha=0.9)

# Arrow helper
def draw_arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.15, my, label, fontsize=7.5, color='#555', style='italic')

# ── USER INPUT ──
draw_box(ax, 7, 8.2, 4, 0.7, '👤 User Input',
         'Natural Language Query', '#2980b9')

# ── LANGGRAPH BORDER ──
langgraph_box = mpatches.FancyBboxPatch((1.2, 2.2), 11.6, 5.2,
                                         boxstyle="round,pad=0.15",
                                         linewidth=2.5,
                                         edgecolor='#8e44ad',
                                         facecolor='#f5eef8',
                                         linestyle='--')
ax.add_patch(langgraph_box)
ax.text(7, 7.25, '⚙️  LangGraph Orchestration Engine',
        ha='center', va='center', fontsize=9.5,
        fontweight='bold', color='#8e44ad')

# ── AGENT 1: PREFERENCE ──
draw_box(ax, 7, 6.4, 4.5, 0.75,
         '🧠 Agent 1: Preference Agent',
         'Extracts budget, category & priorities',
         '#27ae60')

# ── AGENT 2: RETRIEVAL ──
draw_box(ax, 7, 5.2, 4.5, 0.75,
         '🔍 Agent 2: Product Retrieval Agent',
         'Filters products from dataset by budget & category',
         '#e67e22')

# ── FALLBACK BOX ──
draw_box(ax, 11.5, 5.2, 2.2, 0.65,
         '⚠️ Fallback',
         'Relax budget +30%',
         '#c0392b')

# ── AGENT 3: COMPARISON ──
draw_box(ax, 7, 4.0, 4.5, 0.75,
         '⚖️  Agent 3: Comparison Agent',
         'Scores & ranks products by user priorities',
         '#2980b9')

# ── AGENT 4: RECOMMENDATION ──
draw_box(ax, 7, 2.8, 4.5, 0.75,
         '💡 Agent 4: Recommendation Agent',
         'Generates top 3 picks with justification via LLM',
         '#8e44ad')

# ── DATA STORE ──
draw_box(ax, 2.2, 5.2, 2.8, 0.65,
         '🗄️  Data Store',
         'products.json (50 products)',
         '#16a085')

# ── OUTPUT ──
draw_box(ax, 7, 1.5, 4.5, 0.7,
         '📋 Final Output',
         'Top 3–5 Recommendations with Reasoning',
         '#2c3e50')

# ── LLM ──
draw_box(ax, 11.5, 3.9, 2.2, 0.65,
         '🤖 LLM',
         'Groq (LLaMA 3.3)',
         '#d35400')

# ── ARROWS ──
draw_arrow(ax, 7, 7.85, 7, 7.35, '')          # user → langgraph
draw_arrow(ax, 7, 7.05, 7, 6.78, '')          # langgraph → agent1
draw_arrow(ax, 7, 6.03, 7, 5.58, 'preferences')  # agent1 → agent2
draw_arrow(ax, 7, 4.83, 7, 4.38, 'candidates')   # agent2 → agent3
draw_arrow(ax, 7, 3.63, 7, 3.18, 'ranked list')  # agent3 → agent4
draw_arrow(ax, 7, 2.43, 7, 1.85, '')          # agent4 → output

# data store → retrieval agent
draw_arrow(ax, 3.6, 5.2, 4.75, 5.2, '')

# fallback arrow
draw_arrow(ax, 9.25, 5.2, 10.4, 5.2, 'if 0 found')

# LLM → recommendation agent
draw_arrow(ax, 10.4, 3.9, 9.25, 3.95, '')

# LLM → preference agent
ax.annotate('', xy=(9.25, 6.4), xytext=(10.4, 4.22),
            arrowprops=dict(arrowstyle='->', color='#d35400',
                           lw=1.5, linestyle='dashed'))

# ── LEGEND ──
legend_items = [
    mpatches.Patch(color='#27ae60', label='Preference Agent'),
    mpatches.Patch(color='#e67e22', label='Retrieval Agent'),
    mpatches.Patch(color='#2980b9', label='Comparison Agent'),
    mpatches.Patch(color='#8e44ad', label='Recommendation Agent'),
    mpatches.Patch(color='#16a085', label='Data Store'),
    mpatches.Patch(color='#d35400', label='LLM (Groq)'),
    mpatches.Patch(color='#c0392b', label='Fallback Logic'),
]
ax.legend(handles=legend_items, loc='lower left',
          fontsize=8, framealpha=0.9, ncol=2)

import os
if not os.path.exists('../ss'):
    os.makedirs('../ss')
plt.tight_layout()
plt.savefig('../ss/architecture_diagram.png', dpi=150, bbox_inches='tight',
            facecolor='#f8f9fa')
print("\n✅ Diagram saved as ../ss/architecture_diagram.png")