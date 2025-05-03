"""
战斗可视化模块
"""

import pygame
from typing import List, Dict, Any
from ..models.battle_state import BattleState, Unit, UnitState
from .battle_info import BattleInfoCalculator

class BattleVisualizer:
    def __init__(self, width: int = 800, height: int = 600):
        """初始化可视化器"""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("战斗模拟")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.width = width
        self.height = height
        self.info_calculator = BattleInfoCalculator()

    def render(self, battle_state: BattleState, fps: int = 60):
        """渲染当前战斗状态"""
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "space"
                elif event.key == pygame.K_ESCAPE:
                    return "esc"

        # 清空屏幕
        self.screen.fill((255, 255, 255))

        # 绘制防御塔
        self._draw_tower(battle_state.player_tower, (0, 0, 255))
        self._draw_tower(battle_state.enemy_tower, (255, 0, 0))

        # 绘制单位
        self._draw_units(battle_state.player_units, (0, 0, 255))
        self._draw_units(battle_state.enemy_units, (255, 0, 0))

        # 显示战斗信息
        self._draw_battle_info(battle_state)

        # 显示战斗日志
        self._draw_battle_log(battle_state)

        pygame.display.flip()
        self.clock.tick(fps)
        return True

    def _draw_tower(self, tower: Unit, color: tuple):
        """绘制防御塔"""
        pygame.draw.rect(self.screen, color,
            (tower.position.x * 10,
             tower.position.y * 10, 20, 20))

    def _draw_units(self, units: List[Unit], color: tuple):
        """绘制单位"""
        for unit in units:
            if unit.state != UnitState.DEAD:
                pygame.draw.circle(self.screen, color,
                    (int(unit.position.x * 10),
                     int(unit.position.y * 10)), 5)

    def _draw_battle_info(self, battle_state: BattleState):
        """绘制战斗信息"""
        battle_stats = self.info_calculator.calculate_battle_stats(battle_state)
        info_texts = self.info_calculator.format_battle_info(battle_stats)

        for i, text in enumerate(info_texts):
            text_surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surface, (10, 10 + i * 25))

    def _draw_battle_log(self, battle_state: BattleState):
        """绘制战斗日志"""
        for i, log in enumerate(battle_state.battle_log[-5:]):
            text = self.font.render(log, True, (0, 0, 0))
            self.screen.blit(text, (10, 500 + i * 20))

    def show_battle_result(self, battle_result):
        """显示战斗结果并等待ESC键退出"""
        while True:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True

            # 清空屏幕
            self.screen.fill((255, 255, 255))

            # 显示战斗结果
            header_texts, log_texts = self.info_calculator.format_battle_result(battle_result)
            
            # 显示标题文本
            for i, text in enumerate(header_texts):
                text_surface = self.font.render(text, True, (0, 0, 0))
                self.screen.blit(text_surface, (10, 10 + i * 25))
            
            # 显示日志文本
            for i, log in enumerate(log_texts):
                text = self.font.render(log, True, (0, 0, 0))
                self.screen.blit(text, (10, 100 + i * 20))
            
            # 显示提示信息
            prompt = "按ESC键退出"
            prompt_surface = self.font.render(prompt, True, (0, 0, 0))
            self.screen.blit(prompt_surface, (10, 500))
            
            pygame.display.flip()
            self.clock.tick(60)

    def cleanup(self):
        """清理资源"""
        pygame.quit()

class VisualizationInfo:
    """可视化信息数据类"""
    def __init__(self):
        self.unit_positions: Dict[str, List[Dict[str, float]]] = {}
        self.unit_states: Dict[str, List[str]] = {}
        self.battle_events: List[Dict[str, Any]] = []
        self.frame_times: List[float] = []

def visualize_battle(visualization_info: VisualizationInfo):
    """可视化战斗过程"""
    # 实现可视化逻辑
    pass 