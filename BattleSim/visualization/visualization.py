"""
战斗可视化模块
"""

import pygame
from typing import List, Dict, Any, Tuple, Optional
from ..models.battle_state import BattleState, Unit, UnitState
from ..statistics import BattleStatistics
from .battle_info import BattleInfoCalculator

class BattleVisualizer:
    # 颜色常量
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_PLAYER_UNIT = (0, 0, 255)    # 蓝色 - 我方单位
    COLOR_ENEMY_UNIT = (255, 0, 0)     # 红色 - 敌方单位
    COLOR_PLAYER_TOWER = (0, 255, 0)   # 绿色 - 我方防御塔
    COLOR_ENEMY_TOWER = (255, 0, 0)    # 红色 - 敌方防御塔
    COLOR_PATH = (255, 215, 0)         # 深黄色 - 单位行进路线
    
    # 配置常量
    DEFAULT_SCREEN_WIDTH = 800
    DEFAULT_SCREEN_HEIGHT = 600
    DEFAULT_FPS = 60
    TOWER_DISTANCE = 40  # 两塔之间的单位格数量
    POSITION_SCALE = DEFAULT_SCREEN_WIDTH / TOWER_DISTANCE  # 坐标缩放因子，使单位移动速度与屏幕显示对应
    TOWER_SIZE = 10     # 防御塔大小
    UNIT_RADIUS = 5     # 单位半径
    FONT_SIZE = 20      # 字体大小
    LOG_LINES = 5       # 显示的战斗日志行数
    MARGIN = 10         # 边距
    PATH_WIDTH = 2      # 路径线宽

    def __init__(self, width: int = DEFAULT_SCREEN_WIDTH, height: int = DEFAULT_SCREEN_HEIGHT):
        """初始化可视化器
        
        Args:
            width: 屏幕宽度
            height: 屏幕高度
            
        Raises:
            RuntimeError: 如果pygame初始化失败
        """
        try:
            pygame.init()
            pygame.font.init()  # 初始化字体模块
            
            # 加载黑体字体
            self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", self.FONT_SIZE)
            
            # 创建屏幕
            self.screen = pygame.display.set_mode((width, height))
            self.width = width
            self.height = height
            
            # 设置窗口标题
            pygame.display.set_caption("战斗模拟器")
            
            # 初始化统计模块
            self.statistics = BattleStatistics()
            
        except Exception as e:
            raise RuntimeError(f"初始化可视化器失败: {str(e)}")

    def _convert_to_screen_pos(self, x: float, y: float) -> Tuple[int, int]:
        """将游戏坐标转换为屏幕坐标
        
        Args:
            x: 游戏x坐标
            y: 游戏y坐标
            
        Returns:
            Tuple[int, int]: 屏幕坐标(x, y)
        """
        # 将游戏坐标转换为屏幕坐标
        # 对于防御塔，使用特殊的位置计算
        if abs(x) > 19:  # 如果x坐标接近边界，认为是防御塔
            if x > 0:  # 敌方防御塔
                screen_x = self.width - self.TOWER_SIZE
            else:  # 我方防御塔
                screen_x = self.TOWER_SIZE
            screen_y = self.height // 2
        else:
            # 普通单位的坐标转换
            screen_x = int(x * self.POSITION_SCALE + self.width // 2)
            screen_y = int(self.height // 2 - y * self.POSITION_SCALE)  # 注意y轴方向相反
        
        # 确保坐标在屏幕范围内
        screen_x = max(0, min(screen_x, self.width))
        screen_y = max(0, min(screen_y, self.height))
        
        return screen_x, screen_y

    def _draw_path(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float]):
        """绘制单位行进路线
        
        Args:
            start_pos: 起始位置 (x, y)
            end_pos: 目标位置 (x, y)
        """
        # 计算屏幕坐标
        start_x, start_y = self._convert_to_screen_pos(start_pos[0], start_pos[1])
        end_x, end_y = self._convert_to_screen_pos(end_pos[0], end_pos[1])
        
        # 绘制实线路径
        pygame.draw.line(
            self.screen,
            self.COLOR_PATH,
            (start_x, start_y),
            (end_x, end_y),
            self.PATH_WIDTH
        )
        
        # 在路径两端绘制小圆点
        pygame.draw.circle(self.screen, self.COLOR_PATH, (start_x, start_y), 2)
        pygame.draw.circle(self.screen, self.COLOR_PATH, (end_x, end_y), 2)

    def render(self, battle_state: BattleState, fps: int = DEFAULT_FPS) -> Optional[str]:
        """渲染当前战斗状态
        
        Args:
            battle_state: 战斗状态
            fps: 帧率
            
        Returns:
            Optional[str]: 如果用户关闭窗口返回False，按空格返回"space"，按ESC返回"esc"
        """
        try:
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
            self.screen.fill(self.COLOR_WHITE)

            # 绘制防御塔
            if battle_state.player_tower:
                print(f"绘制我方防御塔: {battle_state.player_tower.position}")
                self._draw_tower(battle_state.player_tower, self.COLOR_PLAYER_TOWER)
            if battle_state.enemy_tower:
                print(f"绘制敌方防御塔: {battle_state.enemy_tower.position}")
                self._draw_tower(battle_state.enemy_tower, self.COLOR_ENEMY_TOWER)

            # 绘制单位行进路线
            for unit in battle_state.player_units + battle_state.enemy_units:
                if unit.state != UnitState.DEAD and unit.target_id:
                    target = next((u for u in battle_state.player_units + battle_state.enemy_units 
                                 if u.id == unit.target_id), None)
                    if target:
                        print(f"绘制路线: {unit.id} -> {target.id}")
                        self._draw_path(
                            (unit.position.x, unit.position.y),
                            (target.position.x, target.position.y)
                        )

            # 绘制单位
            print(f"绘制我方单位数量: {len(battle_state.player_units)}")
            self._draw_units(battle_state.player_units, self.COLOR_PLAYER_UNIT)
            print(f"绘制敌方单位数量: {len(battle_state.enemy_units)}")
            self._draw_units(battle_state.enemy_units, self.COLOR_ENEMY_UNIT)

            # 显示战斗信息
            self._draw_battle_info(battle_state)

            # 显示战斗日志
            self._draw_battle_log(battle_state)

            # 更新显示
            pygame.display.flip()

            # 控制帧率
            pygame.time.Clock().tick(fps)

            return None
        except Exception as e:
            print(f"渲染时发生错误: {str(e)}")
            return False

    def _draw_tower(self, tower: Unit, color: Tuple[int, int, int]):
        """绘制防御塔
        
        Args:
            tower: 防御塔单位
            color: 颜色值
        """
        if tower is None or tower.state == UnitState.DEAD:
            return
            
        # 计算屏幕坐标
        screen_x, screen_y = self._convert_to_screen_pos(tower.position.x, tower.position.y)
        
        # 绘制防御塔（正方形）
        pygame.draw.rect(
            self.screen, 
            color,
            (screen_x - self.TOWER_SIZE // 2,
             screen_y - self.TOWER_SIZE // 2,
             self.TOWER_SIZE,
             self.TOWER_SIZE),
            width=2  # 添加边框
        )
        
        # 绘制防御塔ID
        text = self.font.render(tower.id, True, self.COLOR_BLACK)
        text_rect = text.get_rect(center=(screen_x, screen_y - self.TOWER_SIZE))
        self.screen.blit(text, text_rect)

    def _update_unit_position(self, unit: Unit, target: Unit, delta_time: float) -> None:
        """更新单位位置，考虑移动速度与显示的关系
        
        Args:
            unit: 要移动的单位
            target: 目标单位
            delta_time: 时间增量（秒）
        """
        # 计算方向向量
        direction_x = target.position.x - unit.position.x
        direction_y = target.position.y - unit.position.y
        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        
        if distance > 0:
            # 计算单位时间内的移动距离（考虑POSITION_SCALE）
            move_distance = unit.move_speed * delta_time * self.POSITION_SCALE
            
            # 计算新的位置
            unit.position.x += (direction_x / distance) * move_distance
            unit.position.y += (direction_y / distance) * move_distance

    def _draw_units(self, units: List[Unit], color: Tuple[int, int, int]):
        """绘制单位
        
        Args:
            units: 单位列表
            color: 颜色值
        """
        for unit in units:
            if unit.state != UnitState.DEAD:
                # 计算屏幕坐标
                screen_x, screen_y = self._convert_to_screen_pos(unit.position.x, unit.position.y)
                
                # 绘制单位
                pygame.draw.circle(
                    self.screen,
                    color,
                    (screen_x, screen_y),
                    self.UNIT_RADIUS
                )
                
                # 绘制单位ID
                text = self.font.render(unit.id, True, self.COLOR_BLACK)
                text_rect = text.get_rect(center=(screen_x, screen_y - self.UNIT_RADIUS * 2))
                self.screen.blit(text, text_rect)

    def _draw_battle_info(self, battle_state: BattleState):
        """绘制战斗信息
        
        Args:
            battle_state: 战斗状态
        """
        try:
            # 计算战斗统计信息
            player_alive = len([u for u in battle_state.player_units if u.state != UnitState.DEAD])
            enemy_alive = len([u for u in battle_state.enemy_units if u.state != UnitState.DEAD])
            
            # 计算总战力
            player_power = sum(u.attack * u.hp for u in battle_state.player_units if u.state != UnitState.DEAD)
            enemy_power = sum(u.attack * u.hp for u in battle_state.enemy_units if u.state != UnitState.DEAD)
            
            # 格式化信息
            info_texts = [
                f"我方存活单位: {player_alive}",
                f"敌方存活单位: {enemy_alive}",
                f"我方总战力: {player_power:.1f}",
                f"敌方总战力: {enemy_power:.1f}",
                f"当前波次: {battle_state.current_wave + 1}/{len(battle_state.wave_configs)}"
            ]
            
            # 绘制信息
            for i, text in enumerate(info_texts):
                text_surface = self.font.render(text, True, self.COLOR_BLACK)
                self.screen.blit(text_surface, (self.MARGIN, self.MARGIN + i * 25))
                
        except Exception as e:
            print(f"绘制战斗信息时发生错误: {str(e)}")

    def _draw_battle_log(self, battle_state: BattleState):
        """绘制战斗日志
        
        Args:
            battle_state: 战斗状态
        """
        try:
            # 获取最近的日志
            recent_logs = battle_state.battle_log[-self.LOG_LINES:]
            
            # 绘制日志
            for i, log in enumerate(recent_logs):
                text = self.font.render(log, True, self.COLOR_BLACK)
                self.screen.blit(text, (self.MARGIN, self.height - (self.LOG_LINES - i) * 25))
                
        except Exception as e:
            print(f"绘制战斗日志时发生错误: {str(e)}")

    def show_battle_result(self, battle_result) -> bool:
        """显示战斗结果
        
        Args:
            battle_result: 战斗结果
            
        Returns:
            bool: 如果用户关闭窗口返回False，按ESC返回True
        """
        try:
            # 清空屏幕
            self.screen.fill(self.COLOR_WHITE)
            
            # 格式化结果文本
            header_texts, log_texts = BattleInfoCalculator.format_battle_result(battle_result)
            
            # 绘制标题
            for i, text in enumerate(header_texts):
                text_surface = self.font.render(text, True, self.COLOR_BLACK)
                self.screen.blit(text_surface, (self.MARGIN, self.MARGIN + i * 30))
            
            # 绘制日志
            for i, text in enumerate(log_texts):
                text_surface = self.font.render(text, True, self.COLOR_BLACK)
                self.screen.blit(text_surface, (self.MARGIN, self.MARGIN + len(header_texts) * 30 + i * 25))
            
            # 更新显示
            pygame.display.flip()
            
            # 等待用户输入
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return True
            
        except Exception as e:
            print(f"显示战斗结果时发生错误: {str(e)}")
            return False

    def cleanup(self):
        """清理资源"""
        try:
            pygame.quit()
        except Exception as e:
            print(f"清理资源时发生错误: {str(e)}") 