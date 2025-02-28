# Web版俄罗斯方块（Tetris）

这是一个使用Pygame开发的经典俄罗斯方块游戏，通过Pygbag转换为WebAssembly在浏览器中运行。

## 在线游玩

访问GitHub Pages链接即可直接在浏览器中游玩：
https://[用户名].github.io/[仓库名]/

## 控制方式

- 左箭头：向左移动
- 右箭头：向右移动
- 下箭头：加速下落
- 上箭头：旋转方块
- 空格键：快速下落

## 本地运行

### 运行原始Pygame版本

```
pip install pygame numpy
python hello_tetris/tetris_2d.py
```

### 构建Web版本

```
pip install pygbag
pygbag hello_tetris/tetris_2d.py
```

然后访问 http://localhost:8000 即可游玩。

## 技术细节

- 使用Pygame开发
- 通过Pygbag转换为WebAssembly
- 自动通过GitHub Actions部署到GitHub Pages
