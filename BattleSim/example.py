"""
战斗模拟示例
"""

import pygame
import sys
from BattleSim.battle_engine import BattleEngine
from BattleSim.models.battle_state import Unit, UnitState, UnitType
from BattleSim.config.battle_config import WAVE_CONFIGS, PLAYER_CONFIG, TOWER_CONFIG, ROGUE_SKILL_TRIGGER
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
    # 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("战斗模拟")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
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
    
    # 主循环
    running = True
    while running and not battle_state.game_over:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    engine.handle_keyboard_input(battle_state, " ")
        
        # 更新战斗状态
        engine._update_battle(battle_state)
        
        # 渲染
        screen.fill((255, 255, 255))
        
        # 绘制防御塔
        pygame.draw.rect(screen, (0, 0, 255), 
            (battle_state.player_tower.position.x * 10, 
             battle_state.player_tower.position.y * 10, 20, 20))
        pygame.draw.rect(screen, (255, 0, 0), 
            (battle_state.enemy_tower.position.x * 10, 
             battle_state.enemy_tower.position.y * 10, 20, 20))
        
        # 绘制单位
        for unit in battle_state.player_units:
            if unit.state != UnitState.DEAD:
                pygame.draw.circle(screen, (0, 0, 255), 
                    (int(unit.position.x * 10), int(unit.position.y * 10)), 5)
        
        for unit in battle_state.enemy_units:
            if unit.state != UnitState.DEAD:
                pygame.draw.circle(screen, (255, 0, 0), 
                    (int(unit.position.x * 10), int(unit.position.y * 10)), 5)
        
        # 显示战斗信息
        player_alive = sum(1 for u in battle_state.player_units if u.state != UnitState.DEAD)
        enemy_alive = sum(1 for u in battle_state.enemy_units if u.state != UnitState.DEAD)
        player_power = calculate_total_power(battle_state.player_units)
        enemy_power = calculate_total_power(battle_state.enemy_units)
        spawn_rate = calculate_spawn_rate(battle_state)
        rogue_skill_count = len(battle_state.active_rogue_skills)
        
        info_texts = [
            f"我方存活单位: {player_alive}",
            f"敌方存活单位: {enemy_alive}",
            f"我方总战力: {player_power:.1f}",
            f"敌方总战力: {enemy_power:.1f}",
            f"出兵速度: {spawn_rate:.1f}/秒",
            f"已触发肉鸽技能: {rogue_skill_count}次"
        ]
        
        for i, text in enumerate(info_texts):
            text_surface = font.render(text, True, (0, 0, 0))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 显示战斗日志
        for i, log in enumerate(battle_state.battle_log[-5:]):
            text = font.render(log, True, (0, 0, 0))
            screen.blit(text, (10, 500 + i * 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    # 输出战斗结果
    battle_result = engine._generate_battle_result(battle_state)
    print(f"战斗结束！胜利者: {battle_result.winner}")
    print(f"总战斗时长: {battle_result.total_duration:.1f} 秒")
    print("\n战斗日志:")
    for log in battle_result.battle_log:
        print(log)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 