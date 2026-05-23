import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output
from sqlalchemy import create_engine
import os

# ── CONFIG — switch here ─────────────────────────────────────
USE_DATABASE = False  # Set True when FS-06 gives PostgreSQL credentials

# ── NHS Colours ──────────────────────────────────────────────
NHS_BLUE   = '#003087'
NHS_GREEN  = '#009639'
NHS_RED    = '#DA291C'
NHS_ORANGE = '#ED8B00'
NHS_DARK   = '#231f20'

# ── Data Source ──────────────────────────────────────────────
if USE_DATABASE:
    engine = create_engine("postgresql://user:password@host:5432/dbname")
    def load_data():
        return pd.read_sql("SELECT * FROM claims", engine)
else:
    def load_data():
        df = pd.read_csv("claim_data.csv")
        df['Date of Service'] = pd.to_datetime(df['Date of Service'])
        df['Month'] = df['Date of Service'].dt.to_period('M')
        df['amount_saved'] = df['Billed Amount'] - df['Paid Amount']
        return df

# ── App ───────────────────────────────────────────────────────
app = Dash(__name__)

app.layout = html.Div([

    dcc.Interval(id='refresh', interval=30*1000, n_intervals=0),

    # Header
    html.Div([
        html.H1("AI Insurance Claim Automation Analytics Dashboard — DS-03 W3",
                style={'margin': '0', 'fontSize': '22px'}),
        html.P(
            f"Data Science & Analytics Squad | Week 3 | {'PostgreSQL' if USE_DATABASE else 'claim_data.csv'} (1,000 records) | Auto-refreshes every 30s",
            style={'margin': '5px 0 0', 'fontSize': '13px', 'opacity': '0.85'}
        ),
    ], style={'background': NHS_BLUE, 'color': 'white',
              'padding': '20px 30px', 'borderRadius': '8px', 'marginBottom': '20px'}),

    # Blocker banner
    html.Div([
        html.Strong("⚠ Active Blockers: ", style={'color': '#e65100'}),
        "KPI 2 (Avg Days to Decision) — waiting on FS-06 for decision_date field.  |  ",
        "KPI 4 (Auto-Decision Rate) — proxy logic in use, waiting on ML-04 auto_decision_flag."
    ], style={'background': '#fff3e0', 'borderLeft': '4px solid #e65100',
              'padding': '12px 16px', 'borderRadius': '4px',
              'marginBottom': '20px', 'fontSize': '13px'}),

    # Last refresh
    html.P(id='last-refresh',
           style={'textAlign': 'right', 'color': '#888',
                  'fontSize': '12px', 'marginBottom': '10px'}),

    # Charts — same 4 as W2
    html.Div(dcc.Graph(id='kpi-cards'),
             style={'background': 'white', 'borderRadius': '8px', 'padding': '10px',
                    'marginBottom': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),

    html.Div(dcc.Graph(id='trend-charts'),
             style={'background': 'white', 'borderRadius': '8px', 'padding': '10px',
                    'marginBottom': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),

    html.Div(dcc.Graph(id='breakdown-charts'),
             style={'background': 'white', 'borderRadius': '8px', 'padding': '10px',
                    'marginBottom': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),

    html.Div(dcc.Graph(id='auto-decision'),
             style={'background': 'white', 'borderRadius': '8px', 'padding': '10px',
                    'marginBottom': '20px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'}),

], style={'fontFamily': 'Arial, sans-serif', 'background': '#f5f7fa',
          'margin': '0', 'padding': '20px'})


# ── Callback — fires every 30s ────────────────────────────────
@app.callback(
    Output('kpi-cards',       'figure'),
    Output('trend-charts',    'figure'),
    Output('breakdown-charts','figure'),
    Output('auto-decision',   'figure'),
    Output('last-refresh',    'children'),
    Input('refresh', 'n_intervals')
)
def update_dashboard(n):
    from datetime import datetime

    # Load data from DB or CSV
    df = load_data()

    FRAUD_INDICATORS = ['Duplicate claim', 'Incorrect billing information']
    df['Month'] = pd.to_datetime(df['Date of Service']).dt.to_period('M')
    df['amount_saved'] = df['Billed Amount'] - df['Paid Amount']

    # KPIs
    KPI = {
        'approval_rate': round((df['Claim Status'] == 'Paid').sum() / len(df) * 100, 1),
        'fraud_rate':    round(df['Reason Code'].isin(FRAUD_INDICATORS).sum() / len(df) * 100, 1),
        'auto_rate':     round(((df['Outcome'] == 'Paid') & (df['Claim Status'] == 'Paid')).sum() / len(df) * 100, 1),
        'total_saved':   int(df['amount_saved'].sum())
    }

    # Monthly aggregation
    monthly = df.groupby('Month').agg(
        total    = ('Claim ID', 'count'),
        approved = ('Claim Status', lambda x: (x == 'Paid').sum()),
        fraud    = ('Reason Code', lambda x: x.isin(FRAUD_INDICATORS).sum()),
        saved    = ('amount_saved', 'sum'),
        auto     = ('Claim ID', lambda x: (
                      (df.loc[x.index, 'Outcome'] == 'Paid') &
                      (df.loc[x.index, 'Claim Status'] == 'Paid')
                    ).sum())
    ).reset_index()
    monthly['approval_rate'] = round(monthly['approved'] / monthly['total'] * 100, 1)
    monthly['fraud_rate']    = round(monthly['fraud']    / monthly['total'] * 100, 1)
    monthly['auto_rate']     = round(monthly['auto']     / monthly['total'] * 100, 1)
    monthly['month_str']     = monthly['Month'].astype(str)
    months = monthly['month_str'].tolist()

    # ── Chart 1 — KPI Cards ──
    fig_cards = make_subplots(
        rows=1, cols=5,
        specs=[[{'type': 'indicator'}] * 5],
        subplot_titles=['Approval Rate', 'Avg Days to Decision',
                        'Fraud Flag Rate', 'Auto-Decision Rate', '£ Saved']
    )
    cards = [
        (KPI['approval_rate'], NHS_GREEN,  False, False, '',  '%'),
        (0,                    NHS_ORANGE, True,  False, '',  ' days'),
        (KPI['fraud_rate'],    NHS_RED,    False, False, '',  '%'),
        (KPI['auto_rate'],     NHS_BLUE,   False, True,  '',  '%'),
        (KPI['total_saved'],   NHS_DARK,   False, False, '£', ''),
    ]
    labels = ['Approval Rate', 'Avg Days to Decision',
              'Fraud Flag Rate', 'Auto-Decision Rate', '£ Saved']
    for i, (val, color, blocked, proxy, prefix, suffix) in enumerate(cards):
        fig_cards.add_trace(go.Indicator(
            mode='number',
            value=None if blocked else val,
            number=dict(prefix=prefix, suffix=suffix,
                        font=dict(size=40, color=color, family='Arial Black')),
            title=dict(
                text=(f'<b>{labels[i]}</b>'
                      + ('<br><span style="font-size:10px;color:#e65100">⚠ Blocked — FS-06</span>' if blocked else '')
                      + ('<br><span style="font-size:10px;color:#f57f17">⚠ Proxy — ML-04</span>' if proxy else '')),
                font=dict(size=13, color='#333', family='Arial')
            ),
            domain=dict(row=0, column=i)
        ), row=1, col=i+1)
    fig_cards.update_layout(
        title=dict(
            text='<b>NHS Claims Analytics Dashboard</b> — KPI Overview<br>'
                 '<sup>AI Insurance Claim Automation | DS-03 W3 | claim_data.csv (1,000 records)</sup>',
            font=dict(size=18, color=NHS_BLUE, family='Arial'), x=0.5, xanchor='center'),
        height=220, paper_bgcolor='white', plot_bgcolor='white',
        margin=dict(t=80, b=10, l=20, r=20))

    # ── Chart 2 — Monthly Trends ──
    fig_trends = make_subplots(rows=1, cols=3,
        subplot_titles=['Approval Rate % — Monthly Trend',
                        'Fraud Flag Rate % — Monthly Trend', '£ Saved — Monthly Trend'],
        horizontal_spacing=0.08)
    fig_trends.add_trace(go.Scatter(
        x=months, y=monthly['approval_rate'], mode='lines+markers+text',
        line=dict(color=NHS_GREEN, width=3),
        marker=dict(size=10, color=NHS_GREEN, symbol='circle'),
        text=[f'{v}%' for v in monthly['approval_rate']],
        textposition='top center', textfont=dict(size=11, color=NHS_GREEN),
        fill='tozeroy', fillcolor='rgba(0,150,57,0.08)'
    ), row=1, col=1)
    fig_trends.add_trace(go.Scatter(
        x=months, y=monthly['fraud_rate'], mode='lines+markers+text',
        line=dict(color=NHS_RED, width=3),
        marker=dict(size=10, color=NHS_RED, symbol='diamond'),
        text=[f'{v}%' for v in monthly['fraud_rate']],
        textposition='top center', textfont=dict(size=11, color=NHS_RED),
        fill='tozeroy', fillcolor='rgba(218,41,28,0.08)'
    ), row=1, col=2)
    fig_trends.add_trace(go.Bar(
        x=months, y=monthly['saved'], marker_color=NHS_BLUE, opacity=0.85,
        text=[f'£{v:,}' for v in monthly['saved']],
        textposition='outside', textfont=dict(size=11, color=NHS_BLUE)
    ), row=1, col=3)
    fig_trends.update_yaxes(title_text='Rate (%)', row=1, col=1, range=[0, 50])
    fig_trends.update_yaxes(title_text='Rate (%)', row=1, col=2, range=[0, 50])
    fig_trends.update_yaxes(title_text='£ Amount', row=1, col=3)
    fig_trends.update_layout(
        title=dict(
            text='<b>Monthly KPI Trends</b> — May to Sep 2024<br>'
                 '<sup>Approval improving ✅ | Fraud declining ✅ | Savings consistent ✅</sup>',
            font=dict(size=16, color=NHS_BLUE, family='Arial'), x=0.5, xanchor='center'),
        height=380, showlegend=False, paper_bgcolor='white', plot_bgcolor='#FAFBFD',
        margin=dict(t=90, b=40, l=60, r=40), font=dict(family='Arial'))

    # ── Chart 3 — Breakdown ──
    fig_breakdown = make_subplots(rows=1, cols=3,
        specs=[[{'type': 'pie'}, {'type': 'pie'}, {'type': 'bar'}]],
        subplot_titles=['Claim Status Distribution', 'Insurance Type Mix', 'Monthly Claim Volume'])
    status_counts = df['Claim Status'].value_counts()
    fig_breakdown.add_trace(go.Pie(
        labels=status_counts.index.tolist(), values=status_counts.values.tolist(),
        hole=0.45, marker=dict(colors=[NHS_GREEN, NHS_RED, NHS_ORANGE]),
        textinfo='label+percent', textfont=dict(size=12, family='Arial'), showlegend=False
    ), row=1, col=1)
    ins_counts = df['Insurance Type'].value_counts()
    fig_breakdown.add_trace(go.Pie(
        labels=ins_counts.index.tolist(), values=ins_counts.values.tolist(),
        hole=0.45, marker=dict(colors=[NHS_BLUE, '#005EB8', '#0072CE', '#41B6E6']),
        textinfo='label+percent', textfont=dict(size=12, family='Arial'), showlegend=False
    ), row=1, col=2)
    fig_breakdown.add_trace(go.Bar(
        x=monthly['month_str'], y=monthly['total'],
        marker_color=NHS_BLUE, opacity=0.85,
        text=monthly['total'], textposition='outside',
        textfont=dict(size=12, color=NHS_BLUE), showlegend=False
    ), row=1, col=3)
    fig_breakdown.update_yaxes(title_text='Number of Claims', row=1, col=3)
    fig_breakdown.update_layout(
        title=dict(
            text='<b>Claims Distribution & Volume</b><br>'
                 '<sup>Status mix | Insurance type | Monthly throughput</sup>',
            font=dict(size=16, color=NHS_BLUE, family='Arial'), x=0.5, xanchor='center'),
        height=380, paper_bgcolor='white', plot_bgcolor='#FAFBFD',
        margin=dict(t=90, b=40, l=40, r=40), font=dict(family='Arial'))

    # ── Chart 4 — Auto Decision Donut ──
    auto_count  = int(((df['Outcome'] == 'Paid') & (df['Claim Status'] == 'Paid')).sum())
    human_count = len(df) - auto_count
    fig_auto = go.Figure(go.Pie(
        labels=['Auto-Decided', 'Human Review Required'],
        values=[auto_count, human_count], hole=0.6,
        marker=dict(colors=[NHS_BLUE, '#E0E8F5']),
        textinfo='label+percent', textfont=dict(size=13, family='Arial'), showlegend=True
    ))
    fig_auto.update_layout(
        title=dict(
            text=f'<b>Auto-Decision Rate — {KPI["auto_rate"]}%</b> (Proxy)<br>'
                 f'<sup>⚠ Using Outcome=Paid AND Status=Paid as proxy. Replace with ML-04 auto_decision_flag when available.</sup>',
            font=dict(size=15, color=NHS_BLUE, family='Arial'), x=0.5, xanchor='center'),
        annotations=[dict(text=f'<b>{KPI["auto_rate"]}%</b><br>Auto',
                         x=0.5, y=0.5, font=dict(size=18, color=NHS_BLUE, family='Arial Black'),
                         showarrow=False)],
        height=350, paper_bgcolor='white', margin=dict(t=100, b=40, l=40, r=40))

    last_refresh = f"Last refreshed: {datetime.now().strftime('%H:%M:%S')} · {'PostgreSQL' if USE_DATABASE else 'CSV mode'} · Auto-refresh every 30s"

    return fig_cards, fig_trends, fig_breakdown, fig_auto, last_refresh


if __name__ == '__main__':
    app.run(debug=True)