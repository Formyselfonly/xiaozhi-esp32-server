import traceback
import time
from collections import deque

from ..base import MemoryProviderBase, logger
from mem0 import Memory  # 使用 Mem0 Open Source
from core.utils.util import check_model_key

TAG = __name__

class MemoryProviderOpenSource(MemoryProviderBase):
    """使用 Mem0 Open Source 的记忆提供者"""
    
    def __init__(self, config, summary_memory=None):
        super().__init__(config)
        
        # 批量保存配置
        self.batch_size = config.get("batch_size", 5)
        self.pending_messages = deque()
        self.last_save_time = 0
        
        try:
            # 配置 Mem0 Open Source
            mem0_config = {
                "llm": {
                    "provider": "deepseek",
                    "config": {
                        "model": "deepseek-chat",
                        "api_key": config.get("deepseek_api_key", "")
                    }
                }
            }
            
            # 使用 Mem0 Open Source
            self.client = Memory(config=mem0_config)
            logger.bind(tag=TAG).info(f"成功初始化 Mem0 Open Source，使用 DeepSeek 作为 LLM，批量保存阈值: {self.batch_size} 轮对话")
            self.use_mem0 = True
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"初始化 Mem0 Open Source 时发生错误: {str(e)}")
            logger.bind(tag=TAG).error(f"详细错误: {traceback.format_exc()}")
            self.use_mem0 = False

    async def save_memory(self, msgs):
        if not self.use_mem0:
            return None
        if len(msgs) < 2:
            return None

        try:
            # 将当前对话添加到待保存队列
            current_messages = [
                {"role": message.role, "content": message.content}
                for message in msgs
                if message.role != "system"
            ]
            
            # 计算对话轮数
            user_messages = [msg for msg in current_messages if msg["role"] == "user"]
            assistant_messages = [msg for msg in current_messages if msg["role"] == "assistant"]
            dialogue_rounds = min(len(user_messages), len(assistant_messages))
            
            logger.bind(tag=TAG).debug(f"当前对话轮数: {dialogue_rounds}, 批量保存阈值: {self.batch_size}")
            
            # 如果达到批量保存阈值，则保存到 mem0
            if dialogue_rounds >= self.batch_size:
                logger.bind(tag=TAG).info(f"达到批量保存阈值({self.batch_size}轮)，开始保存到 Mem0 Open Source")
                
                # 使用 Mem0 Open Source 的 API
                result = self.client.add_memory(
                    messages=current_messages,
                    user_id=self.role_id
                )
                self.last_save_time = time.time()
                logger.bind(tag=TAG).debug(f"批量保存成功，结果: {result}")
                return result
            else:
                logger.bind(tag=TAG).debug(f"未达到批量保存阈值，跳过保存。当前: {dialogue_rounds}轮，阈值: {self.batch_size}轮")
                return None
                
        except Exception as e:
            logger.bind(tag=TAG).error(f"保存记忆失败: {str(e)}")
            return None

    async def force_save_memory(self, msgs):
        """强制保存记忆，用于连接关闭时保存剩余对话"""
        if not self.use_mem0:
            return None
        if len(msgs) < 2:
            return None

        try:
            messages = [
                {"role": message.role, "content": message.content}
                for message in msgs
                if message.role != "system"
            ]
            
            result = self.client.add_memory(
                messages=messages,
                user_id=self.role_id
            )
            logger.bind(tag=TAG).info(f"强制保存记忆成功，对话轮数: {len(messages)//2}")
            return result
        except Exception as e:
            logger.bind(tag=TAG).error(f"强制保存记忆失败: {str(e)}")
            return None

    async def query_memory(self, query: str) -> str:
        if not self.use_mem0:
            return ""
        try:
            # 使用 Mem0 Open Source 的查询 API
            results = self.client.search_memory(
                query=query,
                user_id=self.role_id
            )
            
            if not results:
                return ""

            # 格式化记忆结果
            memories = []
            for entry in results:
                memory = entry.get("memory", "")
                if memory:
                    memories.append(f"- {memory}")

            memories_str = "\n".join(memories)
            logger.bind(tag=TAG).debug(f"Query results: {memories_str}")
            return memories_str
        except Exception as e:
            logger.bind(tag=TAG).error(f"查询记忆失败: {str(e)}")
            return ""
