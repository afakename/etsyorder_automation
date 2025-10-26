"""
Etsy Order Automation - Web Interface
A Streamlit-based web application for managing Etsy orders
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys
from config import Config

# Import the main automation
from main import EtsyAutomation

# Page configuration
st.set_page_config(
    page_title="Etsy Order Automation",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-new {
        background-color: #90EE90;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .status-pulled {
        background-color: #FFD700;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .preview-alert {
        background-color: #FFE4B5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FFA500;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_run_data' not in st.session_state:
    st.session_state.last_run_data = None
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False

def load_last_run_summary():
    """Load the most recent automation run summary"""
    output_path = Config.get_output_path()

    if not output_path.exists():
        return None

    # Find the most recent run folder
    run_folders = sorted([f for f in output_path.iterdir() if f.is_dir()], reverse=True)

    if not run_folders:
        return None

    latest_run = run_folders[0]
    excel_file = latest_run / "etsy_orders.xlsx"

    if not excel_file.exists():
        return None

    return {
        'run_folder': latest_run,
        'excel_file': excel_file,
        'run_time': latest_run.name
    }

def get_order_statistics():
    """Get statistics from the last run"""
    last_run = load_last_run_summary()

    if not last_run:
        return None

    try:
        # Read all sheets
        excel_data = pd.read_excel(last_run['excel_file'], sheet_name=None)

        stats = {
            'run_time': last_run['run_time'],
            'total_workflow': len(excel_data.get('All Workflow Orders', [])),
            'ms_make': len(excel_data.get('MS - Needs Made', [])),
            'ms_update': len(excel_data.get('MS - Needs Updated', [])),
            'rr_make': len(excel_data.get('RR - Needs Made', [])),
            'rr_update': len(excel_data.get('RR - Needs Updated', [])),
            'already_made': len(excel_data.get('Already Made', [])),
            'preview_requests': len(excel_data.get('Preview Requests', [])),
            'peace_love_hope': len(excel_data.get('Peace-Love-Hope Orders', [])),
            'other_orders': len(excel_data.get('Other Orders', [])),
            'excel_data': excel_data,
            'excel_file': last_run['excel_file']
        }

        return stats
    except Exception as e:
        st.error(f"Error loading statistics: {e}")
        return None

def run_automation(mode, days):
    """Run the automation with progress tracking"""
    try:
        with st.spinner(f"Pulling orders ({mode} mode, {days} days back)..."):
            automation = EtsyAutomation(mode=mode, days_back=days)
            automation.run()
            return True
    except Exception as e:
        st.error(f"Automation failed: {e}")
        return False

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    st.markdown("### Order Pulling Mode")
    mode = st.radio(
        "Mode",
        options=['open_only', 'time_based'],
        format_func=lambda x: 'Open Orders Only (Recommended)' if x == 'open_only' else 'All Orders (Time-based)',
        help="Open Orders: Only pulls orders with status != Complete\nTime-based: Pulls all orders within the time period"
    )

    default_days = 90 if mode == 'open_only' else 30
    days_back = st.number_input(
        "Days to Look Back",
        min_value=1,
        max_value=365,
        value=default_days,
        help="How many days back to search for orders"
    )

    st.markdown("---")

    # Run automation button
    if st.button("🔄 Pull Orders Now", type="primary", use_container_width=True):
        if run_automation(mode, days_back):
            st.success("Orders pulled successfully!")
            st.rerun()
        else:
            st.error("Failed to pull orders")

    st.markdown("---")

    # Quick stats
    stats = get_order_statistics()
    if stats:
        st.markdown("### 📊 Last Run")
        st.markdown(f"**Time:** {stats['run_time']}")
        st.metric("Total Orders", stats['total_workflow'])
        st.metric("Preview Requests", stats['preview_requests'])
        st.metric("Needs Made", stats['ms_make'] + stats['rr_make'])

# Main content
st.markdown('<p class="main-header">❄️ Etsy Order Automation Dashboard</p>', unsafe_allow_html=True)

# Load statistics
stats = get_order_statistics()

if stats is None:
    st.info("👋 Welcome! Click 'Pull Orders Now' in the sidebar to get started.")
    st.markdown("""
    ## What This App Does

    This automation helps you manage your Etsy snowflake ornament orders by:

    1. **Pulling Orders** from Etsy API
    2. **Categorizing** products (MS, RR, Peace/Love/Hope, Other)
    3. **Checking** if designs already exist in your database
    4. **Detecting** preview requests from customers
    5. **Generating** Excel reports and CSV files for Adobe Illustrator
    6. **Staging** files ready for 3D printing

    ### Getting Started

    1. Use the sidebar to configure settings
    2. Click "Pull Orders Now" to run the automation
    3. View results and download reports below
    """)
else:
    # Display statistics in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Dashboard", "🔔 Preview Requests", "🎨 Needs Made", "📁 Already Made", "📥 Downloads"])

    with tab1:
        st.markdown("## Order Statistics")

        # Top metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Total Workflow Orders",
                stats['total_workflow'],
                help="Total MS and RR orders"
            )

        with col2:
            total_make = stats['ms_make'] + stats['rr_make']
            st.metric(
                "Needs Made",
                total_make,
                delta=f"MS: {stats['ms_make']}, RR: {stats['rr_make']}",
                help="Orders that need new designs created"
            )

        with col3:
            total_update = stats['ms_update'] + stats['rr_update']
            st.metric(
                "Needs Updated",
                total_update,
                delta=f"MS: {stats['ms_update']}, RR: {stats['rr_update']}",
                help="Orders that need existing designs updated"
            )

        with col4:
            st.metric(
                "Already Made",
                stats['already_made'],
                help="Orders with existing designs ready to go"
            )

        with col5:
            st.metric(
                "Preview Requests",
                stats['preview_requests'],
                delta="Needs attention!" if stats['preview_requests'] > 0 else None,
                delta_color="inverse",
                help="Customers requesting design previews"
            )

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            # Workflow breakdown
            workflow_data = pd.DataFrame({
                'Category': ['MS - Needs Made', 'MS - Needs Updated', 'RR - Needs Made', 'RR - Needs Updated', 'Already Made'],
                'Count': [stats['ms_make'], stats['ms_update'], stats['rr_make'], stats['rr_update'], stats['already_made']]
            })

            fig_workflow = px.bar(
                workflow_data,
                x='Category',
                y='Count',
                title='Workflow Order Breakdown',
                color='Category',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_workflow.update_layout(showlegend=False)
            st.plotly_chart(fig_workflow, use_container_width=True)

        with col2:
            # Order types pie chart
            order_types = pd.DataFrame({
                'Type': ['Workflow (MS/RR)', 'Peace/Love/Hope', 'Other Orders'],
                'Count': [stats['total_workflow'], stats['peace_love_hope'], stats['other_orders']]
            })

            fig_types = px.pie(
                order_types,
                values='Count',
                names='Type',
                title='Order Types Distribution',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_types, use_container_width=True)

        # Other orders summary
        st.markdown("### Other Orders")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Peace/Love/Hope Orders", stats['peace_love_hope'])
        with col2:
            st.metric("Other Orders", stats['other_orders'])

    with tab2:
        st.markdown("## 🔔 Preview Requests")

        if stats['preview_requests'] > 0:
            st.markdown(f'<div class="preview-alert">⚠️ You have <strong>{stats["preview_requests"]}</strong> preview requests that need attention!</div>', unsafe_allow_html=True)

            preview_df = stats['excel_data'].get('Preview Requests', pd.DataFrame())

            if not preview_df.empty:
                # Make the dataframe more interactive
                st.dataframe(
                    preview_df,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Status": st.column_config.TextColumn("Status", width="small"),
                        "Sent": st.column_config.CheckboxColumn("Sent", width="small"),
                        "Order ID": st.column_config.NumberColumn("Order ID", width="medium"),
                        "Customer": st.column_config.TextColumn("Customer", width="medium"),
                        "Name": st.column_config.TextColumn("Name", width="medium"),
                        "Message": st.column_config.TextColumn("Message", width="large")
                    }
                )

                # Quick actions
                st.markdown("### Quick Actions")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📧 Copy All Customer Emails"):
                        st.info("Feature coming soon!")
                with col2:
                    if st.button("✅ Mark All as Sent"):
                        st.info("Feature coming soon!")
        else:
            st.success("✅ No preview requests at this time!")

    with tab3:
        st.markdown("## 🎨 Orders Needing Designs")

        # MS Needs Made
        ms_make_df = stats['excel_data'].get('MS - Needs Made', pd.DataFrame())
        if not ms_make_df.empty:
            st.markdown(f"### MS - Needs Made ({len(ms_make_df)} orders)")
            st.dataframe(
                ms_make_df,
                use_container_width=True,
                column_config={
                    "Completed": st.column_config.CheckboxColumn("Done", width="small"),
                    "Preview": st.column_config.TextColumn("Preview", width="small"),
                }
            )

        # MS Needs Updated
        ms_update_df = stats['excel_data'].get('MS - Needs Updated', pd.DataFrame())
        if not ms_update_df.empty:
            st.markdown(f"### MS - Needs Updated ({len(ms_update_df)} orders)")
            st.dataframe(ms_update_df, use_container_width=True)

        # RR Needs Made
        rr_make_df = stats['excel_data'].get('RR - Needs Made', pd.DataFrame())
        if not rr_make_df.empty:
            st.markdown(f"### RR - Needs Made ({len(rr_make_df)} orders)")
            st.dataframe(rr_make_df, use_container_width=True)

        # RR Needs Updated
        rr_update_df = stats['excel_data'].get('RR - Needs Updated', pd.DataFrame())
        if not rr_update_df.empty:
            st.markdown(f"### RR - Needs Updated ({len(rr_update_df)} orders)")
            st.dataframe(rr_update_df, use_container_width=True)

        if ms_make_df.empty and ms_update_df.empty and rr_make_df.empty and rr_update_df.empty:
            st.success("✅ All orders have designs ready!")

    with tab4:
        st.markdown("## 📁 Already Made Designs")

        already_made_df = stats['excel_data'].get('Already Made', pd.DataFrame())

        if not already_made_df.empty:
            st.markdown(f"Found **{len(already_made_df)}** orders with existing designs!")
            st.dataframe(
                already_made_df,
                use_container_width=True,
                column_config={
                    "File Path": st.column_config.LinkColumn("File Path", width="large")
                }
            )
        else:
            st.info("No orders with existing designs in this batch.")

    with tab5:
        st.markdown("## 📥 Download Reports & Files")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Excel Reports")

            # Main Excel file
            if stats['excel_file'].exists():
                with open(stats['excel_file'], 'rb') as f:
                    st.download_button(
                        label="📊 Download Full Excel Report",
                        data=f,
                        file_name=f"etsy_orders_{stats['run_time']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

        with col2:
            st.markdown("### CSV Files (Illustrator)")

            # MS CSV
            ms_csv = stats['excel_file'].parent / 'illustrator_ms.csv'
            if ms_csv.exists():
                with open(ms_csv, 'rb') as f:
                    st.download_button(
                        label="📄 Download MS Variable CSV",
                        data=f,
                        file_name=f"illustrator_ms_{stats['run_time']}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            # RR CSV
            rr_csv = stats['excel_file'].parent / 'illustrator_rr.csv'
            if rr_csv.exists():
                with open(rr_csv, 'rb') as f:
                    st.download_button(
                        label="📄 Download RR Variable CSV",
                        data=f,
                        file_name=f"illustrator_rr_{stats['run_time']}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

        st.markdown("---")

        # Output folder location
        st.info(f"📂 All files are also saved to: `{stats['excel_file'].parent}`")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Etsy Order Automation v1.0 | Built with Streamlit ❄️</p>
    </div>
    """,
    unsafe_allow_html=True
)
