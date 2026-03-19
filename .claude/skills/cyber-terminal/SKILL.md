---
name: cyber-terminal
description: 生成和使用赛博终端/CLI 风格的组件 - 复古计算风格，绿色磷光主题(#00ff00)，CRT 效果、扫描线和等宽字体。适用于创建网络安全、黑客主题或复古计算界面，需要： (1) 终端/CLI/DOS 视觉风格 (2) 黑客矩阵绿色配色 (3) CRT 扫描线和发光效果 (4) 等宽字体文本布局 (5) ASCII 风格进度条和边框 (6) 系统诊断面板设计 (7) 数据表格和定价卡的终端美学
---

# 赛博终端 / CLI 设计系统

受 1980 年代 CRT 终端和网络安全命令行界面启发的复古计算界面设计系统。

## 快速开始

1. **颜色系统**：使用 `var(--theme-primary: #00ff00)` 作为主要磷光绿色
2. **字体**：`Space Grotesk` 用于显示和等宽文本
3. **CRT 效果**：始终包含 `.crt-overlay` 和 `.crt-vignette` 覆盖层
4. **边框**：使用 `.retro-border` 类实现标志性的发光边框效果

## 核心 CSS 变量

```css
:root {
    --theme-primary: #00ff00;
    --theme-primary-dim: #00cc00;
    --theme-primary-dark: #003300;
    --theme-background: #050a05;
    --theme-surface: #0a140a;
    --font-display: 'Space Grotesk', monospace;
    --font-mono: 'Space Grotesk', monospace;
}
```

## 必要效果

### CRT 覆盖层 (必需)
```css
.crt-overlay {
    pointer-events: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
                linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    background-size: 100% 2px, 3px 100%;
    z-index: 9999;
    mix-blend-mode: overlay;
}

.crt-vignette {
    pointer-events: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,20,0,0.4) 100%);
    z-index: 9998;
}
```

### 文本发光
```css
.text-glow { text-shadow: 0 0 4px rgba(0, 255, 0, 0.5); }
```

### 复古边框
```css
.retro-border {
    border: 1px solid var(--theme-primary);
    position: relative;
}
.retro-border::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    box-shadow: 0 0 8px rgba(0, 255, 0, 0.3);
    pointer-events: none;
    z-index: -1;
}
```

## 组件参考

详见 [references/components.md](references/components.md) 中的完整组件模板：
- 顶部导航栏
- 主标题区域
- 诊断面板
- 模块卡片
- 终端窗口
- 数据表格
- 定价卡片
- 滚动横幅
- 页脚

## 排版规范

| 元素 | 大小 | 字重 | 备注 |
|----------|-------|--------|-------|
| 主标题 | 2.25rem → 4.5rem | 700 | -0.05em 字间距 |
| 区块标题 | 1.5rem | 700 | 大写 |
| 正文 | 0.875rem | 400 | 等宽 |
| 标签 | 0.75rem | 400-700 | 大写，0.05em 字间距 |

## 文本模式

- **终端命令**：`C:\PATH\DIRECTORY\> command_arguments`
- **系统状态**：`[ 在线 ]` `[ 离线 ]` `[ 处理中 ]`
- **进度条**：`[|||||||||||||||.........] 75%`
- **提示符**：`root@system:~#`

## 常用动画

```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes marquee {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
```

## 检查清单

- [ ] 所有颜色使用 CSS 变量
- [ ] 排版遵循规范
- [ ] 包含 CRT 覆盖层
- [ ] 边框使用 retro-border 类
- [ ] 代码/终端内容使用等宽字体
- [ ] ASCII 风格进度条
- [ ] 标签/标题使用大写
- [ ] 发光效果仅用于强调
