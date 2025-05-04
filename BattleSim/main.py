"""
主程序入口
"""

from battle_engine import BattleEngine
from statistics import BattleStatistics
from visualization import BattleVisualizer
from models.battle_state import BattleState
from battle_configs.battle_config import DEFAULT_PLAYER_CONFIG, DEFAULT_WAVE_CONFIGS

def main():
    # 初始化战斗引擎
    battle_engine = BattleEngine()
    
    # 初始化统计模块
    statistics = BattleStatistics()
    
    # 注册事件处理器
    battle_engine.register_event_handler(statistics.handle_event)
    
    # 初始化可视化器
    visualizer = BattleVisualizer()
    
    # 初始化战斗状态
    battle_state = battle_engine.initialize_battle(
        player_config=DEFAULT_PLAYER_CONFIG,
        wave_configs=DEFAULT_WAVE_CONFIGS
    )
    
    # 运行战斗
    while True:
        # 更新战斗状态
        result = battle_engine.run_battle(battle_state)
        
        # 显示战斗结果
        visualizer.show_battle_result(result)
        
        # 显示统计数据
        stats = statistics.calculate_statistics()
        print("\n战斗统计:")
        print(f"单位生成: {stats.unit_spawns}")
        print(f"单位死亡: {stats.unit_deaths}")
        print(f"伤害输出: {stats.damage_dealt}")
        print(f"承受伤害: {stats.damage_taken}")
        print(f"肉鸽技能次数: {stats.rogue_skill_count}")
        print(f"战斗时长: {stats.battle_duration:.1f}秒")
        print(f"胜利者: {stats.winner}")
        
        # 等待用户输入
        key = input("\n按回车键继续，输入q退出: ")
        if key.lower() == 'q':
            break
    
    # 清理资源
    visualizer.cleanup()

if __name__ == "__main__":
    main() 