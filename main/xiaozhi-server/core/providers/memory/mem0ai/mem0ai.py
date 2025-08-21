import traceback
import time
from collections import deque

from ..base import MemoryProviderBase, logger
from mem0 import MemoryClient
from core.utils.util import check_model_key

TAG = __name__
# 禁用mem0ai的telemetry
MEM0_TELEMETRY=False

class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory=None):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.api_version = config.get("api_version", "v1.1")
        
        # 批量保存配置
        self.batch_size = config.get("batch_size", 5)  # 默认每轮都保存
        self.pending_messages = deque()  # 待保存的消息队列
        self.last_save_time = 0  # 上次保存时间
        
        model_key_msg = check_model_key("Mem0ai", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)
            self.use_mem0 = False
            return
        else:
            self.use_mem0 = True

        try:
            # 配置 Mem0ai 使用 DeepSeek 作为内部 LLM
            mem0_config = {
                "llm": {
                    "provider": "deepseek",
                    "config": {
                        "model": "deepseek-chat",
                        "api_key": config.get("deepseek_api_key", "sk-27df0a24e6ab4c28aada3a1f04ce923b")  # 从配置中获取 DeepSeek API Key
                    }
                }
            }
            
            self.client = MemoryClient(api_key=self.api_key, config=mem0_config)
            logger.bind(tag=TAG).info(f"成功连接到 Mem0ai 服务，使用 {mem0_config["llm"]["config"]["model"]} 作为内部 LLM，批量保存阈值: {self.batch_size} 轮对话")
        except Exception as e:
            logger.bind(tag=TAG).error(f"连接到 Mem0ai 服务时发生错误: {str(e)}")
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
            
            # 计算对话轮数（用户和助手的对话对）
            user_messages = [msg for msg in current_messages if msg["role"] == "user"]
            assistant_messages = [msg for msg in current_messages if msg["role"] == "assistant"]
            dialogue_rounds = min(len(user_messages), len(assistant_messages))
            
            logger.bind(tag=TAG).debug(f"当前对话轮数: {dialogue_rounds}, 批量保存阈值: {self.batch_size}")
            
            # 如果达到批量保存阈值，则保存到 mem0ai
            if dialogue_rounds >= self.batch_size:
                logger.bind(tag=TAG).info(f"达到批量保存阈值({self.batch_size}轮)，开始保存到 mem0ai")
                
                result = self.client.add(
                    current_messages, user_id=self.role_id, output_format=self.api_version
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
            # 强制保存所有对话
            messages = [
                {"role": message.role, "content": message.content}
                for message in msgs
                if message.role != "system"
            ]
            
            result = self.client.add(
                messages, user_id=self.role_id, output_format=self.api_version
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
            results = self.client.search(
                query, user_id=self.role_id, output_format=self.api_version
            )
            if not results or "results" not in results:
                return ""

            # Format each memory entry with its update time up to minutes
            memories = []
            for entry in results["results"]:
                timestamp = entry.get("updated_at", "")
                if timestamp:
                    try:
                        # Parse and reformat the timestamp
                        dt = timestamp.split(".")[0]  # Remove milliseconds
                        formatted_time = dt.replace("T", " ")
                    except:
                        formatted_time = timestamp
                memory = entry.get("memory", "")
                if timestamp and memory:
                    # Store tuple of (timestamp, formatted_string) for sorting
                    memories.append((timestamp, f"[{formatted_time}] {memory}"))

            # Sort by timestamp in descending order (newest first)
            memories.sort(key=lambda x: x[0], reverse=True)

            # Extract only the formatted strings
            memories_str = "\n".join(f"- {memory[1]}" for memory in memories)
            logger.bind(tag=TAG).debug(f"Query results: {memories_str}")
            return memories_str
        except Exception as e:
            logger.bind(tag=TAG).error(f"查询记忆失败: {str(e)}")
            return ""
