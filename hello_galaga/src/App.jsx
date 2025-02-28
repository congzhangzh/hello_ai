import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import GalagaGame from './GalagaGame'

function App() {
  return (
    <>
      <Canvas camera={{ position: [0, 0, 20], fov: 45, up: [0, 1, 0], far: 100 }}>
        <Suspense fallback={null}>
          <GalagaGame />
        </Suspense>
      </Canvas>
      <div className="controls-info">
        <p style={{ fontSize: '18pt', fontWeight: 'bold' }}>控制说明:</p>
        <p style={{ fontSize: '18pt' }}>← → 方向键: 移动飞船</p>
        <p style={{ fontSize: '18pt' }}>空格键: 发射子弹</p>
        <p style={{ fontSize: '18pt' }}>鼠标拖拽: 旋转视角</p>
      </div>
    </>
  )
}

export default App
