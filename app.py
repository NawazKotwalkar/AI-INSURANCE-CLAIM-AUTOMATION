import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, dash_table
from sqlalchemy import create_engine
import os

# ── CONFIG ────────────────────────────────────────────────────
USE_DATABASE = False  # Set True when FS-06 provides PostgreSQL credentials

# ── Design Tokens — Figma matched ────────────────────────────
PRIMARY    = '#1a3a6b'
BLUE       = '#2563eb'
GREEN      = '#16a34a'
GREEN_BG   = '#dcfce7'
RED        = '#dc2626'
RED_BG     = '#fee2e2'
ORANGE     = '#f59e0b'
ORANGE_BG  = '#fef3c7'
DARK       = '#1e293b'
WHITE      = '#ffffff'
BG         = '#f1f5f9'
BORDER     = '#e2e8f0'
TEXT_SUB   = '#64748b'

FRAUD_CODES = ['Duplicate claim', 'Incorrect billing information']

# ── Data Source ───────────────────────────────────────────────
if USE_DATABASE:
    engine = create_engine("postgresql://user:password@host:5432/dbname")
    def load_data():
        return pd.read_sql("SELECT * FROM claims", engine)
else:
    def load_data():
        for fname in ['claim_data_w4.csv', 'claim_data.csv', 'claims_demo.csv']:
            if os.path.exists(fname):
                df = pd.read_csv(fname)
                print(f"[data] Loaded {fname} — {len(df)} records")
                break
        else:
            raise FileNotFoundError("No dataset found. Place claim_data.csv in the same folder.")

        date_col = 'Date of Service' if 'Date of Service' in df.columns else 'Date'
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col])
            df['_date'] = df[date_col]
        else:
            df['_date'] = pd.NaT

        if 'Billed Amount' in df.columns and 'Paid Amount' in df.columns:
            df['amount_saved'] = df['Billed Amount'] - df['Paid Amount']
        elif 'Amount' in df.columns:
            df['amount_saved'] = 0
            df['Billed Amount'] = df['Amount']
            df['Paid Amount']   = df['Amount']

        if 'Claim Status' not in df.columns and 'Status' in df.columns:
            df['Claim Status'] = df['Status']
        if 'Claim ID' not in df.columns and 'Claim_ID' in df.columns:
            df['Claim ID'] = df['Claim_ID']

        return df


# ── Smart Column Detection ────────────────────────────────────
def detect_columns(df):
    return {
        'has_trust':         'Trust' in df.columns,
        'has_decision_date': 'decision_date' in df.columns,
        'has_fraud_score':   'fraud_score' in df.columns,
        'has_auto_flag':     'auto_decision_flag' in df.columns,
        'has_reason_code':   'Reason Code' in df.columns,
        'has_insurance':     'Insurance Type' in df.columns,
        'has_outcome':       'Outcome' in df.columns,
        'has_ar_status':     'AR Status' in df.columns,
    }


# ── Load once for filter options ──────────────────────────────
_df   = load_data()
_cols = detect_columns(_df)

MIN_DATE = _df['_date'].min().date() if not _df['_date'].isna().all() else None
MAX_DATE = _df['_date'].max().date() if not _df['_date'].isna().all() else None

TRUST_OPTIONS = (
    [{'label': 'All Trusts', 'value': 'all'}] +
    [{'label': t, 'value': t} for t in sorted(_df['Trust'].unique())]
) if _cols['has_trust'] else [{'label': 'Trust not available', 'value': 'all'}]

TYPE_OPTIONS = (
    [{'label': 'All Types', 'value': 'all'}] +
    [{'label': t, 'value': t} for t in sorted(_df['Insurance Type'].unique())]
) if _cols['has_insurance'] else [{'label': 'Insurance Type not available', 'value': 'all'}]


# ── App ───────────────────────────────────────────────────────
app = Dash(__name__)

app.layout = html.Div([

    dcc.Interval(id='refresh', interval=30*1000, n_intervals=0),

    # Header
    html.Div([
        html.Div([
            html.H1("AI Insurance Claim Automation",
                    style={'margin': '0', 'fontSize': '20px', 'fontWeight': '800'}),
            html.P(id='header-sub',
                   style={'margin': '4px 0 0', 'fontSize': '12px', 'opacity': '0.8'}),
        ]),
        html.Div([
            html.Span("💬", style={'marginRight': '14px', 'fontSize': '18px', 'cursor': 'pointer'}),
            html.Span("🔔", style={'marginRight': '14px', 'fontSize': '18px', 'cursor': 'pointer'}),
            html.Span("👤", style={'fontSize': '18px', 'cursor': 'pointer'}),
        ]),
    ], style={
        'background': PRIMARY, 'color': WHITE,
        'padding': '16px 28px', 'display': 'flex',
        'justifyContent': 'space-between', 'alignItems': 'center',
        'marginBottom': '0'
    }),

    # Blocker banner
    html.Div(id='blocker-banner', style={
        'background': '#fff7ed',
        'borderLeft': f'4px solid {ORANGE}',
        'padding': '10px 20px',
        'fontSize': '12px',
        'color': DARK,
    }),

    # Main content
    html.Div([

        # Filter bar — top row
        html.Div([
            html.Div([
                html.Label("Trust", style={
                    'fontSize': '10px', 'color': TEXT_SUB, 'fontWeight': '600',
                    'letterSpacing': '0.5px', 'textTransform': 'uppercase',
                    'marginBottom': '4px', 'display': 'block'
                }),
                dcc.Dropdown(
                    id='filter-trust', options=TRUST_OPTIONS, value='all',
                    clearable=False, disabled=not _cols['has_trust'],
                    style={'fontSize': '12px', 'minWidth': '180px'}
                )
            ]),
            html.Div([
                html.Label("Insurance Type", style={
                    'fontSize': '10px', 'color': TEXT_SUB, 'fontWeight': '600',
                    'letterSpacing': '0.5px', 'textTransform': 'uppercase',
                    'marginBottom': '4px', 'display': 'block'
                }),
                dcc.Dropdown(
                    id='filter-type', options=TYPE_OPTIONS, value='all',
                    clearable=False, disabled=not _cols['has_insurance'],
                    style={'fontSize': '12px', 'minWidth': '160px'}
                )
            ]),
            html.Div([
                html.Label("Date Range", style={
                    'fontSize': '10px', 'color': TEXT_SUB, 'fontWeight': '600',
                    'letterSpacing': '0.5px', 'textTransform': 'uppercase',
                    'marginBottom': '4px', 'display': 'block'
                }),
                dcc.DatePickerRange(
                    id='filter-date',
                    min_date_allowed=MIN_DATE,
                    max_date_allowed=MAX_DATE,
                    start_date=MIN_DATE,
                    end_date=MAX_DATE,
                    display_format='DD/MM/YYYY',
                ) if MIN_DATE else html.P("Date not available",
                                          style={'fontSize': '12px', 'color': TEXT_SUB})
            ]),
            html.Div([
                html.Label("Records", style={
                    'fontSize': '10px', 'color': TEXT_SUB, 'fontWeight': '600',
                    'letterSpacing': '0.5px', 'textTransform': 'uppercase',
                    'marginBottom': '4px', 'display': 'block'
                }),
                html.P(id='record-count', style={
                    'fontSize': '20px', 'fontWeight': '700',
                    'color': BLUE, 'margin': '0', 'paddingTop': '2px'
                })
            ]),
            html.Div([
                html.Label("Refresh", style={
                    'fontSize': '10px', 'color': TEXT_SUB, 'fontWeight': '600',
                    'letterSpacing': '0.5px', 'textTransform': 'uppercase',
                    'marginBottom': '4px', 'display': 'block'
                }),
                html.P(id='last-refresh', style={
                    'fontSize': '11px', 'color': TEXT_SUB,
                    'margin': '0', 'paddingTop': '5px'
                })
            ]),
        ], style={
            'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap',
            'alignItems': 'flex-start', 'background': WHITE,
            'padding': '14px 20px', 'borderRadius': '8px',
            'border': f'1px solid {BORDER}', 'marginBottom': '16px',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.05)'
        }),
        # KPI Charts
        html.Div(dcc.Graph(id='kpi-cards'), style={
            'background': WHITE, 'borderRadius': '8px', 'padding': '8px',
            'marginBottom': '14px', 'border': f'1px solid {BORDER}',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.05)'
        }),

        # Trend Charts
        html.Div(dcc.Graph(id='trend-charts'), style={
            'background': WHITE, 'borderRadius': '8px', 'padding': '8px',
            'marginBottom': '14px', 'border': f'1px solid {BORDER}',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.05)'
        }),

        # Breakdown Charts
        html.Div(dcc.Graph(id='breakdown-charts'), style={
            'background': WHITE, 'borderRadius': '8px', 'padding': '8px',
            'marginBottom': '14px', 'border': f'1px solid {BORDER}',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.05)'
        }),

        # Auto Decision
        html.Div(dcc.Graph(id='auto-decision'), style={
            'background': WHITE, 'borderRadius': '8px', 'padding': '8px',
            'marginBottom': '14px', 'border': f'1px solid {BORDER}',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.05)'
        }),

        # Drill-down table
        html.Div([
            html.P("Individual Claim Drill-Down", style={
                'fontSize': '13px', 'fontWeight': '700', 'color': PRIMARY,
                'letterSpacing': '0.5px', 'textTransform': 'uppercase', 'marginBottom': '6px'
            }),
            html.P("Showing filtered claims — use column headers to sort and filter.",
                   style={'fontSize': '11px', 'color': TEXT_SUB, 'marginBottom': '12px'}),
            dash_table.DataTable(
                id='drill-table',
                page_size=15,
                sort_action='native',
                filter_action='native',
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': PRIMARY, 'color': WHITE,
                    'fontWeight': '600', 'fontSize': '12px', 'fontFamily': 'Arial'
                },
                style_cell={
                    'fontSize': '12px', 'fontFamily': 'Arial',
                    'padding': '8px 12px', 'textAlign': 'left',
                    'border': f'1px solid {BORDER}', 'minWidth': '80px'
                },
                style_data_conditional=[
                    {'if': {'filter_query': '{Claim Status} = "Paid"'},
                     'backgroundColor': GREEN_BG, 'color': GREEN},
                    {'if': {'filter_query': '{Claim Status} = "Denied"'},
                     'backgroundColor': RED_BG, 'color': RED},
                    {'if': {'filter_query': '{Claim Status} = "Under Review"'},
                     'backgroundColor': ORANGE_BG, 'color': ORANGE},
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#fafafa'},
                ]
            )
        ], style={
            'background': WHITE, 'borderRadius': '8px', 'padding': '18px 20px',
            'marginBottom': '16px', 'border': f'1px solid {BORDER}',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.05)'
        }),

    ], style={'padding': '16px 24px', 'background': BG}),

], style={'fontFamily': 'Arial, sans-serif', 'margin': '0', 'padding': '0'})


# ── Callback ──────────────────────────────────────────────────
@app.callback(
    Output('kpi-cards',        'figure'),
    Output('trend-charts',     'figure'),
    Output('breakdown-charts', 'figure'),
    Output('auto-decision',    'figure'),
    Output('drill-table',      'data'),
    Output('drill-table',      'columns'),
    Output('last-refresh',     'children'),
    Output('record-count',     'children'),
    Output('header-sub',       'children'),
    Output('blocker-banner',   'children'),
    Input('refresh',           'n_intervals'),
    Input('filter-trust',      'value'),
    Input('filter-type',       'value'),
    Input('filter-date',       'start_date'),
    Input('filter-date',       'end_date'),
)
def update_dashboard(n, trust, claim_type, start_date, end_date):
    from datetime import datetime

    df   = load_data()
    cols = detect_columns(df)

    # Apply filters
    if cols['has_trust'] and trust and trust != 'all':
        df = df[df['Trust'] == trust]
    if cols['has_insurance'] and claim_type and claim_type != 'all':
        df = df[df['Insurance Type'] == claim_type]
    if start_date and not df['_date'].isna().all():
        df = df[df['_date'] >= pd.Timestamp(start_date)]
    if end_date and not df['_date'].isna().all():
        df = df[df['_date'] <= pd.Timestamp(end_date)]

    if len(df) == 0:
        empty = go.Figure()
        empty.update_layout(title='No data for selected filters',
                            paper_bgcolor=WHITE, height=200)
        return empty, empty, empty, empty, [], [], 'No data', '0', '', ''

    df['Month'] = df['_date'].dt.to_period('M') if not df['_date'].isna().all() else 'Unknown'
    total = len(df)

    # ── KPIs ──────────────────────────────────────────────────
    approval_rate = round((df['Claim Status'] == 'Paid').sum() / total * 100, 1) \
                    if 'Claim Status' in df.columns else None

    if cols['has_decision_date']:
        df['days'] = (pd.to_datetime(df['decision_date']) - df['_date']).dt.days
        avg_days     = round(df['days'].mean(), 1)
        kpi2_blocked = False
    else:
        avg_days     = None
        kpi2_blocked = True

    if cols['has_fraud_score']:
        fraud_rate  = round((df['fraud_score'] > 0.5).sum() / total * 100, 1)
        fraud_proxy = False
    elif cols['has_reason_code']:
        fraud_rate  = round(df['Reason Code'].isin(FRAUD_CODES).sum() / total * 100, 1)
        fraud_proxy = True
    else:
        fraud_rate  = None
        fraud_proxy = True

    if cols['has_auto_flag']:
        auto_rate  = round(df['auto_decision_flag'].sum() / total * 100, 1)
        auto_proxy = False
    elif cols['has_outcome']:
        auto_rate  = round(((df['Outcome'] == 'Paid') & (df['Claim Status'] == 'Paid')).sum() / total * 100, 1)
        auto_proxy = True
    else:
        auto_rate  = None
        auto_proxy = True

    total_saved = int(df['amount_saved'].sum()) if 'amount_saved' in df.columns else None

    # ── Blocker banner ────────────────────────────────────────
    blockers = []
    if kpi2_blocked:
        blockers.append("KPI 2 (Avg Days to Decision) — waiting on FS-06 for decision_date")
    if auto_proxy:
        blockers.append("KPI 4 (Auto-Decision Rate) — proxy in use, waiting on ML-04")
    if not cols['has_trust']:
        blockers.append("Trust filter — column not in dataset, waiting on DS-01")
    if not cols['has_fraud_score']:
        blockers.append("KPI 3 (Fraud Rate) — reason code proxy, waiting on ML-03")

    banner = (
        [html.Strong("Active Blockers: ", style={'color': '#c2410c', 'marginRight': '6px'})] +
        [html.Span(f"{b}  |  ", style={'marginRight': '4px'}) for b in blockers]
    ) if blockers else [
        html.Strong("All KPIs live — no blockers", style={'color': GREEN})
    ]

    # ── Chart 1 — KPI Cards ───────────────────────────────────
    fig_cards = make_subplots(
        rows=1, cols=5,
        specs=[[{'type': 'indicator'}] * 5],
        subplot_titles=['Approval Rate', 'Avg Days to Decision',
                        'Fraud Flag Rate', 'Auto-Decision Rate', '£ Saved']
    )
    cards = [
        (approval_rate, GREEN,   False,        False,      '',  '%'),
        (avg_days,      ORANGE,  kpi2_blocked, False,      '',  ' days'),
        (fraud_rate,    RED,     False,        fraud_proxy,'',  '%'),
        (auto_rate,     BLUE,    False,        auto_proxy, '',  '%'),
        (total_saved,   DARK,    False,        False,      '£', ''),
    ]
    labels = ['Approval Rate', 'Avg Days to Decision',
              'Fraud Flag Rate', 'Auto-Decision Rate', '£ Saved']

    for i, (val, color, blocked, proxy, prefix, suffix) in enumerate(cards):
        fig_cards.add_trace(go.Indicator(
            mode='number',
            value=None if (blocked or val is None) else val,
            number=dict(prefix=prefix, suffix=suffix,
                        font=dict(size=38, color=color, family='Arial Black')),
            title=dict(
                text=(f'<b>{labels[i]}</b>'
                      + ('<br><span style="font-size:10px;color:#c2410c">Blocked — FS-06</span>' if blocked else '')
                      + ('<br><span style="font-size:10px;color:#d97706">Proxy</span>' if proxy and not blocked else '')),
                font=dict(size=12, color=DARK, family='Arial')
            ),
            domain=dict(row=0, column=i)
        ), row=1, col=i+1)

    fig_cards.update_layout(
        title=dict(
            text=f'<b>KPI Overview</b> — {total:,} records',
            font=dict(size=15, color=PRIMARY, family='Arial'), x=0.5, xanchor='center'),
        height=210, paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        margin=dict(t=60, b=8, l=16, r=16))

    # ── Chart 2 — Trends ──────────────────────────────────────
    monthly = df.groupby('Month').agg(
        total    = ('Claim ID', 'count'),
        approved = ('Claim Status', lambda x: (x == 'Paid').sum()),
        fraud    = ('Reason Code', lambda x: x.isin(FRAUD_CODES).sum())
                   if cols['has_reason_code'] else ('Claim ID', lambda x: 0),
        saved    = ('amount_saved', 'sum')
    ).reset_index()
    monthly['approval_rate'] = round(monthly['approved'] / monthly['total'] * 100, 1)
    monthly['fraud_rate']    = round(monthly['fraud']    / monthly['total'] * 100, 1)
    monthly['month_str']     = monthly['Month'].astype(str)
    months = monthly['month_str'].tolist()

    fig_trends = make_subplots(rows=1, cols=3,
        subplot_titles=['Approval Rate % — Monthly',
                        'Fraud Flag Rate % — Monthly', '£ Saved — Monthly'],
        horizontal_spacing=0.08)
    fig_trends.add_trace(go.Scatter(
        x=months, y=monthly['approval_rate'], mode='lines+markers+text',
        line=dict(color=GREEN, width=2),
        marker=dict(size=8, color=GREEN),
        text=[f'{v}%' for v in monthly['approval_rate']],
        textposition='top center', textfont=dict(size=10, color=GREEN),
        fill='tozeroy', fillcolor='rgba(22,163,74,0.08)'
    ), row=1, col=1)
    fig_trends.add_trace(go.Scatter(
        x=months, y=monthly['fraud_rate'], mode='lines+markers+text',
        line=dict(color=RED, width=2),
        marker=dict(size=8, color=RED, symbol='diamond'),
        text=[f'{v}%' for v in monthly['fraud_rate']],
        textposition='top center', textfont=dict(size=10, color=RED),
        fill='tozeroy', fillcolor='rgba(220,38,38,0.08)'
    ), row=1, col=2)
    fig_trends.add_trace(go.Bar(
        x=months, y=monthly['saved'], marker_color=BLUE, opacity=0.85,
        text=[f'£{int(v):,}' for v in monthly['saved']],
        textposition='outside', textfont=dict(size=10, color=BLUE)
    ), row=1, col=3)
    fig_trends.update_yaxes(title_text='Rate (%)', row=1, col=1, range=[0, 50])
    fig_trends.update_yaxes(title_text='Rate (%)', row=1, col=2, range=[0, 50])
    fig_trends.update_yaxes(title_text='Amount (£)', row=1, col=3)
    fig_trends.update_layout(
        title=dict(text='<b>Monthly KPI Trends</b>',
                   font=dict(size=14, color=PRIMARY, family='Arial'), x=0.5, xanchor='center'),
        height=360, showlegend=False, paper_bgcolor=WHITE, plot_bgcolor='#f8fafc',
        margin=dict(t=60, b=40, l=50, r=30), font=dict(family='Arial'))

    # ── Chart 3 — Breakdown ───────────────────────────────────
    fig_breakdown = make_subplots(rows=1, cols=3,
        specs=[[{'type': 'pie'}, {'type': 'pie'}, {'type': 'bar'}]],
        subplot_titles=['Claim Status', 'Insurance Type', 'Monthly Volume'])

    status_counts = df['Claim Status'].value_counts()
    fig_breakdown.add_trace(go.Pie(
        labels=status_counts.index.tolist(),
        values=status_counts.values.tolist(),
        hole=0.5, marker=dict(colors=[GREEN, RED, ORANGE]),
        textinfo='label+percent', textfont=dict(size=11), showlegend=False
    ), row=1, col=1)

    if cols['has_insurance']:
        ins_counts = df['Insurance Type'].value_counts()
        fig_breakdown.add_trace(go.Pie(
            labels=ins_counts.index.tolist(),
            values=ins_counts.values.tolist(),
            hole=0.5, marker=dict(colors=[PRIMARY, BLUE, '#0ea5e9', '#38bdf8']),
            textinfo='label+percent', textfont=dict(size=11), showlegend=False
        ), row=1, col=2)
    else:
        fig_breakdown.add_trace(go.Pie(
            labels=['Not available'], values=[1], hole=0.5,
            marker=dict(colors=['#e2e8f0']), showlegend=False
        ), row=1, col=2)

    fig_breakdown.add_trace(go.Bar(
        x=monthly['month_str'], y=monthly['total'],
        marker_color=PRIMARY, opacity=0.85,
        text=monthly['total'], textposition='outside',
        textfont=dict(size=11, color=PRIMARY), showlegend=False
    ), row=1, col=3)
    fig_breakdown.update_yaxes(title_text='Claims', row=1, col=3)
    fig_breakdown.update_layout(
        title=dict(text='<b>Claims Distribution & Volume</b>',
                   font=dict(size=14, color=PRIMARY, family='Arial'), x=0.5, xanchor='center'),
        height=360, paper_bgcolor=WHITE, plot_bgcolor='#f8fafc',
        margin=dict(t=60, b=40, l=30, r=30), font=dict(family='Arial'))

    # ── Chart 4 — Auto Decision ───────────────────────────────
    auto_val   = auto_rate or 0
    auto_count = int(total * auto_val / 100)
    fig_auto = go.Figure(go.Pie(
        labels=['Auto-Decided', 'Human Review'],
        values=[auto_count, total - auto_count],
        hole=0.6,
        marker=dict(colors=[PRIMARY, '#e2e8f0']),
        textinfo='label+percent', textfont=dict(size=12), showlegend=True
    ))
    fig_auto.update_layout(
        title=dict(
            text=f'<b>Auto-Decision Rate — {auto_val}%</b>'
                 + (' (Proxy)' if auto_proxy else ' (Live)')
                 + ('<br><sup>Replace with ML-04 auto_decision_flag when available</sup>'
                    if auto_proxy else ''),
            font=dict(size=14, color=PRIMARY, family='Arial'), x=0.5, xanchor='center'),
        annotations=[dict(
            text=f'<b>{auto_val}%</b><br>Auto',
            x=0.5, y=0.5,
            font=dict(size=16, color=PRIMARY, family='Arial Black'),
            showarrow=False
        )],
        height=340, paper_bgcolor=WHITE,
        margin=dict(t=90, b=30, l=30, r=30))

    # ── Drill-down table ──────────────────────────────────────
    base_cols = ['Claim ID', 'Claim Status', 'Billed Amount',
                 'Paid Amount', 'amount_saved', 'Outcome']
    optional = [
        ('Trust',          cols['has_trust']),
        ('Insurance Type', cols['has_insurance']),
        ('Reason Code',    cols['has_reason_code']),
        ('AR Status',      cols['has_ar_status']),
    ]
    dc = 'Date of Service' if 'Date of Service' in df.columns else 'Date'
    if dc in df.columns:
        base_cols.insert(1, dc)
    for col_name, available in optional:
        if available and col_name in df.columns:
            base_cols.append(col_name)

    table_df = df[[c for c in base_cols if c in df.columns]].copy()
    if dc in table_df.columns:
        table_df[dc] = table_df[dc].dt.strftime('%d/%m/%Y')
    if 'amount_saved' in table_df.columns:
        table_df['amount_saved'] = table_df['amount_saved'].astype(int)

    table_cols = [{'name': c, 'id': c} for c in table_df.columns]

    header_sub = (f"DS-03 W5  |  {'PostgreSQL' if USE_DATABASE else 'CSV mode'}  |  "
                  f"{total:,} records  |  Auto-refresh every 30s")

    last_refresh = f"{datetime.now().strftime('%H:%M:%S')}  ·  {'DB' if USE_DATABASE else 'CSV'}  ·  30s"

    return (fig_cards, fig_trends, fig_breakdown, fig_auto,
            table_df.to_dict('records'), table_cols,
            last_refresh, f"{total:,}", header_sub, banner)


if __name__ == '__main__':
    app.run(debug=False)