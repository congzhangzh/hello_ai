import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt

# 方法1：设置默认字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 或 'SimHei', 'SimSun'
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class GRESimulation:
    """简易的梯度回波(GRE)序列磁共振仿真类"""
    
    def __init__(self, fov=240, matrix_size=128, num_tissues=4, te=10, tr=100, flip_angle=30):
        """
        初始化GRE仿真参数
        
        参数:
            fov: 成像视野大小(mm)
            matrix_size: 矩阵大小
            num_tissues: 模拟组织数量
            te: 回波时间(ms)
            tr: 重复时间(ms)
            flip_angle: 翻转角(度)
        """
        self.fov = fov
        self.matrix_size = matrix_size
        self.num_tissues = num_tissues
        self.te = te
        self.tr = tr
        self.flip_angle = flip_angle * np.pi / 180  # 转换为弧度
        
        # 像素尺寸(mm)
        self.pixel_size = fov / matrix_size
        
        # 创建空白图像
        self.phantom = np.zeros((matrix_size, matrix_size))
        self.signal = np.zeros((matrix_size, matrix_size), dtype=complex)
        
        # 组织参数: [T1(ms), T2(ms), 质子密度]
        self.tissue_params = {
            'air': [0, 0, 0],
            'csf': [4000, 2000, 1.0],
            'gray_matter': [1100, 95, 0.8],
            'white_matter': [800, 80, 0.65],
            'muscle': [900, 50, 0.7]
        }
        
        # 创建简单的数字模型
        self._create_phantom()
    
    def _create_phantom(self):
        """创建简单的数字模型"""
        center = self.matrix_size // 2
        radius = self.matrix_size // 3
        
        # 背景为空气
        self.phantom.fill(0)
        
        # 创建头部轮廓(圆形)
        y, x = np.ogrid[:self.matrix_size, :self.matrix_size]
        dist_from_center = np.sqrt((x - center)**2 + (y - center)**2)
        skull_mask = dist_from_center <= radius
        self.phantom[skull_mask] = 1  # CSF
        
        # 脑组织(灰质)
        brain_mask = dist_from_center <= radius * 0.9
        self.phantom[brain_mask] = 2  # 灰质
        
        # 脑组织(白质) - 创建几个椭圆区域
        for i in range(-2, 3):
            for j in range(-2, 3):
                if i == 0 and j == 0:
                    continue
                x_center = center + i * radius * 0.3
                y_center = center + j * radius * 0.3
                
                y, x = np.ogrid[:self.matrix_size, :self.matrix_size]
                dist = np.sqrt((x - x_center)**2 + (y - y_center)**2)
                white_matter_mask = dist <= radius * 0.15
                self.phantom[white_matter_mask] = 3  # 白质
        
        # 添加肌肉组织在头部周围
        muscle_region = (dist_from_center >= radius * 0.95) & (dist_from_center <= radius * 1.05)
        self.phantom[muscle_region] = 4  # 肌肉
    
    def simulate_gre(self):
        """模拟GRE序列并生成信号"""
        # 组织类型映射到参数
        tissue_to_params = {
            0: self.tissue_params['air'],
            1: self.tissue_params['csf'],
            2: self.tissue_params['gray_matter'],
            3: self.tissue_params['white_matter'],
            4: self.tissue_params['muscle']
        }
        
        # 对每个像素计算信号
        for i in range(self.matrix_size):
            for j in range(self.matrix_size):
                tissue_idx = int(self.phantom[i, j])
                t1, t2, pd = tissue_to_params[tissue_idx]
                
                if pd == 0:  # 空气没有信号
                    self.signal[i, j] = 0
                    continue
                
                # GRE信号方程: S = PD * sin(α) * (1 - exp(-TR/T1)) / (1 - cos(α) * exp(-TR/T1)) * exp(-TE/T2*)
                # 注意：这里我们使用T2代替T2*作为简化
                e1 = np.exp(-self.tr / t1) if t1 > 0 else 0
                e2 = np.exp(-self.te / t2) if t2 > 0 else 0
                
                # 计算稳态磁化强度
                m_xy = pd * np.sin(self.flip_angle) * (1 - e1) / (1 - np.cos(self.flip_angle) * e1) * e2
                
                # 简单起见，我们假设相位为0
                self.signal[i, j] = m_xy
        
        return np.abs(self.signal)  # 返回信号幅值
    
    def add_noise(self, snr=20):
        """添加高斯噪声到信号"""
        # 计算标准差
        signal_power = np.mean(np.abs(self.signal)**2)
        sigma = np.sqrt(signal_power / snr)
        
        # 添加复数噪声
        noise_real = np.random.normal(0, sigma, self.signal.shape)
        noise_imag = np.random.normal(0, sigma, self.signal.shape)
        noise = noise_real + 1j * noise_imag
        
        self.signal = self.signal + noise
        return np.abs(self.signal)
    
    def plot_results(self):
        """绘制仿真结果"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # 绘制数字模型
        im0 = axes[0].imshow(self.phantom, cmap='viridis')
        axes[0].set_title('数字模型')
        plt.colorbar(im0, ax=axes[0], label='组织类型')
        
        # 绘制无噪声信号
        signal_magnitude = np.abs(self.signal)
        im1 = axes[1].imshow(signal_magnitude, cmap='gray')
        axes[1].set_title(f'GRE信号 (TE={self.te}ms, TR={self.tr}ms, 翻转角={self.flip_angle*180/np.pi:.1f}°)')
        plt.colorbar(im1, ax=axes[1], label='信号强度')
        
        # 绘制添加噪声后的信号
        noisy_signal = self.add_noise(snr=15)
        im2 = axes[2].imshow(noisy_signal, cmap='gray')
        axes[2].set_title('添加噪声后的信号 (SNR=15)')
        plt.colorbar(im2, ax=axes[2], label='信号强度')
        
        # 添加参数信息
        param_text = f"FOV: {self.fov}mm\nMatrix: {self.matrix_size}×{self.matrix_size}\n"
        param_text += f"像素大小: {self.pixel_size:.2f}mm\n"
        param_text += "组织参数 [T1, T2, PD]:\n"
        param_text += f"CSF: {self.tissue_params['csf']}\n"
        param_text += f"灰质: {self.tissue_params['gray_matter']}\n"
        param_text += f"白质: {self.tissue_params['white_matter']}\n"
        param_text += f"肌肉: {self.tissue_params['muscle']}"
        
        plt.figtext(0.01, 0.02, param_text, fontsize=9, bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def simulate_parameter_effects(self):
        """模拟不同参数对GRE信号的影响"""
        # 保存原始参数
        orig_te = self.te
        orig_tr = self.tr
        orig_flip = self.flip_angle
        
        # 创建图表
        fig, axes = plt.subplots(3, 3, figsize=(15, 15))
        
        # 测试不同的TE值
        te_values = [5, 20, 50]
        for i, te in enumerate(te_values):
            self.te = te
            signal = self.simulate_gre()
            axes[0, i].imshow(signal, cmap='gray')
            axes[0, i].set_title(f'TE = {te}ms')
            if i == 0:
                axes[0, i].set_ylabel('变化TE')
        
        # 测试不同的TR值
        self.te = orig_te
        tr_values = [50, 500, 2000]
        for i, tr in enumerate(tr_values):
            self.tr = tr
            signal = self.simulate_gre()
            axes[1, i].imshow(signal, cmap='gray')
            axes[1, i].set_title(f'TR = {tr}ms')
            if i == 0:
                axes[1, i].set_ylabel('变化TR')
        
        # 测试不同的翻转角
        self.tr = orig_tr
        flip_values = [5, 30, 90]
        for i, flip in enumerate(flip_values):
            self.flip_angle = flip * np.pi / 180
            signal = self.simulate_gre()
            axes[2, i].imshow(signal, cmap='gray')
            axes[2, i].set_title(f'翻转角 = {flip}°')
            if i == 0:
                axes[2, i].set_ylabel('变化翻转角')
        
        # 恢复原始参数
        self.te = orig_te
        self.tr = orig_tr
        self.flip_angle = orig_flip
        
        plt.tight_layout()
        return fig

# 运行仿真示例
def run_simulation():
    # 创建仿真对象，使用自定义参数
    sim = GRESimulation(
        fov=240,           # 成像视野 (mm)
        matrix_size=128,   # 矩阵大小
        te=15,             # 回波时间 (ms)
        tr=100,            # 重复时间 (ms)
        flip_angle=30      # 翻转角 (度)
    )
    
    # 执行GRE仿真
    sim.simulate_gre()
    
    # 绘制结果
    fig1 = sim.plot_results()
    
    # 模拟不同参数的效果
    fig2 = sim.simulate_parameter_effects()
    
    plt.show()

if __name__ == "__main__":
    run_simulation()