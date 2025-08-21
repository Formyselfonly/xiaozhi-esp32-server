#!/usr/bin/env python3
"""
WebSocket 客户端测试脚本
用于测试 Mem0ai 批量保存功能，无需连接嵌入式开发板
"""

import asyncio
import websockets
import json
import time
import uuid
from typing import List, Dict


class XiaozhiWebSocketClient:
    """小智 WebSocket 客户端测试类"""
    
    def __init__(self, server_url: str = "ws://localhost:8000/xiaozhi/v1/"):
        self.server_url = server_url
        self.device_id = f"test_device_{uuid.uuid4().hex[:8]}"
        self.client_id = f"test_client_{uuid.uuid4().hex[:8]}"
        self.websocket = None
        self.conversation_count = 0
        
    async def connect(self):
        """连接到服务器"""
        headers = {
            "device-id": self.device_id,
            "client-id": self.client_id
        }
        
        try:
            self.websocket = await websockets.connect(
                self.server_url,
                extra_headers=headers
            )
            print(f"✅ 成功连接到服务器: {self.server_url}")
            print(f"📱 设备ID: {self.device_id}")
            print(f"🆔 客户端ID: {self.client_id}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    async def send_text_message(self, text: str) -> str:
        """发送文本消息"""
        if not self.websocket:
            raise Exception("WebSocket 未连接")
        
        message = {
            "type": "text",
            "content": text
        }
        
        await self.websocket.send(json.dumps(message))
        print(f"📤 发送消息: {text}")
        
        # 接收响应
        response = await self.websocket.recv()
        response_data = json.loads(response)
        
        if response_data.get("type") == "text":
            content = response_data.get("content", "")
            print(f"📥 收到回复: {content}")
            self.conversation_count += 1
            return content
        else:
            print(f"📥 收到其他类型响应: {response_data}")
            return ""
    
    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 连接已关闭")


async def test_mem0ai_batch_save():
    """测试 Mem0ai 批量保存功能"""
    client = XiaozhiWebSocketClient()
    
    # 连接服务器
    if not await client.connect():
        return
    
    try:
        # 测试对话脚本
        test_conversations = [
            "你好",
            "今天天气怎么样？",
            "你叫什么名字？",
            "你会做什么？",
            "谢谢你的介绍",
            "再见"
        ]
        
        print("\n🚀 开始测试 Mem0ai 批量保存功能...")
        print("=" * 50)
        
        # 执行对话
        for i, message in enumerate(test_conversations, 1):
            print(f"\n🔄 第 {i} 轮对话:")
            print("-" * 30)
            
            response = await client.send_text_message(message)
            
            # 等待一下，模拟真实对话间隔
            await asyncio.sleep(1)
            
            # 如果是第5轮对话，说明达到了批量保存阈值
            if i == 5:
                print("🎯 达到批量保存阈值 (5轮对话)，应该触发保存")
            
            # 如果是最后一轮对话，说明连接即将关闭
            if i == len(test_conversations):
                print("🔚 最后一轮对话，连接关闭时会强制保存")
        
        print("\n" + "=" * 50)
        print(f"✅ 测试完成！总共进行了 {client.conversation_count} 轮对话")
        
        # 等待一下，让服务器有时间处理
        print("⏳ 等待服务器处理...")
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    
    finally:
        # 关闭连接
        await client.close()


async def test_memory_recall():
    """测试记忆召回功能"""
    client = XiaozhiWebSocketClient()
    
    # 连接服务器
    if not await client.connect():
        return
    
    try:
        print("\n🧠 开始测试记忆召回功能...")
        print("=" * 50)
        
        # 询问之前的对话内容
        recall_questions = [
            "我们之前聊过什么？",
            "你还记得我的名字吗？",
            "我们刚才聊了什么话题？"
        ]
        
        for question in recall_questions:
            print(f"\n❓ 询问: {question}")
            response = await client.send_text_message(question)
            
            # 分析回复是否包含记忆内容
            if any(keyword in response.lower() for keyword in ["之前", "记得", "聊过", "说过"]):
                print("✅ 检测到记忆召回")
            else:
                print("❌ 未检测到记忆召回")
            
            await asyncio.sleep(1)
        
    except Exception as e:
        print(f"❌ 记忆召回测试出错: {e}")
    
    finally:
        await client.close()


async def test_performance_comparison():
    """性能对比测试"""
    print("\n⚡ 开始性能对比测试...")
    print("=" * 50)
    
    # 测试不同 batch_size 的性能
    batch_sizes = [1, 3, 5, 10]
    
    for batch_size in batch_sizes:
        print(f"\n🔧 测试 batch_size = {batch_size}")
        
        # 创建新的客户端连接
        client = XiaozhiWebSocketClient()
        
        if not await client.connect():
            continue
        
        try:
            start_time = time.time()
            
            # 执行5轮对话
            test_messages = ["你好", "今天天气怎么样？", "你叫什么名字？", "谢谢", "再见"]
            
            for message in test_messages:
                await client.send_text_message(message)
                await asyncio.sleep(0.5)  # 模拟对话间隔
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"⏱️  总耗时: {total_time:.2f} 秒")
            print(f"📊 平均每轮对话: {total_time/len(test_messages):.2f} 秒")
            
        except Exception as e:
            print(f"❌ 测试出错: {e}")
        
        finally:
            await client.close()
            await asyncio.sleep(1)  # 等待连接完全关闭


async def test_error_handling():
    """错误处理测试"""
    print("\n🛡️ 开始错误处理测试...")
    print("=" * 50)
    
    # 测试无效的 WebSocket URL
    print("\n🔧 测试无效连接...")
    invalid_client = XiaozhiWebSocketClient("ws://localhost:9999/xiaozhi/v1/")
    await invalid_client.connect()
    
    # 测试正常连接
    print("\n🔧 测试正常连接...")
    client = XiaozhiWebSocketClient()
    
    if await client.connect():
        try:
            # 测试发送空消息
            print("\n📤 测试发送空消息...")
            await client.send_text_message("")
            
            # 测试发送特殊字符
            print("\n📤 测试发送特殊字符...")
            await client.send_text_message("!@#$%^&*()")
            
            # 测试发送长消息
            print("\n📤 测试发送长消息...")
            long_message = "这是一个很长的消息，" * 50
            await client.send_text_message(long_message)
            
        except Exception as e:
            print(f"❌ 错误处理测试出错: {e}")
        
        finally:
            await client.close()


async def interactive_test():
    """交互式测试"""
    print("\n🎮 开始交互式测试...")
    print("=" * 50)
    print("💡 你可以输入消息与AI对话，输入 'quit' 退出")
    
    client = XiaozhiWebSocketClient()
    
    if not await client.connect():
        return
    
    try:
        while True:
            # 获取用户输入
            user_input = input("\n💬 请输入消息: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not user_input:
                print("⚠️ 消息不能为空")
                continue
            
            # 发送消息
            try:
                response = await client.send_text_message(user_input)
            except Exception as e:
                print(f"❌ 发送消息失败: {e}")
                break
    
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出测试")
    
    finally:
        await client.close()


def main():
    """主函数"""
    print("🧪 小智 Mem0ai 批量保存功能测试工具")
    print("=" * 60)
    
    # 测试选项
    tests = {
        "1": ("批量保存功能测试", test_mem0ai_batch_save),
        "2": ("记忆召回功能测试", test_memory_recall),
        "3": ("性能对比测试", test_performance_comparison),
        "4": ("错误处理测试", test_error_handling),
        "5": ("交互式测试", interactive_test),
        "6": ("运行所有测试", lambda: asyncio.gather(
            test_mem0ai_batch_save(),
            test_memory_recall(),
            test_performance_comparison(),
            test_error_handling()
        ))
    }
    
    print("请选择测试类型:")
    for key, (name, _) in tests.items():
        print(f"  {key}. {name}")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    
    if choice in tests:
        test_name, test_func = tests[choice]
        print(f"\n🚀 开始执行: {test_name}")
        
        try:
            asyncio.run(test_func())
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
