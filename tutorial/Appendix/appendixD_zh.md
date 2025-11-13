# 附录D：使用AgentSpace构建代理 (Building Agents with AgentSpace)

## 概述
AgentSpace是一个开源框架，专注于创建分布式、事件驱动的代理系统。它提供了一种独特的方法来构建能够协作和共享知识的代理。

## AgentSpace核心概念

### 1. 代理空间 (Agent Space)
代理空间是代理系统的核心数据存储，代理可以写入和读取信息：

- **共享知识库**：所有代理都可以访问和修改的空间
- **事件驱动**：当空间中的内容发生变化时，会触发事件
- **分布式**：支持多个代理空间实例

### 2. 代理 (Agent)
代理是系统中的独立单元，可以：

- 观察代理空间中的变化
- 在空间中写入信息
- 响应事件

## 基本架构

### 代码示例：基本代理空间设置
```python
# 首先，需要安装agentspace包
# pip install agentspace

from agentspace import Space, event, run

class RobotAgent:
    def __init__(self, name, space):
        self.name = name
        self.space = space
    
    def start(self):
        # 设置事件处理器
        self.space.attach(self.sense_environment, ['sensor_input'])
        self.space.attach(self.respond_to_command, ['command'])
    
    def sense_environment(self, sensor_data):
        """处理传感器输入"""
        print(f"{self.name} 感知到: {sensor_data}")
        # 处理传感器数据并决定行动
        if 'object' in sensor_data:
            self.space.write('detected_object', sensor_data['object'])
    
    def respond_to_command(self, command):
        """响应命令"""
        print(f"{self.name} 收到命令: {command}")
        if command == 'move_forward':
            # 执行移动操作
            self.space.write('robot_status', 'moving')
            self.space.write('action_taken', 'moved_forward')
        elif command == 'stop':
            self.space.write('robot_status', 'stopped')

# 使用示例
if __name__ == "__main__":
    # 创建代理空间
    space = Space()
    
    # 创建并启动机器人代理
    robot = RobotAgent("Robo1", space)
    robot.start()
    
    # 模拟传感器输入
    space.write('sensor_input', {'object': 'red_ball', 'distance': 10})
    
    # 模拟命令
    space.write('command', 'move_forward')
    
    # 运行代理系统
    run()
```

### 3. 事件系统
事件系统允许代理响应代理空间中的变化：

```python
from agentspace import Space, event

class MonitoringAgent:
    def __init__(self, space):
        self.space = space
        # 注册事件处理程序
        event('robot_status', self.monitor_robot_status)
        event('detected_object', self.monitor_detected_objects)
    
    def monitor_robot_status(self, status):
        """监控机器人状态变化"""
        print(f"监控代理: 机器人状态改变为 {status}")
        if status == 'error':
            # 执行错误处理逻辑
            self.space.write('error_handler', 'activate')
    
    def monitor_detected_objects(self, obj):
        """监控检测到的对象"""
        print(f"监控代理: 检测到对象 {obj}")
        if obj['type'] == 'hazard':
            self.space.write('warning', f'Hazard detected: {obj["name"]}')
```

## 高级用法

### 1. 分布式代理系统
AgentSpace支持分布式设置：

```python
from agentspace import Space, remote
import threading

# 在不同节点上创建代理空间
def create_local_agent_space():
    space = Space()
    
    # 添加本地代理
    sensor_agent = SensorAgent(space)
    sensor_agent.start()
    
    return space

def connect_to_remote_space():
    # 连接到远程空间
    remote_space = remote('tcp://192.168.1.100:8000')
    return remote_space

# 同步本地和远程空间
class SynchronizationAgent:
    def __init__(self, local_space, remote_space):
        self.local_space = local_space
        self.remote_space = remote_space
        
        # 设置双向同步
        self.local_space.attach(self.sync_to_remote, ['*'])
        self.remote_space.attach(self.sync_to_local, ['*'])
    
    def sync_to_remote(self, key, value):
        """将本地更新同步到远程"""
        self.remote_space.write(key, value)
    
    def sync_to_local(self, key, value):
        """将远程更新同步到本地"""
        self.local_space.write(key, value)
```

### 2. 条件代理 (Conditional Agents)
代理可以响应特定条件：

```python
from agentspace import Space, when

class ConditionalAgent:
    def __init__(self, space):
        self.space = space
        self.setup_conditions()
    
    def setup_conditions(self):
        # 当检测到红色物体且机器人状态为空闲时
        when(
            lambda: self.space.read('detected_object', {}).get('color') == 'red' and 
                    self.space.read('robot_status') == 'idle',
            self.handle_red_object
        )
        
        # 当电池电量低于20%时
        when(
            lambda: self.space.read('battery_level', 100) < 20,
            self.handle_low_battery
        )
    
    def handle_red_object(self):
        """处理红色物体"""
        print("发现红色物体，移动到物体位置")
        self.space.write('command', 'move_to_object')
        self.space.write('action_priority', 'high')
    
    def handle_low_battery(self):
        """处理低电量"""
        print("电池电量低，返回充电站")
        self.space.write('command', 'return_to_charger')
        self.space.write('action_priority', 'critical')
```

## 实际应用示例

### 家庭自动化系统
```python
from agentspace import Space, event, run

class HomeAutomationSystem:
    def __init__(self):
        self.space = Space()
        self.agents = []
        
        # 初始化各种代理
        self.create_sensor_agents()
        self.create_control_agents()
        self.create_monitoring_agents()
    
    def create_sensor_agents(self):
        """创建传感器代理"""
        class TemperatureSensor:
            def __init__(self, space):
                self.space = space
                self.simulate_reading()
            
            def simulate_reading(self):
                import random
                temperature = 20 + random.uniform(-5, 5)
                self.space.write('temperature', temperature)
                # 每5秒更新一次
                threading.Timer(5.0, self.simulate_reading).start()
        
        temp_sensor = TemperatureSensor(self.space)
        self.agents.append(temp_sensor)
    
    def create_control_agents(self):
        """创建控制代理"""
        class ThermostatController:
            def __init__(self, space):
                self.space = space
                event('temperature', self.adjust_temperature)
            
            def adjust_temperature(self, temp):
                if temp < 18:
                    self.space.write('heater', 'on')
                    self.space.write('ac', 'off')
                elif temp > 24:
                    self.space.write('heater', 'off')
                    self.space.write('ac', 'on')
                else:
                    self.space.write('heater', 'auto')
                    self.space.write('ac', 'auto')
        
        thermostat = ThermostatController(self.space)
        self.agents.append(thermostat)
    
    def create_monitoring_agents(self):
        """创建监控代理"""
        class EnergyMonitor:
            def __init__(self, space):
                self.space = space
                event(['heater', 'ac'], self.calculate_energy_usage)
            
            def calculate_energy_usage(self, value):
                # 简单的能耗计算
                usage = 1.5 if value == 'on' else 0.1
                self.space.write('energy_usage', usage)
        
        energy_monitor = EnergyMonitor(self.space)
        self.agents.append(energy_monitor)

# 启动家庭自动化系统
if __name__ == "__main__":
    system = HomeAutomationSystem()
    run()
```

### 机器人协作系统
```python
from agentspace import Space, event, broadcast

class RobotCollaborationSystem:
    def __init__(self):
        self.space = Space()
        self.robots = []
        
        # 创建多个机器人代理
        for i in range(3):
            robot = RobotAgent(f"Robot_{i}", self.space)
            self.robots.append(robot)
    
    def coordinate_robots(self):
        """协调机器人行动"""
        # 机器人可以读取彼此的状态和意图
        event('robot_intent', self.handle_coordination)
        
    def handle_coordination(self, intent_data):
        """处理协调信息"""
        robot_id = intent_data['robot_id']
        intent = intent_data['intent']
        
        # 检查是否有冲突
        other_intents = self.space.match('robot_intent', 
                                       lambda x: x['robot_id'] != robot_id)
        
        for other_intent in other_intents:
            if self.check_conflict(intent, other_intent['intent']):
                # 解决冲突
                self.resolve_conflict(robot_id, other_intent['robot_id'])

class RobotAgent:
    def __init__(self, name, space):
        self.name = name
        self.space = space
        
        # 机器人状态
        self.position = [0, 0]
        self.task = None
        
        # 设置事件处理
        event(f'{name}_task', self.assign_task)
        event('global_task_queue', self.check_for_tasks)
    
    def assign_task(self, task):
        """分配任务给机器人"""
        self.task = task
        print(f"{self.name} 被分配任务: {task}")
        self.execute_task()
    
    def check_for_tasks(self, task_queue):
        """检查是否有可用任务"""
        available_tasks = [task for task in task_queue 
                          if task.get('assigned_to') is None]
        if available_tasks:
            task = available_tasks[0]
            task['assigned_to'] = self.name
            self.space.write('global_task_queue', task_queue)
            self.space.write(f'{self.name}_task', task)
    
    def execute_task(self):
        """执行分配的任务"""
        if self.task:
            print(f"{self.name} 正在执行任务: {self.task}")
            # 执行任务逻辑
            # ...
            
            # 任务完成后更新状态
            self.space.write(f'{self.name}_status', 'completed')
            self.task = None

# 使用示例
collaboration_system = RobotCollaborationSystem()
collaboration_system.coordinate_robots()
```

## 优势和挑战

### 优势
- **简单性**：易于理解和实现
- **灵活性**：支持各种类型的应用
- **分布式**：天然支持分布式系统
- **松耦合**：代理之间高度解耦

### 挑战
- **调试**：分布式事件驱动系统可能难以调试
- **状态一致性**：确保所有代理看到一致的状态
- **性能**：大量代理可能导致性能问题

## 最佳实践

### 1. 设计良好的命名空间
```python
# 使用清晰的命名空间组织数据
space.write('robot1.position.x', 10)
space.write('robot1.position.y', 20)
space.write('robot1.status', 'active')
```

### 2. 错误处理
```python
def safe_space_read(space, key, default=None):
    """安全地从空间读取数据"""
    try:
        return space.read(key, default)
    except Exception as e:
        print(f"从空间读取 {key} 时出错: {e}")
        return default
```

### 3. 性能优化
- 限制事件频率
- 使用适当的数据序列化
- 实现缓存机制

## 总结
AgentSpace提供了一种独特的事件驱动方法来构建代理系统。其共享空间概念使得代理之间的协作变得简单直观。通过正确使用其事件系统和分布式能力，可以构建复杂的协作代理系统。虽然在调试和性能方面存在一些挑战，但其简单性和灵活性使其成为构建某些类型代理应用的良好选择。