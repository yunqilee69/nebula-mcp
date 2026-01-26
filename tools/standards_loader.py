"""
Nebula 规范加载器模块
负责从 standards 目录加载规范文件
"""

import os
from pathlib import Path
from typing import Dict


# 获取当前文件所在目录的父目录（项目根目录）
PROJECT_ROOT = Path(__file__).parent.parent
STANDARDS_DIR = PROJECT_ROOT / "standards"


class StandardsLoader:
    """Nebula 规范加载器"""

    # 规范文件映射
    STANDARDS_MAP: Dict[str, str] = {
        "architecture": "architecture.md",
        "arch": "architecture.md",
        "naming": "naming.md",
        "controller": "controller.md",
        "service": "service.md",
        "dao": "dao.md",
        "mapper": "dao.md",
        "converter": "converter.md",
        "api": "api.md",
        "exception": "exception.md",
        "constant": "constant_enum.md",
        "enum": "constant_enum.md",
        "other": "other.md",
        "database": "database_design.md",
        "db": "database_design.md",
        "config": "configuration_management.md",
        "configuration": "configuration_management.md",
    }

    @classmethod
    def load_standard(cls, category: str) -> str:
        """
        加载指定类别的规范内容

        Args:
            category: 规范类别

        Returns:
            规范内容
        """
        category = category.lower().strip()

        # 获取规范文件名
        filename = cls.STANDARDS_MAP.get(category)

        if not filename:
            return cls._get_unavailable_message(category)

        # 构建文件路径
        file_path = STANDARDS_DIR / filename

        # 检查文件是否存在
        if not file_path.exists():
            return f"错误：规范文件 '{filename}' 不存在，请检查文件路径：{file_path}"

        # 读取文件内容
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                return f"以下是 Nebula 中台 {category.upper()} 规范：\n\n{content}"
        except Exception as e:
            return f"错误：读取规范文件失败，原因：{str(e)}"

    @classmethod
    def _get_unavailable_message(cls, category: str) -> str:
        """
        生成不可用规范的消息

        Args:
            category: 规范类别

        Returns:
            错误消息
        """
        available = [
            "architecture (架构设计规范)",
            "naming (命名规范)",
            "controller (Controller 层规范)",
            "service (Service 层规范)",
            "dao/mapper (DAO 层规范)",
            "converter (数据转换规范)",
            "api (API 设计规范)",
            "exception (异常处理规范)",
            "constant/enum (常量和枚举规范)",
            "other (其他规范)",
            "database (数据库设计规范)",
            "config/configuration (配置管理规范)",
        ]

        return f"暂时不支持 '{category}' 规范。\n\n支持的规范：\n" + "\n".join(
            f"- {item}" for item in available
        )

    @classmethod
    def get_available_categories(cls) -> list:
        """
        获取所有可用的规范类别

        Returns:
            规范类别列表
        """
        return list(set(cls.STANDARDS_MAP.values()))

    @classmethod
    def get_aliases(cls) -> Dict[str, str]:
        """
        获取规范类别的别名映射

        Returns:
            别名映射字典
        """
        # 反转映射，从文件名到类别
        alias_map = {}
        for category, filename in cls.STANDARDS_MAP.items():
            if filename not in alias_map:
                alias_map[filename] = []
            alias_map[filename].append(category)

        return alias_map
