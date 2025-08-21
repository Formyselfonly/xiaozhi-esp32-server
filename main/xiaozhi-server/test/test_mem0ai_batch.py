import unittest
import asyncio
import json
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from collections import deque

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.providers.memory.mem0ai.mem0ai import MemoryProvider
from core.utils.dialogue import Message


class TestMem0aiBatchSave(unittest.TestCase):
    """Mem0ai 批量保存功能单元测试"""

    def setUp(self):
        """测试前准备"""
        # 模拟配置
        self.config = {
            "api_key": "test_api_key_12345",
            "api_version": "v1.1",
            "batch_size": 5
        }
        
        # 创建测试用的对话消息
        self.test_messages = [
            Message(role="user", content="你好"),
            Message(role="assistant", content="你好！有什么可以帮助你的吗？"),
            Message(role="user", content="今天天气怎么样？"),
            Message(role="assistant", content="抱歉，我无法获取实时天气信息。"),
            Message(role="user", content="你叫什么名字？"),
            Message(role="assistant", content="我是小智，一个AI助手。"),
            Message(role="user", content="你会做什么？"),
            Message(role="assistant", content="我可以帮助你回答问题、聊天等。"),
            Message(role="user", content="谢谢你的介绍"),
            Message(role="assistant", content="不客气！很高兴能帮助你。"),
        ]

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_init_with_batch_size(self, mock_client):
        """测试初始化时正确设置批量保存阈值"""
        # 模拟客户端初始化成功
        mock_client.return_value = Mock()
        
        # 创建 MemoryProvider 实例
        provider = MemoryProvider(self.config)
        
        # 验证批量保存阈值设置正确
        self.assertEqual(provider.batch_size, 5)
        self.assertTrue(provider.use_mem0)
        self.assertIsInstance(provider.pending_messages, deque)

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_init_with_invalid_api_key(self, mock_client):
        """测试无效API Key时的降级处理"""
        # 模拟客户端初始化失败
        mock_client.side_effect = Exception("Invalid API key")
        
        # 创建 MemoryProvider 实例
        provider = MemoryProvider(self.config)
        
        # 验证降级到无记忆模式
        self.assertFalse(provider.use_mem0)

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_save_memory_below_threshold(self, mock_client):
        """测试未达到批量保存阈值时跳过保存"""
        # 模拟客户端
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 测试3轮对话（少于阈值5）
        test_messages = self.test_messages[:6]  # 3轮对话
        
        # 执行保存
        result = asyncio.run(provider.save_memory(test_messages))
        
        # 验证跳过保存
        self.assertIsNone(result)
        # 验证没有调用客户端保存方法
        mock_client_instance.add.assert_not_called()

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_save_memory_at_threshold(self, mock_client):
        """测试达到批量保存阈值时执行保存"""
        # 模拟客户端
        mock_client_instance = Mock()
        mock_client_instance.add.return_value = {"status": "success", "id": "test_memory_001"}
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 测试5轮对话（达到阈值）
        test_messages = self.test_messages[:10]  # 5轮对话
        
        # 执行保存
        result = asyncio.run(provider.save_memory(test_messages))
        
        # 验证执行保存
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        
        # 验证调用客户端保存方法
        mock_client_instance.add.assert_called_once()
        call_args = mock_client_instance.add.call_args
        
        # 验证传递的消息格式
        messages = call_args[0][0]  # 第一个参数是消息列表
        self.assertEqual(len(messages), 10)  # 5轮对话 = 10条消息
        
        # 验证消息格式正确
        for msg in messages:
            self.assertIn("role", msg)
            self.assertIn("content", msg)
            self.assertIn(msg["role"], ["user", "assistant"])

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_save_memory_above_threshold(self, mock_client):
        """测试超过批量保存阈值时执行保存"""
        # 模拟客户端
        mock_client_instance = Mock()
        mock_client_instance.add.return_value = {"status": "success", "id": "test_memory_002"}
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 测试6轮对话（超过阈值）
        test_messages = self.test_messages[:12]  # 6轮对话
        
        # 执行保存
        result = asyncio.run(provider.save_memory(test_messages))
        
        # 验证执行保存
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        
        # 验证调用客户端保存方法
        mock_client_instance.add.assert_called_once()
        call_args = mock_client_instance.add.call_args
        
        # 验证传递的消息数量
        messages = call_args[0][0]
        self.assertEqual(len(messages), 12)  # 6轮对话 = 12条消息

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_force_save_memory(self, mock_client):
        """测试强制保存功能"""
        # 模拟客户端
        mock_client_instance = Mock()
        mock_client_instance.add.return_value = {"status": "success", "id": "test_memory_003"}
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 测试强制保存（即使只有2轮对话）
        test_messages = self.test_messages[:4]  # 2轮对话
        
        # 执行强制保存
        result = asyncio.run(provider.force_save_memory(test_messages))
        
        # 验证执行保存
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        
        # 验证调用客户端保存方法
        mock_client_instance.add.assert_called_once()
        call_args = mock_client_instance.add.call_args
        
        # 验证传递的消息数量
        messages = call_args[0][0]
        self.assertEqual(len(messages), 4)  # 2轮对话 = 4条消息

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_query_memory(self, mock_client):
        """测试查询记忆功能"""
        # 模拟客户端
        mock_client_instance = Mock()
        mock_client_instance.search.return_value = {
            "results": [
                {
                    "memory": "用户询问了天气情况",
                    "updated_at": "2024-01-01T12:00:00.000Z"
                },
                {
                    "memory": "用户询问了AI助手的名字",
                    "updated_at": "2024-01-01T12:05:00.000Z"
                }
            ]
        }
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 执行查询
        result = asyncio.run(provider.query_memory("我们之前聊过什么？"))
        
        # 验证查询结果
        self.assertIsNotNone(result)
        self.assertIn("用户询问了天气情况", result)
        self.assertIn("用户询问了AI助手的名字", result)
        self.assertIn("[2024-01-01 12:00:00]", result)
        self.assertIn("[2024-01-01 12:05:00]", result)
        
        # 验证调用客户端查询方法
        mock_client_instance.search.assert_called_once()

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_save_memory_with_system_messages(self, mock_client):
        """测试保存时过滤系统消息"""
        # 模拟客户端
        mock_client_instance = Mock()
        mock_client_instance.add.return_value = {"status": "success", "id": "test_memory_004"}
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 创建包含系统消息的对话
        messages_with_system = [
            Message(role="system", content="你是一个有用的AI助手"),
            Message(role="user", content="你好"),
            Message(role="assistant", content="你好！"),
            Message(role="system", content="记住用户偏好"),
            Message(role="user", content="再见"),
            Message(role="assistant", content="再见！"),
        ]
        
        # 执行保存
        result = asyncio.run(provider.save_memory(messages_with_system))
        
        # 验证执行保存
        self.assertIsNotNone(result)
        
        # 验证调用客户端保存方法
        call_args = mock_client_instance.add.call_args
        messages = call_args[0][0]
        
        # 验证系统消息被过滤
        self.assertEqual(len(messages), 4)  # 只有user和assistant消息
        for msg in messages:
            self.assertNotEqual(msg["role"], "system")

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_save_memory_error_handling(self, mock_client):
        """测试保存时的错误处理"""
        # 模拟客户端保存失败
        mock_client_instance = Mock()
        mock_client_instance.add.side_effect = Exception("Network error")
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 测试5轮对话
        test_messages = self.test_messages[:10]
        
        # 执行保存
        result = asyncio.run(provider.save_memory(test_messages))
        
        # 验证错误处理
        self.assertIsNone(result)

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_query_memory_error_handling(self, mock_client):
        """测试查询时的错误处理"""
        # 模拟客户端查询失败
        mock_client_instance = Mock()
        mock_client_instance.search.side_effect = Exception("API error")
        mock_client.return_value = mock_client_instance
        
        provider = MemoryProvider(self.config)
        provider.role_id = "test_user_001"
        
        # 执行查询
        result = asyncio.run(provider.query_memory("test query"))
        
        # 验证错误处理
        self.assertEqual(result, "")

    def test_dialogue_rounds_calculation(self):
        """测试对话轮数计算逻辑"""
        # 测试不同长度的对话
        test_cases = [
            (2, 1),   # 2条消息 = 1轮对话
            (4, 2),   # 4条消息 = 2轮对话
            (6, 3),   # 6条消息 = 3轮对话
            (10, 5),  # 10条消息 = 5轮对话
            (12, 6),  # 12条消息 = 6轮对话
        ]
        
        for message_count, expected_rounds in test_cases:
            with self.subTest(message_count=message_count):
                messages = self.test_messages[:message_count]
                
                # 手动计算对话轮数（模拟代码逻辑）
                user_messages = [msg for msg in messages if msg.role == "user"]
                assistant_messages = [msg for msg in messages if msg.role == "assistant"]
                dialogue_rounds = min(len(user_messages), len(assistant_messages))
                
                self.assertEqual(dialogue_rounds, expected_rounds)

    def test_config_default_values(self):
        """测试配置默认值"""
        # 测试不提供 batch_size 时的默认值
        config_without_batch = {
            "api_key": "test_key",
            "api_version": "v1.1"
        }
        
        with patch('core.providers.memory.mem0ai.mem0ai.MemoryClient'):
            provider = MemoryProvider(config_without_batch)
            # 默认值应该是 5（根据你的修改）
            self.assertEqual(provider.batch_size, 5)


class TestMem0aiIntegration(unittest.TestCase):
    """Mem0ai 集成测试"""

    @patch('core.providers.memory.mem0ai.mem0ai.MemoryClient')
    def test_full_conversation_flow(self, mock_client):
        """测试完整对话流程"""
        # 模拟客户端
        mock_client_instance = Mock()
        mock_client_instance.add.return_value = {"status": "success", "id": "test_memory_005"}
        mock_client_instance.search.return_value = {
            "results": [
                {
                    "memory": "用户进行了测试对话",
                    "updated_at": "2024-01-01T12:00:00.000Z"
                }
            ]
        }
        mock_client.return_value = mock_client_instance
        
        config = {
            "api_key": "test_api_key",
            "batch_size": 3  # 设置较小的阈值便于测试
        }
        
        provider = MemoryProvider(config)
        provider.role_id = "test_user_002"
        
        # 模拟多轮对话
        conversation_rounds = [
            # 第1-2轮：不保存
            [Message(role="user", content="你好"), Message(role="assistant", content="你好！")],
            [Message(role="user", content="今天天气怎么样？"), Message(role="assistant", content="天气不错")],
            
            # 第3轮：触发保存
            [Message(role="user", content="你叫什么名字？"), Message(role="assistant", content="我是小智")],
            
            # 第4-5轮：不保存
            [Message(role="user", content="谢谢"), Message(role="assistant", content="不客气")],
            [Message(role="user", content="再见"), Message(role="assistant", content="再见！")],
        ]
        
        save_count = 0
        
        # 执行对话流程
        for i, messages in enumerate(conversation_rounds, 1):
            result = asyncio.run(provider.save_memory(messages))
            if result is not None:
                save_count += 1
        
        # 验证保存次数（应该在第3轮和第6轮保存）
        self.assertEqual(save_count, 1)  # 只有第3轮会保存
        
        # 测试查询
        query_result = asyncio.run(provider.query_memory("我们聊过什么？"))
        self.assertIsNotNone(query_result)
        self.assertIn("用户进行了测试对话", query_result)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
