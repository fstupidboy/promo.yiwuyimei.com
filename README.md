# promo.yiwuyimei.com

壹物壹美产品展示网站 - Promotional landing site for yiwuyimei

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

## 添加新产品

在 `content/products/` 目录下创建新的 Markdown 文件：

```markdown
---
title: "产品名称"
category: "产品分类"
description: "产品描述"
image: "/images/products/产品图片.jpg"
specifications:
  - name: "品牌"
    value: "壹物壹美"
  - name: "型号"
    value: "YW-001"
gallery:
  - "/images/products/图片1.jpg"
  - "/images/products/图片2.jpg"
---

产品详细介绍内容。
```

## 主题颜色

- 主色调：橙色 (#ff8c00)
- 辅助色：白色 (#fff)
- 文字颜色：深灰 (#333)

## 许可证

MIT License

