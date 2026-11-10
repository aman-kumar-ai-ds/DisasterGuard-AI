import streamlit as st
import pandas as pd
import plotly.express as px

from database import (
    create_table,
    add_incident,
    get_incidents,
    delete_incident,
    create_resource_table,
    add_resource,
    get_resources,
    delete_resource,
    create_allocation_table,
    allocate_resource,
    auto_allocate_resources,
    get_allocations,
    release_resource
)

from modules.classification import classify_disaster
from modules.severity_prediction import predict_severity
from modules.disaster_map import show_disaster_map
from modules.resource_allocation import recommend_resources


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="DisasterGuard AI",
    page_icon="🚨",
    layout="wide"
)


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

create_table()
create_resource_table()
create_allocation_table()


# =====================================================
# PROFESSIONAL UI STYLING
# =====================================================

st.markdown("""
<style>
:root {
    --dg-bg: #08111f;
    --dg-panel: #111f34;
    --dg-border: #2b4669;
    --dg-text: #f4f7fb;
    --dg-muted: #a9bbd2;
}
.stApp {
    background:
        radial-gradient(ellipse at 85% 0%, rgba(37, 99, 235, 0.18), transparent 38%),
        linear-gradient(145deg, #08111f 0%, #0d1930 52%, #0a1425 100%);
    color: var(--dg-text);
}
.block-container {
    max-width: 1500px;
    padding-top: 3.5rem;
    padding-bottom: 3rem;
}

/* Keep the Streamlit toolbar from overlapping the page heading */
[data-testid="stHeader"] {
    background: rgba(8, 17, 31, 0.92);
}
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0.5rem;
}
h1, h2, h3, h4, h5 {
    color: var(--dg-text);
    letter-spacing: -0.35px;
}
p, label, [data-testid="stCaptionContainer"] {
    color: var(--dg-muted);
}
[data-testid="stMarkdownContainer"] p { line-height: 1.55; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101e34 0%, #0a1425 100%);
    border-right: 1px solid #263d5c;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #f8fbff; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 9px; padding: 7px 10px; margin: 2px 0;
}
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(37, 99, 235, 0.13); border: 1px solid #294b78;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(26, 48, 78, 0.98), rgba(16, 32, 55, 0.98));
    padding: 18px 20px; border-radius: 15px; border: 1px solid #35557e;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.20); min-height: 108px;
}
[data-testid="stMetricLabel"] { color: #bdcde1; font-size: 0.86rem; }
[data-testid="stMetricValue"] { color: #fff; font-size: 1.9rem; font-weight: 750; }
[data-testid="stMetricDelta"] { color: #8ee0bd; }

/* Forms, expanders and input controls */
[data-testid="stForm"], [data-testid="stExpander"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(17, 31, 52, 0.55); border: 1px solid #2a4567; border-radius: 14px;
}
[data-testid="stForm"] { padding: 18px; }
[data-testid="stExpander"] summary { color: #e8f1fc; font-weight: 650; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input {
    background: #101f35; color: #f8fafc; border-radius: 9px; border: 1px solid #355477;
}
[data-baseweb="select"] > div {
    background: #101f35; border-color: #355477; border-radius: 9px; color: #f8fafc;
}

/* Buttons */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
    border-radius: 10px; min-height: 2.55rem; font-weight: 650;
    border: 1px solid #42658f; transition: all 0.18s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover, .stDownloadButton button:hover {
    border-color: #60a5fa; color: #fff; transform: translateY(-1px);
}

/* Tables, alerts, charts and tabs */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border: 1px solid #2c4769; border-radius: 12px; overflow: hidden;
}
div[data-testid="stAlert"], div[data-testid="stNotification"] { border-radius: 11px; }
button[data-baseweb="tab"] { color: #b9cbe2; font-weight: 650; }
button[data-baseweb="tab"][aria-selected="true"] { color: #fff; }
hr { border-color: #2b4363; }
div[data-testid="stPlotlyChart"] { border-radius: 12px; }

/* Footer */
.dg-footer {
    text-align: center; color: #8fa6c3; padding: 22px 10px 8px;
    border-top: 1px solid #263d5c; margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.markdown(
    "# 🚨 DisasterGuard AI"
)

st.sidebar.caption(
    "Smart Disaster Management System"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Incident Management",
        "Resources",
        "Smart Allocation",
        "Disaster Map",
        "Analytics"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "AI-powered disaster monitoring and emergency response."
)

st.sidebar.caption(
    "Academic Demonstration Project"
)


# =====================================================
# APPLICATION HEADER
# =====================================================

st.markdown("""
<div style="
    display:flex; align-items:center; gap:14px;
    padding:5px 0 17px 0; border-bottom:1px solid #2b4363;
    margin-bottom:22px;">
    <div style="font-size:34px;">🚨</div>
    <div>
        <div style="font-size:27px; font-weight:800; color:#f8fafc;">
            DisasterGuard AI
        </div>
        <div style="font-size:13px; color:#a9bbd2; margin-top:3px;">
            Smart Disaster Management &amp; Emergency Response System
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# FETCH INCIDENT RECORDS
# =====================================================

records = get_incidents()

columns = [
    "ID",
    "Disaster",
    "Location",
    "Affected People",
    "Severity",
    "Description",
    "Status"
]

df = pd.DataFrame(
    records,
    columns=columns
)# =====================================================
# 1. DASHBOARD
# =====================================================

if page == "Dashboard":

    refresh_col, info_col = st.columns([1, 4])
    with refresh_col:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    with info_col:
        st.caption("Refresh the dashboard to reload the latest database records.")

    st.markdown("""
    <div style="
        padding: 24px 28px;
        border-radius: 18px;
        background: linear-gradient(110deg, #172f55 0%, #1d4d78 58%, #17365d 100%);
        border: 1px solid #41658d;
        margin-bottom: 22px;">
        <div style="color:#9ec5f8; font-size:12px; font-weight:700;
                    letter-spacing:1.5px; text-transform:uppercase;">
            Emergency Response Platform
        </div>
        <div style="font-size:30px; font-weight:800; color:#ffffff;
                    margin-top:7px;">
            Emergency Operations Center
        </div>
        <div style="color:#d5e5f7; font-size:14px; margin-top:7px;">
            Monitor incidents, review available resources and track response activity.
        </div>
    </div>
    """, unsafe_allow_html=True)

    total = len(df)

    critical = (
        len(df[df["Severity"] == "Critical"])
        if total else 0
    )

    active = (
        len(df[df["Status"] == "Active"])
        if total else 0
    )

    resolved = (
        len(df[df["Status"] == "Resolved"])
        if total else 0
    )

    st.markdown("### 🚨 Incident Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", total, help="All incidents registered in the local database.")
    c2.metric("Critical Incidents", critical)
    c3.metric("Active Operations", active)
    c4.metric("Resolved Cases", resolved)

    st.markdown("---")

    # Resource overview
    st.markdown("### 🚑 Emergency Resource Overview")

    resources = get_resources()

    if resources:
        resource_columns = [
            "ID", "Resource Name", "Category",
            "Quantity", "Location", "Status"
        ]
        resource_df = pd.DataFrame(resources, columns=resource_columns)

        total_stock = int(resource_df["Quantity"].sum())
        available_stock = int(
            resource_df.loc[
                resource_df["Status"] == "Available", "Quantity"
            ].sum()
        )
        out_of_stock = int(
            (resource_df["Quantity"] <= 0).sum()
            + (resource_df["Status"] == "Out of Stock").sum()
        )
    else:
        total_stock = 0
        available_stock = 0
        out_of_stock = 0

    r1, r2, r3 = st.columns(3)
    r1.metric("Total Stock Units", total_stock)
    r2.metric("Available Stock", available_stock)
    r3.metric("Out-of-Stock Records", out_of_stock)

    st.markdown("---")

    # Disaster intelligence
    if total > 0:
        st.markdown("### 📈 Disaster Intelligence")

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("#### Disaster Distribution")
                fig = px.pie(
                    df,
                    names="Disaster",
                    hole=0.58,
                    template="plotly_dark"
                )
                fig.update_traces(
                    textposition="inside",
                    textinfo="label+value+percent",
                    insidetextfont=dict(size=13, color="white")
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=8, r=8, t=25, b=8),
                    legend_title_text=""
                )
                st.plotly_chart(fig, width="stretch")

        with col2:
            with st.container(border=True):
                st.markdown("#### Incident Severity")
                severity_data = (
                    df["Severity"].value_counts().reset_index()
                )
                severity_data.columns = ["Severity", "Count"]

                severity_colors = {
                    "Low": "#00E676",
                    "Medium": "#2979FF",
                    "High": "#FF9100",
                    "Critical": "#FF1744"
                }

                fig2 = px.bar(
                    severity_data,
                    x="Severity",
                    y="Count",
                    color="Severity",
                    color_discrete_map=severity_colors,
                    text="Count",
                    template="plotly_dark",
                    category_orders={
                        "Severity": ["Low", "Medium", "High", "Critical"]
                    }
                )
                fig2.update_traces(
                    textposition="outside",
                    textfont=dict(size=13, color="white")
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=8, r=8, t=25, b=8),
                    showlegend=False,
                    yaxis_title="Number of Incidents",
                    xaxis_title="Severity"
                )
                st.plotly_chart(fig2, width="stretch")

        # Location-wise incident chart
        st.markdown("### 📍 Location-wise Incident Overview")
        location_data = (
            df["Location"].fillna("Unknown").value_counts()
            .rename_axis("Location")
            .reset_index(name="Incidents")
        )
        location_fig = px.bar(
            location_data,
            x="Location",
            y="Incidents",
            text="Incidents",
            color="Incidents",
            color_continuous_scale="Blues",
            template="plotly_dark"
        )
        location_fig.update_traces(
            textposition="outside",
            textfont=dict(size=13, color="white")
        )
        location_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=8, r=8, t=25, b=8),
            coloraxis_showscale=False,
            xaxis_title="Location",
            yaxis_title="Number of Incidents"
        )
        st.plotly_chart(location_fig, width="stretch")

        st.markdown("### 📋 Recent Incidents")
        recent_df = df.sort_values("ID", ascending=False).head(5).copy()

        def severity_style(value):
            colors = {
                "Low": "background-color:#14532d;color:#bbf7d0;font-weight:700;",
                "Medium": "background-color:#1e3a8a;color:#dbeafe;font-weight:700;",
                "High": "background-color:#7c2d12;color:#ffedd5;font-weight:700;",
                "Critical": "background-color:#7f1d1d;color:#fee2e2;font-weight:700;"
            }
            return colors.get(value, "")

        def status_style(value):
            colors = {
                "Active": "background-color:#78350f;color:#fef3c7;font-weight:700;",
                "Resolved": "background-color:#14532d;color:#bbf7d0;font-weight:700;"
            }
            return colors.get(value, "")

        styled_recent = recent_df.style.map(
            severity_style, subset=["Severity"]
        ).map(
            status_style, subset=["Status"]
        )

        st.dataframe(
            styled_recent,
            width="stretch",
            hide_index=True
        )
    else:
        st.info(
            "No incidents registered yet. Register your first incident "
            "from Incident Management to populate the dashboard."
        )

    st.caption(
        "Dashboard data comes from the local SQLite database. "
        "This is an academic demonstration and not a live emergency command system."
    )


# =====================================================
# 2. INCIDENT MANAGEMENT
# =====================================================

elif page == "Incident Management":

    st.markdown("## 🤖 AI Incident Management")

    st.caption(
        "Register disaster incidents and generate AI-based predictions."
    )

    st.divider()

    st.subheader("📝 Report a New Disaster")

    with st.form("ai_incident_form"):

        col1, col2 = st.columns(2)

        with col1:

            location = st.text_input(
                "📍 Incident Location",
                placeholder="Example: Ara, Bihar"
            )

        with col2:

            people = st.number_input(
                "👥 Affected People",
                min_value=0,
                value=0,
                step=1
            )

        description = st.text_area(
            "📝 Incident Description",
            placeholder=(
                "Example: Heavy rainfall caused flooding "
                "in residential areas."
            ),
            height=130
        )

        submitted = st.form_submit_button(
            "🤖 Predict & Register Incident",
            width="stretch"
        )

        if submitted:

            if not location.strip() or not description.strip():

                st.error(
                    "Please enter location and incident description."
                )

            else:

                try:

                    prediction, disaster_confidence = (
                        classify_disaster(description)
                    )

                    severity, severity_confidence = (
                        predict_severity(
                            description,
                            int(people)
                        )
                    )

                    recommended_resources, priority = (
                        recommend_resources(
                            prediction,
                            severity,
                            int(people)
                        )
                    )

                    add_incident(
                        prediction,
                        location.strip(),
                        int(people),
                        severity,
                        description.strip()
                    )

                    st.session_state.last_prediction = {
                        "disaster": prediction,
                        "disaster_confidence": disaster_confidence,
                        "severity": severity,
                        "severity_confidence": severity_confidence,
                        "location": location.strip(),
                        "people": int(people),
                        "resources": recommended_resources,
                        "priority": priority
                    }

                    st.success(
                        "Incident registered successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Could not process incident: {error}"
                    )

    # AI prediction results

    if "last_prediction" in st.session_state:

        result = st.session_state.last_prediction

        st.divider()

        st.subheader("🧠 AI Prediction Results")

        c1, c2 = st.columns(2)

        c1.metric(
            "Predicted Disaster",
            result["disaster"]
        )

        c2.metric(
            "Predicted Severity",
            result["severity"]
        )

        c3, c4 = st.columns(2)

        c3.metric(
            "Disaster Confidence",
            f"{result['disaster_confidence']}%"
        )

        c4.metric(
            "Severity Confidence",
            f"{result['severity_confidence']}%"
        )

        st.info(
            f"📍 Location: {result['location']} | "
            f"👥 Affected People: {result['people']}"
        )

        st.subheader("🚑 Smart Resource Recommendations")

        st.metric(
            "Response Priority",
            result["priority"]
        )

        for resource in result["resources"]:

            st.success(f"✓ {resource}")

        st.caption(
            "These are educational recommendations, "
            "not real emergency dispatch instructions."
        )

        st.caption(
            "The ML models use synthetic demonstration data. "
            "Confidence scores are not validated real-world accuracy."
        )

    # Registered incidents

    st.divider()

    st.subheader("📋 Registered Incidents")

    current_records = get_incidents()

    current_df = pd.DataFrame(
        current_records,
        columns=columns
    )

    if not current_df.empty:

        st.dataframe(
            current_df,
            width="stretch",
            hide_index=True
        )

        st.divider()

        st.subheader("🗑️ Delete Incident")

        selected_id = st.selectbox(
            "Select Incident ID",
            current_df["ID"].tolist()
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this incident."
        )

        if st.button("Delete Incident"):

            if confirm:

                deleted = delete_incident(
                    int(selected_id)
                )

                if deleted:

                    st.success(
                        "Incident deleted successfully!"
                    )

                    st.rerun()

                else:

                    st.error("Incident not found.")

            else:

                st.warning(
                    "Please confirm deletion first."
                )

    else:

        st.info("No incidents registered yet.")


# =====================================================
# 3. RESOURCE MANAGEMENT
# =====================================================

elif page == "Resources":

    st.markdown("## 🚑 Emergency Resource Management")

    st.caption(
        "Register, search and monitor emergency resources."
    )

    st.divider()

    # Resource registration

    st.subheader("➕ Register New Resource")

    with st.form("resource_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Resource Name",
                placeholder="Example: Ambulance Unit 01"
            )

            category = st.selectbox(
                "Resource Category",
                [
                    "Ambulance",
                    "Rescue Team",
                    "Food Supplies",
                    "Water Supplies",
                    "Medical Supplies",
                    "Rescue Boats",
                    "Fire Engines",
                    "Emergency Shelters",
                    "Heavy Equipment",
                    "Other"
                ]
            )

        with col2:

            quantity = st.number_input(
                "Available Quantity",
                min_value=1,
                value=1,
                step=1
            )

            location = st.text_input(
                "Resource Location",
                placeholder="Example: Ara, Bihar"
            )

        submit = st.form_submit_button(
            "➕ Add Resource",
            width="stretch"
        )

        if submit:

            if not name.strip() or not location.strip():

                st.error(
                    "Please enter resource name and location."
                )

            else:

                add_resource(
                    name.strip(),
                    category,
                    int(quantity),
                    location.strip()
                )

                st.success(
                    "Resource added successfully!"
                )

                st.rerun()

    st.divider()

    # Inventory

    st.subheader("📦 Resource Inventory")

    resources = get_resources()

    resource_columns = [
        "ID",
        "Resource Name",
        "Category",
        "Quantity",
        "Location",
        "Status"
    ]

    resource_df = pd.DataFrame(
        resources,
        columns=resource_columns
    )

    if not resource_df.empty:

        # Inventory metrics

        total_stock = int(
            resource_df["Quantity"].sum()
        )

        available_stock = int(
            resource_df[
                resource_df["Status"] == "Available"
            ]["Quantity"].sum()
        )

        categories_count = (
            resource_df["Category"].nunique()
        )

        out_of_stock = len(
            resource_df[
                resource_df["Status"] == "Out of Stock"
            ]
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Total Stock", total_stock)
        m2.metric("Available Units", available_stock)
        m3.metric("Categories", categories_count)
        m4.metric("Out of Stock", out_of_stock)

        st.divider()

        # Search and filters

        st.subheader("🔎 Search & Filter")

        f1, f2, f3 = st.columns(3)

        with f1:

            search = st.text_input(
                "Search Resource",
                placeholder="Enter name or location"
            )

        with f2:

            category_filter = st.selectbox(
                "Category Filter",
                ["All"] + sorted(
                    resource_df["Category"].unique().tolist()
                )
            )

        with f3:

            status_filter = st.selectbox(
                "Stock Status",
                ["All", "Available", "Out of Stock"]
            )

        filtered_df = resource_df.copy()

        if search:

            filtered_df = filtered_df[
                filtered_df["Resource Name"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                filtered_df["Location"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if category_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Category"] == category_filter
            ]

        if status_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Status"] == status_filter
            ]

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True
        )

        st.caption(
            f"Showing {len(filtered_df)} of {len(resource_df)} resources."
        )

        # Safe deletion

        st.divider()

        st.subheader("🗑️ Delete Resource")

        selected_resource = st.selectbox(
            "Select Resource ID",
            resource_df["ID"].tolist()
        )

        confirm_resource = st.checkbox(
            "I confirm resource deletion.",
            key="confirm_resource_delete"
        )

        if st.button("Delete Selected Resource"):

            if not confirm_resource:

                st.warning(
                    "Please confirm resource deletion."
                )

            else:

                all_allocations = get_allocations()

                active_allocations = [
                    allocation
                    for allocation in all_allocations
                    if allocation[2] == selected_resource
                    and allocation[6] == "Allocated"
                ]

                if active_allocations:

                    st.error(
                        "This resource has active allocations. "
                        "Release them before deleting the resource."
                    )

                else:

                    delete_result = delete_resource(int(selected_resource))

                    if isinstance(delete_result, tuple):
                        deleted, delete_message = delete_result
                    else:
                        deleted = bool(delete_result)
                        delete_message = (
                            "Resource deleted successfully!"
                            if deleted else "Resource not found."
                        )

                    if deleted:

                        st.success(delete_message)
                        st.rerun()

                    else:

                        st.error(delete_message)

    else:

        st.info(
            "No resources registered yet. "
            "Use the form above to add emergency resources."
        )# =====================================================
# 4. SMART RESOURCE ALLOCATION
# =====================================================

elif page == "Smart Allocation":

    st.markdown("## 🚑 Smart Resource Allocation Center")

    st.caption(
        "Manage emergency resource distribution and allocation history."
    )

    st.divider()

    saved_incidents = get_incidents()

    if not saved_incidents:

        st.warning(
            "No incidents available. Register an incident first."
        )

    else:

        # Incident selection

        incident_options = {
            f"ID {row[0]} | {row[1]} | {row[2]}": row
            for row in saved_incidents
        }

        selected_label = st.selectbox(
            "Select Disaster Incident",
            list(incident_options.keys())
        )

        incident = incident_options[selected_label]

        incident_id = incident[0]
        disaster = incident[1]
        location = incident[2]
        people = incident[3]
        severity = incident[4]

        st.divider()

        st.subheader("📊 Incident Information")

        c1, c2, c3 = st.columns(3)

        c1.metric("Disaster Type", disaster)
        c2.metric("Severity", severity)
        c3.metric("Affected People", people)

        st.caption(f"📍 Incident Location: {location}")

        # Resource recommendations

        recommended, priority = recommend_resources(
            disaster,
            severity,
            int(people)
        )

        st.divider()

        st.subheader("🤖 AI Resource Recommendations")

        st.metric(
            "Emergency Response Priority",
            priority
        )

        for item in recommended:

            st.info(f"🚑 {item}")

        # Automatic resource allocation

        st.divider()

        st.subheader("🤖 Automatic Resource Allocation")

        st.caption(
            "Allocate available inventory automatically using the "
            "incident recommendations. Resources at the incident location "
            "are preferred."
        )

        if st.button(
            "🤖 Auto Allocate Resources",
            type="primary",
            width="stretch",
            key="auto_allocate_button"
        ):

            success, message, allocated, shortages = auto_allocate_resources(
                int(incident_id),
                recommended
            )

            st.session_state["auto_allocation_result"] = {
                "incident_id": int(incident_id),
                "success": success,
                "message": message,
                "allocated": allocated,
                "shortages": shortages
            }

            st.rerun()

        # Show the result after the page refreshes

        allocation_result = st.session_state.get("auto_allocation_result")

        if (
            allocation_result
            and allocation_result["incident_id"] == int(incident_id)
        ):

            if allocation_result["success"]:

                st.success(allocation_result["message"])

                if allocation_result["allocated"]:

                    st.markdown("**Allocated Resources**")

                    st.dataframe(
                        pd.DataFrame(allocation_result["allocated"]),
                        width="stretch",
                        hide_index=True
                    )

                if allocation_result["shortages"]:

                    st.warning(
                        "Some recommended resource quantities were not "
                        "available in the inventory."
                    )

                    st.dataframe(
                        pd.DataFrame(allocation_result["shortages"]),
                        width="stretch",
                        hide_index=True
                    )

            else:

                st.error(allocation_result["message"])

        # Inventory

        st.divider()

        st.subheader("📦 Available Resource Inventory")

        inventory = get_resources()

        inventory_columns = [
            "ID",
            "Resource Name",
            "Category",
            "Quantity",
            "Location",
            "Status"
        ]

        inventory_df = pd.DataFrame(
            inventory,
            columns=inventory_columns
        )

        if not inventory_df.empty:

            st.dataframe(
                inventory_df,
                width="stretch",
                hide_index=True
            )

            # Allocation

            st.divider()

            st.subheader("📤 Allocate Emergency Resources")

            available = inventory_df[
                (inventory_df["Quantity"] > 0)
                &
                (inventory_df["Status"] == "Available")
            ]

            if not available.empty:

                selected_id = st.selectbox(
                    "Select Resource",
                    available["ID"].tolist(),
                    format_func=lambda rid: (
                        f"{available.loc[available['ID'] == rid, 'Resource Name'].iloc[0]} "
                        f"(Available: {available.loc[available['ID'] == rid, 'Quantity'].iloc[0]})"
                    )
                )

                selected = available[
                    available["ID"] == selected_id
                ].iloc[0]

                quantity = st.number_input(
                    "Quantity to Allocate",
                    min_value=1,
                    max_value=int(selected["Quantity"]),
                    value=1,
                    step=1
                )

                if st.button(
                    "🚑 Allocate Resource",
                    width="stretch"
                ):

                    success, message = allocate_resource(
                        int(incident_id),
                        int(selected_id),
                        int(quantity)
                    )

                    if success:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)

            else:

                st.warning(
                    "No resources currently available for allocation."
                )

        else:

            st.warning(
                "No resources registered. Add resources from the Resources page."
            )

        # Allocation history

        st.divider()

        st.subheader("📋 Allocation History")

        history = get_allocations(int(incident_id))

        if history:

            history_df = pd.DataFrame(
                history,
                columns=[
                    "Allocation ID",
                    "Incident ID",
                    "Resource ID",
                    "Resource Name",
                    "Quantity",
                    "Allocated At",
                    "Status"
                ]
            )

            st.dataframe(
                history_df,
                width="stretch",
                hide_index=True
            )

            # Release allocation

            st.divider()

            st.subheader("🔄 Release Allocated Resources")

            active_allocations = [
                item for item in history
                if item[6] == "Allocated"
            ]

            if active_allocations:

                allocation_options = {
                    (
                        f"Allocation ID {item[0]} | "
                        f"{item[3]} | Quantity: {item[4]}"
                    ): item[0]
                    for item in active_allocations
                }

                selected_allocation = st.selectbox(
                    "Select Allocation to Release",
                    list(allocation_options.keys()),
                    key="release_allocation_select"
                )

                if st.button(
                    "🔄 Release Resource",
                    width="stretch"
                ):

                    allocation_id = allocation_options[
                        selected_allocation
                    ]

                    success, message = release_resource(
                        int(allocation_id)
                    )

                    if success:

                        st.success(message)
                        st.rerun()

                    else:

                        st.error(message)

            else:

                st.info(
                    "No active allocations available for release."
                )

        else:

            st.info(
                "No allocation history available for this incident."
            )

    st.caption(
        "Academic demonstration only. Resource allocation updates "
        "local inventory records and does not dispatch emergency services."
    )


# =====================================================
# 5. DISASTER MAP
# =====================================================

elif page == "Disaster Map":

    st.markdown("## 🗺️ Disaster Monitoring Map")

    st.caption(
        "Visualize all registered disaster incidents geographically."
    )

    st.divider()

    # Fetch the latest incident records directly from SQLite
    map_incidents = get_incidents()

    st.subheader("📊 Incident Records")

    if map_incidents:

        st.success(
            f"Database returned {len(map_incidents)} incident records."
        )

        map_df = pd.DataFrame(
            map_incidents,
            columns=[
                "ID",
                "Disaster",
                "Location",
                "Affected People",
                "Severity",
                "Description",
                "Status"
            ]
        )

        # Show all records received from the database
        st.dataframe(
            map_df[
                [
                    "ID",
                    "Disaster",
                    "Location",
                    "Severity",
                    "Affected People",
                    "Status"
                ]
            ],
            width="stretch",
            hide_index=True
        )

        st.divider()
        st.subheader("📍 Incident Location Map")

        # Pass the complete database result to the map module
        show_disaster_map(map_incidents)

    else:

        st.warning(
            "No incidents found in the database. "
            "Please register incidents from Incident Management first."
        )


# =====================================================
# 6. ANALYTICS
# =====================================================

elif page == "Analytics":

    st.markdown("## 📊 Disaster Analytics Center")

    st.caption(
        "Analyze disaster incidents, severity and affected locations."
    )

    st.divider()

    analytics_records = get_incidents()

    analytics_df = pd.DataFrame(
        analytics_records,
        columns=columns
    )

    if not analytics_df.empty:

        # Summary metrics

        st.subheader("📈 Overall Statistics")

        total_incidents = len(analytics_df)

        total_people = int(
            analytics_df["Affected People"].sum()
        )

        disaster_types = (
            analytics_df["Disaster"].nunique()
        )

        locations = (
            analytics_df["Location"].nunique()
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Total Incidents",
            total_incidents
        )

        c2.metric(
            "People Affected",
            total_people
        )

        c3.metric(
            "Disaster Types",
            disaster_types
        )

        c4.metric(
            "Affected Locations",
            locations
        )

        st.divider()

        # Disaster distribution

        st.subheader("🌪️ Disaster Type Analysis")

        disaster_count = (
            analytics_df["Disaster"]
            .value_counts()
            .reset_index()
        )

        disaster_count.columns = [
            "Disaster",
            "Count"
        ]

        fig1 = px.pie(
            disaster_count,
            names="Disaster",
            values="Count",
            hole=0.45,
            template="plotly_dark",
            title="Disaster Distribution"
        )

        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig1,
            width="stretch"
        )

        st.divider()

        # Severity analysis

        st.subheader("🚨 Severity Analysis")

        severity_count = (
            analytics_df["Severity"]
            .value_counts()
            .reset_index()
        )

        severity_count.columns = [
            "Severity",
            "Count"
        ]

        fig2 = px.bar(
            severity_count,
            x="Severity",
            y="Count",
            color="Severity",
            template="plotly_dark",
            title="Incident Severity Distribution"
        )

        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig2,
            width="stretch"
        )

        st.divider()

        # Location analysis

        st.subheader("📍 Location Analysis")

        location_count = (
            analytics_df["Location"]
            .value_counts()
            .reset_index()
        )

        location_count.columns = [
            "Location",
            "Incidents"
        ]

        fig3 = px.bar(
            location_count,
            x="Location",
            y="Incidents",
            color="Incidents",
            template="plotly_dark",
            title="Incidents by Location"
        )

        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig3,
            width="stretch"
        )

        st.divider()

        # Full report

        st.subheader("📋 Complete Incident Report")

        st.dataframe(
            analytics_df,
            width="stretch",
            hide_index=True
        )

        # CSV download

        csv_data = analytics_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Incident Report (CSV)",
            data=csv_data,
            file_name="disaster_incident_report.csv",
            mime="text/csv",
            width="stretch"
        )

    else:

        st.warning(
            "No incident records available. "
            "Register incidents to generate analytics."
        )


# =====================================================
# APPLICATION FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div class="dg-footer">
        <h4>🚨 DisasterGuard AI</h4>
        <p>Smart Disaster Management & Emergency Response System</p>
        <p>Academic Demonstration Project | AI & Data Science</p>
    </div>
    """,
    unsafe_allow_html=True
)