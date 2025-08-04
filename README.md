# GPT-as-participants

本项目提供一个简洁的命令行工具，用于利用大型语言模型模拟心理或社会科学实验中的被试。脚本基于 [`litellm`](https://github.com/BerriAI/litellm) 封装层，允许在保持统一接口的前提下切换不同的模型提供商。

## 仓库结构
```
├── pythonProject/
│   ├── simulate.py       # 生成被试的核心脚本
│   ├── conditionA.txt    # 实验条件 A 的提示词
│   ├── conditionB.txt    # 实验条件 B 的提示词
│   ├── .env.example      # 示例环境变量文件
├── requirements.txt      # 依赖声明
└── README.md             # 使用说明
```

## 环境准备
1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
2. **配置 API Key**
   ```bash
   cp pythonProject/.env.example pythonProject/.env
   # 在 .env 中填写 LITELLM_API_KEY（例如 OpenAI 的密钥）
   ```
   脚本会自动从 `pythonProject/.env` 读取该密钥；你也可以在运行前通过环境变量提供：
   ```bash
   export LITELLM_API_KEY=sk-xxxx
   ```
3. **准备实验条件**
   修改 `pythonProject/conditionA.txt` 与 `pythonProject/conditionB.txt` 以适配你的实验设计；文本内容会作为对被试的提示词。

## 运行模拟
从仓库根目录执行：
```bash
python pythonProject/simulate.py --participants 50 --model gpt-4o-mini
```
常用参数：
- `-n / --participants`：生成的被试数量，默认 200。
- `-m / --model`：`litellm` 识别的模型名称，默认 `gpt-4o-mini`。
- `-o / --output`：结果 Excel 文件的保存路径，默认使用时间戳命名并写在当前目录。

## 运行流程解析
`simulate.py` 的核心逻辑位于 `simulate_participants` 函数，其执行步骤如下：
1. 读取 `.env` 获取 `LITELLM_API_KEY`，并加载实验条件文本。
2. 针对每个被试：
   - 随机选择 A 或 B 条件，并生成年龄、性别、文化背景、社交敏感度、情绪等人口统计信息。
   - 调用 `build_messages` 构造发送给模型的多轮对话消息，其中系统角色描述被试的身份信息，后续用户消息给出实验提示。
   - 使用 `litellm.completion` 向指定模型请求回答，随机设置 `temperature` 与 `top_p` 以增加多样性。
   - 将模型输出作为因变量（`DV`）并连同元数据一起存储。
3. 所有被试完成后，将结果写入 Excel，文件包含列：`Age`、`Sex`、`Culture Background`、`Social Sensitivity`、`Mood`、`Condition` 与 `DV`。

## 示例
```bash
LITELLM_API_KEY=dummy \
python pythonProject/simulate.py -n 2 -m gpt-4o-mini -o demo.xlsx
```
运行后终端会输出结果文件路径，例如 `demo.xlsx`，其中包含 2 行被试的模拟数据。

## 自定义与扩展
- **新增实验条件**：可在 `pythonProject` 目录中创建更多条件文件，并在脚本中加载。
- **替换人口统计信息生成规则**：编辑 `generate_participant_details` 函数，自定义年龄范围或其他属性列表。
- **更换模型或参数**：通过命令行参数选择模型，或修改 `simulate_participants` 内的 `temperature`、`top_p` 范围以调整生成风格。

## 许可协议
本仓库仅供研究和教学使用，具体许可请自行根据实际需求补充。

