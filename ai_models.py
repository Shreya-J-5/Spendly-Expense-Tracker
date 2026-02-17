"""
AI Models for Spendly - Expense Tracking & Forecasting
=======================================================
Models used:
  1. Linear Regression (numpy.polyfit)  – forecasts future daily spending
  2. Z-Score Anomaly Detection (numpy)  – flags unusual transactions
  3. Category breakdown helpers         – pie / bar / line chart generation

All chart rendering uses matplotlib with a dark theme that matches the UI.
"""

import io
import base64
from datetime import datetime, timedelta
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ──────────────────────────────────────────────
#  Shared chart styling
# ──────────────────────────────────────────────

def _chart_style(fig, ax):
    """Apply dark theme so charts match the glassmorphic UI."""
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.tick_params(colors='#cbd5e1', labelsize=9)
    ax.xaxis.label.set_color('#cbd5e1')
    ax.yaxis.label.set_color('#cbd5e1')
    ax.title.set_color('#ffffff')
    ax.title.set_fontweight('bold')
    for spine in ax.spines.values():
        spine.set_color('#334155')
    ax.grid(True, color='#1e293b', linewidth=0.5, alpha=0.6)


def _to_b64(buf_bytes):
    """Return base64 string from raw PNG bytes."""
    return base64.b64encode(buf_bytes).decode('utf-8')


# ──────────────────────────────────────────────
#  Category-level charts  (Pie / Bar / Line)
# ──────────────────────────────────────────────

def get_expense_category_totals(user_id):
    """Return dict {category: total} for expenses."""
    from models import Expense
    expenses = Expense.query.filter_by(user_id=user_id, type='Expense').all()
    totals = {}
    for e in expenses:
        totals[e.category] = totals.get(e.category, 0) + e.amount
    return totals


def get_income_category_totals(user_id):
    """Return dict {category: total} for income."""
    from models import Expense
    incomes = Expense.query.filter_by(user_id=user_id, type='Income').all()
    totals = {}
    for e in incomes:
        totals[e.category] = totals.get(e.category, 0) + e.amount
    return totals


# ── Gradient colour palettes ──
_EXPENSE_COLORS = ['#6366f1', '#818cf8', '#a78bfa', '#c084fc', '#e879f9',
                   '#f472b6', '#fb7185', '#f87171', '#fbbf24', '#34d399']
_INCOME_COLORS  = ['#34d399', '#2dd4bf', '#22d3ee', '#38bdf8', '#60a5fa',
                   '#818cf8', '#a78bfa', '#c084fc', '#e879f9', '#f472b6']


def render_pie_chart(category_totals, title='Expenses by Category', colors=None):
    """Render a styled pie chart and return PNG bytes."""
    if colors is None:
        colors = _EXPENSE_COLORS
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(7, 7), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')

    if category_totals:
        n = len(category_totals)
        palette = (colors * ((n // len(colors)) + 1))[:n]
        wedges, labels, autotexts = ax.pie(
            category_totals.values(),
            labels=category_totals.keys(),
            autopct='%1.1f%%',
            colors=palette,
            textprops={'color': '#e2e8f0', 'fontsize': 11},
            wedgeprops={'edgecolor': '#0f172a', 'linewidth': 2},
            pctdistance=0.78,
        )
        for t in autotexts:
            t.set_fontsize(9)
            t.set_color('#0f172a')
            t.set_fontweight('bold')
        ax.set_title(title, color='#ffffff', fontsize=16, fontweight='bold', pad=20)
    else:
        ax.text(0.5, 0.5, 'No data yet.\nAdd transactions from Dashboard.',
                ha='center', va='center', fontsize=13, color='#94a3b8',
                transform=ax.transAxes)
        ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#0f172a', edgecolor='none', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_bar_chart(category_totals, title='Expenses by Category', color='#818cf8'):
    """Render a styled bar chart and return PNG bytes."""
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(9, 5), facecolor='#0f172a')
    _chart_style(fig, ax)

    if category_totals:
        cats = list(category_totals.keys())
        vals = list(category_totals.values())
        bars = ax.bar(cats, vals, color=color, edgecolor='#0f172a',
                      linewidth=1.5, width=0.55, zorder=3)
        # Add value labels on bars
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals)*0.02,
                    f'₹{val:,.0f}', ha='center', va='bottom',
                    color='#e2e8f0', fontsize=9, fontweight='bold')
        ax.set_ylabel('Amount (₹)', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
        plt.xticks(rotation=25, ha='right', fontsize=9)
    else:
        ax.text(0.5, 0.5, 'No data yet.', ha='center', va='center',
                fontsize=13, color='#94a3b8', transform=ax.transAxes)
        ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#0f172a', edgecolor='none', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_line_chart(category_totals, title='Expenses by Category', color='#818cf8'):
    """Render a styled line chart and return PNG bytes."""
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(9, 5), facecolor='#0f172a')
    _chart_style(fig, ax)

    if category_totals:
        cats = list(category_totals.keys())
        vals = list(category_totals.values())
        ax.plot(cats, vals, marker='o', color=color, linewidth=2.5,
                markersize=8, markerfacecolor='#ffffff', markeredgecolor=color,
                markeredgewidth=2, zorder=3)
        ax.fill_between(range(len(cats)), vals, alpha=0.15, color=color)
        ax.set_ylabel('Amount (₹)', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
        plt.xticks(rotation=25, ha='right', fontsize=9)
    else:
        ax.text(0.5, 0.5, 'No data yet.', ha='center', va='center',
                fontsize=13, color='#94a3b8', transform=ax.transAxes)
        ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#0f172a', edgecolor='none', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# ──────────────────────────────────────────────
#  AI Model 1 : Linear Regression Forecast
#               (numpy.polyfit  –  degree 1)
# ──────────────────────────────────────────────

def _get_daily_spending(user_id, days=60):
    """Aggregate daily spending totals for the last *days* days."""
    from models import Expense
    cutoff = datetime.now() - timedelta(days=days)
    expenses = (Expense.query
                .filter(Expense.user_id == user_id,
                        Expense.type == 'Expense',
                        Expense.date >= cutoff)
                .order_by(Expense.date).all())

    daily = defaultdict(float)
    for e in expenses:
        daily[e.date.strftime('%Y-%m-%d')] += e.amount

    if not daily:
        return [], []

    sorted_keys = sorted(daily.keys())
    start = datetime.strptime(sorted_keys[0], '%Y-%m-%d')
    end = datetime.now()

    dates, amounts = [], []
    cur = start
    while cur <= end:
        d = cur.strftime('%Y-%m-%d')
        dates.append(d)
        amounts.append(daily.get(d, 0))
        cur += timedelta(days=1)

    return dates, amounts


def generate_forecast(user_id, forecast_days=7):
    """
    AI Model: Linear Regression via numpy.polyfit (degree 1).
    Returns (chart_b64, insight_text).
    """
    dates, amounts = _get_daily_spending(user_id, days=60)

    if len(amounts) < 3:
        return None, 'Not enough spending data to generate a forecast. Add more expenses!'

    x = np.arange(len(amounts), dtype=float)
    y = np.array(amounts, dtype=float)

    # ── Fit linear model ──
    slope, intercept = np.polyfit(x, y, 1)

    # ── Build forecast line ──
    total_len = len(amounts) + forecast_days
    fx = np.arange(total_len, dtype=float)
    fy = slope * fx + intercept

    # ── Draw chart ──
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#0f172a')
    _chart_style(fig, ax)

    ax.bar(x, y, color='#6366f1', alpha=0.45, width=0.8, label='Daily Spending', zorder=2)
    ax.plot(fx, fy, color='#34d399', linewidth=2.5, linestyle='--',
            label=f'Trend + {forecast_days}-Day Forecast', zorder=3)

    # Shade forecast area
    ax.axvspan(len(amounts) - 0.5, total_len - 0.5, alpha=0.08, color='#34d399')
    ax.axvline(len(amounts) - 0.5, color='#fbbf24', linewidth=1, linestyle=':', alpha=0.7)

    ax.set_title(f'AI Spending Forecast  (Linear Regression)', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Day', fontsize=11)
    ax.set_ylabel('Amount (₹)', fontsize=11)
    ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=9)

    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#0f172a', edgecolor='none', dpi=120)
    plt.close(fig)
    buf.seek(0)

    # ── Insight text ──
    direction = 'increasing 📈' if slope > 0 else 'decreasing 📉'
    next_week_est = max(0, sum(fy[-forecast_days:]))
    avg_daily = np.mean(y)
    insight = (
        f"🤖 <strong>AI Model: Linear Regression (NumPy)</strong><br>"
        f"Your daily spending is <strong>{direction}</strong> by ~₹{abs(slope):.2f}/day.<br>"
        f"Average daily spend: <strong>₹{avg_daily:,.2f}</strong><br>"
        f"Estimated next {forecast_days} days total: <strong>₹{next_week_est:,.2f}</strong>"
    )

    return _to_b64(buf.getvalue()), insight


# ──────────────────────────────────────────────
#  AI Model 2 : Z-Score Anomaly Detection
# ──────────────────────────────────────────────

def detect_anomalies(user_id, threshold=2.0):
    """
    AI Model: Z-Score Anomaly Detection (NumPy).
    Returns list of anomaly dicts with date, amount, z_score.
    """
    dates, amounts = _get_daily_spending(user_id, days=60)

    if len(amounts) < 5:
        return []

    data = np.array(amounts, dtype=float)
    mean = np.mean(data)
    std  = np.std(data)

    if std == 0:
        return []

    anomalies = []
    for i, (date, amt) in enumerate(zip(dates, amounts)):
        z = (amt - mean) / std
        if z > threshold:
            anomalies.append({
                'date': date,
                'amount': round(amt, 2),
                'z_score': round(z, 2),
                'severity': 'High' if z > 3 else 'Medium',
            })

    return anomalies


# ──────────────────────────────────────────────
#  High-level function used by the /charts route
# ──────────────────────────────────────────────

def generate_all_charts(user_id):
    """
    Generate all chart data for the charts page.
    Returns a dict with all base64 images and AI insights.
    """
    exp_totals = get_expense_category_totals(user_id)
    inc_totals = get_income_category_totals(user_id)

    result = {
        # Category charts – expenses
        'pie_expense_b64':  _to_b64(render_pie_chart(exp_totals, 'Expense Breakdown', _EXPENSE_COLORS)),
        'bar_expense_b64':  _to_b64(render_bar_chart(exp_totals, 'Expenses by Category', '#818cf8')),
        'line_expense_b64': _to_b64(render_line_chart(exp_totals, 'Expense Trend by Category', '#818cf8')),

        # Category charts – income
        'pie_income_b64':  _to_b64(render_pie_chart(inc_totals, 'Income Breakdown', _INCOME_COLORS)),
        'bar_income_b64':  _to_b64(render_bar_chart(inc_totals, 'Income by Category', '#34d399')),
        'line_income_b64': _to_b64(render_line_chart(inc_totals, 'Income Trend by Category', '#34d399')),

        # AI Forecast
        'forecast_b64': None,
        'forecast_insight': '',

        # AI Anomaly Detection
        'anomalies': [],
    }

    # Run AI models
    forecast_b64, forecast_insight = generate_forecast(user_id)
    result['forecast_b64'] = forecast_b64
    result['forecast_insight'] = forecast_insight
    result['anomalies'] = detect_anomalies(user_id)

    return result
