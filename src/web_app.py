"""
Crypto Insight Agent - Web 界面
基于 Streamlit 的友好交互界面
"""
import sys
from pathlib import Path
from datetime import datetime

# 获取项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

# 兼容 Streamlit Cloud Secrets
import os
if hasattr(st, 'secrets'):
    for key in ["DEEPSEEK_API_KEY", "ETHERSCAN_API_KEY", "BINANCE_API_KEY", 
                 "BINANCE_API_SECRET", "LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT"]:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

from src.graph.smart_workflow import create_smart_workflow, SmartAgentState
from src.tools.fear_greed_api import FearGreedAPI
from src.tools.etherscan_api import EtherscanAPI

# ========== 页面配置 ==========
st.set_page_config(
    page_title="Crypto Insight Agent",
    page_icon=str(project_root / "assets" / "icon.png"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 样式定义 ==========
st.markdown("""
<style>
    /* ===== 全局背景 ===== */
    .stApp {
        background: #0d1117;
    }
    
    /* ===== 标题 ===== */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f472b6 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #8b949e;
        margin-bottom: 2rem;
    }
    
    /* ===== 风险颜色 ===== */
    .risk-low { color: #4ade80; font-weight: 700; font-size: 1.2rem; }
    .risk-medium { color: #fbbf24; font-weight: 700; font-size: 1.2rem; }
    .risk-high { color: #f87171; font-weight: 700; font-size: 1.2rem; }
    
    /* ===== 卡片 ===== */
    .card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #f472b6;
        color: #e6edf3;
        font-size: 1rem;
        line-height: 1.8;
    }
    
    /* ===== 异常信号 ===== */
    .anomaly-high { color: #f87171; font-weight: 600; }
    .anomaly-medium { color: #fbbf24; font-weight: 600; }
    .anomaly-low { color: #4ade80; font-weight: 600; }
    
    /* ===== 指标盒子 ===== */
    .metric-box {
        text-align: center;
        padding: 1.2rem 0.8rem;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
    }
    
    /* ===== 按钮美化 ===== */
    .stButton > button {
        background: linear-gradient(135deg, #f472b6 0%, #a78bfa 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(244, 114, 182, 0.25) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(244, 114, 182, 0.4) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* 主按钮（type="primary"）更亮 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f687b3 0%, #b794f4 100%) !important;
        box-shadow: 0 4px 20px rgba(244, 114, 182, 0.4) !important;
    }
    
    /* ===== 下载按钮 ===== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #238636 0%, #1a6b2a 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(35, 134, 54, 0.25) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(35, 134, 54, 0.4) !important;
    }
    
    /* ===== Tab 标签 ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #8b949e;
        background: transparent;
        padding: 0.6rem 1.2rem;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #f472b6;
        background: #161b22;
        border-bottom: 2px solid #f472b6;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem;
        color: #e6edf3;
    }
    
    /* ===== 侧边栏 ===== */
    [data-testid="stSidebar"] {
        background: #010409;
        border-right: 1px solid #21262d;
    }
    [data-testid="stSidebar"] * {
        color: #e6edf3 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: #21262d !important;
        border: 1px solid #30363d !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: #f472b6 !important;
        background: #292e36 !important;
    }
    
    /* ===== 输入框 ===== */
    .stTextInput input {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 10px;
        color: #e6edf3;
        padding: 0.6rem 1rem;
    }
    .stTextInput input:focus {
        border-color: #f472b6;
        box-shadow: 0 0 0 3px rgba(244, 114, 182, 0.15);
    }
    .stTextInput input::placeholder {
        color: #484f58;
    }
    
    /* ===== 状态容器 ===== */
    .stStatus {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        color: #e6edf3;
    }
    
    /* ===== 分割线 ===== */
    hr {
        border-color: #21262d;
    }
    
    /* ===== 标题 ===== */
    h3 {
        color: #f0f6fc;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #21262d;
    }
    
    /* ===== 侧边栏度量 ===== */
    [data-testid="stSidebar"] .stMetricValue {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# ========== 初始化 ==========
@st.cache_resource
def get_workflow():
    return create_smart_workflow()


@st.cache_resource
def get_fear_greed_api():
    return FearGreedAPI()


# ========== 辅助函数 ==========
def get_risk_emoji(score):
    if score <= 30:
        return "🟢", "安心desu~", "risk-low"
    elif score <= 60:
        return "🟡", "稍微紧张", "risk-medium"
    else:
        return "🔴", "紧急情况！", "risk-high"


def format_price(price):
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.2f}"
    else:
        return f"${price:.4f}"


# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("## 🎸 Crypto Insight")
    st.markdown("---")
    
    # ===== API 设置（可折叠） =====
        # ===== API 设置（可折叠） =====
    # 没配 DeepSeek 时默认展开
    deepseek_configured = bool(os.getenv("DEEPSEEK_API_KEY", "")) and "your_" not in os.getenv("DEEPSEEK_API_KEY", "")
    with st.expander("⚙️ API 设置", expanded=not deepseek_configured):
        # 读取当前环境变量
        current_deepseek = os.getenv("DEEPSEEK_API_KEY", "")
        current_etherscan = os.getenv("ETHERSCAN_API_KEY", "")
        current_binance_key = os.getenv("BINANCE_API_KEY", "")
        current_binance_secret = os.getenv("BINANCE_API_SECRET", "")
        current_langsmith = os.getenv("LANGCHAIN_API_KEY", "")
        current_langsmith_project = os.getenv("LANGCHAIN_PROJECT", "crypto-insight-agent")
        current_news = os.getenv("NEWS_API_KEY", "")
        
        st.markdown("**🔴 必填**")
        
        deepseek_key = st.text_input(
            "🔑 DeepSeek API Key *这个好像不得不填欸*",
            value=current_deepseek if current_deepseek and "your_" not in current_deepseek else "",
            type="password",
            placeholder="sk-xxx（必填！萝卜子引擎依赖此 Key）",
            help="需要从 platform.deepseek.com 获取哦。不填的话萝卜子会没电的哦。"
        )
        
        st.markdown("---")
        st.markdown("**🟡 建议填写（因为是免费的...）**")
        
        etherscan_key = st.text_input(
            "⛓️ Etherscan API Key",
            value=current_etherscan if current_etherscan and "your_" not in current_etherscan else "",
            type="password",
            placeholder="免费注册获取，链上数据需要",
            help="可以从 etherscan.io 免费注册（链上数据）哦"
        )
        
        st.markdown("---")
        st.markdown("**可选（能增强萝卜子性能哦）**")
        
        binance_key = st.text_input(
            "📊 币安 API Key",
            value=current_binance_key if current_binance_key and "your_" not in current_binance_key else "",
            type="password",
            placeholder="可选，公开接口无需填写",
            help="可以从 binance.com 获取（更高请求频率）哦"
        )
        
        binance_secret = st.text_input(
            "📊 币安 Secret Key",
            value=current_binance_secret if current_binance_secret and "your_" not in current_binance_secret else "",
            type="password",
            placeholder="可选",
            help="可以配合 API Key 使用哦"
        )
        
        langsmith_key = st.text_input(
            "🔍 LangSmith API Key",
            value=current_langsmith if current_langsmith and "your_" not in current_langsmith else "",
            type="password",
            placeholder="可选，调试追踪用",
            help="可以从 smith.langchain.com 获取哦"
        )
        
        langsmith_project = st.text_input(
            "📝 LangSmith 项目名",
            value=current_langsmith_project,
            placeholder="crypto-insight-agent",
            help="LangSmith 项目名称"
        )
        
        news_key = st.text_input(
            "📰 News API Key",
            value=current_news if current_news and "your_" not in current_news else "",
            type="password",
            placeholder="可选，新闻数据",
            help="可以从 newsapi.org 获取哦"
        )
        
        if st.button("💾 保存所有设置", use_container_width=True):
            if deepseek_key:
                os.environ["DEEPSEEK_API_KEY"] = deepseek_key
            if etherscan_key:
                os.environ["ETHERSCAN_API_KEY"] = etherscan_key
            if binance_key:
                os.environ["BINANCE_API_KEY"] = binance_key
            if binance_secret:
                os.environ["BINANCE_API_SECRET"] = binance_secret
            if langsmith_key:
                os.environ["LANGCHAIN_API_KEY"] = langsmith_key
                os.environ["LANGCHAIN_PROJECT"] = langsmith_project
            if news_key:
                os.environ["NEWS_API_KEY"] = news_key
            st.cache_resource.clear()
            st.success("✅ 设置已经保存喽")
            st.rerun()
        
        
        st.caption("💡 设置仅保存在当前会话哦，可复制到 .env 文件持久化哦")
    
    st.markdown("---")
    
    # ===== API 状态指示 =====
    st.markdown("### 📡 API 状态")
    
    deepseek_ok = bool(os.getenv("DEEPSEEK_API_KEY", "")) and "your_" not in os.getenv("DEEPSEEK_API_KEY", "")
    etherscan_ok = bool(os.getenv("ETHERSCAN_API_KEY", "")) and "your_" not in os.getenv("ETHERSCAN_API_KEY", "")
    
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        if deepseek_ok:
            st.success("✅ DeepSeek")
        else:
            st.error("❌ DeepSeek")
    with status_col2:
        if etherscan_ok:
            st.success("✅ Etherscan")
        else:
            st.warning("⚠️ Etherscan")
    
    st.markdown("---")
    
    st.markdown("### ⚡ 快捷指令")
    
    if st.button("📊 看看市场心情", use_container_width=True):
        st.session_state.quick_action = "sentiment"
    if st.button("💰 ETH 观察中", use_container_width=True):
        st.session_state.quick_action = "eth"
    if st.button("⛽ Gas 多少钱？", use_container_width=True):
        st.session_state.quick_action = "gas"
    if st.button("₿ BTC 今天怎样", use_container_width=True):
        st.session_state.quick_action = "btc"
    
    st.markdown("---")
    st.markdown("### 📡 今日数据")
    
    try:
        fg = FearGreedAPI()
        fg_data = fg.get_current_index()
        if fg_data:
            st.metric(
                "😱 恐慌指数",
                f"{fg_data['value']}/100",
                delta=fg_data['value_classification'],
                delta_color="off"
            )
    except:
        pass
    
    st.markdown("---")
    st.caption("📖 数据来源: Binance | Etherscan | Alternative.me")
    st.caption("🧠 AI引擎: DeepSeek")


# ========== 主页面 ==========
st.markdown('<p class="main-header">🎸 Crypto Insight Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">✨ 和萝卜子一起看盘，今天也要加油哦！ | 数据驱动 · 智能决策</p>', unsafe_allow_html=True)

# ===== 智能输入区 =====
st.markdown("---")

# 示例提示
example_queries = [
    "BTC最近怎么样？能定投吗？",
    "ETH有什么异常吗？",
    "市场是不是又慌了？",
    "帮我看看SOL~",
    "ETH和BTC哪个更香？"
]

# 主输入框
st.markdown("### 💬 随便问，高性能萝卜子随时待命~")
user_query = st.text_input(
    "question_input",
    placeholder="例如：BTC最近怎么样？能定投吗？",
    label_visibility="collapsed"
)

# 示例快捷点击
st.markdown("**💡 试试这些问法：**")
example_cols = st.columns(len(example_queries))
for i, example in enumerate(example_queries):
    with example_cols[i]:
        if st.button(example, key=f"example_{i}", use_container_width=True):
            user_query = example
            st.session_state.user_query = user_query
            st.session_state.run_analysis = True
            st.rerun()

# 主按钮
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🔍 开始分析！", use_container_width=True, type="primary"):
        if user_query:
            st.session_state.user_query = user_query
            st.session_state.run_analysis = True
            st.rerun()
        else:
            st.warning("诶？还没输入问题哦~")

# 也支持回车触发
if user_query and user_query != st.session_state.get('_last_query', ''):
    st.session_state.user_query = user_query
    st.session_state._last_query = user_query
    st.session_state.run_analysis = True
    st.rerun()

# ===== 热门币种快捷按钮 =====
st.markdown("---")
st.markdown("**🔥 热门币种一键查看：**")
hot_col1, hot_col2, hot_col3, hot_col4, hot_col5, hot_col6 = st.columns(6)
with hot_col1:
    if st.button("₿ BTC", use_container_width=True):
        st.session_state.user_query = "BTC最近怎么样？"
        st.session_state.run_analysis = True
        st.rerun()
with hot_col2:
    if st.button("💎 ETH", use_container_width=True):
        st.session_state.user_query = "ETH最近怎么样？"
        st.session_state.run_analysis = True
        st.rerun()
with hot_col3:
    if st.button("🔷 SOL", use_container_width=True):
        st.session_state.user_query = "SOL最近怎么样？"
        st.session_state.run_analysis = True
        st.rerun()
with hot_col4:
    if st.button("🔶 BNB", use_container_width=True):
        st.session_state.user_query = "BNB最近怎么样？"
        st.session_state.run_analysis = True
        st.rerun()
with hot_col5:
    if st.button("🐶 DOGE", use_container_width=True):
        st.session_state.user_query = "DOGE最近怎么样？"
        st.session_state.run_analysis = True
        st.rerun()
with hot_col6:
    if st.button("❌ XRP", use_container_width=True):
        st.session_state.user_query = "XRP最近怎么样？"
        st.session_state.run_analysis = True
        st.rerun()


# ========== Session State 初始化 ==========
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""
if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False
if 'quick_action' not in st.session_state:
    st.session_state.quick_action = None
if '_last_query' not in st.session_state:
    st.session_state._last_query = ""


# ========== 处理快捷操作 ==========
if st.session_state.quick_action:
    action = st.session_state.quick_action
    if action == "sentiment":
        st.session_state.user_query = "市场情绪怎么样？"
    elif action == "eth":
        st.session_state.user_query = "ETH有什么异常吗？"
    elif action == "btc":
        st.session_state.user_query = "BTC有什么异常吗？"
    elif action == "gas":
        st.session_state.user_query = "Gas价格多少？"
    
    st.session_state.run_analysis = True
    st.session_state.quick_action = None
    st.rerun()


# ========== 执行分析 ==========
if st.session_state.run_analysis:
    st.session_state.run_analysis = False
    
    query = st.session_state.user_query
    
    # 用智能路由分析意图（先提取币种用于显示）
    from src.agents.smart_router import SmartRouter
    router = SmartRouter()
    intent = router.analyze_intent(query)
    symbol = intent.get("symbols", ["ETH"])[0] if intent.get("symbols") else "ETH"
    
    status_container = st.status(f"🔍 分析中：{query} ...", expanded=True)
    
    try:
        workflow = get_workflow()
        state = SmartAgentState(query=query, symbol=symbol)
        config = {"configurable": {"thread_id": f"web-{datetime.now().timestamp()}"}}
        
        with status_container:
            st.write(f"🎯 识别币种...中...: {symbol}")
            st.write(f"🧠 分析维度...中...: {', '.join(intent.get('actions', ['综合分析']))}")
            st.write("⏳ 正在采集数据，稍等一会哦...")
            
            result = workflow.invoke(state, config)
            
            if isinstance(result, dict):
                final_state = SmartAgentState(**result)
            else:
                final_state = result
            
            st.write("✅ 分析完成！")
        
        # ========== 显示结果 ==========
        if final_state.report:
            report = final_state.report
            
            st.markdown("---")
            
            # 顶部概览
            overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
            
            with overview_col1:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                emoji, risk_text, risk_class = get_risk_emoji(report.risk_score or 50)
                st.markdown(f'<p class="{risk_class}">{emoji} {risk_text}</p>', unsafe_allow_html=True)
                st.caption(f"风险评分: {report.risk_score:.0f}/100")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with overview_col2:
                if final_state.market_data:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    md = final_state.market_data
                    change_color = "green" if md.price_change_24h > 0 else "red"
                    st.markdown(f"### :{change_color}[{md.price_change_24h:+.2f}%]")
                    st.caption(f"价格: {format_price(md.current_price)}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with overview_col3:
                if final_state.sentiment_data:
                    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                    sd = final_state.sentiment_data
                    st.markdown(f"### {sd.fear_greed_index}/100")
                    st.caption(f"状态: {sd.fear_greed_label}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with overview_col4:
                st.markdown('<div class="metric-box">', unsafe_allow_html=True)
                anomaly_count = len(report.anomalies) if report.anomalies else 0
                anomaly_color = "green" if anomaly_count == 0 else "red"
                st.markdown(f"### :{anomaly_color}[{anomaly_count}]")
                st.caption("异常信号")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 摘要
            st.markdown("### 📝 萝卜子 总结")
            st.markdown(f'<div class="card">{report.summary}</div>', unsafe_allow_html=True)
            
            # 详细分析
            tab1, tab2, tab3, tab4 = st.tabs(["📈 市场情报", "⛓️ 链上数据", "🎭 情绪分析", "🚨 异常检测"])
            
            with tab1:
                st.markdown(report.market_analysis)
            with tab2:
                st.markdown(report.onchain_analysis)
            with tab3:
                st.markdown(report.sentiment_analysis)
            with tab4:
                if report.anomalies:
                    for anomaly in report.anomalies:
                        if isinstance(anomaly, dict):
                            severity = anomaly.get('severity', 'low')
                            description = anomaly.get('description', '')
                        else:
                            severity = anomaly.severity
                            description = anomaly.description
                        
                        severity_class = f"anomaly-{severity}"
                        st.markdown(f'<p class="{severity_class}">[{severity.upper()}] {description}</p>', unsafe_allow_html=True)
                else:
                    st.success("✅ 一切正常，没有发现异常~")
            
            # 底部操作
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("🔄 再来一次", use_container_width=True):
                    st.session_state.run_analysis = True
                    st.rerun()
            with col2:
                report_text = f"""
Crypto Insight 分析报告
======================
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
币种: {symbol}
风险评分: {report.risk_score:.0f}/100

{report.summary}

市场分析:
{report.market_analysis}

链上分析:
{report.onchain_analysis}

情绪分析:
{report.sentiment_analysis}
"""
                st.download_button(
                    "📥 保存报告",
                    report_text,
                    file_name=f"crypto_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    use_container_width=True
                )
    
    except Exception as e:
        st.error(f"呜呜...分析出错了: {str(e)}")
        status_container.update(label="❌ 分析失败", state="error")

else:
    # 检查 API 配置状态
    deepseek_ok = bool(os.getenv("DEEPSEEK_API_KEY", "")) and "your_" not in os.getenv("DEEPSEEK_API_KEY", "")
    etherscan_ok = bool(os.getenv("ETHERSCAN_API_KEY", "")) and "your_" not in os.getenv("ETHERSCAN_API_KEY", "")
    
    # 欢迎界面
    st.markdown("---")
    st.markdown("""
    <div style="background:#161b22; border:1px solid #30363d; border-radius:16px; padding:2rem; margin-top:1rem;">
        <h3 style="color:#f0f6fc; border:none; margin-bottom:1.2rem;">🎸 欢迎来到 Crypto Insight</h3>
        <p style="color:#e6edf3; font-size:1.05rem; line-height:2rem;">
            基于 DeepSeek + LangGraph 的智能加密货币分析萝卜子<br>
            我可是高性能的哦~~~
        </p>
        <ul style="color:#e6edf3; font-size:1rem; line-height:2.2rem; list-style:none; padding-left:0.5rem;">
            <li>📊 <b>实时行情</b> — 价格涨跌波动，全部✨闪闪发光✨地呈现！</li>
            <li>⛓️ <b>链上监控</b> — 大额转账资金流向，逃不过萝卜子的眼睛！</li>
            <li>🎭 <b>情绪感知</b> — 恐惧贪婪指数，今天市场心情如--何呢？</li>
            <li>🌟 <b>萝卜子研判</b> — 智能风险评估，交给萝卜子我吧！💪 <span style="font-size:0.85rem; color:#8b949e;">（不是姐姐但也很靠谱哦！）</span></li>
        </ul>
        <p style="color:#8b949e; font-size:0.95rem; margin-top:1.5rem;">
            👆 直接在上方输入框提问，萝卜子会自动识别币种和分析维度<br>
            今天也要Kirakira哦！✨
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # API 未配置提示
    if not deepseek_ok:
        st.warning("⚠️ 未配置 DeepSeek API Key，请在左侧「⚙️ API 设置」中填入，否则 AI 分析功能不可用")
    if not etherscan_ok:
        st.info("💡 建议配置 Etherscan API Key（免费），获取链上数据更全面")

# ========== 底部 ==========
st.markdown("---")
st.caption("⚠️ 免责声明：本工具仅供学习和参考，不构成任何投资建议。加密货币投资有风险，请谨慎决策。")