# Mem0ai 批量保存功能测试指南

## 概述

本测试套件用于验证 Mem0ai 批量保存功能的正确性和性能，无需连接嵌入式开发板即可进行完整测试。

## 测试文件结构

```
test/
├── README.md                    # 本文件
├── test_mem0ai_batch.py        # 单元测试
├── test_websocket_client.py    # WebSocket 客户端测试
├── run_tests.py                # 测试运行脚本
└── test_report.md              # 测试报告（自动生成）
```

## 测试类型

### 1. 单元测试 (`test_mem0ai_batch.py`)

**功能**：测试 Mem0ai 批量保存功能的核心逻辑

**测试内容**：
- ✅ 批量保存阈值设置
- ✅ 对话轮数计算逻辑
- ✅ 条件保存机制
- ✅ 强制保存功能
- ✅ 错误处理机制
- ✅ 配置默认值验证
- ✅ 系统消息过滤

**运行方法**：
```bash
# 方法1：直接运行
cd main/xiaozhi-server
python test/test_mem0ai_batch.py

# 方法2：使用 unittest 模块
python -m unittest test.test_mem0ai_batch -v

# 方法3：使用测试运行脚本
python test/run_tests.py --unit
```

### 2. WebSocket 客户端测试 (`test_websocket_client.py`)

**功能**：模拟真实设备连接，测试完整的对话流程

**测试内容**：
- ✅ 服务器连接建立
- ✅ 消息发送和接收
- ✅ 批量保存触发机制
- ✅ 记忆召回功能
- ✅ 性能对比测试
- ✅ 错误处理测试
- ✅ 交互式测试

**运行方法**：
```bash
# 方法1：直接运行（交互式选择）
cd main/xiaozhi-server
python test/test_websocket_client.py

# 方法2：使用测试运行脚本
python test/run_tests.py --websocket
```

**测试选项**：
1. 批量保存功能测试
2. 记忆召回功能测试
3. 性能对比测试
4. 错误处理测试
5. 交互式测试
6. 运行所有测试

### 3. 集成测试

**功能**：测试整个系统的集成功能

**运行方法**：
```bash
python test/run_tests.py --integration
```

## 快速开始

### 1. 环境准备

确保已安装必要的依赖：
```bash
pip install websockets mem0 requests
```

### 2. 启动服务器

在另一个终端中启动 xiaozhi-server：
```bash
cd main/xiaozhi-server
python app.py
```

### 3. 运行测试

#### 运行所有测试：
```bash
python test/run_tests.py --all
```

#### 运行特定测试：
```bash
# 只运行单元测试
python test/run_tests.py --unit

# 只运行 WebSocket 测试
python test/run_tests.py --websocket

# 检查依赖和服务器状态
python test/run_tests.py --check

# 生成测试报告
python test/run_tests.py --report
```

## 测试场景详解

### 1. 批量保存功能测试

**测试目标**：验证批量保存机制是否按预期工作

**测试步骤**：
1. 配置 `batch_size: 5`
2. 进行 6 轮对话
3. 验证：
   - 前 4 轮对话不触发保存
   - 第 5 轮对话触发保存
   - 连接关闭时强制保存

**预期结果**：
```
🔄 第 1 轮对话: 跳过保存
🔄 第 2 轮对话: 跳过保存
🔄 第 3 轮对话: 跳过保存
🔄 第 4 轮对话: 跳过保存
🔄 第 5 轮对话: 触发保存 ✅
🔄 第 6 轮对话: 跳过保存
🔚 连接关闭: 强制保存 ✅
```

### 2. 记忆召回功能测试

**测试目标**：验证记忆是否正确保存和召回

**测试步骤**：
1. 进行多轮对话
2. 询问之前的对话内容
3. 验证 AI 是否能回忆起之前的对话

**预期结果**：
```
❓ 询问: 我们之前聊过什么？
📥 收到回复: 我们之前聊了天气、我的名字、我的功能等话题...
✅ 检测到记忆召回
```

### 3. 性能对比测试

**测试目标**：对比不同 `batch_size` 的性能差异

**测试参数**：
- `batch_size: 1` (每轮都保存)
- `batch_size: 3` (每3轮保存)
- `batch_size: 5` (每5轮保存)
- `batch_size: 10` (每10轮保存)

**性能指标**：
- 总耗时
- 平均每轮对话时间
- API 调用次数

### 4. 错误处理测试

**测试目标**：验证系统在异常情况下的稳定性

**测试内容**：
- 无效的 WebSocket 连接
- 空消息处理
- 特殊字符处理
- 长消息处理
- API 调用失败处理

## 配置要求

### 1. Mem0ai 配置

确保在 `data/.config.yaml` 中正确配置：
```yaml
selected_module:
  Memory: mem0ai

Memory:
  mem0ai:
    type: mem0ai
    api_key: "你的mem0ai api key"
    batch_size: 5  # 测试用的批量保存阈值
```

### 2. 服务器配置

确保服务器正在运行：
- HTTP 服务：`http://localhost:8000`
- WebSocket 服务：`ws://localhost:8000/xiaozhi/v1/`

## 测试结果分析

### 1. 成功指标

- ✅ 单元测试全部通过
- ✅ WebSocket 连接正常
- ✅ 批量保存按预期触发
- ✅ 记忆召回功能正常
- ✅ 错误处理机制有效

### 2. 性能指标

| batch_size | API调用频率 | 对话速度 | 记忆效果 | 推荐度 |
|------------|-------------|----------|----------|--------|
| 1 | 最高 | 较慢 | 最好 | ⭐⭐ |
| 3 | 高 | 中等 | 好 | ⭐⭐⭐ |
| 5 | 中等 | 快 | 好 | ⭐⭐⭐⭐⭐ |
| 10 | 低 | 最快 | 一般 | ⭐⭐⭐⭐ |

### 3. 常见问题

#### 问题1：连接失败
**原因**：服务器未启动或端口被占用
**解决**：检查服务器状态，确保端口 8000 可用

#### 问题2：API 调用失败
**原因**：Mem0ai API Key 无效或配额用完
**解决**：检查 API Key 配置，监控配额使用情况

#### 问题3：记忆召回失败
**原因**：批量保存未正确触发或 API 调用失败
**解决**：检查日志，确认保存操作是否成功

## 自动化测试

### 1. CI/CD 集成

可以将测试集成到 CI/CD 流程中：
```yaml
# .github/workflows/test.yml
name: Mem0ai Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python test/run_tests.py --all
```

### 2. 定时测试

可以设置定时任务定期运行测试：
```bash
# 每天凌晨2点运行测试
0 2 * * * cd /path/to/xiaozhi-server && python test/run_tests.py --all
```

## 扩展测试

### 1. 压力测试

可以扩展测试脚本进行压力测试：
- 并发连接测试
- 大量消息测试
- 长时间运行测试

### 2. 兼容性测试

测试不同环境下的兼容性：
- 不同 Python 版本
- 不同操作系统
- 不同网络环境

## 贡献指南

### 1. 添加新测试

1. 在相应的测试文件中添加新的测试方法
2. 确保测试覆盖新的功能点
3. 更新测试文档

### 2. 改进测试

1. 提高测试覆盖率
2. 优化测试性能
3. 改进错误处理

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 参与讨论

---

*最后更新：2024年1月*
