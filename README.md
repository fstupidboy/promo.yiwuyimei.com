# promo.yiwuyimei.com

Note: This site targets English-speaking customers only. Brand is standardized as "Yiwuyimei" (English). Any previous Chinese brand naming has been removed.

Yiwuyimei Product Showcase Website - Promotional landing site for Yiwuyimei

## 项目介绍

这是一个基于 Hugo 构建的产品展示网站，采用橙白色主题，展示多个产品类别。

### 网站功能

1. **首页** - 展示所有产品类别，每个类别显示 8 个产品
2. **产品分类页** - 显示特定类别下的所有产品
3. **产品详情页** - 显示产品的主图、规格和图片库
4. **联系我们页** - 显示联系信息

### 网站结构

- 三个主导航：首页、产品（带下拉菜单）、联系我们
- 产品分类：电子产品、家居用品、服装配饰
- 每个产品包含：标题、描述、图片、规格、图片库

## 安装和运行

### 前置要求

- Hugo Extended 版本（建议 v0.121.0 或更高）

### 安装 Hugo

```bash
# Ubuntu/Debian
sudo apt-get install hugo

# macOS
brew install hugo

# 或者从 https://github.com/gohugoio/hugo/releases 下载
```

### 运行开发服务器

```bash
# 克隆仓库
git clone https://github.com/fstupidboy/promo.yiwuyimei.com.git
cd promo.yiwuyimei.com

# 启动开发服务器
hugo server --buildDrafts

# 访问 http://localhost:1313
```

### 构建生产版本

```bash
hugo --minify
```

生成的静态文件将位于 `public/` 目录。

## 目录结构

```
.
├── content/              # 内容文件
│   ├── _index.md        # 首页
│   ├── contact/         # 联系页面
│   ├── products/        # 产品内容
│   └── categories/      # 分类内容
├── static/              # 静态资源
│   └── images/          # 图片文件
├── themes/yiwuyimei/    # 自定义主题
│   ├── layouts/         # 模板文件
│   └── assets/          # CSS/JS 资源
└── hugo.toml           # 配置文件
```

## 添加 / 批量生成新产品

### 手动添加

在 `content/products/<分类 slug>/` 目录下创建新的 Markdown 文件：

```markdown
---
title: "产品名称"
category: "分类显示名称"
categories: ["分类显示名称"]
description: "产品描述"
image: "/images/products/<分类>/<文件名>.jpg"
specifications:
  - name: "Material"
    value: "Polyester"
  - name: "SKU"
    value: "YW-001"
---

产品详细介绍内容。
```

### 使用通用批量生成脚本

脚本：`scripts/generate_products.py`

功能：根据图片文件批量生成对应产品 Markdown。自动生成标题、Slug、SKU、前置说明。

参数说明：

- `--category` 分类显示名称（写入 front matter）
- `--images` 图片目录（例如 `static/images/products/headwear`）
- `--out` 输出目录（可选；默认 `content/products/<category slug>`）
- `--material` 材质字段（可选，默认 `Polyester`）
- `--dry-run` 只预览不写入

示例：

```bash
python3 scripts/generate_products.py \
  --category "Headwear" \
  --images static/images/products/headwear \
  --material Cotton
```

添加新分类（例如 Lanyards）：

```bash
mkdir -p static/images/products/lanyards
# 放入若干图片: e.g. Lanyard1.jpg, Lanyard2.jpg
python3 scripts/generate_products.py --category "Lanyards" --images static/images/products/lanyards
hugo --minify
```

脚本规则：

- 标题：文件名去下划线并智能分词后首字母大写（`BaseballCap12` → `Baseball Cap 12`）
- Slug：标题转为小写并用连字符连接（`Baseball Cap 12` → `baseball-cap-12`）
- SKU：原始文件名（去除空格下划线）大写
- 跳过：已存在同名 slug 或 SKU 的文件

### 修改或增量添加

重复运行脚本只会生成缺失的产品，不会覆盖已存在的 Markdown。

如需更新规格，直接编辑对应 Markdown 文件。

## 主题颜色

- 主色调：橙色 (#ff8c00)
- 辅助色：白色 (#fff)
- 文字颜色：深灰 (#333)

## 许可证

MIT License

## 移动端导航说明

移动端显示汉堡菜单按钮（☰）。点击后添加 Body 类 `nav-open`，显示折叠菜单。再次点击或点击菜单链接后关闭。相关代码：

- 标记：`themes/yiwuyimei/layouts/partials/header.html`
- 菜单：`themes/yiwuyimei/layouts/partials/menu.html`
- 样式：`themes/yiwuyimei/assets/css/main.css`（`.nav-toggle`, `body.nav-open .main-nav`）
- 逻辑：`themes/yiwuyimei/assets/js/main.js`

可通过扩展 CSS/JS 添加动画或持久化展开状态。

