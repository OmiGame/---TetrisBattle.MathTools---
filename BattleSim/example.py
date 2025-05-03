"""
战斗模拟示例
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from BattleSim.battle_engine import BattleEngine
from BattleSim.models.battle_state import Unit, UnitState, UnitType
from BattleSim.battle_configs.battle_config import WAVE_CONFIGS, PLAYER_CONFIG, TOWER_CONFIG, ROGUE_SKILL_TRIGGER
from BattleSim.visualization.visualization import BattleVisualizer
import time

def calculate_total_power(units: list) -> float:
    """计算单位总战力"""
    return sum(unit.attack * unit.hp for unit in units if unit.state != UnitState.DEAD)

def calculate_spawn_rate(battle_state) -> float:
    """计算当前出兵速度（每秒）"""
    if not battle_state.last_spawn_time.get('player_spawn'):
        return 0
    current_time = time.time()
    time_since_last_spawn = current_time - battle_state.last_spawn_time['player_spawn']
    if time_since_last_spawn == 0:
        return 0
    return 1 / time_since_last_spawn

def main():
    # 创建战斗引擎实例
    engine = BattleEngine()
    
    # 创建防御塔单位
    player_tower = Unit(
        id="player_tower",
        type=UnitType.TOWER,
        level=1,
        hp=TOWER_CONFIG["player_tower"]["hp"],
        max_hp=TOWER_CONFIG["player_tower"]["hp"],
        attack=TOWER_CONFIG["player_tower"]["attack"],
        attack_speed=TOWER_CONFIG["player_tower"]["attack_speed"],
        attack_range=TOWER_CONFIG["player_tower"]["attack_range"],
        move_speed=TOWER_CONFIG["player_tower"]["move_speed"],
        position=TOWER_CONFIG["player_tower"]["position"]
    )
    
    enemy_tower = Unit(
        id="enemy_tower",
        type=UnitType.TOWER,
        level=1,
        hp=TOWER_CONFIG["enemy_tower"]["hp"],
        max_hp=TOWER_CONFIG["enemy_tower"]["hp"],
        attack=TOWER_CONFIG["enemy_tower"]["attack"],
        attack_speed=TOWER_CONFIG["enemy_tower"]["attack_speed"],
        attack_range=TOWER_CONFIG["enemy_tower"]["attack_range"],
        move_speed=TOWER_CONFIG["enemy_tower"]["move_speed"],
        position=TOWER_CONFIG["enemy_tower"]["position"]
    )
    
    # 初始化战斗状态
    battle_state = engine.initialize_battle(
        player_config=PLAYER_CONFIG,
        wave_configs=WAVE_CONFIGS,
        player_tower=player_tower,
        enemy_tower=enemy_tower
    )
    
    # 创建可视化器
    visualizer = BattleVisualizer()
    
    # 主循环
    running = True
    while running and not battle_state.game_over:
        # 更新战斗状态
        engine._update_battle(battle_state)
        
        # 渲染
        result = visualizer.render(battle_state)
        if result == False:  # 用户关闭窗口
            running = False
        elif result == "space":  # 空格键触发
            engine.handle_keyboard_input(battle_state, " ")
    
    # 输出战斗结果
    battle_result = engine._generate_battle_result(battle_state)
    
    # 显示战斗结果并等待ESC键退出
    visualizer.show_battle_result(battle_result)
    
    # 清理资源
    visualizer.cleanup()
    sys.exit()

if __name__ == "__main__":
    main() 