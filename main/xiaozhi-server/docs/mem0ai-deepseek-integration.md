# Mem0ai 与 DeepSeek 集成配置指南

## 概述

本配置允许 Mem0ai 使用 DeepSeek Chat 作为其内部 LLM，而不是使用 Mem0ai 默认的 LLM。这样可以确保记忆处理使用与主系统相同的 LLM 模型。

## 配置说明

### 1. Mem0ai 配置

在 `config.yaml` 中的 `Memory.mem0ai` 部分添加以下配置：

```yaml
Memory:
  mem0ai:
    type: mem0ai
    # Mem0ai API Key
    api_key: xx
    # DeepSeek API Key，用于 Mem0ai 内部 LLM
    deepseek_api_key: sk-xx
    # OpenAI API Key，用于 Mem0ai 内部 Embedder
    openai_api_key: sk-xxx  # 请替换为你的 OpenAI API Key
    # 批量保存配置
    batch_size: 5
```

### 2. 主要 LLM 配置

确保主系统也使用 DeepSeek：

```yaml
selected_module:
  LLM: DeepSeekLLM
  Memory: mem0ai

LLM:
  DeepSeekLLM:
    type: openai
    model_name: deepseek-chat
    url: https://api.deepseek.com
    api_key: sk-01568d3c6e8949d18f76fc37a51344ed
```

## 工作原理

1. **Mem0ai 内部 LLM**: Mem0ai 使用 DeepSeek Chat 进行记忆处理和检索
2. **Mem0ai 内部 Embedder**: Mem0ai 使用 OpenAI text-embedding-3-small 进行文本向量化
3. **主系统 LLM**: 主对话系统也使用 DeepSeek Chat
4. **统一模型**: 确保整个系统使用相同的 LLM 模型，提供一致的用户体验

## 优势

- **模型一致性**: 记忆处理和主对话使用相同的 LLM
- **高质量嵌入**: 使用 OpenAI text-embedding-3-small 提供更准确的语义搜索
- **性能优化**: 利用 DeepSeek 的高性能模型
- **批量保存**: 减少 API 调用频率，提升对话速度

## 注意事项

- 确保 DeepSeek API Key 有效且有足够的配额
- 确保 OpenAI API Key 有效且有足够的配额（用于文本嵌入）
- 批量保存功能可以减少 API 调用，但可能影响记忆的实时性
- 建议在生产环境中使用环境变量来管理 API Key
