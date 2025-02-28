# 小蜜蜂游戏 (Galaga-style Game)

这是一个基于React Three Fiber构建的3D小蜜蜂游戏，专为视力障碍用户优化。

## AI助理提示

请注意：
- 请使用中文与用户交流
- 用户是资深程序员，熟悉React、Three.js和前端开发
- 提供技术性解释时可以直接使用专业术语
- 代码示例应包含详细注释
- 优先考虑性能优化和代码质量
- 优先使用CMD而不是PowerShell
- 

## 项目背景

- 复古风格小蜜蜂游戏改造版
- 核心改动：
  - 敌方单位：真实蜜蜂贴图（assets/textures/honeybee.png）
  - 玩家角色：大黄蜂贴图（assets/textures/bumblebee.png） 
  - 背景：动态紫藤花效果（assets/textures/wisteria.jpg）
  - 视角：支持拖拽旋转（基于panolens.js）
  ```bash
    # 先创建目录（如果不存在）
    # 下载高质量紫藤花背景
    curl -o assets\textures\wisteria.jpg https://images.pexels.com/photos/19108086/pexels-photo-19108086.jpeg

    # 下载真实蜜蜂贴图
    curl -o assets\textures\honeybee.png https://www.pngwing.com/en/free-png-qyqyj

    # 下载大黄蜂贴图
    curl -o assets\textures\bumblebee.png https://www.pngwing.com/en/free-png-qyqyj
  ```
## 视觉无障碍设计

本游戏针对视力障碍用户进行了特别优化：
- 高对比度：使用强对比色彩区分游戏元素
- 大字体：所有文字至少18pt，重要信息加粗显示
- 清晰边界：游戏元素有明确边界，便于识别
- 可调节视角：支持拖拽和缩放，适应不同视力需求
- 分级任务：根据分数自动调整游戏速度，提供渐进式挑战

## 技术栈

- React + Vite
- React Three Fiber (@react-three/fiber)
- Drei (@react-three/drei)
- Panolens.js (视角控制)

## 第三方资源

### 依赖库
- panolens (npm package): 用于实现3D视角控制
- @react-three/fiber: React的Three.js渲染器
- @react-three/drei: Three.js的React组件集合
- three.js: 3D图形库

### 素材
- 大黄蜂贴图: OpenGameArt.org (CC0许可)
- 蜜蜂贴图: OpenGameArt.org (CC0许可)
- 紫藤花背景: Pexels.com (Pexels许可 - 免费商用)

## 开发注意事项

### Windows环境下的curl使用

在Windows环境中使用curl下载资源时，请使用系统安装的curl.exe而非PowerShell的curl别名：

```bash
# 正确用法
C:\Windows\System32\curl.exe -o 目标文件 URL地址

# 避免使用PowerShell的curl别名(实际是Invoke-WebRequest)
```

## 游戏控制

- ← → 方向键: 移动飞船
- 空格键: 发射子弹
- 鼠标拖拽: 旋转视角

## 开发指南

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 任务系统

游戏根据得分自动调整难度：
- 初级 (0-1000分): 基础速度 1x
- 中级 (1000-3000分): 提升速度 1.5x
- 高级 (3000+分): 最高速度 2x
