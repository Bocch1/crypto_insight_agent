# src/main.py
import os
from dotenv import load_dotenv

load_dotenv()

print("✅ 项目结构初始化成功！")
print(f"当前虚拟环境: {os.getenv('VIRTUAL_ENV', '未激活')}")