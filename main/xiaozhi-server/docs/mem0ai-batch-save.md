# Mem0ai 批量保存功能使用指南

## 功能概述

Mem0ai 批量保存功能允许你设置对话轮数阈值，只有在达到指定轮数时才保存到 Mem0ai 服务，从而大大提升对话速度和减少 API 调用次数。

## 配置方法

### 1. 本地配置模式

在 `data/.config.yaml` 文件中配置：

```yaml
selected_module:
  Memory: mem0ai

Memory:
  mem0ai:
    type: mem0ai
    api_key: "你的mem0ai api key"
    api_version: "v1.1"
    batch_size: 5  # 每5轮对话保存一次
```

### 2. API 配置模式

如果使用智控台，在智控台的参数管理中配置 `batch_size` 参数。

## 参数说明

### batch_size
- **类型**: 整数
- **默认值**: 1（每轮对话都保存）
- **推荐值**: 5（每5轮对话保存一次）
- **说明**: 设置对话轮数阈值，达到阈值时才保存到 Mem0ai

## 配置建议

| batch_size | API调用频率 | 对话速度 | 记忆效果 | 适用场景 |
|------------|-------------|----------|----------|----------|
| 1 | 最高 | 较慢 | 最好 | 需要精确记忆 |
| 3 | 高 | 中等 | 好 | 平衡性能和记忆 |
| 5 | 中等 | 快 | 好 | **推荐配置** |
| 10 | 低 | 最快 | 一般 | 高性能场景 |

## 工作原理

### 1. 对话轮数计算
- 系统自动计算用户和助手的对话对数量
- 例如：用户说3句话，助手回复3句话 = 3轮对话

### 2. 保存逻辑
- **未达到阈值**: 跳过保存，继续对话
- **达到阈值**: 保存当前所有对话到 Mem0ai
- **连接关闭**: 强制保存剩余对话（防止丢失）

### 3. 日志输出
```
[INFO] - core.providers.memory.mem0ai.mem0ai - 成功连接到 Mem0ai 服务，批量保存阈值: 5 轮对话
[DEBUG] - core.providers.memory.mem0ai.mem0ai - 当前对话轮数: 3, 批量保存阈值: 5
[DEBUG] - core.providers.memory.mem0ai.mem0ai - 未达到批量保存阈值，跳过保存。当前: 3轮，阈值: 5轮
[INFO] - core.providers.memory.mem0ai.mem0ai - 达到批量保存阈值(5轮)，开始保存到 mem0ai
[INFO] - core.providers.memory.mem0ai.mem0ai - 强制保存记忆成功，对话轮数: 8
```

## 性能提升效果

### 原始行为（batch_size=1）
- 每轮对话都调用 Mem0ai API
- 对话延迟：每次保存约 200-500ms
- API 调用：频繁，容易达到配额限制

### 批量保存（batch_size=5）
- 每5轮对话调用一次 Mem0ai API
- 对话延迟：减少 80% 的保存延迟
- API 调用：减少 80% 的调用次数

## 注意事项

1. **记忆完整性**: 连接关闭时会强制保存所有未保存的对话
2. **API 配额**: 大幅减少 API 调用次数，延长免费额度使用时间
3. **对话体验**: 显著提升对话响应速度
4. **配置建议**: 建议从 batch_size=5 开始测试，根据实际需求调整

## 故障排除

### 问题：记忆没有保存
**原因**: 对话轮数未达到阈值
**解决**: 检查日志中的对话轮数计数

### 问题：API 调用仍然频繁
**原因**: batch_size 设置过小
**解决**: 增加 batch_size 值

### 问题：记忆效果不好
**原因**: batch_size 设置过大
**解决**: 减少 batch_size 值

## 示例配置

### 高性能配置
```yaml
Memory:
  mem0ai:
    type: mem0ai
    api_key: "你的api_key"
    batch_size: 10  # 每10轮保存一次
```

### 平衡配置（推荐）
```yaml
Memory:
  mem0ai:
    type: mem0ai
    api_key: "你的api_key"
    batch_size: 5   # 每5轮保存一次
```

### 精确记忆配置
```yaml
Memory:
  mem0ai:
    type: mem0ai
    api_key: "你的api_key"
    batch_size: 1   # 每轮都保存
```
