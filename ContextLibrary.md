# Context Library

## 1. 文件概览

### pythonProject/simulate.py
- **职责与功能**：提供核心模拟流程，负责读取参与者配置、构造提示消息、调用语言模型并将结果写入 Excel【F:pythonProject/simulate.py†L31-L50】【F:pythonProject/simulate.py†L111-L148】【F:pythonProject/simulate.py†L156-L224】
- **依赖关系**：使用 `pandas` 处理数据、`python-dotenv` 读取 API key、`litellm` 调用语言模型；依赖 `conditionA.txt`/`conditionB.txt` 与 `profile_config.json` 作为输入【F:pythonProject/simulate.py†L20-L23】【F:pythonProject/simulate.py†L188-L191】

### pythonProject/gui.py
- **职责与功能**：提供基于 Tkinter 的图形界面，收集用户输入并后台调用 `simulate_participants` 运行模拟【F:pythonProject/gui.py†L1-L47】【F:pythonProject/gui.py†L155-L187】
- **依赖关系**：依赖 `tkinter` 组件和 `threading`，并从 `simulate` 模块导入核心函数；使用 `MODEL_CATALOG` 预定义可选模型【F:pythonProject/gui.py†L9-L21】【F:pythonProject/gui.py†L17-L21】

### setup.py
- **职责与功能**：交互式配置向导，用于写入 `.env`、生成 `profile_config.json` 并测试 API 连接【F:setup.py†L1-L66】
- **依赖关系**：依赖 `dotenv`、`requests`、`litellm` 等库进行配置和连通性测试【F:setup.py†L14-L22】【F:setup.py†L67-L122】

### pythonProject/profile_config.example.json
- **职责与功能**：示例参与者配置，定义人口统计选项及 Big Five 特质描述，供模拟脚本读取【F:pythonProject/profile_config.example.json†L1-L22】
- **依赖关系**：被 `simulate.py` 和 `setup.py` 作为默认配置引用。

### pythonProject/conditionA.txt 与 conditionB.txt
- **职责与功能**：描述两种实验情境的提示文本，作为对语言模型的输入材料【F:pythonProject/conditionA.txt†L1-L4】【F:pythonProject/conditionB.txt†L1-L4】
- **依赖关系**：由 `simulate.py` 读取并在 `build_messages` 中注入到对话【F:pythonProject/simulate.py†L188-L201】

### requirements.txt
- **职责与功能**：声明运行所需依赖，包括 `litellm`、`pandas`、`openpyxl`、`python-dotenv`【F:requirements.txt†L1-L4】

## 2. 模块关系图与依赖说明

```
setup.py
  └─ 生成 .env 和 profile_config.json

gui.py ──> simulate.py ──> litellm.completion
                          ├─ conditionA.txt
                          ├─ conditionB.txt
                          └─ profile_config.json
```
- `gui.py` 仅调用 `simulate_participants`，无反向依赖，避免循环引用。
- `simulate.py` 集中处理业务逻辑并对外暴露函数，其他模块通过该函数间接访问语言模型。
- `setup.py` 独立运行，用于初始化环境和配置文件。

## 3. 核心功能路径

### 命令行模拟
1. `main()` 解析参数后调用 `simulate_participants`【F:pythonProject/simulate.py†L232-L267】
2. `simulate_participants` 读取配置与条件 → `build_messages` 生成提示 → 调用 `litellm.completion` 获取回答 → 写入 Excel【F:pythonProject/simulate.py†L156-L224】

### 图形界面流程
1. `SimulatorGUI` 构建界面并在用户点击“Start Simulation”后触发 `_start`【F:pythonProject/gui.py†L25-L47】【F:pythonProject/gui.py†L155-L173】
2. `_run_simulation` 在后台线程中调用 `simulate_participants` 并更新状态【F:pythonProject/gui.py†L174-L187】

### 设置向导流程
1. `SetupWizard.run` 顺序执行 API key 配置、profile 配置与连接测试【F:setup.py†L33-L66】
2. `_save_api_key` 写入 `.env`；`_create_default_profile`/`_create_custom_profile` 生成配置；`test_configuration` 调用外部接口验证【F:setup.py†L67-L160】【F:setup.py†L191-L205】

## 4. 对外接口（API）

- **命令行接口**：`python pythonProject/simulate.py [-n NUM] [-m MODEL] [-o PATH] [--profile-config FILE]`【F:pythonProject/simulate.py†L232-L259】
- **函数接口**：`simulate_participants(count, model, output=None, profile_config=None) -> Path`【F:pythonProject/simulate.py†L156-L224】
- **图形界面**：`python pythonProject/gui.py` 打开窗口操作，无网络 API。
- **外部调用**：内部使用 `litellm.completion(model, messages, api_key, temperature, top_p)` 与模型服务通信【F:pythonProject/simulate.py†L204-L210】

## 5. 常见开发场景上下文建议

| 场景 | 关注文件/模块 | 说明 |
| --- | --- | --- |
| 新增实验条件 | `pythonProject/condition*.txt`、`simulate.py` | 添加新的条件文件并在 `simulate_participants` 中加载选择逻辑 |
| 自定义人口统计或特质 | `profile_config.json`、`generate_participant_details` | 编辑配置或修改生成函数以适配新的字段和评分规则【F:pythonProject/simulate.py†L53-L92】 |
| 更换/新增模型 | `simulate.py` CLI 参数、`gui.py` 中 `MODEL_CATALOG` | CLI 通过 `--model` 指定，GUI 需更新模型列表【F:pythonProject/gui.py†L17-L21】 |
| 调试模型输出 | `simulate_participants` | 可在循环中加入日志或异常处理，便于定位问题【F:pythonProject/simulate.py†L193-L216】 |
| 修改依赖或环境变量 | `requirements.txt`、`.env`、`setup.py` | 更新依赖后重新安装，使用 `setup.py` 管理 API key 与配置【F:setup.py†L1-L66】 |

