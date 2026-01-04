"""
Cludix MCP Server
提供编码规范、分层规范等开发工具的 MCP 服务
"""

from mcp.server.fastmcp import FastMCP
from tools import register_all_tools

# 创建 FastMCP 实例
mcp = FastMCP(
    name="cludix-tools",
    instructions="提供编码规范、分层架构规范等开发工具的 MCP 服务"
)

# 注册所有工具
register_all_tools(mcp)


if __name__ == "__main__":
    # 运行服务器,使用 streamable-http 传输
    mcp.run(transport="streamable-http")
