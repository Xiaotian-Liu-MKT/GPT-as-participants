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
   `pythonProject/conditionA.txt` 与 `pythonProject/conditionB.txt` 可以是文本或图片
   （如 `.png`、`.jpg`），其内容将作为对被试的提示材料。
4. **设置人口统计与特质**
   ```bash
   cp pythonProject/profile_config.example.json pythonProject/profile_config.json
   # 编辑 profile_config.json 以调整人口统计选项及特质含义
   ```

## 图形界面
运行简单图形界面：
```bash
python pythonProject/gui.py
```
在窗口中填写参与者数量，通过下拉列表选择模型供应商和模型名称，还可设置输出路径和配置文件，最后点击“Start Simulation”即可。

实验版的现代化界面（含仪表盘与抽屉式“新建运行”面板）可运行：
```bash
python pythonProject/app.py
```
该界面展示了设计文档中的信息架构与双语标签，包含：仪表盘概览、运行队列与详情、结果浏览器以及配置页，并在“新建运行”抽屉中提供条件编辑、参与者画像、模型参数、运行参数与复核等区块，可作为后续功能开发的基础。

## 运行模拟
从仓库根目录执行：
```bash
python pythonProject/simulate.py --participants 50 --model gpt-4o-mini
```
常用参数：
- `-n / --participants`：生成的被试数量，默认 200。
- `-m / --model`：`litellm` 识别的模型名称，默认 `gpt-4o-mini`。
- `-o / --output`：结果 Excel 文件的保存路径，默认使用时间戳命名并写在当前目录。
- `--profile-config`：JSON 文件，集中配置人口统计选项及特质含义（默认读取 `pythonProject/profile_config.json`）。

## 运行流程解析
`simulate.py` 的核心逻辑位于 `simulate_participants` 函数，其执行步骤如下：
1. 读取 `.env` 获取 `LITELLM_API_KEY`，并加载实验条件文本或图片。
2. 针对每个被试：
   - 随机选择 A 或 B 条件，并按配置生成年龄、性别、文化背景等人口统计信息，以及若干 1–7 计分的个体特质（如 Big Five）。
   - 调用 `build_messages` 构造发送给模型的多轮对话消息，其中系统角色描述被试的身份信息和特质含义，后续用户消息给出实验提示。
   - 使用 `litellm.completion` 向指定模型请求回答，随机设置 `temperature` 与 `top_p` 以增加多样性。
   - 将模型输出作为因变量（`DV`）并连同元数据一起存储。
3. 所有被试完成后，将结果写入 Excel，文件包含人口统计信息、各项特质、实验条件与因变量（`DV`）。

## 示例
```bash
LITELLM_API_KEY=dummy \
python pythonProject/simulate.py -n 2 -m gpt-4o-mini -o demo.xlsx
```
运行后终端会输出结果文件路径，例如 `demo.xlsx`，其中包含 2 行被试的模拟数据。

## 自定义与扩展
- **新增实验条件**：在 `pythonProject` 目录中创建更多文本或图片条件文件，并在脚本中加载。
- **自定义人口统计与特质**：编辑 `profile_config.json` 或通过 `--profile-config` 提供自定义 JSON，控制年龄范围、性别列表以及特质的 1–7 级解释。
- **更换模型或参数**：通过命令行参数选择模型，或修改 `simulate_participants` 内的 `temperature`、`top_p` 范围以调整生成风格。

## 许可协议
本仓库仅供研究和教学使用，具体许可请自行根据实际需求补充。

---

# GPT-as-participants (English)

This repository provides a lightweight command-line tool for generating synthetic “participants” in psychology or social-science experiments using a language model. It wraps the [`litellm`](https://github.com/BerriAI/litellm) package so you can switch providers behind a consistent API.

## Repository structure
```
├── pythonProject/
│   ├── simulate.py       # core script generating participants
│   ├── conditionA.txt    # prompt for experimental condition A
│   ├── conditionB.txt    # prompt for experimental condition B
│   ├── .env.example      # example environment variable file
├── requirements.txt      # dependency list
└── README.md             # usage instructions
```

## Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Provide an API key**
   ```bash
   cp pythonProject/.env.example pythonProject/.env
   # fill in LITELLM_API_KEY (e.g. an OpenAI key)
   ```
   The script reads `pythonProject/.env` automatically, or you can export `LITELLM_API_KEY` before running.
3. **Edit experimental conditions**
   `pythonProject/conditionA.txt` and `pythonProject/conditionB.txt` can be text or images (e.g. `.png`, `.jpg`). Their contents are shown to the simulated participants.
4. **Configure demographics and traits**
   ```bash
   cp pythonProject/profile_config.example.json pythonProject/profile_config.json
   # edit the file to adjust demographic options and trait scale meanings
   ```

## Graphical interfaces
Run the simple GUI:
```bash
python pythonProject/gui.py
```
Enter the number of participants, choose a model provider and model name from the drop-down lists, optionally set the output path and profile configuration, then click “Start Simulation”.

An experimental modern interface with a dashboard and “New Run” drawer is available:
```bash
python pythonProject/app.py
```
This prototype demonstrates the information architecture and bilingual labels described in the design document, including a dashboard overview, run queue and details, results browser, and settings page. The “New Run” drawer contains sections for condition editing, participant profile, model parameters, run parameters, and review, serving as a basis for future enhancements.

## Run the simulator
From the repository root:
```bash
python pythonProject/simulate.py --participants 50 --model gpt-4o-mini
```
Command-line options:
- `--participants` / `-n` – number of synthetic participants (default 200)
- `--model` / `-m` – model name understood by `litellm` (default `gpt-4o-mini`)
- `--output` / `-o` – path to save the Excel file (default uses a timestamped name)
- `--profile-config` – JSON file listing demographic choices and trait scale descriptions (defaults to `pythonProject/profile_config.json`)

## How it works
The `simulate_participants` function in `simulate.py` performs the following steps:
1. Load `LITELLM_API_KEY` from `.env` and read the condition files.
2. For each participant:
   - Randomly pick condition A or B and generate demographic attributes and traits scored 1–7.
   - Build a multi-turn message sequence via `build_messages`, with system messages describing identity and trait scales and user messages containing the experimental prompt.
   - Call `litellm.completion` with randomized `temperature` and `top_p` to increase diversity.
   - Store the model output as the dependent variable (`DV`) along with metadata.
3. After all participants are processed, write an Excel file containing demographics, traits, condition, and `DV`.

## Example
```bash
LITELLM_API_KEY=dummy \
python pythonProject/simulate.py -n 2 -m gpt-4o-mini -o demo.xlsx
```
The terminal prints the path to the results file, e.g. `demo.xlsx`, containing two rows of simulated data.

## Customization and extension
- **Additional experimental conditions** – create more text or image files in `pythonProject` and load them in the script.
- **Custom demographics and traits** – edit `profile_config.json` or supply `--profile-config` to define demographic ranges, gender options, and trait meanings.
- **Model or parameter tweaks** – choose different models via command-line options or adjust `temperature` and `top_p` ranges in `simulate_participants` to change output style.

## License
This repository is intended for research and educational use only. Please supply a license that fits your needs.
