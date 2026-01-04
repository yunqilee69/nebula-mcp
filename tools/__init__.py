"""
工具模块初始化文件
自动发现并注册所有工具到 MCP 实例
"""

from mcp.server.fastmcp import FastMCP
from .base import BaseTool
from .coding_standards import CodingStandardsTool
from .layer_standards import LayerStandardsTool


def register_all_tools(mcp: FastMCP):
    """
    自动发现并注册所有工具到 MCP 实例

    Args:
        mcp: FastMCP 实例
    """
    # 导入所有工具类并注册
    tools = [
        CodingStandardsTool,
        LayerStandardsTool,
    ]

    for tool_cls in tools:
        if issubclass(tool_cls, BaseTool):
            tool_cls.register(mcp)


__all__ = ["register_all_tools", "BaseTool"]
