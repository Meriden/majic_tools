import random
import os
import json

import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw

from majic_tools.sys.utils.text import intToAlpha

from majic_tools.maya.apps.games.snake import game, images, font
from .utils import ALIGN_LEFT, ALIGN_V_CENTER, ALIGN_H_CENTER

# ------------------------------------------------------------------------------------------------ #

MAIN_COLOUR = qg.QColor(18, 30, 0)
SHADOW_COLOUR = qg.QColor(18, 30, 0, 100)

MAIN_BRUSHES = [qg.QPen(MAIN_COLOUR), qg.QBrush(MAIN_COLOUR)]        
SHADOW_BRUSHES = [qg.QPen(SHADOW_COLOUR), qg.QBrush(SHADOW_COLOUR)]

# snake directions
#
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# snake speeds
#
SLOWEST = 'Slowest'
SLOW = 'Slow'
NORMAL = 'Normal'
FAST = 'Fast'
FASTEST = 'Fastest'

SPEED = {SLOWEST: 120,
         SLOW: 95,
         NORMAL: 70,
         FAST: 50,
         FASTEST: 40}

POINTS = {SLOWEST: 1,
          SLOW: 3,
          NORMAL: 5,
          FAST: 7,
          FASTEST: 9}

# ------------------------------------------------------------------------------------------------ #

class SnakeData(game.GameData):
    title = 'SNAKE II'

    background_color = (128, 175, 1)

    pixel_width = 5
    screen_width = 104
    screen_height = 84

    width = screen_width * (pixel_width + 2)
    height = screen_height * (pixel_width + 2)

    game_mode = 0

    snake_length = 10
    snake_speed = NORMAL

    bonus_trigger = 10
    bonus_countdown_speed = 100
    bonus_countdown = 20

    # high scores
    #
    scores = [('---', 0) for i in range(10)]
    new_high_score = None

    score_filepath = 'D:\snake_high_scores.json'


    @staticmethod
    def isHighScore(score):
        """Checks if given score is higher than the lowest recorded score."""
        return score > min([score for _, score in SnakeData.scores])


    @staticmethod
    def saveScores():
        with open(SnakeData.score_filepath, 'w') as f:
            json.dump(SnakeData.scores, f, sort_keys=True, indent=2, separators=(',', ': '))


    @staticmethod
    def loadScores():
        if not os.path.exists(SnakeData.score_filepath):
            print "Snake II: Failed to load High Scores."
            return

        try:
            with open(SnakeData.score_filepath, 'r') as f:
                json_data = json.load(f)
        except Exception as e:
            print e
            print "Snake II: Failed to load High Scores."
            return

        SnakeData.scores = json_data

# ------------------------------------------------------------------------------------------------ #

class Snake(game.Game):
    data = SnakeData
     
    def __init__(self):
        super(Snake, self).__init__()

        # add levels
        #
        start_screen = self.addLevel(Splash)
        main_menu = self.addLevel(Menu, 'Menu')
        level_menu = self.addLevel(LevelMenu, 'Level')
        high_scores = self.addLevel(HighScores)
        arena = self.addLevel(Arena)

        # connect levels together
        #
        self.addConnection(start_screen, main_menu)

        # setup splash screen
        #
        start_screen.initialize(images.title)

        # setup menus
        #
        menu_to_arena = self.addConnection(main_menu, arena)
        menu_to_level = self.addConnection(main_menu, level_menu)
        menu_to_scores = self.addConnection(main_menu, high_scores)

        menu_items = [('New Game', menu_to_arena),
                      ('Level', menu_to_level),
                      ('High Scores', menu_to_scores),
                      ('Mode', menu_to_level)]
        main_menu.initialize(menu_items)

        # setup level menu
        #
        to_main_menu = self.addConnection(level_menu, main_menu)

        menu_items = [(SLOWEST, to_main_menu),
                      (SLOW, to_main_menu),
                      (NORMAL, to_main_menu),
                      (FAST, to_main_menu),
                      (FASTEST, to_main_menu)]
        level_menu.initialize(menu_items, self.data.snake_speed)

        # setup arena
        #
        self.addConnection(arena, main_menu)
        self.addConnection(arena, high_scores)

        # setup high score board
        #
        self.addConnection(high_scores, main_menu)
        
# ------------------------------------------------------------------------------------------------ #

def paintPixel(painter, x, y):
    """
    Paints a pixel of defined width, with a shadow.

    :param painter: QPainter object to draw with
    :param int x: real x position to draw the pixel
    :param int y: real y position to draw the pixel
    """

    x = x * (SnakeData.pixel_width + 2)
    y = y * (SnakeData.pixel_width + 2)

    for color in (MAIN_BRUSHES, SHADOW_BRUSHES):
        painter.setPen(color[0])
        painter.setBrush(color[1])

        painter.drawRect(x, y, SnakeData.pixel_width, SnakeData.pixel_width)

        x += 1
        y += 1

# ------------------------------------------------------------------------------------------------ #

class Splash(game.Level):
    def __init__(self, data):
        super(Splash, self).__init__(data)
        self.image = None
        self.offset = [0, 0]
        self.alignment = ALIGN_H_CENTER | ALIGN_V_CENTER


    def initialize(self, image, alignment=0):
        self.image = image
        self.alignment = alignment

    
    def paintEvent(self, _):
        if self.image is None:
            return

        painter = qw.QStylePainter(self)

        paint_area = [0, 0, self.data.screen_width, self.data.screen_height]

        self.image.paint(painter, paint_area, False, paintPixel, self.alignment)


    def keyPressEvent(self, _):
        self.switch(0)
                    
# ------------------------------------------------------------------------------------------------ #

class ScrollArea(game.Level):
    def __init__(self, data, title='Untitled'):
        super(ScrollArea, self).__init__(data)

        self.title = title
        self.title_image = None
        self.scrollbar = False

        self.items = []
        self.item_positions = {}

        self.setTitle(title)

        self.margins = [2, 0, 2, 2]

        self.scroll_area = [0, 0, 0, 0]
        self.scroll_area[0] = self.margins[0]
        self.scroll_area[1] = self.title_image.height + 2 + self.margins[1]
        self.scroll_area[2] = self.data.screen_width - self.margins[0] - self.margins[2]
        self.scroll_area[3] = self.data.screen_height - self.scroll_area[1] - self.margins[3]

        self.selected_item_index = 0
        self.scroll_range = [0, self.scroll_area[3], []]


    def setTitle(self, title):
        self.title = title
        self.title_image = font.small_font.getImage('- {} -'.format(title))
        self.repaint()


    def initialize(self, items):
        self.items = items
        self.item_positions = {}

        self.scroll_range = [0, self.scroll_area[3], []]
        self.selected_item_index = 0

        scroll_value = 0
        for i, item in enumerate(self.items):
            scroll_value += item.height
            self.item_positions[i] = scroll_value

        if max(self.item_positions.values()) > self.scroll_area[3]:
            self.scrollbar = True
            self.scroll_area[2] -= 4

        # update scroll area
        #
        self._scroll()


    def keyPressEvent(self, event):
        """ Handles scrolling and selection of menu items.

        :param QEvent event: key press event
        :return:
        """
        key = event.key()
        if key in (qc.Qt.Key_Up, qc.Qt.Key_Down):
            if key == qc.Qt.Key_Up:
                self.selected_item_index -= 1
            elif key == qc.Qt.Key_Down:
                self.selected_item_index += 1

            num_items = len(self.items)
            if self.selected_item_index < 0:
                self.selected_item_index = num_items - 1
            elif self.selected_item_index >= num_items:
                self.selected_item_index = 0

            self._scroll()
            self.repaint()

        elif key in (qc.Qt.Key_Return, qc.Qt.Key_Enter):
            self.select(self.selected_item_index)


    def select(self, selected_item_index):
        """Base function for selecting an item Override in inherited classes."""
        self.selected_item_index = selected_item_index
        self._scroll()


    def _scroll(self):
        """ Handles menu scrolling area, which items are visible and partial items."""
        selected_lower = self.item_positions.get(self.selected_item_index - 1, 0)
        selected_upper = self.item_positions[self.selected_item_index] - 1

        if selected_lower <= self.scroll_range[0]:
            self.scroll_range[0] = selected_lower
            self.scroll_range[1] = selected_lower + self.scroll_area[3]
        elif selected_upper > self.scroll_range[1]:
            self.scroll_range[1] = selected_upper
            self.scroll_range[0] = selected_upper - self.scroll_area[3] + 1

        # figure out which items are currently visible
        #
        visible_items = self.scroll_range[2] = []

        previous_scroll_value = 0
        for i, item in enumerate(self.items):
            scroll_value = self.item_positions[i] - 1

            # check if lower or upper edge is in menu range
            #
            lower = upper = False
            if self.scroll_range[0] <= previous_scroll_value <= self.scroll_range[1]:
                lower = True
            if self.scroll_range[0] <= scroll_value <= self.scroll_range[1]:
                upper = True

            # based on visible edges add to visible menu items
            #
            if lower and upper:
                visible_items.append((i, None, None))
            elif lower:
                value = self.scroll_range[1] - previous_scroll_value
                if value == 0:
                    continue
                visible_items.append((i, 0, value))
            elif upper:
                value = scroll_value - self.scroll_range[0]
                visible_items.append((i, item.height - value, item.height))

            previous_scroll_value = scroll_value + 1


    def paintEvent(self, _):
        painter = qw.QStylePainter(self)

        title_area = (0, 0, self.data.screen_width, 10)
        self.title_image.paint(painter, title_area, False, paintPixel)

        x, y = self.scroll_area[0], self.scroll_area[1]

        # draw scroll bar
        #
        if self.scrollbar:
            scroll_height = self.scroll_area[3]

            scroll_incr = float(scroll_height) / len(self.items)
            start_scroll = round(scroll_incr * self.selected_item_index)
            end_scroll = round(scroll_incr * (self.selected_item_index + 1))
            end_scroll = min([end_scroll, scroll_height - 1])

            scroll_bar_offset = self.data.screen_width - self.margins[2]
            for i in range(scroll_height):
                if i in (start_scroll, end_scroll):
                    paintPixel(painter, scroll_bar_offset - 2, i + y)

                if start_scroll < i < end_scroll:
                    paintPixel(painter, scroll_bar_offset - 1, i + y)
                else:
                    paintPixel(painter, scroll_bar_offset - 3, i + y)

        # draw menu items
        #
        for item_index, lower, upper in self.scroll_range[2]:
            invert = False
            if item_index == self.selected_item_index:
                invert = True

            item = self.items[item_index]

            # get item height. some items might be partially visible
            #
            item_height = (upper - lower) if lower is not None else item.height

            # create paint area, start x, y and width, height
            #
            paint_area = (x, y, self.scroll_area[2], item_height)

            # paint menu item in allowed paint area
            #
            item.paint(painter, paint_area, invert)

            y += item_height


class MenuItem(object):
    def __init__(self, text):
        self.text = text
        self.height = 18
        self.image = font.main_font.getImage(text)
        self.margins = [3, 3, 3, 3]


    def paint(self, painter, paint_area, invert=False):
        sub_paint_area = [paint_area[0] + self.margins[0],
                          paint_area[1] + self.margins[1],
                          paint_area[2] - self.margins[0] - self.margins[2],
                          paint_area[3] - self.margins[3] - self.margins[1]]

        if invert:
            x, y = paint_area[0:2]

            for i in range(paint_area[2]):
                for j in range(self.margins[1]):
                    paintPixel(painter, x + i, y + j)

                base_y = y + paint_area[3] - self.margins[3]
                for j in range(self.margins[3]):
                    paintPixel(painter, x + i, base_y + j)

            for j in range(self.margins[1], sub_paint_area[3] + self.margins[1]):
                for i in range(self.margins[0]):
                    paintPixel(painter, x + i, y + j)

                for i in range(1, self.margins[0] + 1):
                    paintPixel(painter, x + paint_area[2] - i, y + j)

        self.image.paint(painter, sub_paint_area, invert, paintPixel, ALIGN_LEFT)


class Menu(ScrollArea):
    def __init__(self, data, title='Untitled'):
        super(Menu, self).__init__(data, title)

        self.signals = []


    def initialize(self, menu_items):
        """ Setup the menu with given items and signal connections. Should be pairs of
         text:signal_id.

        :param list menu_items: list of menu items to display
        :return:
        """
        items = []
        self.signals = []

        for menu_item_name, signal_id in menu_items:
            items.append(MenuItem(menu_item_name))
            self.signals.append(signal_id)

        super(Menu, self).initialize(items)


    def select(self, selected_item_index):
        """Trigger level switch based on connected signal."""
        self.switch(self.signals[selected_item_index])


class LevelMenu(Menu):
    def initialize(self, items, default):
        super(LevelMenu, self).initialize(items)
        for i, item in enumerate(self.items):
            if item.text == default:
                break
        self.selected_item_index = i


    def select(self, selected_item_index):
        """Set snake speed to selected, then run menu select function."""
        self.data.snake_speed = self.items[self.selected_item_index].text
        super(LevelMenu, self).select(selected_item_index)
                    
# ------------------------------------------------------------------------------------------------ #

class Arena(game.Level):
    GAME_OVER = 'GAME OVER'
    
    def __init__(self, data):
        super(Arena, self).__init__(data)

        self.score_board = ScoreBoard(self)
        self.bonus_countdown = BonusCountdown(self)
        self.grid = GameGrid(self)

        self._bonus_counter = 0
        self._game_over_counter = 0

        self.game_mode = True
        self.running = False
        self._high_score = False

        # create and connect timers
        #
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self.grid.update)

        self._bonus_timer = qc.QTimer()
        self._bonus_timer.timeout.connect(self.bonus_countdown.update)
        self._bonus_speed = self.data.bonus_countdown_speed

        self._game_over_timer = qc.QTimer()
        self._game_over_timer.timeout.connect(self.gameOver)

        # connect widgets
        #
        self.connect(self.grid, GameGrid.APPLE_EATEN_SIGNAL, self.score_board.add)
        self.connect(self.grid, GameGrid.APPLE_EATEN_SIGNAL, self.updateBonus)
        self.connect(self.grid, GameGrid.COLLISION_SIGNAL, self.endGame)
        self.connect(self.bonus_countdown, BonusCountdown.COUNTDOWN_END_SIGNAL, self.endBonus)
        self.connect(self.grid, GameGrid.BONUS_EATEN_SIGNAL, self.collectBonus)

        self.bonus_countdown.hide()

        # create game over text
        #
        self.game_over_image = font.main_font.getImage('Game over!')
        self.your_score_image = font.main_font.getImage('Your score:')
        self.high_score_image = font.main_font.getImage('NEW HIGH SCORE!')
        self.score_image = font.main_font.getImage('0000')

    
    def reset(self):
        self._bonus_counter = 0
        self._game_over_counter = 0
        
        self.game_mode = True
        self.running = True
        self._high_score = False

        self.score_board.reset()
        self.bonus_countdown.reset()

        self.grid.show()
        self.score_board.show()
        self.bonus_countdown.hide()

        
    def keyPressEvent(self, event):
        key = event.key()
        if key == qc.Qt.Key_Left:
            self.grid.moveLeft()
        elif key == qc.Qt.Key_Right:
            self.grid.moveRight()
        elif key == qc.Qt.Key_Up:
            self.grid.moveUp()
        elif key == qc.Qt.Key_Down:
            self.grid.moveDown()

        # pause or exit
        elif key in (qc.Qt.Key_Return, qc.Qt.Key_Enter) and not self.game_mode:
            if self.data.new_high_score:
                self.switch(1)
            else:
                self.switch(0)
        
    
    def start(self):
        self.reset()
        self.grid.start()
        self._anim_timer.start(SPEED[self.data.snake_speed])
        
        
    def end(self):
        self._anim_timer.stop()
        self._bonus_timer.stop()
        self._game_over_timer.stop()
        self.running = False


    @qc.Slot()
    def endGame(self):
        self._game_over_counter = 0

        self._anim_timer.stop()
        self._bonus_timer.stop()

        self._game_over_timer.start(150)


    @qc.Slot()
    def gameOver(self):
        self._game_over_counter += 1
        self.grid.draw_snake = not self._game_over_counter % 2
        self.grid.repaint()

        if self._game_over_counter != 10:
            return

        self._game_over_timer.stop()

        self.game_mode = False

        # check for new high score
        #
        score = self.score_board.score_counter
        if self.data.isHighScore(score):
            self.data.new_high_score = score

        # hide other arena widgets
        #
        self.grid.hide()
        self.score_board.hide()
        self.bonus_countdown.hide()

        # create score image
        #
        self.score_image = font.main_font.getImage(self.score_board.asString())

        self.repaint()


    def showEvent(self, event):
        super(Arena, self).showEvent(event)
        if self.running:
            self._anim_timer.start()


    def hideEvent(self, event):
        super(Arena, self).hideEvent(event)
        if self.running:
            self._anim_timer.stop()
        
    
    def paintEvent(self, _):
        painter = qw.QStylePainter(self)
        option  = qw.QStyleOption()
        option.initFrom(self)

        if self.game_mode:
            upper_edge = 10
            lower_edge = self.data.screen_height - 3
            for i in range(2, self.data.screen_width - 2):
                paintPixel(painter, i, upper_edge-2)
                paintPixel(painter, i, upper_edge)
                paintPixel(painter, i, lower_edge)

            left_edge = 2
            right_edge = self.data.screen_width - 3
            for i in range(11, self.data.screen_height - 3):
                paintPixel(painter, left_edge, i)
                paintPixel(painter, right_edge, i)

        else:
            paint_area = [0, 15, self.data.screen_width, 20]
            self.game_over_image.paint(painter, paint_area, False, paintPixel)
            paint_area[1] += 20
            if self.data.new_high_score:
                self.high_score_image.paint(painter, paint_area, False, paintPixel)
            else:
                self.your_score_image.paint(painter, paint_area, False, paintPixel)
            paint_area[1] += 12
            self.score_image.paint(painter, paint_area, False, paintPixel)


    @qc.Slot()
    def updateBonus(self):
        self._bonus_counter += 1
        if self._bonus_counter != self.data.bonus_trigger:
            return

        self._bonus_counter = 0
        self.grid.addBonus()
        self.bonus_countdown.reset()
        self._bonus_timer.start(self._bonus_speed)
        self.bonus_countdown.show()


    @qc.Slot()
    def collectBonus(self):
        self.score_board.add(self.bonus_countdown.countdown)
        self._bonus_timer.stop()
        self.bonus_countdown.hide()


    @qc.Slot()
    def endBonus(self):
        self._bonus_timer.stop()
        self.bonus_countdown.hide()
        self.grid.removeBonus()

    
    def __del__(self):
        self._anim_timer.stop()
        self._anim_timer.timeout.disconnect(self.update)
        self._game_over_timer.stop()
        self._game_over_timer.timeout.disconnect(self.update)
        
# ------------------------------------------------------------------------------------------------ #

class GameGrid(qw.QWidget):
    COLLISION_SIGNAL = qc.SIGNAL('collision()')
    APPLE_EATEN_SIGNAL = qc.SIGNAL('appleEaten(int)')
    BONUS_EATEN_SIGNAL = qc.SIGNAL('bonusEaten()')

    def __init__(self, parent):
        super(GameGrid, self).__init__(parent)

        self.data = parent.data
        width = self.data.screen_width - 8
        height = self.data.screen_height - 16
        snake_length = self.data.snake_length

        self.setFixedWidth(self.data.width)
        self.setFixedHeight(self.data.height)

        self.width = (width / 4)
        self.height = (height / 4)

        self.grid = [Row(self.height) for _ in range(self.width)]

        self.direction = RIGHT
        self.next_direction = RIGHT

        self.position = (self.width / 2, self.height / 2)
        self.length = snake_length

        self.draw_snake = True

        self.bonus_blocks = []


    def moveUp(self):
        if self.direction == DOWN:
            return
        self.next_direction = UP


    def moveDown(self):
        if self.direction == UP:
            return
        self.next_direction = DOWN


    def moveLeft(self):
        if self.direction == RIGHT:
            return
        self.next_direction = LEFT


    def moveRight(self):
        if self.direction == LEFT:
            return
        self.next_direction = RIGHT


    def start(self):
        self.reset()

        x, y = self.position
        block = self.grid[x][y]
        block.type = Block.HEAD
        block.direction = self.direction
        block.counter = self.length

        for index in range(1, self.length):
            block = self.grid[x - index][y]
            block.type = Block.TAIL if index == self.length - 1 else Block.BODY
            block.direction = self.direction
            block.counter = self.length - index

        self.addApple()
        
    
    def reset(self):
        self.direction = RIGHT
        self.next_direction = RIGHT

        self.position = (self.width / 2, self.height / 2)
        self.length = self.data.snake_length

        self.draw_snake = True

        self.bonus_blocks = []

        for column in self.grid:
            for row in column.rows:
                row.reset()


    def freeBlocks(self, dimensions=(1,1)):
        free_blocks = []
        if dimensions != (1,1):
            max_columns = len(self.grid) - dimensions[0] + 1
            max_rows = len(self.grid[0]) - dimensions[1] + 1

            free_block_set = set([Block.FREE])

            for column_index in range(max_columns):
                for row_index in range(max_rows):
                    blocks = set([])
                    for i in range(dimensions[0]):
                        for j in range(dimensions[1]):
                            blocks.add(self.grid[column_index+i][row_index+j].type)

                    if blocks == free_block_set:
                        free_blocks.append((column_index, row_index))

        else:
            for column_index, column in enumerate(self.grid):
                for row_index, block in enumerate(column.rows):
                    if block.type == Block.FREE:
                        free_blocks.append((column_index, row_index))

        return free_blocks


    def addApple(self):
        free_blocks = self.freeBlocks()
        random_index = random.randint(0, len(free_blocks)-1)
        x, y = free_blocks[random_index]
        block = self.grid[x][y]
        block.type = Block.APPLE
        block.food = True


    def addBonus(self):
        free_blocks = self.freeBlocks((2, 1))
        random_index = random.randint(0, len(free_blocks)-1)
        x, y = free_blocks[random_index]

        bonus = Block.BONUSES[random.randint(0, len(Block.BONUSES) - 1)]

        block = self.grid[x][y]
        block.type = bonus[0]
        block.food = True

        block = self.grid[x+1][y]
        block.type = bonus[1]
        block.food = True

        self.bonus_blocks = [(x, y), (x+1, y)]


    def removeBonus(self):
        for x, y in self.bonus_blocks:
            block = self.grid[x][y]
            block.type = Block.FREE
            block.food = False
        self.bonus_blocks = []


    def update(self):
        x, y = self.position
        current_block = self.grid[x][y]

        x, y = self.nextPositions(x, y)
        next_block = self.grid[x][y]

        x2, y2 = self.nextPositions(x, y)
        future_block = self.grid[x2][y2]

        added_length = 0
        if next_block.type == Block.APPLE:
            added_length = 1
            self.emit(GameGrid.APPLE_EATEN_SIGNAL, POINTS[self.data.snake_speed])
            self.addApple()

        elif next_block.type in Block.ALL_BONUSES:
            self.emit(GameGrid.BONUS_EATEN_SIGNAL)
            self.removeBonus()
            next_block.food = True

        elif next_block.type not in (Block.FREE, Block.TAIL):
            self.emit(GameGrid.COLLISION_SIGNAL)
            return False

        next_block.counter = self.length + 1
        next_block.direction = self.direction
        next_block.type = Block.HEAD

        if future_block.type == Block.APPLE:
            next_block.open = True

        self.length += added_length

        if next_block.direction != current_block.direction:
            current_block.type = Block.CORNER
            d1, d2 = current_block.direction, next_block.direction
            if (d1, d2) in ((RIGHT, UP), (DOWN, LEFT)):
                current_block.corner_direction = RIGHT
            elif (d1, d2) in ((LEFT, UP), (DOWN, RIGHT)):
                current_block.corner_direction = LEFT
            elif (d1, d2) in ((LEFT, DOWN), (UP, RIGHT)):
                current_block.corner_direction = UP
            elif (d1, d2) in ((RIGHT, DOWN), (UP, LEFT)):
                current_block.corner_direction = DOWN
        else:
            current_block.type = Block.BODY

        self.position = [x, y]

        body_parts = {}
        for column in self.grid:
            for row in column.rows:
                if row.counter == 0 or row.type == Block.APPLE:
                    continue

                counter_value = row.counter = row.counter - 1 + added_length
                if counter_value == 0:
                    row.reset()
                    continue

                body_parts[counter_value] = row

        keys = sorted(body_parts.keys())
        tail = body_parts[keys[0]]
        tail.type = Block.TAIL
        tail.direction = body_parts[keys[1]].direction

        self.repaint()


    def nextPositions(self, x, y):
        self.direction = self.next_direction

        x += self.direction[0]
        y += self.direction[1]

        if x < 0:
            x += self.width
        elif x >= self.width:
            x -= self.width

        if y < 0:
            y += self.height
        elif y >= self.height:
            y -= self.height

        return x, y


    def draw(self):
        symbols = {Block.FREE: '_',
                   Block.HEAD: '&',
                   Block.BODY: '#',
                   Block.TAIL: '^',
                   Block.CORNER: '%',
                   Block.APPLE: 'O'}
        for row_index in range(len(self.grid[0])):
            line = '  '
            for column_index in range(len(self.grid)):
                block = self.grid[column_index][row_index]
                line += symbols[block.type] + ' '
            print line


    def paintEvent(self, _):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)

        for i in range(self.width):
            for j in range(self.height):
                block = self.grid[i][j]
                if block.type is Block.FREE:
                    continue

                if self.draw_snake is False and block.type in Block.BODY_PARTS:
                    continue

                block_value = block.draw()

                block_x = (i * 4) + 4
                block_y = (j * 4) + 12

                check = 1
                for gx in range(4):
                    for gy in range(4):
                        if block_value & check:
                            paintPixel(painter,
                                       block_x + gy,
                                       block_y + gx)
                        check <<= 1

    
    def __del__(self):
        print 'deleting game grid'

# ------------------------------------------------------------------------------------------------ #

class ScoreBoard(qw.QWidget):
    NUMBERS = [0x7b6f, 0x2c92, 0x73e7, 0x73cf, 0x5bc9,
               0x79cf, 0x79ef, 0x7249, 0x7bef, 0x7bcf]
    
    def __init__(self, parent):
        qw.QWidget.__init__(self, parent)

        self.data = parent.data

        self.setFixedWidth(self.data.width)
        self.setFixedHeight(self.data.height)

        self.numbers = dict([(str(i), ScoreBoard.NUMBERS[i]) for i in range(10)])
        
        self.score_counter = 0
        
        
    def reset(self):
        self.score_counter = 0


    def add(self, value):
        self.score_counter += value
        self.repaint()


    def asString(self):
        return '{:04d}'.format(self.score_counter)
        
    
    def paintEvent(self, _):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)

        score_str = self.asString()

        for index in range(4):
            grid = self.numbers[score_str[index]]
            grid_offset = 4 * index

            check = 1 << 14
            for i in range(5):
                for j in range(3):
                    if grid & check:
                        paintPixel(painter, j + grid_offset + 2, i + 2)
                    check >>= 1

                        
    def __del__(self):
        print 'deleting scoreboard'


class BonusCountdown(qw.QWidget):
    NUMBERS = [0x7b6f, 0x2c92, 0x73e7, 0x73cf, 0x5bc9,
               0x79cf, 0x79ef, 0x7249, 0x7bef, 0x7bcf]

    COUNTDOWN_END_SIGNAL = qc.SIGNAL('countdownEnd()')

    def __init__(self, parent):
        qw.QWidget.__init__(self, parent)

        self.data = parent.data

        self.setFixedWidth(self.data.width)
        self.setFixedHeight(self.data.height)

        self.numbers = dict([(str(i), BonusCountdown.NUMBERS[i]) for i in range(10)])

        self.countdown = 0


    def reset(self):
        self.countdown = self.data.bonus_countdown


    def update(self):
        self.countdown -= 1
        self.repaint()

        if self.countdown == 0:
            self.emit(BonusCountdown.COUNTDOWN_END_SIGNAL)


    def paintEvent(self, _):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)

        countdown_str = '{:02d}'.format(self.countdown)

        for index in range(2):
            grid = self.numbers[countdown_str[index]]
            grid_offset = (4 * index) + self.data.screen_width - 11

            check = 1 << 14
            for i in range(5):
                for j in range(3):
                    if grid & check:
                        paintPixel(painter, j + grid_offset + 2, i + 2)
                    check >>= 1

# ------------------------------------------------------------------------------------------------ #
        
class Row(object):
    def __init__(self, width):
        self.rows = [Block() for _ in range(width)]
        
        
    def __len__(self):
        return len(self.rows)
    
    
    def __getitem__(self, index):
        return self.rows[index]
        
# ------------------------------------------------------------------------------------------------ #

class Block(object):
    FREE = 0
    BODY = 1
    HEAD = 2
    HEAD_OPEN = 3
    TAIL = 4
    CORNER = 5
    BODY_PARTS = {BODY, HEAD, HEAD_OPEN, TAIL, CORNER}

    FOOD = 0x6bd6
    APPLE = 0x252
    BONUS_A_1 = 0xcfac
    BONUS_A_2 = 0x3750
    BONUS_B_1 = 0xed90
    BONUS_B_2 = 0xf753
    BONUS_C_1 = 0xaf10
    BONUS_C_2 = 0xaf00
    BONUS_D_1 = 0x5dfc
    BONUS_D_2 = 0xabf3
    ALL_BONUSES = {BONUS_A_1, BONUS_A_2,
                   BONUS_B_1, BONUS_B_2,
                   BONUS_C_1, BONUS_C_2,
                   BONUS_D_1, BONUS_D_2}
    BONUSES = [(BONUS_A_1, BONUS_A_2),
               (BONUS_B_1, BONUS_B_2),
               (BONUS_C_1, BONUS_C_2),
               (BONUS_D_1, BONUS_D_2)]


    DRAW = {BODY: {LEFT: 0xbd0, RIGHT: 0xdb0, UP: 0x6246, DOWN: 0x6426},
            HEAD: {LEFT: 0xe68, RIGHT: 0x761, UP: 0xa660, DOWN: 0x66a},
            HEAD_OPEN: {LEFT: 0x2c4a, RIGHT: 0x4325, UP: 0x5690, DOWN: 0x965},
            TAIL: {LEFT: 0xf30, RIGHT: 0xfc0, UP: 0x4466, DOWN: 0x6644},
            CORNER: {LEFT: 0xca6, RIGHT: 0x356, UP: 0x6ac0, DOWN: 0x6530}}
    
    def __init__(self):
        self.type = Block.FREE
        self.direction = LEFT
        self.corner_direction = LEFT
        self.counter = 0
        self.food = False
        self.open = False
              
        
    def reset(self):
        self.type = Block.FREE
        self.direction = LEFT
        self.corner_direction = LEFT
        self.counter = 0
        self.food = False
        self.open = False
        
        
    def draw(self):
        if self.type == Block.APPLE:
            return Block.APPLE

        if self.type in Block.ALL_BONUSES:
            return self.type
        
        if self.food and self.type not in (Block.HEAD, Block.TAIL):
            return Block.FOOD
        
        direction = self.corner_direction if self.type == Block.CORNER else self.direction        
        if self.type == Block.HEAD and self.open:
            return Block.DRAW[Block.HEAD_OPEN][direction]        

        return Block.DRAW[self.type][direction]

#--------------------------------------------------------------------------------------------------#

class HighScores(ScrollArea):
    def __init__(self, data):
        super(HighScores, self).__init__(data, 'High Scores')

        self.data.loadScores()
        self.initialize()

        self._edit_mode = False

        self._edit_timer = qc.QTimer()
        self._edit_timer.timeout.connect(self._toggleEdit)

        self._edit_item = None
        self._edit_index = 0
        self._edit_indices = [0, None, None]


    def initialize(self):
        """ Setup the menu with given items and signal connections. Should be pairs of
         text:signal_id.
        """
        items = []
        for position, (name, score) in enumerate(self.data.scores):
            items.append(HighScoreItem(position, name, score))

        return super(HighScores, self).initialize(items)


    def select(self, selected_item_index):
        """
        Normally this would select the item at the given index, but in this case it triggers a
        return to the main menu.

        :param int selected_item_index: the index of the item selected

        :return:
        """
        """Returns to main menu."""
        self.switch(0)


    def start(self):
        """
        Triggered on start up of high score screen. If entered from the main menu, no new
        score is stored, so nothing happens. If entered from the arena, a new score is
        stored, in which case this function checks if the score is high enough to be on the board.
        If so it enters edit mode to allow the player to enter a name.

        :return:
        """
        super(ScrollArea, self).start()

        # if no new high score, return
        #
        if not self.data.new_high_score:
            return

        # test if new high score should be in high score list
        #
        position = -1
        for i, (_, score) in enumerate(self.data.scores):
            if self.data.new_high_score > score:
                position = i
                break

        # if new high score is lower than lowest high score, return
        #
        if position == -1:
            return

        # select score item
        #
        self.selected_item_index = position
        self._scroll()

        # insert new score
        #
        self.data.scores.insert(position, ('---', self.data.new_high_score))
        self.data.scores = self.data.scores[:-1]

        # shift scores and names to match high score list
        #
        for i, (name, score) in enumerate(self.data.scores):
            self.items[i].score = score
            self.items[i].name = name

        # reset high scores
        #
        self.data.new_high_score = None

        # start edit mode
        #
        self._edit_item = self.items[position]
        self.start_edit()


    def keyPressEvent(self, event):
        """
        Handles scrolling and selection of menu items. In edit mode, also handles scrolling
        letter selection.

        :param QEvent event: key press event
        :return:
        """
        if self._edit_mode:
            key = event.key()
            if key in (qc.Qt.Key_Up, qc.Qt.Key_Down):
                if key == qc.Qt.Key_Up:
                    self.scroll_edit(1)
                elif key == qc.Qt.Key_Down:
                    self.scroll_edit(-1)
            elif key in (qc.Qt.Key_Return, qc.Qt.Key_Enter):
                self.next_edit()

            self.repaint()
            return

        super(HighScores, self).keyPressEvent(event)


    @qc.Slot()
    def _toggleEdit(self):
        """
        Toggles the edit paint attribute. If False the name text is not drawn. Used to make
        the text flash on and off.

        :return:
        """
        if not self._edit_item:
            return

        self._edit_item._edit_paint = not self._edit_item._edit_paint
        self.repaint()


    def start_edit(self):
        """
        Begins edit mode. Starts the name text flickering animation timer, sets the edit
        data to default, and updates the name image.

        :return:
        """
        self._edit_mode = True
        self._edit_timer.start(300)

        self._edit_index = 0
        self._edit_indices = [0, None, None]

        self._updateName()


    def scroll_edit(self, scroll):
        """
        Scrolls through the letter selection. Adds or subtracts from the current letter value.
        Wraps A-Z.

        :param scroll: plus or minus 1 scroll value.
        :return:
        """
        self._edit_indices[self._edit_index] += scroll

        current_value = self._edit_indices[self._edit_index]
        if  current_value >= 26:
            self._edit_indices[self._edit_index] -= 26
        elif current_value < 0:
            self._edit_indices[self._edit_index] += 26

        self._updateName()


    def next_edit(self):
        """
        Move to the next letter to edit.

        :return:
        """
        self._edit_index += 1
        if self._edit_index == 3:
            self.end_edit()
            return

        self._edit_indices[self._edit_index] = self._edit_indices[self._edit_index-1]
        self._updateName()


    def end_edit(self):
        """
        Finish letter editing. Stops edit animation, stores the new name and saves the high score
        data to disk.

        :return:
        """
        # store new name and score
        #
        self.data.scores[self.selected_item_index] = (self._edit_item.name, self._edit_item.score)

        # reset edit variables
        #
        self._edit_item._edit_paint = False
        self._edit_item = None
        self._edit_mode = False
        self._edit_timer.stop()

        # save scores to disk
        #
        SnakeData.saveScores()


    def _updateName(self):
        """
        Updates the name image based on the current edit.

        :return:
        """
        name = ''
        for i in self._edit_indices:
            if i is None:
                name += '-'
            else:
                name += intToAlpha(i, upper=True)

        self._edit_item.name = name
        self.repaint()


class HighScoreItem(object):
    score_positions = ('1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th')

    blank_image = font.small_font.getImage('   ')


    def __init__(self, position, name, score):
        self.images = [None, None, None]
        self.height = 12

        self._name = None
        self._position = None
        self._score = None
        self._edit_paint = False

        self.position = position
        self.name = name
        self.score = score


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, name):
        name = str(name)
        if len(name) > 3:
            name = name[0:3]
        else:
            for _ in range(len(name), 3):
                name += 'A'

        self._name = name.upper()

        self.images[2] = font.small_font.getImage(self.name)


    @property
    def score(self):
        return self._score


    @score.setter
    def score(self, score):
        self._score = int(score)
        self.images[1] = font.small_font.getImage('{:04d}'.format(self.score))


    @property
    def positions(self):
        return self._position


    @positions.setter
    def position(self, position):
        """
        Set the position (1st, 2nd, 3rd etc) of the high score item. Creates the required image.

        :param int position: position value (1 - 10)

        :return:
        """
        self._position = min(max(0, int(position)), 10)
        self.images[0] = font.small_font.getImage(HighScoreItem.score_positions[self.position])


    def paint(self, painter, paint_area, invert=False):
        """
        Paints on row of the high score item. Position -> Score -> Name.

        :param QPainter painter: QPainter object to paint with
        :param list paint_area: the area to paint in (x, y, width, height)
        :param bool invert: if true pixels are inverted

        :return:
        """
        # calculate column widths and sub paint area
        #
        column_width = int(paint_area[2] / 3.0)
        sub_paint_area = [paint_area[0], paint_area[1], column_width, paint_area[3]]

        for i, image in enumerate(self.images):
            # don't paint name for animated flickering
            #
            if i == 2 and self._edit_paint:
                HighScoreItem.blank_image.paint(painter, sub_paint_area, invert, paintPixel)
                continue

            # paint text
            #
            image.paint(painter, sub_paint_area, invert, paintPixel)
            sub_paint_area[0] += column_width

# ------------------------------------------------------------------------------------------------ #

ui = None

def run():
    global ui

    if not ui:
        ui = Snake()
    
    ui.show()
    

def end():
    global ui
    
    if ui:
        del ui
    
    ui = None