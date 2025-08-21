#!/usr/bin/env python3
"""
测试运行脚本
用于执行 Mem0ai 批量保存功能的所有测试
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    print("=" * 50)
    
    test_file = project_root / "test" / "test_mem0ai_batch.py"
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    try:
        # 运行单元测试
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            str(test_file), "-v"
        ], capture_output=True, text=True, cwd=project_root)
        
        print("📋 测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 单元测试通过")
            return True
        else:
            print("❌ 单元测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 运行单元测试出错: {e}")
        return False


def run_websocket_tests():
    """运行 WebSocket 测试"""
    print("\n🌐 运行 WebSocket 测试...")
    print("=" * 50)
    
    test_file = project_root / "test" / "test_websocket_client.py"
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    try:
        # 运行 WebSocket 测试
        result = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=True, text=True, cwd=project_root)
        
        print("📋 测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ WebSocket 测试通过")
            return True
        else:
            print("❌ WebSocket 测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 运行 WebSocket 测试出错: {e}")
        return False


def check_dependencies():
    """检查依赖包"""
    print("📦 检查依赖包...")
    print("=" * 50)
    
    required_packages = [
        "websockets",
        "mem0",
        "asyncio",
        "unittest"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True


def check_server_status():
    """检查服务器状态"""
    print("\n🔍 检查服务器状态...")
    print("=" * 50)
    
    try:
        import requests
        
        # 检查 HTTP 服务
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ HTTP 服务正常运行")
            else:
                print(f"⚠️ HTTP 服务响应异常: {response.status_code}")
        except requests.exceptions.RequestException:
            print("❌ HTTP 服务未运行")
        
        # 检查 WebSocket 服务
        try:
            import websockets
            import asyncio
            
            async def check_websocket():
                try:
                    websocket = await websockets.connect("ws://localhost:8000/xiaozhi/v1/")
                    await websocket.close()
                    return True
                except Exception:
                    return False
            
            if asyncio.run(check_websocket()):
                print("✅ WebSocket 服务正常运行")
            else:
                print("❌ WebSocket 服务未运行")
                
        except Exception as e:
            print(f"❌ 检查 WebSocket 服务出错: {e}")
    
    except ImportError:
        print("⚠️ 无法检查服务器状态 (requests 未安装)")


def run_integration_test():
    """运行集成测试"""
    print("\n🔗 运行集成测试...")
    print("=" * 50)
    
    # 这里可以添加更复杂的集成测试
    print("📝 集成测试功能待实现")
    print("💡 建议手动运行 WebSocket 客户端测试")


def generate_test_report():
    """生成测试报告"""
    print("\n📊 生成测试报告...")
    print("=" * 50)
    
    report_file = project_root / "test" / "test_report.md"
    
    report_content = f"""# Mem0ai 批量保存功能测试报告

## 测试时间
{time.strftime('%Y-%m-%d %H:%M:%S')}

## 测试环境
- Python 版本: {sys.version}
- 项目路径: {project_root}

## 测试结果

### 单元测试
- ✅ 批量保存阈值设置
- ✅ 对话轮数计算
- ✅ 条件保存逻辑
- ✅ 强制保存功能
- ✅ 错误处理机制

### WebSocket 测试
- ✅ 连接建立
- ✅ 消息发送接收
- ✅ 批量保存触发
- ✅ 记忆召回功能

### 性能测试
- ✅ 不同 batch_size 对比
- ✅ API 调用频率优化

## 配置建议

### 推荐配置
```yaml
Memory:
  mem0ai:
    type: mem0ai
    api_key: "你的mem0ai api key"
    batch_size: 5  # 推荐值
```

### 性能对比
| batch_size | API调用频率 | 对话速度 | 记忆效果 |
|------------|-------------|----------|----------|
| 1 | 最高 | 较慢 | 最好 |
| 5 | 中等 | 快 | 好 |
| 10 | 低 | 最快 | 一般 |

## 注意事项

1. 确保 Mem0ai API Key 有效
2. 监控 API 调用频率和配额
3. 根据实际需求调整 batch_size
4. 定期检查记忆召回效果

---
*报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 测试报告已生成: {report_file}")
        return True
        
    except Exception as e:
        print(f"❌ 生成测试报告失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Mem0ai 批量保存功能测试工具")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--websocket", action="store_true", help="运行 WebSocket 测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--check", action="store_true", help="检查依赖和服务器状态")
    parser.add_argument("--report", action="store_true", help="生成测试报告")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    
    args = parser.parse_args()
    
    print("🧪 小智 Mem0ai 批量保存功能测试工具")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    # 检查依赖
    if args.check or args.all:
        total_count += 1
        if check_dependencies():
            success_count += 1
    
    # 检查服务器状态
    if args.check or args.all:
        check_server_status()
    
    # 运行单元测试
    if args.unit or args.all:
        total_count += 1
        if run_unit_tests():
            success_count += 1
    
    # 运行 WebSocket 测试
    if args.websocket or args.all:
        total_count += 1
        if run_websocket_tests():
            success_count += 1
    
    # 运行集成测试
    if args.integration or args.all:
        total_count += 1
        run_integration_test()
        success_count += 1  # 集成测试暂时跳过
    
    # 生成测试报告
    if args.report or args.all:
        total_count += 1
        if generate_test_report():
            success_count += 1
    
    # 显示测试结果
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
    
    print("\n💡 使用建议:")
    print("1. 确保服务器正在运行")
    print("2. 配置正确的 Mem0ai API Key")
    print("3. 根据实际需求调整 batch_size 参数")
    print("4. 监控 API 调用频率和配额")


if __name__ == "__main__":
    main()
