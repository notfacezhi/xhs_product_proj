# 赛博终端组件模板

赛博终端美学的即用型 HTML/CSS 组件。

---

## 顶部导航栏

```html
<header class="site-header">
    <div class="container">
        <div class="header-content">
            <div class="header-left">
                <div class="brand">
                    <span class="material-symbols-outlined animate-pulse">terminal</span>
                    <span class="brand-text text-glow">品牌名称</span>
                </div>
                <span class="separator">//</span>
                <span class="status">系统状态: 在线</span>
            </div>
            <div class="header-right">
                <div class="header-stats">
                    <span>内存: 64KB</span>
                    <span>端口: 8080</span>
                </div>
                <a class="btn-login" href="#">[ 登录 ]</a>
            </div>
        </div>
    </div>
    <div class="scanline">
        <div class="scanline-bar"></div>
    </div>
</header>
```

```css
.site-header {
    position: sticky;
    top: 0;
    z-index: 50;
    background-color: rgba(5, 10, 5, 0.95);
    border-bottom: 1px solid rgba(0, 255, 0, 0.3);
    backdrop-filter: blur(4px);
}
.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.btn-login {
    border: 1px solid var(--theme-primary);
    padding: 0.25rem 0.75rem;
    font-weight: 700;
    transition: background-color 0.2s, color 0.2s;
}
.btn-login:hover {
    background-color: var(--theme-primary);
    color: #000000;
}
```

---

## 主标题区域

```html
<section class="hero-grid">
    <div class="hero-main">
        <div class="retro-border hero-card box-glow">
            <div class="hero-bg-grid"></div>
            <div class="hero-content">
                <div class="terminal-line">C:\SYSTEM\ROOT> 执行协议.EXE</div>
                <h1 class="hero-title text-glow">
                    <span class="block">&gt; 主</span>
                    <span class="block white">标题_</span>
                </h1>
                <p class="hero-desc">系统初始化中...</p>
            </div>
            <div class="hero-actions">
                <button class="btn-primary">
                    <span class="material-symbols-outlined">play_arrow</span>
                    [ 执行 ]
                </button>
            </div>
        </div>
    </div>
</section>
```

---

## 诊断面板

```html
<div class="retro-border diagnostics-card box-glow">
    <div class="diag-header">
        <h3 class="diag-title">系统诊断</h3>
        <span class="animate-pulse">● 实时</span>
    </div>
    <div class="diag-bars">
        <div class="diag-item">
            <div class="diag-label">
                <span>威胁检测</span>
                <span>98%</span>
            </div>
            <div class="diag-bar">[||||||||||||||||||||||||||||||||||..]</div>
        </div>
    </div>
    <div class="console-log">
        <p>&gt; 扫描端口中...</p>
        <p class="text-white">&gt; 恶意软件已检测: 已拦截</p>
    </div>
</div>
```

---

## 模块卡片

```html
<div class="retro-border module-card">
    <div class="module-header">
        <span class="module-filename">模块.EXE</span>
        <span class="material-symbols-outlined">shield</span>
    </div>
    <div class="module-body">
        <div class="module-icon">
            <span class="material-symbols-outlined">security</span>
        </div>
        <h3 class="module-name">模块名称</h3>
        <p class="module-desc">描述文本在这里。</p>
    </div>
</div>
```

```css
.module-card {
    background-color: var(--theme-surface);
    border-radius: 0.125rem;
    transition: background-color 0.3s;
}
.module-card:hover { background-color: rgba(0, 255, 0, 0.1); }
.module-header {
    background-color: rgba(0, 255, 0, 0.2);
    padding: 0.25rem 0.75rem;
    border-bottom: 1px solid rgba(0, 255, 0, 0.3);
}
.module-icon {
    height: 3rem; width: 3rem;
    border: 1px solid var(--theme-primary);
    display: flex; align-items: center; justify-content: center;
    background-color: #000000;
}
```

---

## 终端窗口

```html
<div class="terminal-window">
    <div class="terminal-header">
        <span>终端_V1.2</span>
        <span>[ 进程ID: 0xF4A2 ]</span>
    </div>
    <div class="terminal-body">
        <div>
            <span class="term-prompt">root@system:~#</span>
            <span> 扫描 --网络</span>
        </div>
        <div>[信息] 初始化扫描器...</div>
        <div>
            <span class="term-prompt">root@system:~#</span>
            <span class="animate-pulse">█</span>
        </div>
    </div>
</div>
```

```css
.terminal-window {
    background-color: #000000;
    padding: 1rem;
    font-family: var(--font-mono);
    font-size: 0.875rem;
    border: 1px solid var(--theme-primary-dark);
}
.term-prompt { color: #ffffff; }
```

---

## 数据表格

```html
<div class="vuln-container">
    <div class="table-responsive">
        <table class="vuln-table">
            <thead>
                <tr>
                    <th>目标文件</th>
                    <th>状态</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>module.js</td>
                    <td>已修复</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
```

```css
.vuln-table {
    width: 100%;
    text-align: left;
    font-family: var(--font-mono);
    border-collapse: collapse;
}
.vuln-table th {
    border-bottom: 1px solid rgba(0, 255, 0, 0.3);
    padding: 0.5rem 1rem 0.5rem 0;
}
.vuln-table td {
    padding: 0.75rem 1rem 0.75rem 0;
    border-bottom: 1px solid rgba(0, 255, 0, 0.1);
}
.vuln-table tr:hover td { background-color: rgba(0, 255, 0, 0.1); }
```

---

## 定价卡片

```html
<div class="pricing-card featured">
    <div class="featured-badge">推荐</div>
    <div class="pricing-header">
        <h3 class="pricing-title">读写权限</h3>
        <div class="pricing-price">¥49.99</div>
    </div>
    <div class="pricing-body">
        <ul class="pricing-features">
            <li class="feature-item">
                <span class="material-symbols-outlined">check</span>
                <span>功能名称</span>
            </li>
        </ul>
    </div>
    <div class="pricing-footer">
        <button class="btn-primary btn-full">[ 升级 ]</button>
    </div>
</div>
```

---

## 按钮

### 主要按钮
```css
.btn-primary {
    background-color: var(--theme-primary);
    color: #000000;
    padding: 0.75rem 1.5rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: none;
    cursor: pointer;
    box-shadow: 4px 4px 0px 0px rgba(0,50,0,1);
}
.btn-primary:hover {
    background-color: #ffffff;
    transform: translate(2px, 2px);
    box-shadow: 2px 2px 0px 0px rgba(0,50,0,1);
}
```

### 轮廓按钮
```css
.btn-outline {
    border: 1px solid var(--theme-primary);
    color: var(--theme-primary);
    padding: 0.75rem 1.5rem;
    font-weight: 700;
    text-transform: uppercase;
    background: transparent;
    cursor: pointer;
}
.btn-outline:hover {
    background-color: rgba(0, 255, 0, 0.2);
}
```

---

## 网格布局

### 双列网格
```css
.grid-2 {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}
@media (min-width: 1024px) {
    .grid-2 { grid-template-columns: repeat(2, 1fr); }
}
```

### 四列网格
```css
.grid-4 {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}
@media (min-width: 768px) {
    .grid-4 { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 1024px) {
    .grid-4 { grid-template-columns: repeat(4, 1fr); }
}
```

---

## 字体引入

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
```
