"""
nebula MCP Server
提供编码规范、分层架构规范等开发工具的 MCP 服务
"""

from mcp.server.fastmcp import FastMCP
from tools import register_all_tools

# 创建 FastMCP 实例
mcp = FastMCP(
    name="nebula-tools",
    instructions="提供 Nebula 中台 Java 后端编码规范等开发工具的 MCP 服务",
    host="0.0.0.0",
    port=8000,
)

# 注册所有工具
register_all_tools(mcp)


if __name__ == "__main__":
    # 运行服务器，使用 Streamable HTTP 传输
    mcp.run(transport="streamable-http")
