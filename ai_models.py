

import io
import base64
from datetime import datetime, timedelta

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt



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


def render_merged_bar_chart(expense_totals, income_totals, title='Expense vs Income by Category'):
    """Render a merged bar chart comparing expenses (red) and income (green)."""
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0f172a')
    _chart_style(fig, ax)

    # Get all unique categories from both
    all_categories = set(list(expense_totals.keys()) + list(income_totals.keys()))
    all_categories = sorted(list(all_categories))

    if all_categories:
        expense_vals = [expense_totals.get(cat, 0) for cat in all_categories]
        income_vals = [income_totals.get(cat, 0) for cat in all_categories]

        x = np.arange(len(all_categories))
        width = 0.35

        bars1 = ax.bar(x - width/2, expense_vals, width, label='Expense', 
                       color='#ef4444', edgecolor='#0f172a', linewidth=1.5, zorder=3)
        bars2 = ax.bar(x + width/2, income_vals, width, label='Income', 
                       color='#22c55e', edgecolor='#0f172a', linewidth=1.5, zorder=3)

        # Add value labels on bars
        for bar, val in zip(bars1, expense_vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(max(expense_vals), max(income_vals) if income_vals else 0)*0.02,
                        f'₹{val:,.0f}', ha='center', va='bottom',
                        color='#e2e8f0', fontsize=8, fontweight='bold')

        for bar, val in zip(bars2, income_vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(max(expense_vals), max(income_vals) if income_vals else 0)*0.02,
                        f'₹{val:,.0f}', ha='center', va='bottom',
                        color='#e2e8f0', fontsize=8, fontweight='bold')

        ax.set_xlabel('Category', fontsize=11)
        ax.set_ylabel('Amount (₹)', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(all_categories, rotation=25, ha='right', fontsize=9)
        ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=10, loc='upper left')
    else:
        ax.text(0.5, 0.5, 'No data yet.', ha='center', va='center',
                fontsize=13, color='#94a3b8', transform=ax.transAxes)
        ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#0f172a', edgecolor='none', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def render_merged_line_chart(expense_totals, income_totals, title='Expense vs Income Trend'):
    """Render a merged line chart comparing expenses (red) and income (blue)."""
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(11, 6), facecolor='#0f172a')
    _chart_style(fig, ax)

    # Get all unique categories from both
    all_categories = set(list(expense_totals.keys()) + list(income_totals.keys()))
    all_categories = sorted(list(all_categories))

    if all_categories:
        expense_vals = [expense_totals.get(cat, 0) for cat in all_categories]
        income_vals = [income_totals.get(cat, 0) for cat in all_categories]

        x = np.arange(len(all_categories))

        # Plot expense line in red
        ax.plot(x, expense_vals, marker='o', color='#dc2626', linewidth=2.5,
                markersize=7, markerfacecolor='#ffffff', markeredgecolor='#dc2626',
                markeredgewidth=2, label='Expense', zorder=3)
        ax.fill_between(x, expense_vals, alpha=0.1, color='#dc2626')

        # Plot income line in blue
        ax.plot(x, income_vals, marker='o', color='#2563eb', linewidth=2.5,
                markersize=7, markerfacecolor='#ffffff', markeredgecolor='#2563eb',
                markeredgewidth=2, label='Income', zorder=3)
        ax.fill_between(x, income_vals, alpha=0.1, color='#2563eb')

        ax.set_xlabel('Category', fontsize=11)
        ax.set_ylabel('Amount (₹)', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(all_categories, rotation=25, ha='right', fontsize=9)
        ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=10, loc='upper left')
    else:
        ax.text(0.5, 0.5, 'No data yet.', ha='center', va='center',
                fontsize=13, color='#94a3b8', transform=ax.transAxes)
        ax.set_axis_off()

    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#0f172a', edgecolor='none', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


#  AI Model 1 : Linear Regression Forecast (numpy.polyfit  –  degree 1)

def _get_daily_spending(user_id, days=60):
    """Fetch daily expense totals directly from spendly.db and return dense day series."""
    from models import Expense
    from sqlalchemy import func

    cutoff = datetime.now() - timedelta(days=days)
    rows = (Expense.query
            .with_entities(
                func.date(Expense.date).label('day'),
                func.sum(Expense.amount).label('daily_total'),
                func.count(Expense.id).label('txn_count'),
            )
            .filter(Expense.user_id == user_id,
                    Expense.type == 'Expense',
                    Expense.date >= cutoff)
            .group_by(func.date(Expense.date))
            .order_by(func.date(Expense.date))
            .all())

    daily = {}
    txn_count = 0
    for day, daily_total, count in rows:
        day_str = str(day)
        daily[day_str] = float(daily_total or 0)
        txn_count += int(count or 0)

    if not daily:
        return [], [], 0

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

    return dates, amounts, txn_count


def generate_forecast(user_id, forecast_days=7):
    """Build forecast from live spendly.db data for the current user."""
    dates, amounts, txn_count = _get_daily_spending(user_id, days=60)

    if len(amounts) < 3:
        return None, (
            f"Auto analysis from spendly.db found only {txn_count} expense transaction(s). "
            "Add more expenses to generate a forecast."
        )

    x = np.arange(len(amounts), dtype=float)
    y = np.array(amounts, dtype=float)

    slope, intercept = np.polyfit(x, y, 1)

    total_len = len(amounts) + forecast_days
    fx = np.arange(total_len, dtype=float)
    fy = slope * fx + intercept

    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#0f172a')
    _chart_style(fig, ax)

    ax.bar(x, y, color='#6366f1', alpha=0.45, width=0.8, label='Daily Spending', zorder=2)
    ax.plot(fx, fy, color='#34d399', linewidth=2.5, linestyle='--',
            label=f'Trend + {forecast_days}-Day Forecast', zorder=3)

    # Shade forecast area
    ax.axvspan(len(amounts) - 0.5, total_len - 0.5, alpha=0.08, color='#34d399')
    ax.axvline(len(amounts) - 0.5, color='#fbbf24', linewidth=1, linestyle=':', alpha=0.7)

    ax.set_title('Auto Spending Forecast (from spendly.db)', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Day', fontsize=11)
    ax.set_ylabel('Amount (Rs)', fontsize=11)
    ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=9)

    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor='#0f172a', edgecolor='none', dpi=120)
    plt.close(fig)
    buf.seek(0)

    direction = 'increasing' if slope > 0 else 'decreasing'
    next_week_est = max(0, sum(fy[-forecast_days:]))
    avg_daily = np.mean(y)
    start_date = dates[0] if dates else 'N/A'
    end_date = dates[-1] if dates else 'N/A'
    insight = (
        "<strong>Auto analysis from spendly.db</strong><br>"
        f"Based on <strong>{txn_count}</strong> expense transaction(s) from "
        f"<strong>{start_date}</strong> to <strong>{end_date}</strong>.<br>"
        f"Daily spending is <strong>{direction}</strong> by ~Rs {abs(slope):.2f}/day.<br>"
        f"Average daily spend: <strong>Rs {avg_daily:,.2f}</strong><br>"
        f"Estimated next {forecast_days} days total: <strong>Rs {next_week_est:,.2f}</strong>"
    )

    return _to_b64(buf.getvalue()), insight


#  AI Model 2 : Z-Score Anomaly Detection

def detect_anomalies(user_id, threshold=2.0):
    """
    AI Model: Z-Score Anomaly Detection (NumPy).
    Returns list of anomaly dicts with date, amount, z_score.
    """
    dates, amounts, _ = _get_daily_spending(user_id, days=60)

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



#  High-level function used by the /charts route

def render_income_vs_expense_pie(expense_totals, income_totals, title='Income vs Expense'):
    """Render one pie chart that compares total income and total expense."""
    total_expense = sum(expense_totals.values()) if expense_totals else 0
    total_income = sum(income_totals.values()) if income_totals else 0

    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(7, 7), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')

    if total_expense > 0 or total_income > 0:
        _, _, autotexts = ax.pie(
            [total_expense, total_income],
            labels=['Expense', 'Income'],
            autopct='%1.1f%%',
            colors=['#ef4444', '#22c55e'],
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


def generate_all_charts(user_id):
    
    exp_totals = get_expense_category_totals(user_id)
    inc_totals = get_income_category_totals(user_id)

    merged_pie_b64 = _to_b64(render_income_vs_expense_pie(exp_totals, inc_totals, 'Income vs Expense'))
    merged_bar_b64 = _to_b64(render_merged_bar_chart(exp_totals, inc_totals, 'Income vs Expense by Category'))
    merged_line_b64 = _to_b64(render_merged_line_chart(exp_totals, inc_totals, 'Income & Expense Comparison'))

    result = {
        # Feed merged charts into both toggle states for consistent behavior.
        'pie_expense_b64': merged_pie_b64,
        'pie_income_b64': merged_pie_b64,
        'bar_expense_b64': merged_bar_b64,
        'bar_income_b64': merged_bar_b64,
        'merged_pie_b64': merged_pie_b64,
        'merged_bar_b64': merged_bar_b64,
        'merged_line_b64': merged_line_b64,
        'forecast_b64': None,
        'forecast_insight': '',
        'anomalies': [],
    }

    forecast_b64, forecast_insight = generate_forecast(user_id)
    result['forecast_b64'] = forecast_b64
    result['forecast_insight'] = forecast_insight
    result['anomalies'] = detect_anomalies(user_id)

    return result

