"""
工具基类模块
提供 MCP 工具注册的基础类和装饰器
"""

from typing import Callable, Any
from functools import wraps
from mcp.server.fastmcp import FastMCP


class ToolRegistry:
    """工具注册表"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = []
        return cls._instance

    def register(self, name: str, func: Callable, description: str = ""):
        """注册工具"""
        self._tools.append({
            "name": name,
            "func": func,
            "description": description
        })

    def get_tools(self):
        """获取所有注册的工具"""
        return self._tools

    def clear(self):
        """清空注册表(主要用于测试)"""
        self._tools = []


registry = ToolRegistry()


def register_tool(name: str = None, description: str = ""):
    """
    工具注册装饰器

    Args:
        name: 工具名称,默认使用函数名
        description: 工具描述

    Example:
        @register_tool("my_tool", "这是一个示例工具")
        async def my_function(param: str) -> str:
            return "result"
    """
    def decorator(func: Callable):
        tool_name = name or func.__name__
        registry.register(tool_name, func, description)
        return func
    return decorator


class BaseTool:
    """
    工具基类

    子类可以通过继承此类并实现 register 方法来注册工具
    """

    @classmethod
    def register(cls, mcp: FastMCP):
        """
        注册工具到 MCP 实例

        Args:
            mcp: FastMCP 实例
        """
        raise NotImplementedError("子类必须实现 register 方法")
