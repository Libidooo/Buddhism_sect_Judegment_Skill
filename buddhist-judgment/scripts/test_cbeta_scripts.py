#!/usr/bin/env python3
"""
CBETA脚本综合测试脚本

功能：
- 测试所有CBETA相关脚本的完整性
- 验证索引文件是否正确加载
- 测试各种查询功能
- 生成测试报告

使用示例：
python scripts/test_cbeta_scripts.py
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# 动态获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"命令: {cmd}")
    print('-'*60)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT)
        )

        if result.returncode == 0:
            print(f"✓ 成功")
            if result.stdout:
                print(f"输出: {result.stdout[:500]}")
            return True, result.stdout
        else:
            print(f"✗ 失败 (返回码: {result.returncode})")
            print(f"错误: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"✗ 超时")
        return False, "命令超时"
    except Exception as e:
        print(f"✗ 异常: {str(e)}")
        return False, str(e)

def main():
    """主测试函数"""
    print("CBETA脚本综合测试")
    print("="*60)

    test_results = []

    # 测试1: cbeta_query.py - T号查询
    success, output = run_command(
        'python scripts/cbeta_query.py --t-number T0262',
        "cbeta_query.py - T号查询 (T0262)"
    )
    test_results.append(("T号查询", success))

    # 测试2: cbeta_query.py - 经名查询
    success, output = run_command(
        'python scripts/cbeta_query.py --sutra-name 金刚经',
        "cbeta_query.py - 经名查询 (金刚经)"
    )
    test_results.append(("经名查询", success))

    # 测试3: cbeta_query.py - 关键词查询
    success, output = run_command(
        'python scripts/cbeta_query.py --keyword 观世音',
        "cbeta_query.py - 关键词查询 (观世音)"
    )
    test_results.append(("关键词查询", success))

    # 测试4: sutra_lookup.py - 按卷别查找
    success, output = run_command(
        'python scripts/sutra_lookup.py --volume 卷二',
        "sutra_lookup.py - 按卷别查找 (卷二)"
    )
    test_results.append(("按卷别查找", success))

    # 测试5: sutra_lookup.py - 按T号查找
    success, output = run_command(
        'python scripts/sutra_lookup.py --t-number 0262',
        "sutra_lookup.py - 按T号查找 (0262)"
    )
    test_results.append(("按T号查找", success))

    # 测试6: sutra_lookup.py - 按经名查找
    success, output = run_command(
        'python scripts/sutra_lookup.py --name 妙法莲华经',
        "sutra_lookup.py - 按经名查找 (妙法莲华经)"
    )
    test_results.append(("按经名查找", success))

    # 测试7: sutra_lookup.py - 按关键词查找
    success, output = run_command(
        'python scripts/sutra_lookup.py --keyword 弥勒',
        "sutra_lookup.py - 按关键词查找 (弥勒)"
    )
    test_results.append(("按关键词查找", success))

    # 测试8: cbeta_index_search.py - 全文搜索
    success, output = run_command(
        'python scripts/cbeta_index_search.py --search "药师"',
        "cbeta_index_search.py - 全文搜索 (药师)"
    )
    test_results.append(("全文搜索", success))

    # 测试9: cbeta_index_search.py - 按卷别搜索
    success, output = run_command(
        'python scripts/cbeta_index_search.py --search "佛" --volume 卷三',
        "cbeta_index_search.py - 按卷别搜索 (卷三)"
    )
    test_results.append(("按卷别搜索", success))

    # 测试10: cbeta_index_search.py - 精确匹配
    success, output = run_command(
        'python scripts/cbeta_index_search.py --search "T0262" --exact',
        "cbeta_index_search.py - 精确匹配 (T0262)"
    )
    test_results.append(("精确匹配", success))

    # 测试11: cbeta_index_search.py - 统计信息
    success, output = run_command(
        'python scripts/cbeta_index_search.py --stats',
        "cbeta_index_search.py - 统计信息"
    )
    test_results.append(("统计信息", success))

    # 测试12: 检查索引文件是否存在
    print(f"\n{'='*60}")
    print("测试: 检查索引文件是否存在")
    print('-'*60)

    assets_dir = PROJECT_ROOT / "assets"
    required_files = [
        "cbeta-t-number-index.md",
        "cbeta-keyword-index.md",
        "cbeta-volume-query-path.md"
    ]

    all_files_exist = True
    for file_name in required_files:
        file_path = assets_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ {file_name} 存在 (大小: {size} 字节)")
        else:
            print(f"✗ {file_name} 不存在")
            all_files_exist = False

    test_results.append(("索引文件存在性", all_files_exist))

    # 测试13: 检查脚本文件是否存在
    print(f"\n{'='*60}")
    print("测试: 检查脚本文件是否存在")
    print('-'*60)

    scripts_dir = PROJECT_ROOT / "scripts"
    required_scripts = [
        "cbeta_query.py",
        "sutra_lookup.py",
        "cbeta_index_search.py"
    ]

    all_scripts_exist = True
    for script_name in required_scripts:
        script_path = scripts_dir / script_name
        if script_path.exists():
            size = script_path.stat().st_size
            print(f"✓ {script_name} 存在 (大小: {size} 字节)")
        else:
            print(f"✗ {script_name} 不存在")
            all_scripts_exist = False

    test_results.append(("脚本文件存在性", all_scripts_exist))

    # 生成测试报告
    print(f"\n{'='*60}")
    print("测试报告摘要")
    print('='*60)

    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    failed_tests = total_tests - passed_tests

    print(f"\n总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"通过率: {(passed_tests/total_tests*100):.1f}%")

    print(f"\n详细结果:")
    for test_name, success in test_results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {status} - {test_name}")

    # 最终结果
    if failed_tests == 0:
        print(f"\n{'='*60}")
        print("✓ 所有测试通过！CBETA索引系统工作正常。")
        print('='*60)
        return 0
    else:
        print(f"\n{'='*60}")
        print(f"✗ 有 {failed_tests} 个测试失败，请检查错误信息。")
        print('='*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
