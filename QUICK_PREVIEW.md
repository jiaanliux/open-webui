# 快速预览 CSS 修改的方法

## 方法 1: 浏览器开发者工具（最快）

1. 打开网站，按 `F12` 打开开发者工具
2. 找到 UNU logo 的 `<img>` 元素
3. 在 Elements 面板中，右键点击 `<img>` 标签 → "Edit as HTML"
4. 或者直接在 Styles 面板中修改 CSS

**快速修改 CSS：**
```css
.unu-logo {
    height: 2.5rem; /* 可以改成 3rem, 3.5rem 等 */
    width: auto;
    margin-right: 0.5rem;
    margin-top: -0.25rem;
    margin-bottom: -0.25rem;
}
```

修改后立即看到效果！确定满意后再更新代码文件。

## 方法 2: 挂载源代码到容器（需要重启容器）

如果你想在容器内实时看到代码修改，需要：

1. 修改 `docker-compose.yaml`，添加源代码挂载
2. 重启容器

但这需要容器支持开发模式，当前镜像可能不支持。

## 方法 3: 本地开发服务器（需要 Node.js）

如果你有 Node.js 环境：
```bash
npm install
npm run dev
```

然后在浏览器访问 `http://localhost:5173`，修改会立即生效。

