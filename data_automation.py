import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==============================================================================
# 1. GENERATE "DIRTY" RAW DATA (Simulating uncleaned business inputs)
# ==============================================================================
def generate_dirty_raw_data():
    """Simulates a highly corrupted raw dataset with missing values, duplicates, and bad parsing."""
    np.random.seed(24)
    base_date = datetime(2026, 1, 1)
    n_records = 200
    
    dates = [base_date + timedelta(days=int(np.random.randint(0, 90))) for _ in range(n_records)]
    regions = ['North', 'South', 'East', 'West', 'NORTH', 'south ', 'N_East', 'W. Region'] # Inconsistent text
    revenue = np.random.normal(5000, 1500, size=n_records)
    transactions = np.random.randint(10, 100, size=n_records).astype(float)
    
    df = pd.DataFrame({
        'Transaction_Date': dates,
        'Region_Code': [np.random.choice(regions) for _ in range(n_records)],
        'Revenue_Gross': revenue,
        'Volume_Orders': transactions
    })
    
    # Intentionally inject bad artifacts
    # A. Introduce missing values (NaNs)
    df.loc[np.random.choice(df.index, size=15, replace=False), 'Revenue_Gross'] = np.nan
    df.loc[np.random.choice(df.index, size=10, replace=False), 'Volume_Orders'] = np.nan
    
    # B. Inject strict exact duplicates
    duplicates = df.iloc[np.random.choice(df.index, size=20, replace=False)]
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df

dirty_raw_df = generate_dirty_raw_data()

# ==============================================================================
# 2. AUTOMATED CLEANING ENGINE PIPELINE
# ==============================================================================
def execute_automated_cleaning_pipeline(raw_df):
    """Automated ETL cleaning step: handles standard enterprise data anomalies."""
    metrics = {}
    metrics['initial_rows'] = len(raw_df)
    
    # Step A: Deduplication
    deduped_df = raw_df.drop_duplicates()
    metrics['duplicates_removed'] = metrics['initial_rows'] - len(deduped_df)
    
    # Step B: Standardize Inconsistent Text Formatting
    cleaned_df = deduped_df.copy()
    cleaned_df['Region_Code'] = cleaned_df['Region_Code'].astype(str).str.upper().str.strip()
    
    # Remap regional variants into standard naming conventions
    region_map = {
        'NORTH': 'North', 'SOUTH': 'South', 'EAST': 'East', 'WEST': 'West',
        'N_EAST': 'East', 'W. REGION': 'West'
    }
    cleaned_df['Cleaned_Region'] = cleaned_df['Region_Code'].map(region_map).fillna('Other')
    
    # Step C: Handle Missing Values via Statistical Imputation
    # Flag rows that contained null entries before fixing them for audit purposes
    metrics['missing_revenue_count'] = cleaned_df['Revenue_Gross'].isna().sum()
    metrics['missing_volume_count'] = cleaned_df['Volume_Orders'].isna().sum()
    
    # Impute missing numeric data using regional medians
    cleaned_df['Revenue_Gross'] = cleaned_df.groupby('Cleaned_Region')['Revenue_Gross'].transform(lambda x: x.fillna(x.median()))
    cleaned_df['Volume_Orders'] = cleaned_df.groupby('Cleaned_Region')['Volume_Orders'].transform(lambda x: x.fillna(x.median()))
    
    # Step D: Type Casting Optimization
    cleaned_df['Volume_Orders'] = cleaned_df['Volume_Orders'].astype(int)
    cleaned_df['Revenue_Gross'] = cleaned_df['Revenue_Gross'].round(2)
    
    metrics['final_rows'] = len(cleaned_df)
    
    return cleaned_df, metrics

# Run automation routine on launch
clean_df, pipeline_metrics = execute_automated_cleaning_pipeline(dirty_raw_df)

# ==============================================================================
# 3. INTERACTIVE EXECUTIVE REPORTING INTERFACE
# ==============================================================================
app = dash.Dash(__name__, title="Automated Data Pipeline Reporting")

app.layout = html.Div(style={'fontFamily': 'Segoe UI, Helvetica, Arial, sans-serif', 'backgroundColor': '#f8fafc', 'padding': '25px'}, children=[
    
    # Top Banner Header
    html.Div(style={'backgroundColor': '#047857', 'color': 'white', 'padding': '20px 30px', 'borderRadius': '12px', 'marginBottom': '25px'}, children=[
        html.H1("Automated Data Pipeline & Executive Report", style={'margin': '0', 'fontSize': '26px', 'fontWeight': '600'}),
        html.P("Real-time automated deduplication, textual remediation, and metric statistical imputation", style={'margin': '5px 0 0 0', 'opacity': '0.8', 'fontSize': '14px'})
    ]),
    
    # Pipeline Automation Performance Summary Log Cards
    html.H3("Pipeline Execution Metrics Log", style={'color': '#1e293b', 'marginBottom': '15px'}),
    html.Div(style={'display': 'flex', 'gap': '15px', 'marginBottom': '30px', 'flexWrap': 'wrap'}, children=[
        
        html.Div(style={'flex': '1', 'minWidth': '180px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)', 'borderLeft': '4px solid #3b82f6'}, children=[
            html.H6("Raw Rows Ingested", style={'margin': '0', 'color': '#64748b', 'fontSize': '11px', 'textTransform': 'uppercase'}),
            html.H2(f"{pipeline_metrics['initial_rows']}", style={'margin': '5px 0 0 0', 'color': '#1e293b'})
        ]),
        
        html.Div(style={'flex': '1', 'minWidth': '180px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)', 'borderLeft': '4px solid #ef4444'}, children=[
            html.H6("Duplicates Purged", style={'margin': '0', 'color': '#64748b', 'fontSize': '11px', 'textTransform': 'uppercase'}),
            html.H2(f"{pipeline_metrics['duplicates_removed']}", style={'margin': '5px 0 0 0', 'color': '#1e293b'})
        ]),
        
        html.Div(style={'flex': '1', 'minWidth': '180px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)', 'borderLeft': '4px solid #f59e0b'}, children=[
            html.H6("Null Fields Imputed", style={'margin': '0', 'color': '#64748b', 'fontSize': '11px', 'textTransform': 'uppercase'}),
            html.H2(f"{pipeline_metrics['missing_revenue_count'] + pipeline_metrics['missing_volume_count']} Cells", style={'margin': '5px 0 0 0', 'color': '#1e293b'})
        ]),
        
        html.Div(style={'flex': '1', 'minWidth': '180px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)', 'borderLeft': '4px solid #10b981'}, children=[
            html.H6("Clean Records Finalized", style={'margin': '0', 'color': '#64748b', 'fontSize': '11px', 'textTransform': 'uppercase'}),
            html.H2(f"{pipeline_metrics['final_rows']}", style={'margin': '5px 0 0 0', 'color': '#1e293b'})
        ])
    ]),
    
    # Interactive Report Slicers Row
    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)', 'marginBottom': '25px'}, children=[
        html.Label("Select Target Region Filter Hierarchy:", style={'fontWeight': 'bold', 'color': '#475569', 'fontSize': '14px'}),
        dcc.Checklist(
            id='region-checklist',
            options=[{'label': f" Region {r}", 'value': r} for r in sorted(clean_df['Cleaned_Region'].unique())],
            value=list(clean_df['Cleaned_Region'].unique()),
            labelStyle={'display': 'inline-block', 'marginRight': '25px', 'marginTop': '8px', 'color': '#334155'}
        )
    ]),
    
    # Summary Visualizations Outputs
    html.Div(style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap', 'marginBottom': '25px'}, children=[
        html.Div(style={'flex': '1.2', 'minWidth': '400px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)'}, children=[
            dcc.Graph(id='revenue-trend-bar')
        ]),
        html.Div(style={'flex': '1', 'minWidth': '300px', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)'}, children=[
            dcc.Graph(id='volume-pie-share')
        ])
    ]),
    
    # Processed Audit Table Log
    html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.05)'}, children=[
        html.H4("Cleaned Production-Ready Dataset Records Log", style={'marginTop': '0', 'color': '#1e293b', 'fontSize': '15px'}),
        dash_table.DataTable(
            id='cleaned-log-table',
            columns=[
                {"name": "Transaction Date", "id": "Transaction_Date"},
                {"name": "Normalized Region", "id": "Cleaned_Region"},
                {"name": "Imputed Net Revenue ($)", "id": "Revenue_Gross"},
                {"name": "Order Volume (Units)", "id": "Volume_Orders"}
            ],
            page_size=6,
            style_cell={'padding': '10px', 'fontSize': '12px', 'textAlign': 'left'},
            style_header={'backgroundColor': '#f1f5f9', 'fontWeight': 'bold', 'color': '#334155', 'borderBottom': '2px solid #cbd5e1'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8fafc'}]
        )
    ])
])

# ==============================================================================
# 4. REPORTING LOGIC CALLBACK PIPELINE
# ==============================================================================
@app.callback(
    [Output('revenue-trend-bar', 'figure'),
     Output('volume-pie-share', 'figure'),
     Output('cleaned-log-table', 'data')],
    [Input('region-checklist', 'value')]
)
def update_automated_report(selected_regions):
    # Slice the clean dataset dynamically based on checklist
    filtered_df = clean_df[clean_df['Cleaned_Region'].isin(selected_regions)].copy()
    
    # A. Render Cleaned Revenue Trend Time Sequence
    trend_data = filtered_df.groupby('Transaction_Date')['Revenue_Gross'].sum().reset_index()
    fig_bar = px.bar(
        trend_data, x='Transaction_Date', y='Revenue_Gross',
        title="Normalized Clean Revenue Stream Trajectory",
        color_discrete_sequence=['#059669']
    )
    fig_bar.update_layout(template='plotly_white', xaxis_title='Timeline Calendar', yaxis_title='Aggregated Value ($)')
    
    # B. Render Regional Market Share Contribution Pie Chart (Fixed Attribute Error here)
    region_share = filtered_df.groupby('Cleaned_Region')['Volume_Orders'].sum().reset_index()
    fig_pie = px.pie(
        region_share, values='Volume_Orders', names='Cleaned_Region',
        title="Order Unit Composition Breakdown by Clean Region",
        hole=0.3, 
        color_discrete_sequence=['#047857', '#10b981', '#34d399', '#a7f3d0']
    )
    fig_pie.update_traces(textinfo='percent+label')
    
    # C. Prepare Data Strings for Data Presentation Log Table View
    table_records = filtered_df.copy()
    table_records['Transaction_Date'] = table_records['Transaction_Date'].dt.strftime('%Y-%m-%d')
    table_records['Revenue_Gross'] = table_records['Revenue_Gross'].map('${:,.2f}'.format)
    
    return fig_bar, fig_pie, table_records.to_dict('records')

# ==============================================================================
# 5. AUTOMATED SERVICE INITIATION
# ==============================================================================
if __name__ == '__main__':
    # Initializing on a customized port to avoid web cache collisions
    app.run(debug=True, port=8090)