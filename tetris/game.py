#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2020-05-14 21:23:34
@LastEditors    : yanyongyu
@LastEditTime   : 2020-05-20 14:56:15
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import os
import sys
import logging
from datetime import datetime

import pygame
import pygame.locals as gloc

from .typing import Scene
from .matrix import Matrix
from .store import Database


class Game(object):
    """Main Game Object

    Attributes:
        screen (pygame.Surface): Screen object
        screen_size (Tuple[int, int]): Screen size
        width (int): Screen width
        height (int): Screen height
        
        font (pygame.font.Font): Font object
        clock (pygame.time.Clock): Clock object
        
        home (bool): Scene flag - home
        refresh (bool): Scene flag - refresh
        game (bool): Scene flag - game
        end (bool): Scene flag - end
        
        rects (Dict[str, pygame.Rect]): Rect objects
        words (Dict[str, pygame.Surface]): Static words
        images (Dict[str, pygame.Surface]): Static images
        sounds (Dict[str, pygame.mixer.Sound]): Static sounds
        
        metrix (Matrix): Matrix Sprite
        
        delay (int): Delay
        score (int): Game score
        best_score (int): Best score
        last_score (int): Last score
        sound (bool): Sound on or off
        start_line (int): Start line number
        level (int): Level number
        pause (bool): Pause game
        left_button (bool): Whether left button is pressed or not
        right_button (bool): Whether right button is pressed or not
        up_button (bool): Whether up button is pressed or not
        down_button (bool): Whether down button is pressed or not
        time (bool): Show time colon or not
        logo (List[int]): List of logo animation
        logo_flip (bool): Whether to flip logo or not
        logo_index (int): Index of logo animation
        best_or_last (bool): Whether to show best or last
        best_or_last_index (int): Timer of best or last
    """

    def __init__(self):
        """Initialize the game. Including pictures, musics and variables
        """
        pygame.init()
        self.screen_size = self.width, self.height = 611, 916
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Tetris")

        # Init mixer and load music
        pygame.mixer.init()
        pygame.mixer.set_num_channels(4)
        pygame.mixer.music.load(
            os.path.join(os.path.dirname(__file__), "assets/music/bgm.ogg"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.sounds = {
            "start":
                pygame.mixer.Sound(
                    os.path.join(os.path.dirname(__file__),
                                 "assets/music/start.ogg")),
            "biu1":
                pygame.mixer.Sound(
                    os.path.join(os.path.dirname(__file__),
                                 "assets/music/biu1.ogg")),
            "biu2":
                pygame.mixer.Sound(
                    os.path.join(os.path.dirname(__file__),
                                 "assets/music/biu2.ogg")),
            "drop":
                pygame.mixer.Sound(
                    os.path.join(os.path.dirname(__file__),
                                 "assets/music/drop.ogg")),
            "clear":
                pygame.mixer.Sound(
                    os.path.join(os.path.dirname(__file__),
                                 "assets/music/clear.ogg")),
            "end":
                pygame.mixer.Sound(
                    os.path.join(os.path.dirname(__file__),
                                 "assets/music/end.ogg"))
        }
        for each in self.sounds.values():
            each.set_volume(0.5)

        # Init clock
        self.clock = pygame.time.Clock()

        # Init font
        self.font = pygame.font.Font(
            os.path.join(os.path.dirname(__file__),
                         "assets/font/HYXiaoBoHuaYueYuanW.ttf"), 16)
        self.words = {
            "tetris": self.font.render("T E T R I S", True, (0, 0, 0)),
            "pause": self.font.render("Pause(P)", True, (0, 0, 0)),
            "sound": self.font.render("Sound(S)", True, (0, 0, 0)),
            "reset": self.font.render("Reset(R)", True, (0, 0, 0)),
            "space": self.font.render("Drop(SPACE)", True, (0, 0, 0)),
            "left": self.font.render("Left", True, (0, 0, 0)),
            "up": self.font.render("Rotation", True, (0, 0, 0)),
            "right": self.font.render("Right", True, (0, 0, 0)),
            "down": self.font.render("Down", True, (0, 0, 0)),
            "left_arrow": self.font.render("←", True, (0, 0, 0)),
            "up_arrow": self.font.render("↑", True, (0, 0, 0)),
            "right_arrow": self.font.render("→", True, (0, 0, 0)),
            "down_arrow": self.font.render("↓", True, (0, 0, 0)),
            "start": self.font.render("Press SPACE to start", True, (0, 0, 0)),
            "best": self.font.render("Best", True, (0, 0, 0)),
            "last": self.font.render("Last Round", True, (0, 0, 0)),
            "start_line": self.font.render("Start Line", True, (0, 0, 0)),
            "level": self.font.render("Level", True, (0, 0, 0)),
            "next": self.font.render("Next", True, (0, 0, 0))
        }

        # Load images
        self.load_images()
        self.rects = {
            "pause": pygame.Rect(46, 610, 50, 50),
            "sound": pygame.Rect(136, 610, 50, 50),
            "reset": pygame.Rect(226, 610, 50, 50),
            "space": pygame.Rect(82, 710, 153, 153),
            "left": pygame.Rect(314, 700, 96, 96),
            "up": pygame.Rect(404, 610, 96, 96),
            "right": pygame.Rect(494, 700, 96, 96),
            "down": pygame.Rect(404, 790, 96, 96)
        }

        # Init Scene flags
        self.home = True
        self.refresh = False
        self.game = False
        self.end = False

        # Init Matrix
        self.matrix = Matrix()

        self.init_vars()

    def load_images(self):
        """Load static images"""
        # 背景
        background = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/background.png")).convert_alpha()

        # 按钮
        red = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/red.png")).convert_alpha()
        red_pushed = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/red_pushed.png")).convert_alpha()
        green = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/green.png")).convert_alpha()
        green_pushed = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/green_pushed.png")).convert_alpha()
        blue_sm = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/blue_sm.png")).convert_alpha()
        blue_sm_pushed = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/blue_sm_pushed.png")).convert_alpha()
        blue_lg = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/blue_lg.png")).convert_alpha()
        blue_lg_pushed = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/blue_lg_pushed.png")).convert_alpha()

        # logo
        logo = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/logo.png")).convert_alpha()
        logos = [
            logo.subsurface((0, 0, 80, 86)),
            logo.subsurface((100, 0, 80, 86)),
            logo.subsurface((200, 0, 80, 86)),
            logo.subsurface((300, 0, 80, 86))
        ]

        # icons
        icons = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "assets/image/icon.png")).convert()
        sound = icons.subsurface((175, 75, 25, 21))
        unsound = icons.subsurface((150, 75, 25, 21))
        pause = icons.subsurface((75, 75, 20, 18))
        unpause = icons.subsurface((100, 75, 20, 18))
        numbers = [
            icons.subsurface((75, 25, 14, 24)),
            icons.subsurface((89, 25, 14, 24)),
            icons.subsurface((103, 25, 14, 24)),
            icons.subsurface((117, 25, 14, 24)),
            icons.subsurface((131, 25, 14, 24)),
            icons.subsurface((145, 25, 14, 24)),
            icons.subsurface((159, 25, 14, 24)),
            icons.subsurface((173, 25, 14, 24)),
            icons.subsurface((187, 25, 14, 24)),
            icons.subsurface((201, 25, 14, 24))
        ]
        number_none = icons.subsurface((215, 25, 14, 24))
        colon = icons.subsurface((229, 25, 14, 24))
        colon_none = icons.subsurface((243, 25, 14, 24))

        self.images = {
            "background": background,
            "red": red,
            "red_pushed": red_pushed,
            "green": green,
            "green_pushed": green_pushed,
            "blue_sm": blue_sm,
            "blue_sm_pushed": blue_sm_pushed,
            "blue_lg": blue_lg,
            "blue_lg_pushed": blue_lg_pushed,
            "logos": logos,
            "sound": sound,
            "unsound": unsound,
            "pause": pause,
            "unpause": unpause,
            "numbers": numbers,
            "number_none": number_none,
            "colon": colon,
            "colon_none": colon_none
        }

    def init_vars(self):
        """Initialize the variables."""
        self.delay = 0
        self.score = 0
        data = Database.restore_data()
        self.best_score, self.last_score = data[0], data[1]
        self.sound = bool(data[2])
        self.start_line, self.level = data[3], data[4]
        self.pause = False

        # 按钮
        self.pause_button = False
        self.sound_button = False
        self.reset_button = False
        self.space_button = False
        self.left_button = False
        self.right_button = False
        self.up_button = False
        self.down_button = False

        # 时钟
        self.time = True

        # Logo
        self.logo = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3,
            2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3
        ]
        self.logo_flip = False
        self.logo_index = 0

        # 分数
        self.best_or_last = True
        self.best_or_last_index = 0

    def switch_scene(self, scene: Scene):
        """Switch current scene

        Args:
            scene (Scene): Target scene
        """
        if scene == Scene.HOME:
            self.home = True
            self.refresh = False
            self.game = False
            self.end = False
        elif scene == Scene.REFRESH:
            self.home = False
            self.refresh = True
            self.game = False
            self.end = False
        elif scene == Scene.GAME:
            self.home = False
            self.refresh = False
            self.game = True
            self.end = False
        elif scene == Scene.END:
            self.home = False
            self.refresh = False
            self.game = False
            self.end = True
        else:
            logging.warning(f"Unknow Scene {scene!s}")

    def switch_sound(self):
        self.sound = not self.sound
        pygame.mixer.music.set_volume(0.5 if self.sound else 0)

    def start(self):
        """Main game loop."""
        while True:
            # 事件响应
            for event in pygame.event.get():
                # 退出事件
                if event.type == gloc.QUIT:
                    pygame.quit()
                    sys.exit()

                # 键盘事件
                elif event.type == gloc.KEYDOWN:
                    if event.key == gloc.K_p:
                        self.pause_button = True
                    elif event.key == gloc.K_s:
                        self.sound_button = True
                    elif event.key == gloc.K_r:
                        self.reset_button = True
                    elif event.key == gloc.K_SPACE:
                        self.space_button = True
                    elif event.key == gloc.K_LEFT:
                        self.left_button = True
                    elif event.key == gloc.K_UP:
                        self.up_button = True
                    elif event.key == gloc.K_RIGHT:
                        self.right_button = True
                    elif event.key == gloc.K_DOWN:
                        self.down_button = True

                elif event.type == gloc.KEYUP:
                    if event.key == gloc.K_p:
                        self.pause_button = False
                        if self.game:
                            self.pause = not self.pause
                    elif event.key == gloc.K_s:
                        self.sound_button = False
                        self.switch_sound()
                    elif event.key == gloc.K_r:
                        self.reset_button = False
                        self.switch_scene(Scene.REFRESH)
                    elif event.key == gloc.K_SPACE:
                        self.space_button = False
                        if self.home:
                            self.sounds["start"].play()
                            self.switch_scene(Scene.GAME)
                    elif event.key == gloc.K_LEFT:
                        self.left_button = False
                    elif event.key == gloc.K_UP:
                        self.up_button = False
                    elif event.key == gloc.K_RIGHT:
                        self.right_button = False
                    elif event.key == gloc.K_DOWN:
                        self.down_button = False

                # 鼠标点击
                elif event.type == gloc.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if event.button == 1:
                        if self.rects["pause"].collidepoint(pos):
                            self.pause_button = True
                        elif self.rects["sound"].collidepoint(pos):
                            self.sound_button = True
                        elif self.rects["reset"].collidepoint(pos):
                            self.reset_button = True
                        elif self.rects["space"].collidepoint(pos):
                            self.space_button = True
                        elif self.rects["left"].collidepoint(pos):
                            self.left_button = True
                        elif self.rects["up"].collidepoint(pos):
                            self.up_button = True
                        elif self.rects["right"].collidepoint(pos):
                            self.right_button = True
                        elif self.rects["down"].collidepoint(pos):
                            self.down_button = True

                # 鼠标点击释放
                elif event.type == gloc.MOUSEBUTTONUP:
                    pos = event.pos
                    if event.button == 1:
                        if self.pause_button and self.rects[
                                "pause"].collidepoint(pos):
                            if self.game:
                                self.pause = not self.pause
                        elif self.sound_button and self.rects[
                                "sound"].collidepoint(pos):
                            self.switch_sound()
                        elif self.reset_button and self.rects[
                                "reset"].collidepoint(pos):
                            self.switch_scene(Scene.REFRESH)
                        elif self.space_button and self.rects[
                                "space"].collidepoint(pos):
                            if self.home:
                                self.sounds["start"].play()
                                self.switch_scene(Scene.GAME)
                        elif self.left_button and self.rects[
                                "left"].collidepoint(pos):
                            ...
                        elif self.up_button and self.rects["up"].collidepoint(
                                pos):
                            ...
                        elif self.right_button and self.rects[
                                "right"].collidepoint(pos):
                            ...
                        elif self.down_button and self.rects[
                                "down"].collidepoint(pos):
                            ...
                        self.pause_button = False
                        self.sound_button = False
                        self.reset_button = False
                        self.space_button = False
                        self.left_button = False
                        self.right_button = False
                        self.up_button = False
                        self.down_button = False

            # 基础背景绘制
            self.screen.blit(self.images["background"], (0, 0))
            self.screen.fill((158, 173, 134), (126, 90, 360, 445))
            pygame.draw.rect(self.screen, (0, 0, 0), (140, 104, 210, 410), 2)
            self.screen.blit(self.matrix.image, (146, 110))

            # 绘制按钮
            self.screen.blit(
                self.images["green_pushed"] if self.pause_button else
                self.images["green"], self.rects["pause"])
            self.screen.blit(
                self.images["green_pushed"] if self.sound_button else
                self.images["green"], self.rects["sound"])
            self.screen.blit(
                self.images["red_pushed"] if self.reset_button else
                self.images["red"], self.rects["reset"])
            self.screen.blit(
                self.images["blue_lg_pushed"] if self.space_button else
                self.images["blue_lg"], self.rects["space"])
            self.screen.blit(
                self.images["blue_sm_pushed"] if self.left_button else
                self.images["blue_sm"], self.rects["left"])
            self.screen.blit(
                self.images["blue_sm_pushed"]
                if self.up_button else self.images["blue_sm"], self.rects["up"])
            self.screen.blit(
                self.images["blue_sm_pushed"] if self.right_button else
                self.images["blue_sm"], self.rects["right"])
            self.screen.blit(
                self.images["blue_sm_pushed"] if self.down_button else
                self.images["blue_sm"], self.rects["down"])
            self.screen.blit(self.words["pause"], (40, 665))
            self.screen.blit(self.words["sound"], (130, 665))
            self.screen.blit(self.words["reset"], (220, 665))
            self.screen.blit(self.words["space"], (105, 868))
            self.screen.blit(self.words["left"], (346, 800))
            self.screen.blit(self.words["up"], (504, 630))
            self.screen.blit(self.words["right"], (520, 800))
            self.screen.blit(self.words["down"], (429, 886))
            self.screen.blit(self.words["left_arrow"], (420, 738))
            self.screen.blit(self.words["up_arrow"], (445, 713))
            self.screen.blit(self.words["right_arrow"], (470, 738))
            self.screen.blit(self.words["down_arrow"], (445, 763))

            # 绘制图标
            if self.sound:
                self.screen.blit(self.images["sound"], (360, 499))
            else:
                self.screen.blit(self.images["unsound"], (360, 499))
            if self.pause:
                self.screen.blit(self.images["pause"], (389, 500))
            else:
                self.screen.blit(self.images["unpause"], (389, 500))

            now = datetime.now()
            self.screen.blit(
                self.images["colon"]
                if self.time else self.images["colon_none"], (437, 497))
            self.screen.blit(
                self.images["numbers"][now.hour // 10] if now.hour //
                10 else self.images["number_none"], (412, 497))
            self.screen.blit(self.images["numbers"][now.hour % 10], (426, 497))
            self.screen.blit(self.images["numbers"][now.minute // 10],
                             (451, 497))
            self.screen.blit(self.images["numbers"][now.minute % 10],
                             (465, 497))

            if self.delay == 0:
                self.time = not self.time

            # 首页
            if self.home:
                # 绘制logo
                if self.logo_flip:
                    self.screen.blit(
                        pygame.transform.flip(
                            self.images["logos"][self.logo[self.logo_index]],
                            True, False), (200, 230))
                else:
                    self.screen.blit(
                        self.images["logos"][self.logo[self.logo_index]],
                        (200, 230))
                if self.delay % 5 == 0:
                    self.logo_index = (self.logo_index + 1) % len(self.logo)
                if self.logo_index < 6 and self.delay == 0:
                    self.logo_flip = not self.logo_flip

                self.screen.blit(self.words["tetris"], (205, 330))
                if self.time:
                    self.screen.blit(self.words["start"], (155, 370))

                # 绘制分数
                if self.best_or_last:
                    self.screen.blit(self.words["best"], (370, 110))
                    scores = list(f"{self.best_score: >6}")
                    scores.reverse()
                    for index, score in enumerate(scores):
                        self.screen.blit(
                            self.images["numbers"][int(score)]
                            if score != " " else self.images["number_none"],
                            (460 - index * 14, 140))
                else:
                    self.screen.blit(self.words["last"], (370, 110))
                    scores = list(f"{self.last_score: >6}")
                    scores.reverse()
                    for index, score in enumerate(scores):
                        self.screen.blit(
                            self.images["numbers"][int(score)]
                            if score != " " else self.images["number_none"],
                            (460 - index * 14, 140))
                if self.delay == 0:
                    self.best_or_last_index = (self.best_or_last_index + 1) % 5
                if self.best_or_last_index == 0 and self.delay == 0:
                    self.best_or_last = not self.best_or_last

                # 绘制初始行数
                self.screen.blit(self.words["start_line"], (370, 185))
                start_line = list(f"{self.start_line: >6}")
                start_line.reverse()
                for index, line in enumerate(start_line):
                    self.screen.blit(
                        self.images["numbers"][int(line)] if line != " " else
                        self.images["number_none"], (460 - index * 14, 215))
                if self.delay % 3 == 0 and self.up_button:
                    self.sounds["biu2"].play()
                    self.start_line = (self.start_line + 1) % 11
                elif self.delay % 3 == 0 and self.down_button:
                    self.sounds["biu2"].play()
                    self.start_line = (self.start_line - 1) % 11

                # 绘制level
                self.screen.blit(self.words["level"], (370, 260))
                self.screen.blit(self.images["numbers"][self.level], (460, 290))
                for index in range(5):
                    self.screen.blit(self.images["number_none"],
                                     (446 - index * 14, 290))
                if self.delay % 3 == 0 and self.left_button:
                    self.sounds["biu2"].play()
                    self.level = (self.level - 2) % 6 + 1
                elif self.delay % 3 == 0 and self.right_button:
                    self.sounds["biu2"].play()
                    self.level = self.level % 6 + 1
            # 游戏界面
            elif self.game:
                ...
            # 游戏结束画面
            elif self.end:
                ...
            # Refresh画面
            elif self.refresh:
                ...

            # 记录当前帧数
            self.delay = (self.delay + 1) % 30

            # 设置帧率为30
            self.clock.tick(30)

            # 刷新画面
            pygame.display.update()
