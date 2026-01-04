"""
编码规范工具模块
提供各种编程语言的编码规范检查和查询
"""

from mcp.server.fastmcp import FastMCP
from .base import BaseTool


# Python 编码规范
PYTHON_STANDARDS = """
# Python 编码规范 (PEP 8)

## 基本规范
1. 缩进：使用 4 个空格，不要使用 Tab
2. 行宽：每行最多 79 个字符
3. 编码：所有文件使用 UTF-8 编码
4. 导入：每个导入单独一行，标准库 -> 第三方库 -> 本地模块

## 命名规范
- 函数和变量：snake_case (例: user_name)
- 类：PascalCase (例: UserService)
- 常量：UPPER_SNAKE_CASE (例: MAX_COUNT)
- 私有成员：_leading_underscore

## 代码组织
1. 类定义之间空 2 行
2. 方法定义之间空 1 行
3. 在类内部，方法和第一个方法之间空 1 行

## 文档字符串
使用三引号文档字符串：
def function():
    \"\"\"函数功能的简要描述。

    更详细的描述（如果需要）。
    \"\"\"
    pass
"""

# Java 编码规范
JAVA_STANDARDS = """
# Java 编码规范

## 基本规范
1. 缩进：使用 4 个空格
2. 行宽：每行最多 120 个字符
3. 文件编码：UTF-8
4. 花括号：左花括号不换行

## 命名规范
- 类名：PascalCase (例: UserService)
- 方法名：camelCase (例: getUserById)
- 变量名：camelCase (例: userName)
- 常量：UPPER_SNAKE_CASE (例: MAX_COUNT)
- 包名：全小写，点分隔 (例: com.company.project)

## 代码组织
1. 导入顺序：标准库 -> 第三方库 -> 内部类
2. 类成员顺序：静态字段 -> 实例字段 -> 构造器 -> 方法
3. 访问修饰符：public > protected > private

## 注释规范
/**
 * 方法功能的 Javadoc 注释
 *
 * @param paramName 参数说明
 * @return 返回值说明
 */
"""


# JavaScript/TypeScript 编码规范
JAVASCRIPT_STANDARDS = """
# JavaScript/TypeScript 编码规范

## 基本规范
1. 缩进：使用 2 个空格
2. 行宽：每行最多 100 个字符
3. 分号：语句结束必须使用分号
4. 引号：优先使用单引号

## 命名规范
- 变量和函数：camelCase (例: userName, getUser)
- 类和组件：PascalCase (例: UserService)
- 常量：UPPER_SNAKE_CASE (例: API_BASE_URL)
- 私有成员：_leadingUnderscore

## TypeScript 特定
- 总是显式声明类型
- 使用 interface 定义对象结构
- 使用 type 定义联合类型或交叉类型
- 避免使用 any，优先使用 unknown

## 代码组织
1. 导入顺序：第三方库 -> 绝对路径 -> 相对路径
2. 组件结构：imports -> types -> constants -> helper functions -> main component
3. React 组件：hooks -> state -> effects -> event handlers -> render
"""


async def get_standard(language: str) -> str:
    """
    获取指定语言的编码规范

    Args:
        language: 编程语言名称

    Returns:
        该语言的编码规范文档
    """
    language = language.lower().strip()

    standards_map = {
        "python": PYTHON_STANDARDS,
        "py": PYTHON_STANDARDS,
        "java": JAVA_STANDARDS,
        "javascript": JAVASCRIPT_STANDARDS,
        "js": JAVASCRIPT_STANDARDS,
        "typescript": JAVASCRIPT_STANDARDS,
        "ts": JAVASCRIPT_STANDARDS,
    }

    standard = standards_map.get(language)

    if standard:
        return f"以下是 {language.upper()} 的编码规范：\n\n{standard}"
    else:
        available = ", ".join(set([k for k in standards_map.keys() if len(k) == len(k.replace(" ", ""))]))
        return f"暂时不支持 '{language}' 语言。\n\n支持的语言：{available}"


async def check_convention(code: str, language: str) -> str:
    """
    检查代码是否符合编码规范

    Args:
        code: 要检查的代码
        language: 代码语言

    Returns:
        检查结果和建议
    """
    language = language.lower().strip()
    issues = []
    suggestions = []

    # 基本的代码检查
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        # 检查行长度
        if len(line) > 100:
            issues.append(f"第 {i} 行过长（{len(line)} 字符），建议拆分")

        # 检查 Tab 使用
        if "\t" in line:
            issues.append(f"第 {i} 行使用了 Tab，建议使用空格")

        # Python 特定检查
        if language in ["python", "py"]:
            # 检查类名
            if line.strip().startswith("class ") and not line[0].isspace():
                class_name = line.split("class ")[1].split("(")[0].split(":")[0].strip()
                if not class_name[0].isupper() or "_" in class_name:
                    issues.append(f"第 {i} 行：类名 '{class_name}' 应使用 PascalCase")

            # 检查函数名
            if line.strip().startswith("def ") and not line[0].isspace():
                func_name = line.split("def ")[1].split("(")[0].strip()
                if " " in func_name or func_name[0].isupper():
                    issues.append(f"第 {i} 行：函数名 '{func_name}' 应使用 snake_case")

        # Java 特定检查
        elif language == "java":
            if line.strip().startswith("public class "):
                class_name = line.split("class ")[1].split("{")[0].strip()
                if not class_name[0].isupper():
                    issues.append(f"第 {i} 行：类名 '{class_name}' 应使用 PascalCase")

    # 生成建议
    if not issues:
        suggestions.append("✅ 代码基本符合规范！")
    else:
        suggestions.append(f"发现 {len(issues)} 个潜在问题：")
        suggestions.extend(issues)

        if language in ["python", "py"]:
            suggestions.append("\n💡 建议：使用 `pylint` 或 `flake8` 进行更全面的检查")
        elif language == "java":
            suggestions.append("\n💡 建议：使用 `Checkstyle` 或 `SonarQube` 进行更全面的检查")
        elif language in ["javascript", "js", "typescript", "ts"]:
            suggestions.append("\n💡 建议：使用 `ESLint` 进行更全面的检查")

    return "\n".join(suggestions)


class CodingStandardsTool(BaseTool):
    """编码规范工具类"""

    @classmethod
    def register(cls, mcp: FastMCP):
        """注册编码规范相关工具"""

        @mcp.tool()
        async def get_coding_standard(language: str) -> str:
            """
            获取指定语言的编码规范

            Args:
                language: 编程语言名称,如 python, java, javascript 等

            Returns:
                该语言的编码规范文档
            """
            return await get_standard(language)

        @mcp.tool()
        async def check_code_convention(code: str, language: str) -> str:
            """
            检查代码是否符合编码规范

            Args:
                code: 要检查的代码
                language: 代码语言

            Returns:
                检查结果和建议
            """
            return await check_convention(code, language)
