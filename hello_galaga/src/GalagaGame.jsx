import { useRef, useState, useEffect, useMemo, createRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Box, Capsule, Sphere, Html, useTexture, OrbitControls } from '@react-three/drei'
import { Vector3, InstancedMesh, Object3D, MathUtils, TextureLoader, PlaneGeometry, MeshBasicMaterial, BackSide, SphereGeometry, Mesh } from 'three'

// 音频合成器 - 生成复古游戏音效
class RetroSoundFX {
  constructor() {
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
    this.masterGain = this.audioContext.createGain()
    this.masterGain.gain.value = 0.3
    this.masterGain.connect(this.audioContext.destination)
  }

  // 射击音效 - 短促下降音调
  playShoot() {
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()
    
    oscillator.type = 'square'
    oscillator.frequency.setValueAtTime(880, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(110, this.audioContext.currentTime + 0.1)
    
    gainNode.gain.setValueAtTime(1, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1)
    
    oscillator.connect(gainNode)
    gainNode.connect(this.masterGain)
    
    oscillator.start()
    oscillator.stop(this.audioContext.currentTime + 0.1)
  }

  // 爆炸音效 - 噪声爆破
  playExplosion() {
    const bufferSize = 4096
    const noiseNode = this.audioContext.createScriptProcessor(bufferSize, 1, 1)
    const gainNode = this.audioContext.createGain()
    
    noiseNode.onaudioprocess = (e) => {
      const output = e.outputBuffer.getChannelData(0)
      for (let i = 0; i < bufferSize; i++) {
        output[i] = Math.random() * 2 - 1
      }
    }
    
    gainNode.gain.setValueAtTime(1, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3)
    
    noiseNode.connect(gainNode)
    gainNode.connect(this.masterGain)
    
    setTimeout(() => {
      noiseNode.disconnect()
    }, 300)
  }

  // 敌人移动音效 - 简单音调
  playEnemyMove() {
    const oscillator = this.audioContext.createOscillator()
    const gainNode = this.audioContext.createGain()
    
    oscillator.type = 'sine'
    oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime)
    oscillator.frequency.exponentialRampToValueAtTime(880, this.audioContext.currentTime + 0.05)
    
    gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.05)
    
    oscillator.connect(gainNode)
    gainNode.connect(this.masterGain)
    
    oscillator.start()
    oscillator.stop(this.audioContext.currentTime + 0.05)
  }
}

// 使用简单的颜色材质代替贴图，直到我们解决贴图加载问题
const bumblebeeColor = "#FFCC00"; // 黄色
const honeybeeColor = "#FFA500"; // 橙色
const wisteriaColor = "#9370DB"; // 紫色

// 紫藤花背景组件
function WisteriaBackground({ texture }) {
  return (
    <mesh position={[0, 0, -30]}>
      <sphereGeometry args={[40, 32, 32]} />
      <meshBasicMaterial map={texture} side={BackSide} />
    </mesh>
  )
}

// 花瓣粒子系统
function FlowerPetals() {
  const petalsCount = 100
  const petalsRef = useRef()
  const dummy = useMemo(() => new Object3D(), [])
  const positions = useMemo(() => {
    const pos = []
    for (let i = 0; i < petalsCount; i++) {
      pos.push({
        position: new Vector3(
          MathUtils.randFloatSpread(40),
          MathUtils.randFloatSpread(40),
          MathUtils.randFloatSpread(40)
        ),
        speed: Math.random() * 0.02 + 0.01,
        rotation: Math.random() * Math.PI,
        rotationSpeed: Math.random() * 0.02
      })
    }
    return pos
  }, [])

  useFrame(() => {
    if (petalsRef.current) {
      positions.forEach((petal, i) => {
        petal.position.y -= petal.speed
        petal.rotation += petal.rotationSpeed
        
        // 如果花瓣落到底部，重置到顶部
        if (petal.position.y < -20) {
          petal.position.y = 20
          petal.position.x = MathUtils.randFloatSpread(40)
          petal.position.z = MathUtils.randFloatSpread(40)
        }
        
        dummy.position.copy(petal.position)
        dummy.rotation.set(0, petal.rotation, 0)
        dummy.updateMatrix()
        petalsRef.current.setMatrixAt(i, dummy.matrix)
      })
      petalsRef.current.instanceMatrix.needsUpdate = true
    }
  })

  return (
    <instancedMesh ref={petalsRef} args={[null, null, petalsCount]}>
      <planeGeometry args={[0.3, 0.3]} />
      <meshBasicMaterial color="#e8dfff" transparent opacity={0.7} />
    </instancedMesh>
  )
}

// 玩家大黄蜂组件
function PlayerShip({ position, onShoot, texture }) {
  const shipRef = useRef()
  const [moveDirection, setMoveDirection] = useState(0)
  const speed = 0.15
  const boundaryX = 10
  const time = useRef(0)

  // 键盘控制
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowLeft') setMoveDirection(-1)
      if (e.key === 'ArrowRight') setMoveDirection(1)
      if (e.key === ' ') onShoot(shipRef.current.position.x)
    }
    
    const handleKeyUp = (e) => {
      if (e.key === 'ArrowLeft' && moveDirection === -1) setMoveDirection(0)
      if (e.key === 'ArrowRight' && moveDirection === 1) setMoveDirection(0)
    }
    
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [moveDirection, onShoot])

  // 移动更新
  useFrame((state, delta) => {
    time.current += delta
    
    if (shipRef.current) {
      shipRef.current.position.x += moveDirection * speed
      
      // 边界限制
      if (shipRef.current.position.x < -boundaryX) {
        shipRef.current.position.x = -boundaryX
      } else if (shipRef.current.position.x > boundaryX) {
        shipRef.current.position.x = boundaryX
      }
      
      // 添加轻微的上下浮动动画
      shipRef.current.position.y = position[1] + Math.sin(time.current * 2) * 0.1
    }
  })

  return (
    <group ref={shipRef} position={position}>
      {texture ? (
        // 使用贴图
        <mesh rotation={[0, 0, 0]}>
          <planeGeometry args={[2, 2]} />
          <meshBasicMaterial map={texture} transparent />
        </mesh>
      ) : (
        // 使用3D几何体
        <group>
          {/* 身体 - 椭圆形 */}
          <mesh position={[0, 0, 0]}>
            <sphereGeometry args={[0.8, 16, 16]} />
            <meshBasicMaterial color={bumblebeeColor} />
          </mesh>
          
          {/* 黑色条纹 */}
          <mesh position={[0, 0.2, 0.5]} rotation={[0.3, 0, 0]}>
            <boxGeometry args={[1.2, 0.2, 0.1]} />
            <meshBasicMaterial color="black" />
          </mesh>
          
          <mesh position={[0, -0.2, 0.5]} rotation={[-0.3, 0, 0]}>
            <boxGeometry args={[1.2, 0.2, 0.1]} />
            <meshBasicMaterial color="black" />
          </mesh>
          
          {/* 翅膀 */}
          <mesh position={[0.6, 0, 0.2]} rotation={[0, 0.3, 0]}>
            <planeGeometry args={[1, 0.8]} />
            <meshBasicMaterial color="white" transparent opacity={0.7} side={BackSide} />
          </mesh>
          
          <mesh position={[-0.6, 0, 0.2]} rotation={[0, -0.3, 0]}>
            <planeGeometry args={[1, 0.8]} />
            <meshBasicMaterial color="white" transparent opacity={0.7} side={BackSide} />
          </mesh>
        </group>
      )}
    </group>
  )
}

// 子弹系统
function BulletSystem({ bullets, setBullets }) {
  const bulletSpeed = 0.5 // 增加子弹速度
  const bulletRef = useRef()
  const dummy = useMemo(() => new Object3D(), [])
  const maxBulletDistance = 30 // 子弹最大飞行距离
  
  // 当子弹数组为空时，重置实例化网格
  useEffect(() => {
    if (bulletRef.current && bullets.length === 0) {
      // 重置所有实例
      for (let i = 0; i < 50; i++) {
        dummy.position.set(0, -100, 0) // 移到屏幕外
        dummy.updateMatrix()
        bulletRef.current.setMatrixAt(i, dummy.matrix)
      }
      bulletRef.current.instanceMatrix.needsUpdate = true
    }
  }, [bullets])
  
  // 更新子弹位置
  useFrame(() => {
    if (bulletRef.current && bullets.length > 0) {
      // 创建新的子弹数组，过滤掉超出范围的子弹
      const newBullets = bullets.filter(bullet => {
        // 更新子弹位置 - 在y轴上移动（向上）
        bullet.position.y += bulletSpeed
        bullet.distanceTraveled = (bullet.distanceTraveled || 0) + bulletSpeed
        
        // 移除超出最大距离的子弹
        if (bullet.distanceTraveled > maxBulletDistance) {
          return false
        }
        
        // 更新实例化网格
        dummy.position.set(bullet.position.x, bullet.position.y, bullet.position.z)
        dummy.updateMatrix()
        bulletRef.current.setMatrixAt(bullet.id, dummy.matrix)
        
        return true
      })
      
      // 更新实例化网格
      bulletRef.current.instanceMatrix.needsUpdate = true
      
      // 如果有子弹被移除，更新子弹数组
      if (newBullets.length !== bullets.length) {
        setBullets(newBullets)
      }
    }
  })

  return (
    <instancedMesh ref={bulletRef} args={[null, null, 50]} frustumCulled={false}>
      <cylinderGeometry args={[0.05, 0.05, 0.5, 8]} />
      <meshStandardMaterial color="#FBBC05" emissive="#FBBC05" emissiveIntensity={0.5} />
    </instancedMesh>
  )
}

// 敌人蜜蜂模型组件 - 使用3D几何体
function EnemyModel({ type = 0, texture }) {
  const scale = 1 + type * 0.2
  const time = useRef(0)
  const [frameIndex, setFrameIndex] = useState(0)
  
  // 蜜蜂精灵动画
  useFrame((state, delta) => {
    time.current += delta
    
    // 每0.1秒切换一次帧
    if (time.current > 0.1) {
      time.current = 0
      // 使用第一行的前8帧 (水平方向)
      setFrameIndex(prev => (prev + 1) % 8)
    }
    
    if (texture) {
      // 设置UV映射
      // 8列，3行
      const columns = 8
      const rows = 3
      
      texture.repeat.set(1/columns, 1/rows)
      // 计算当前帧的UV偏移 - 使用第一行
      const column = frameIndex % columns
      texture.offset.x = column / columns
      texture.offset.y = 0 // 第一行蜜蜂形象最完整
    }
  })
  
  // 根据类型选择不同的颜色
  const bodyColor = type === 0 ? honeybeeColor : 
                   type === 1 ? "#FF8C00" : 
                   type === 2 ? "#FF6347" : "#FF4500";
  
  return (
    <group scale={[scale, scale, scale]}>
      {texture ? (
        // 使用精灵表的单个蜜蜂
        <mesh>
          <planeGeometry args={[1.5, 1.5]} />
          <meshBasicMaterial map={texture} transparent />
        </mesh>
      ) : (
        // 3D几何体备用
        <group>
          {/* 身体 - 椭圆形 */}
          <mesh position={[0, 0, 0]}>
            <sphereGeometry args={[0.5, 16, 16]} />
            <meshBasicMaterial color={bodyColor} />
          </mesh>
          
          {/* 黑色条纹 */}
          <mesh position={[0, 0.1, 0.3]} rotation={[0.3, 0, 0]}>
            <boxGeometry args={[0.8, 0.15, 0.1]} />
            <meshBasicMaterial color="black" />
          </mesh>
          
          <mesh position={[0, -0.1, 0.3]} rotation={[-0.3, 0, 0]}>
            <boxGeometry args={[0.8, 0.15, 0.1]} />
            <meshBasicMaterial color="black" />
          </mesh>
          
          {/* 翅膀 - 使用sin函数实现扇动效果 */}
          <mesh position={[0.4, 0, 0.1]} rotation={[0, Math.sin(time.current) * 0.2 + 0.3, 0]}>
            <planeGeometry args={[0.7, 0.5]} />
            <meshBasicMaterial color="white" transparent opacity={0.7} side={BackSide} />
          </mesh>
          
          <mesh position={[-0.4, 0, 0.1]} rotation={[0, Math.sin(time.current) * 0.2 - 0.3, 0]}>
            <planeGeometry args={[0.7, 0.5]} />
            <meshBasicMaterial color="white" transparent opacity={0.7} side={BackSide} />
          </mesh>
        </group>
      )}
    </group>
  )
}

// 敌人系统
function EnemySystem({ enemies, setEnemies, bullets, setBullets, onEnemyDestroyed, speedMultiplier = 1, texture }) {
  const enemyRefs = useRef([])
  const time = useRef(0)
  
  // 初始化敌人引用数组
  useEffect(() => {
    enemyRefs.current = enemies.map(() => createRef())
  }, [enemies.length])
  
  // 碰撞检测和敌人移动
  useFrame(() => {
    time.current += 0.01
    
    // 检测子弹碰撞
    let bulletsToRemove = [];
    
    const newEnemies = enemies.filter((enemy, index) => {
      // 蜜蜂式移动 - 横向摆动
      enemy.position.x = enemy.startX + Math.sin(time.current + enemy.offset) * 2
      
      // 缓慢向玩家移动（向下）- 应用速度乘数
      enemy.position.y -= 0.02 * speedMultiplier
      
      // 检测子弹碰撞
      const hitBulletIndex = bullets.findIndex(bullet => {
        const dx = bullet.position.x - enemy.position.x
        const dy = bullet.position.y - enemy.position.y
        const dz = bullet.position.z - enemy.position.z
        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz)
        return distance < 0.8 // 碰撞半径
      })
      
      if (hitBulletIndex !== -1) {
        // 记录要移除的子弹
        bulletsToRemove.push(bullets[hitBulletIndex].id)
        onEnemyDestroyed(enemy.type || 0)
        return false
      }
      
      // 移除超出屏幕的敌人
      if (enemy.position.y < -10) return false
      
      return true
    })
    
    // 移除击中敌人的子弹
    if (bulletsToRemove.length > 0) {
      setBullets(bullets.filter(bullet => !bulletsToRemove.includes(bullet.id)))
    }
    
    if (newEnemies.length !== enemies.length) {
      setEnemies(newEnemies)
    }
  })

  return (
    <group>
      {enemies.map((enemy, index) => (
        <group 
          key={enemy.id} 
          position={[enemy.position.x, enemy.position.y, enemy.position.z]}
        >
          <EnemyModel type={enemy.type || 0} texture={texture} />
        </group>
      ))}
    </group>
  )
}

// 任务等级组件
function LevelDisplay({ score }) {
  // 根据分数确定当前等级
  const getLevel = (score) => {
    if (score >= 3000) return { level: 3, speedMultiplier: 2.0, color: "#FF0000" };
    if (score >= 1000) return { level: 2, speedMultiplier: 1.5, color: "#FFAA00" };
    return { level: 1, speedMultiplier: 1.0, color: "#00FF00" };
  };
  
  const { level, color } = getLevel(score);
  
  return (
    <Html position={[-10, 6, 0]}>
      <div style={{ 
        color: 'white', 
        fontSize: '18pt', 
        fontFamily: 'monospace',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        gap: '5px'
      }}>
        <div style={{ fontWeight: 'bold' }}>等级: {level}</div>
        <div style={{ 
          width: '100px', 
          height: '12px', 
          backgroundColor: '#333',
          border: '2px solid white',
          borderRadius: '6px',
          overflow: 'hidden'
        }}>
          <div style={{ 
            width: `${Math.min(100, (score % 1000) / 10)}%`, 
            height: '100%', 
            backgroundColor: color,
            transition: 'width 0.3s'
          }} />
        </div>
      </div>
    </Html>
  );
}

// 主游戏组件
function GalagaGame() {
  // 加载贴图，使用try-catch处理加载错误
  const [texturesLoaded, setTexturesLoaded] = useState({
    bumblebee: null,
    honeybee: null,
    wisteria: null
  })
  
  // 尝试加载贴图
  useEffect(() => {
    const loader = new TextureLoader()
    
    // 加载大黄蜂贴图
    loader.load(
      'assets/textures/bumblebee_fixed.png',
      (texture) => {
        setTexturesLoaded(prev => ({ ...prev, bumblebee: texture }))
      },
      undefined,
      (error) => {
        console.error('无法加载大黄蜂贴图:', error)
      }
    )
    
    // 加载蜜蜂贴图
    loader.load(
      'assets/textures/honeybee.png',
      (texture) => {
        setTexturesLoaded(prev => ({ ...prev, honeybee: texture }))
      },
      undefined,
      (error) => {
        console.error('无法加载蜜蜂贴图:', error)
      }
    )
    
    // 加载紫藤花背景贴图
    loader.load(
      'assets/textures/wisteria.png',
      (texture) => {
        setTexturesLoaded(prev => ({ ...prev, wisteria: texture }))
      },
      undefined,
      (error) => {
        console.error('无法加载紫藤花贴图:', error)
      }
    )
  }, [])
  
  const [bullets, setBullets] = useState([])
  const [enemies, setEnemies] = useState([])
  const [score, setScore] = useState(0)
  const [gameOver, setGameOver] = useState(false)
  const nextBulletId = useRef(0)
  const nextEnemyId = useRef(0)
  const spawnTimer = useRef(0)
  const soundFX = useRef(null)
  
  // 根据分数计算速度乘数
  const getSpeedMultiplier = (score) => {
    if (score >= 3000) return 2.0;
    if (score >= 1000) return 1.5;
    return 1.0;
  };
  
  const speedMultiplier = getSpeedMultiplier(score);
  
  // 初始化音效系统和清理初始子弹
  useEffect(() => {
    soundFX.current = new RetroSoundFX()
    
    // 确保游戏开始时没有子弹
    setBullets([])
    
    return () => {
      // 清理音频上下文
      if (soundFX.current && soundFX.current.audioContext) {
        soundFX.current.audioContext.close()
      }
    }
  }, [])
  
  // 射击处理
  const handleShoot = (playerX) => {
    if (gameOver) return
    
    const newBullet = {
      id: nextBulletId.current++,
      position: new Vector3(playerX, -7, 0)
    }
    
    setBullets([...bullets, newBullet])
    
    // 播放射击音效
    if (soundFX.current) {
      soundFX.current.playShoot()
    }
  }
  
  // 敌人被摧毁处理
  const handleEnemyDestroyed = (type = 0) => {
    // 不同类型的敌人给予不同的分数
    const scoreValues = [100, 150, 200, 300]
    const scoreValue = scoreValues[type] || 100
    
    setScore(score + scoreValue)
    
    // 播放爆炸音效
    if (soundFX.current) {
      soundFX.current.playExplosion()
    }
  }
  
  // 游戏循环 - 生成敌人
  useFrame((state) => {
    if (gameOver) return
    
    spawnTimer.current += 1
    
    // 每120帧生成一波敌人
    if (spawnTimer.current % 120 === 0) {
      const newEnemies = []
      const enemyCount = Math.min(5 + Math.floor(score / 1000), 10)
      
      // 创建多行敌人阵型
      const rows = Math.min(3, 1 + Math.floor(score / 2000))
      const enemiesPerRow = Math.ceil(enemyCount / rows)
      
      for (let row = 0; row < rows; row++) {
        for (let i = 0; i < enemiesPerRow; i++) {
          if (newEnemies.length >= enemyCount) break;
          
          const startX = MathUtils.randFloatSpread(8)
          const startY = 10 + row * 2 // 在屏幕顶部生成敌人
          const startZ = 0 // 在z=0平面上
          
          // 根据行数分配不同类型的敌人
          const type = Math.min(row, 3)
          
          newEnemies.push({
            id: nextEnemyId.current++,
            position: new Vector3(startX, startY, startZ),
            startX,
            startY,
            offset: Math.random() * Math.PI * 2,
            type
          })
        }
      }
      
      setEnemies([...enemies, ...newEnemies])
      
      // 播放敌人移动音效
      if (soundFX.current) {
        soundFX.current.playEnemyMove()
      }
    }
    
    // 检测敌人是否到达玩家位置（游戏结束条件）
    if (enemies.some(enemy => enemy.position.y < -8)) {
      setGameOver(true)
    }
  })

  // 添加错误处理和加载状态检测
  useEffect(() => {
    const checkLoading = () => {
      if (!texturesLoaded) {
        console.error('贴图加载失败，检查资源路径');
      }
    };
    
    // 给一个合理的延迟检查资源是否加载
    const timer = setTimeout(checkLoading, 5000);
    return () => clearTimeout(timer);
  }, [texturesLoaded]);

  return (
    <>
      {/* 相机控制 - 允许拖拽和不同视角 */}
      <OrbitControls 
        enableZoom={true}
        enablePan={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={50}
        minPolarAngle={0}
        maxPolarAngle={Math.PI / 2}
      />
      
      {/* 紫藤花背景 */}
      <WisteriaBackground texture={texturesLoaded.wisteria} />
      
      {/* 花瓣粒子效果 */}
      <FlowerPetals />
      
      {/* 环境光 */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 10]} intensity={1} />
      
      {/* 玩家飞船 */}
      <PlayerShip position={[0, -8, 0]} onShoot={handleShoot} texture={texturesLoaded.bumblebee} />
      
      {/* 子弹系统 */}
      <BulletSystem bullets={bullets} setBullets={setBullets} />
      
      {/* 敌人系统 - 传递速度乘数 */}
      <EnemySystem 
        enemies={enemies} 
        setEnemies={setEnemies} 
        bullets={bullets} 
        setBullets={setBullets}
        onEnemyDestroyed={handleEnemyDestroyed}
        speedMultiplier={speedMultiplier}
        texture={texturesLoaded.honeybee}
      />
      
      {/* 分数显示 - HTML叠加层 */}
      <Html position={[-10, 8, 0]} style={{ color: 'white', fontSize: '18pt', fontFamily: 'monospace', fontWeight: 'bold' }}>
        分数: {score}
      </Html>
      
      {/* 等级显示 */}
      <LevelDisplay score={score} />
      
      {/* 游戏结束显示 */}
      {gameOver && (
        <Html center position={[0, 0, 0]} style={{ color: 'red', fontSize: '3em', fontFamily: 'monospace' }}>
          GAME OVER<br/>
          SCORE: {score}<br/>
          <button 
            onClick={() => {
              setGameOver(false)
              setScore(0)
              setEnemies([])
              setBullets([])
              nextEnemyId.current = 0
              nextBulletId.current = 0
            }}
            style={{ 
              background: '#EA4335', 
              color: 'white', 
              border: 'none', 
              padding: '10px 20px',
              marginTop: '20px',
              cursor: 'pointer',
              fontFamily: 'monospace'
            }}
          >
            RESTART
          </button>
        </Html>
      )}
    </>
  )
}

export default GalagaGame
