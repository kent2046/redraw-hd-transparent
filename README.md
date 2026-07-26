# 高清透明重绘（redraw-hd-transparent）

一个面向 Codex 的图像处理 Skill：根据用户提供的 JPG、PNG 或参考图进行高清重绘，补全被遮挡或裁切的区域，去除背景并输出指定尺寸、指定 PPI 的透明 PNG。

它不是简单放大或锐化原图，而是指导 Codex 使用图像生成能力重新构建主体，再通过色键去底和确定性脚本完成透明画布、尺寸与 PPI 校验。

![高清透明重绘示意图](https://github.com/kent2046/redraw-hd-transparent/blob/main/docs/organl.png)->![高清透明重绘示意图2](https://github.com/kent2046/redraw-hd-transparent/blob/main/docs/crayfish-mascot-left-cheer-sign-1680-transparent.png)

> 上图是使用本 Skill 工作流生成的透明背景素材示例。GitHub 页面通常以深色或棋盘格显示透明区域。

## 主要作用

- 参考 JPG/PNG 高清重绘
- 保留原图构图、视角、姿态、色彩和风格
- 补全被裁切、遮挡或缺失的主体区域
- 修复常见的肢体、边缘、线稿和小物件结构问题
- 通过绿幕或品红色幕去除背景
- 输出精确像素尺寸，例如 `1680×1680`、`3840×2150`
- 写入指定 PPI，例如 `300 PPI`
- 验证 Alpha 透明通道、画布尺寸和输出元数据
- 支持 `contain`、`cover`、`stretch` 三种画布适配方式

## 适用场景

当用户提出下面这类请求时，可以触发本 Skill：

- “把这张图高清重绘并保留透明度”
- “帮我把被遮挡的部分补完整”
- “输出 3840×2150、300 PPI 的透明 PNG”
- “把参考图里的角色单独抠出来”
- “去除背景，边缘要干净”
- “生成适合放进海报或 PSD 排版的透明素材”

尤其适合广告海报元素、食品摄影素材、卡通角色、产品抠图、活动装饰物和需要继续排版的独立 PNG 素材。

## 工作原理

完整流程分为四个阶段：

1. **分析参考图**：识别主体数量、构图、视角、姿态、色彩、光线以及需要保留或补全的部分。
2. **高清重绘**：调用 Codex 内置图像生成工具，在纯色背景上重绘主体，并检查结构、裁切与风格一致性。
3. **透明去底**：使用 ImageGen Skill 自带的 `remove_chroma_key.py` 去除纯绿或纯品红背景。
4. **规范化输出**：使用本仓库的 `finalize_transparent.py` 输出精确画布尺寸与 PPI，并检查 Alpha 通道。

## 安装

### 方法一：克隆到 Codex Skills 目录

```bash
git clone https://github.com/kent2046/redraw-hd-transparent.git
cp -R redraw-hd-transparent/skill/redraw-hd-transparent ~/.codex/skills/
```

重新启动 Codex，或开启一个新任务，让 Codex 重新发现 Skill。

### 方法二：手动安装

下载仓库 ZIP，解压后将：

```text
skill/redraw-hd-transparent
```

复制到：

```text
~/.codex/skills/redraw-hd-transparent
```

## 在 Codex 中使用

可以直接点名 Skill：

```text
使用 $redraw-hd-transparent，把这张参考图高清重绘为透明 PNG，
补全被遮挡的部分，输出 3840×2150、300 PPI。
```

也可以自然描述需求：

```text
帮我把参考图里的卡通角色单独高清重绘出来，保留透明度，
画布 1680×1680，300 PPI，四周留出排版空间。
```

推荐在提示中明确这些信息：

- 哪张图片是参考图
- 要保留哪些主体与装饰
- 要删除哪些背景或文字
- 被遮挡、裁切的位置是否需要补全
- 最终宽度、高度和 PPI
- 主体是完整居中，还是允许裁切铺满

## 最终画布脚本

Skill 内置脚本：

```text
skill/redraw-hd-transparent/scripts/finalize_transparent.py
```

安装依赖：

```bash
python3 -m pip install Pillow
```

运行示例：

```bash
python3 skill/redraw-hd-transparent/scripts/finalize_transparent.py \
  --input transparent-source.png \
  --output final.png \
  --width 3840 \
  --height 2150 \
  --dpi 300 \
  --fit contain
```

参数说明：

| 参数 | 作用 |
|---|---|
| `--input` | 已带透明通道的输入 PNG |
| `--output` | 最终 PNG 文件路径；为避免误覆盖，目标文件不能已存在 |
| `--width` | 最终画布宽度（像素） |
| `--height` | 最终画布高度（像素） |
| `--dpi` | 输出 PPI，默认 300 |
| `--fit contain` | 等比完整放入画布，剩余区域透明，推荐 |
| `--fit cover` | 等比铺满画布，超出部分居中裁切 |
| `--fit stretch` | 拉伸到指定尺寸，可能改变比例 |

脚本运行后会输出 JSON 校验结果，包括：

- 输出路径
- 宽度和高度
- DPI/PPI
- 图像模式
- Alpha 通道状态
- Alpha 极值
- 使用的适配方式

## 色键去底

本 Skill 默认与 Codex 系统内置的 `imagegen` Skill 配合使用：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
  --input chroma-source.png \
  --out transparent-source.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill \
  --edge-contract 1
```

- 主体不包含重要绿色细节时，优先使用纯绿色 `#00ff00`。
- 主体需要保留绿色时，改用纯品红 `#ff00ff`。
- 生成提示应明确禁止主体使用色键颜色。

## 目录结构

```text
redraw-hd-transparent/
├── README.md
├── LICENSE
├── docs/
│   └── example-transparent.png
└── skill/
    └── redraw-hd-transparent/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── scripts/
            └── finalize_transparent.py
```

## 注意事项

- 不要覆盖用户的原始参考图。
- 中间色键文件建议保存在项目的 `work/` 或 `tmp/` 目录。
- 最终文件建议保存在项目的 `outputs/` 目录。
- 毛发、玻璃、烟雾、液体和半透明反光边缘对色键去底更敏感，应仔细检查边缘。
- `PPI` 是打印元数据；实际清晰度仍主要由像素尺寸决定。
- 生成式重绘无法保证与原图逐像素一致，但会尽量保持关键构图和视觉特征。

## 依赖

- Codex
- Codex 内置图像生成能力
- Codex 系统 `imagegen` Skill（用于色键去底脚本）
- Python 3.9+
- Pillow

## 许可证

本项目使用 [MIT License](LICENSE)。
