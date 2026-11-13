import plotly.express as px
import plotly.graph_objects as go

def create_annual_comparison_chart(annual_target_val, actual_val):
    """
    رسم المقارنة السنوية (المستهدف السنوي الأصلي مقابل الفعلي السنوي).
    """
    fig = go.Figure(data=[
        go.Bar(name='المستهدف السنوي (Excel)', x=['السنوي'], y=[annual_target_val], marker_color='#008080'),
        go.Bar(name='المبيعات الفعلية', x=['السنوي'], y=[actual_val], marker_color='#1E3A8A')
    ])
    fig.update_layout(
        barmode='group',
        template='plotly_white',
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_monthly_target_chart(monthly_df):
    """
    رسم المستهدف الشهري المجمع منفصلاً.
    """
    if monthly_df.empty:
        return go.Figure()
        
    fig = px.bar(monthly_df, x='Month', y='Monthly_Target', title="المستهدف الشهري المجمع",
                 color_discrete_sequence=['#008080'])
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
