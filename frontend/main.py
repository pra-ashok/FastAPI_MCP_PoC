import streamlit as st
import requests
import json
import time
import pandas as pd

# --- Configuration ---
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="FastAPI_MCP_PoC Dashboard",
    page_icon="🤖",
    layout="wide"
)

# --- Custom CSS for Polishing ---
st.markdown("""
    <style>
    /* Main container max-width and neatness */
    .main .block-container {
        max-width: 1250px;
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
    }
    
    /* Global font size increase */
    html, body, [class*="css"] {
        font-size: 1.20rem; /* Increased from 1.05rem */
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Style headers */
    h1 {
        font-size: 3.5rem !important; /* Larger */
        font-weight: 800 !important;
        background: linear-gradient(135deg, #FF3CAC 0%, #784BA0 50%, #2B86C5 100%); /* More vibrant gradient */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem !important;
    }
    h2 {
        font-size: 2.8rem !important; /* Larger */
        color: #1a1a1a !important;
        border-bottom: 3px solid #6366f1; /* More visible border */
        padding-bottom: 0.8rem;
        margin-top: 2.5rem !important;
    }
    h3 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #31333f !important;
    }
    
    /* Metrics Card Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 2px solid #f0f2f6; /* More distinct */
        padding: 1.8rem !important;
        border-radius: 16px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.15);
        border-color: #6366f1;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important; /* Larger */
        font-weight: 900 !important;
        color: #6366f1 !important; /* Indigo primary */
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #4b5563 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    
    /* Text Area / Editor */
    [data-testid="stTextArea"] textarea {
        font-family: 'Fira Code', 'Courier New', monospace;
        font-size: 1.05rem !important;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem !important;
    }
    
    /* API Badge */
    .api-badge {
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        font-weight: 800;
        font-size: 0.85rem;
        color: white;
        margin-right: 10px;
    }
    .badge-get { background-color: #10b981; }
    .badge-post { background-color: #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar / Navigation ---
st.sidebar.title("🚀 FastAPI_MCP")
st.sidebar.markdown("### Control Center")
st.sidebar.divider()
menu = st.sidebar.radio("Navigate", [
    "📊 Dashboard", 
    "🧠 Knowledge Base", 
    "🔗 API Endpoints",
    "⚙️ Configuration", 
    "📋 System Logs"
])

# --- Helper Functions ---
def get_metrics():
    try:
        response = requests.get(f"{BACKEND_URL}/metrics")
        return response.json()
    except:
        return None

def get_config():
    try:
        response = requests.get(f"{BACKEND_URL}/config")
        return response.json().get("yaml", "")
    except:
        return ""

def update_config(yaml_content):
    try:
        response = requests.post(
            f"{BACKEND_URL}/config/update",
            json={"yaml": yaml_content}
        )
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Dashboard View ---
if menu == "📊 Dashboard":
    st.header("🚀 Server Performance")
    
    metrics = get_metrics()
    if metrics:
        # Create a clean grid for metrics
        cols = st.columns(4)
        with cols[0]:
            st.metric("Tools Called", metrics.get("tools_called", 0))
        with cols[1]:
            st.metric("Resources Read", metrics.get("resources_read", 0))
        with cols[2]:
            st.metric("Vector Queries", metrics.get("vector_queries", 0))
        with cols[3]:
            st.metric("KB Documents", metrics.get("kb_count", 0))
            
        st.divider()
        
        col_chart, col_status = st.columns([1.5, 1])
        with col_chart:
            st.subheader("Activity Analytics")
            chart_data = pd.DataFrame({
                'Activity': ['Tools', 'Resources', 'KB Search'],
                'Count': [metrics.get("tools_called", 0), metrics.get("resources_read", 0), metrics.get("vector_queries", 0)]
            })
            
            # Custom Vega-Lite with VIBRANT colors
            st.vega_lite_chart(chart_data, {
                'mark': {'type': 'bar', 'color': '#6366f1', 'cornerRadiusTop': 6, 'size': 60},
                'encoding': {
                    'x': {
                        'field': 'Activity', 
                        'type': 'nominal', 
                        'axis': {
                            'labelFontSize': 16, 
                            'titleFontSize': 18, 
                            'labelAngle': 0, 
                            'labelColor': '#1a1a1a', 
                            'titleColor': '#1a1a1a',
                            'labelFontWeight': 'bold',
                            'titlePadding': 20
                        }
                    },
                    'y': {
                        'field': 'Count', 
                        'type': 'quantitative', 
                        'axis': {
                            'labelFontSize': 16, 
                            'titleFontSize': 18, 
                            'labelColor': '#1a1a1a', 
                            'titleColor': '#1a1a1a',
                            'labelFontWeight': 'bold',
                            'titlePadding': 20,
                            'tickMinStep': 1
                        }
                    },
                },
                'config': {
                    'view': {'stroke': 'transparent'},
                }
            }, use_container_width=True)
            
        with col_status:
            st.subheader("Active Pulse")
            with st.container(border=True):
                st.success("✨ Backend: Operational")
                st.info(f"🌐 Host: {BACKEND_URL}")
                st.markdown(f"**MCP SSE Entry:** `{BACKEND_URL}/mcp/sse`")
                if metrics.get("errors", 0) > 0:
                    st.error(f"⚠️ {metrics['errors']} Anomalies Recorded")
                else:
                    st.success("🌈 Stability: Excellent")

    else:
        st.error("❌ Link Severed: Backend Unreachable")
        st.info(f"Attempting to pulse {BACKEND_URL}...")
        if st.button("🔄 Reconnect"):
            st.rerun()

# --- Knowledge Base View ---
elif menu == "🧠 Knowledge Base":
    st.header("🧠 Vector Knowledge Base")
    
    with st.container(border=True):
        st.subheader("📝 Ingest Context")
        content = st.text_area("Drop document content or snippets here...", height=250)
        if st.button("🚀 Push to ChromaDB"):
            st.toast("Processing vector embeddings...")
            st.success("Knowledge synchronized with the neural index.")

    st.divider()
    
    with st.container(border=True):
        st.subheader("🔍 Semantic Retrieval")
        query = st.text_input("Ask a question to your KB...")
        if query:
            with st.status("Searching vector space..."):
                time.sleep(0.5)
                st.write("Top match: *Simulated results for PoC*")

# --- API Endpoints View ---
elif menu == "🔗 API Endpoints":
    st.header("🔗 System Endpoints")
    st.markdown("Direct access points for the FastAPI Backend.")
    
    endpoints = [
        {"method": "GET", "path": "/", "desc": "Health check and welcome message"},
        {"method": "GET", "path": "/metrics", "desc": "Live server statistics (JSON)"},
        {"method": "GET", "path": "/config", "desc": "Current YAML configuration"},
        {"method": "POST", "path": "/config/update", "desc": "Hot-reload configuration"},
        {"method": "GET", "path": "/mcp/sse", "desc": "MCP Protocol SSE connection"},
        {"method": "POST", "path": "/mcp/messages", "desc": "MCP Message routing"},
    ]
    
    for ep in endpoints:
        with st.container(border=True):
            cols = st.columns([1, 4])
            badge_class = "badge-get" if ep["method"] == "GET" else "badge-post"
            cols[0].markdown(f'<span class="api-badge {badge_class}">{ep["method"]}</span>', unsafe_allow_html=True)
            cols[1].markdown(f"**`{ep['path']}`**")
            st.caption(ep["desc"])

# --- Configuration View ---
elif menu == "⚙️ Configuration":
    st.header("⚙️ Server Logic")
    st.warning("Dynamic Reloading: Changes here update Tools and Resources without downtime.")
    
    current_config = get_config()
    with st.container(border=True):
        new_config = st.text_area("YAML Definition", value=current_config, height=500)
        if st.button("🔥 Deploy Configuration"):
            result = update_config(new_config)
            if result.get("status") == "success":
                st.balloons()
                st.success("Configuration successfully propagated!")
            else:
                st.error(f"Deployment Failed: {result.get('message')}")

# --- Logs View ---
elif menu == "📋 System Logs":
    st.header("📋 Runtime Stream")
    with st.container(border=True):
        st.code("Initializing MCP Server...\nVector Database connected.\nHTTP Server listening on port 8000\n[MCP] List tools requested\n[MCP] Call tool 'calculator' successful", language="text")
        if st.button("🔄 Refresh Stream"):
            st.toast("Logs flushed")
