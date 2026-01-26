"""
nebula MCP Server
提供编码规范、分层架构规范等开发工具的 MCP 服务
"""

from mcp.server.fastmcp import FastMCP
from tools import register_all_tools
from starlette.responses import JSONResponse
from starlette.requests import Request

# 创建 FastMCP 实例
mcp = FastMCP(
    name="nebula-tools",
    instructions="提供 Nebula 中台 Java 后端编码规范等开发工具的 MCP 服务",
    host="127.0.0.1",
    port=8000,
)

# 注册所有工具
register_all_tools(mcp)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint to verify server is running"""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "nebula-tools",
            "transport": "streamable-http",
            "version": "0.1.0",
        }
    )


if __name__ == "__main__":
    # 运行服务器，使用 Streamable HTTP 传输
    mcp.run(transport="streamable-http")
