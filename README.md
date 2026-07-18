# 🎸 Crypto Insight Agent

基于 DeepSeek + LangGraph 的智能加密货币分析萝卜子，我可是高性能的哦~~~

✨ 功能特色

📊 实时行情 — 价格涨跌波动，全部✨闪闪发光✨地呈现
⛓️ 链上监控 — 大额转账资金流向，逃不过萝卜子的眼睛
🎭 情绪感知 — 恐惧贪婪指数，今天市场心情如--何呢
🤖 萝卜子研判 — 智能风险评估，交给萝卜子我吧💪


🚀 快速开始

方式一：一键启动（推荐）

Windows：双击 start.bat

Mac/Linux：
chmod +x start.sh
./start.sh

方式二：手动启动

# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
streamlit run src/web_app.py

方式三：Streamlit Cloud（免安装）

直接访问部署好的链接，打开即用。


🔑 获取 API Key

| API       | 用途         | 地址                                      | 是否必填     |
|-----------|-------------|------------------------------------------|-------------|
| DeepSeek  | AI 分析引擎   | platform.deepseek.com/api_keys           | 🔴 必填      |
| Etherscan | 链上数据      | etherscan.io/register                    | 🟡 建议（免费）|
| 币安      | 市场数据      | 公开接口无需 Key                           | ⚪ 可选      |

💡 也可以在启动后，在网页左侧「⚙️ API 设置」中直接填写，无需编辑配置文件。


🌐 部署到 Streamlit Cloud

1. Fork 本仓库到你的 GitHub
2. 打开 share.streamlit.io
3. 点击 New app，选择仓库，主文件路径填 streamlit_app.py
4. 点击 Advanced settings → Secrets，填入：
   DEEPSEEK_API_KEY = "sk-你的密钥"
   ETHERSCAN_API_KEY = "你的密钥"
5. 点击 Deploy，获得公开链接 🎉


🛠️ 技术栈

编排框架：LangGraph（多 Agent 状态图编排）
AI 引擎：DeepSeek（智能路由 + 报告生成）
数据源：Binance API / Etherscan API / Fear & Greed Index
前端：Streamlit


❓ 常见问题

Q: 为什么分析 ETH 而不是我输入的币种？
A: 请在左侧「⚙️ API 设置」中确认已填入 DeepSeek API Key，AI 引擎依赖它来识别币种。

Q: 链上数据显示为空？
A: 请配置 Etherscan API Key（免费注册即可），否则链上数据不可用。

Q: 支持哪些币种？
A: BTC、ETH、BNB、SOL、XRP、DOGE、ADA、AVAX、DOT、MATIC 等主流币种。


⚠️ 免责声明

本工具仅供学习和参考，不构成任何投资建议。加密货币投资有风险，请谨慎决策。萝卜子虽然可爱但不对你的盈亏负责哦~