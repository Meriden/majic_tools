import random

import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw

from majic_tools.maya.apps.games.snake import game; reload(game)
from majic_tools.maya.apps.games.snake import images; reload(images)
from majic_tools.maya.apps.games.snake import font; reload(font)

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
        #high_scores = self.addLevel(HighScores)
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
        #menu_to_scores = self.addConnection(main_menu, high_scores)

        menu_items = [('New Game', menu_to_arena),
                      ('Level', menu_to_level),
                      ('High Scores', menu_to_level),
                      ('Mode', menu_to_level),
                      ('Test 1', menu_to_level),
                      ('Test 2', menu_to_level),
                      ('Test 3', menu_to_level),
                      ('Test 4', menu_to_level)]
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
        
# ------------------------------------------------------------------------------------------------ #

def paintPixel(painter, x, y):
    """
    Paints a pixel of defined width, with a shadow.

    :param painter: QPainter object to draw with
    :param int x: real x position to draw the pixel
    :param int y: real y position to draw the pixel
    :param int pixel_width: how many real pixels wide is the game pixel
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
        self.offset = (0, 0)


    def initialize(self, image):
        self.image = image

        x_offset = (self.data.screen_width - self.image.width) / 2
        y_offset = (self.data.screen_height - self.image.height) / 2
        self.offset = (x_offset, y_offset)

    
    def paintEvent(self, _):
        if self.image is None:
            return

        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x() + self.offset[0]
        y = option.rect.y() + self.offset[1]

        self.image.paint(painter, x, y, False, paintPixel)


    def keyPressEvent(self, _):
        self.switch(0)
                    
# ------------------------------------------------------------------------------------------------ #

class ScrollArea(game.Level):
    def __init__(self, data, title='Untitled'):
        super(ScrollArea, self).__init__(data)

        self.title = title
        self.title_image = None

        self.item_width = self.data.screen_width - 4
        self.items = []
        self.item_positions = {}

        self.setTitle(title)

        self.selected_item_index = 0
        self.scroll_range = [0, 0, 0, []]
        self.scroll_range[0] = self.data.screen_height - self.title_image.height - 5
        self.scroll_range[2] = self.scroll_range[0]


    def setTitle(self, title):
        self.title = title
        self.title_image = font.small_font.getImage('- {} -'.format(title),
                                                    width=self.data.screen_width,
                                                    alignment=font.Font.ALIGN_CENTER)
        self.repaint()


    def addItem(self, item):
        new_index = len(self.items)
        self.items.append(item)
        self.item_positions[new_index] = self.item_positions[new_index - 1] + item.height
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
        pass


    def _scroll(self):
        """ Handles menu scrolling area, which items are visible and partial items."""

        selected_lower = self.item_positions.get(self.selected_item_index - 1, 0)
        selected_upper = self.item_positions[self.selected_item_index]

        if selected_lower <= self.scroll_range[1]:
            self.scroll_range[1] = selected_lower
            self.scroll_range[2] = selected_lower + self.scroll_range[0]
        elif selected_upper > self.scroll_range[2]:
            self.scroll_range[2] = selected_upper
            self.scroll_range[1] = selected_upper - self.scroll_range[0]

        # figure out which items are currently visible
        #
        visible_items = self.scroll_range[3] = []

        previous_scroll_value = 0
        for i, item in enumerate(self.items):
            scroll_value = self.item_positions[i]

            # check if lower or upper edge is in menu range
            #
            lower = upper = False
            if self.scroll_range[1] <= previous_scroll_value < self.scroll_range[2]:
                lower = True
            if self.scroll_range[1] < scroll_value <= self.scroll_range[2]:
                upper = True

            # based on visible edges add to visible menu items
            #
            if lower and upper:
                visible_items.append((i, None, None))
            elif lower:
                value = self.scroll_range[2] - previous_scroll_value
                if value == 0:
                    continue
                visible_items.append((i, 0, value))
            elif upper:
                value = scroll_value - self.scroll_range[1] + 2
                visible_items.append((i, value, item.image.height))

            previous_scroll_value = scroll_value


    def paintEvent(self, _):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)

        self.title_image.paint(painter, 0, 2, False, paintPixel)
        x = option.rect.x() + 2
        y = option.rect.y() + 3 + self.title_image.height

        # draw menu items
        #
        for item_index, lower, upper in self.scroll_range[3]:
            invert = False
            if item_index == self.selected_item_index:
                invert = True

            item = self.items[item_index]

            # get image
            #
            image = item.image
            if lower is not None:
                image = item.image.getSubImage(0, lower, item.image.width, upper - lower)

            # paint either full or partial menu item image
            #
            image.paint(painter, x, y, invert, paintPixel)
            y += image.height


class MenuItem(object):
    def __init__(self, text, width, height):
        self.text = text
        self.image = font.main_font.getImage(text,
                                             width = width,
                                             height = height,
                                             alignment = font.Font.ALIGN_LEFT)


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
        self.items = []
        self.signals = []
        self.item_positions = {}

        self.scroll_range = [0, 0, 0, []]
        self.scroll_range[0] = self.data.screen_height - self.title_image.height - 5
        self.scroll_range[2] = self.scroll_range[0]
        self.selected_item_index = 0

        # add each menu item to menu as fancy text
        #
        for menu_item_name, signal_id in menu_items:
            new_item = MenuItem(menu_item_name, self.item_width, 16)
            self.items.append(new_item)
            self.signals.append(signal_id)

        # store heights for quick reference while scrolling
        #
        scroll_value = 0
        for i, item in enumerate(self.items):
            scroll_value += item.image.height
            self.item_positions[i] = scroll_value

        # update scroll area
        #
        self._scroll()


    def select(self, selected_item_index):
        """Trigger level switch based on connected signal."""
        self.switch(self.signals[selected_item_index])


# class Menu(game.Level):
#     def __init__(self, data, title='Untitled'):
#         super(Menu, self).__init__(data)
#
#         self.menu_item_width = 100
#         self.menu_item_height = 16
#
#         self.selected_item_index = 0
#         self.scroll_value = 0
#
#         self.menu_items = []
#         self.menu_signals = []
#         self.menu_item_grids = {}
#         self.menu_items_scroll = {}
#
#         self.menu_range = [0, 0, 0, []]
#
#         self.menu_title = title
#         self.menu_title_grid = font.small_font.getImage('- {} -'.format(self.menu_title),
#                                                         width=self.data.screen_width,
#                                                         alignment=font.Font.ALIGN_CENTER)
#
#
#     def initialize(self, menu_items):
#         """ Setup the menu with given items and signal connections. Should be pairs of
#          text:signal_id.
#
#         :param list menu_items: list of menu items to display
#         :return:
#         """
#         self.menu_items = []
#         self.menu_signals = []
#         self.menu_item_grids = {}
#         self.menu_items_scroll = {}
#
#         # add each menu item to menu as fancy text
#         #
#         for menu_item_name, signal_id in menu_items:
#             self.menu_items.append(menu_item_name)
#             self.menu_signals.append(signal_id)
#             menu_item_image = font.main_font.getImage(menu_item_name,
#                                                       width=self.menu_item_width,
#                                                       height=self.menu_item_height,
#                                                       alignment=font.Font.ALIGN_LEFT)
#             self.menu_item_grids[menu_item_name] = menu_item_image
#
#         # store heights for quick reference while scrolling
#         #
#         scroll_value = 0
#         for i, menu_item_name in enumerate(self.menu_items):
#             scroll_value += self.menu_item_grids[menu_item_name].height
#             self.menu_items_scroll[i] = scroll_value
#
#         # calculate default visible range
#         #
#         self.menu_range[0] = self.data.screen_height - self.menu_title_grid.height - 5
#         self.menu_range[1] = self.scroll_value
#         self.menu_range[2] = self.menu_range[0] + self.menu_range[1]
#         self._scroll()
#
#
#     def keyPressEvent(self, event):
#         """ Handles scrolling and selection of menu items.
#
#         :param QEvent event: key press event
#         :return:
#         """
#         key = event.key()
#         if key in (qc.Qt.Key_Up, qc.Qt.Key_Down):
#             if key == qc.Qt.Key_Up:
#                 self.selected_item_index -= 1
#             elif key == qc.Qt.Key_Down:
#                 self.selected_item_index += 1
#
#             num_items = len(self.menu_items)
#             if self.selected_item_index < 0:
#                 self.selected_item_index = num_items - 1
#             elif self.selected_item_index >= num_items:
#                 self.selected_item_index = 0
#
#             self._scroll()
#             self.repaint()
#
#         elif key in (qc.Qt.Key_Return, qc.Qt.Key_Enter):
#             self.switch(self.menu_signals[self.selected_item_index])
#
#
#     def _scroll(self):
#         """ Handles menu scrolling area, which items are visible and partial items."""
#
#         selected_lower = self.menu_items_scroll.get(self.selected_item_index - 1, 0)
#         selected_upper = self.menu_items_scroll[self.selected_item_index]
#
#         if selected_lower <= self.menu_range[1]:
#             self.menu_range[1] = selected_lower
#             self.menu_range[2] = selected_lower + self.menu_range[0]
#         elif selected_upper > self.menu_range[2]:
#             self.menu_range[2] = selected_upper
#             self.menu_range[1] = selected_upper - self.menu_range[0]
#
#         # figure out which menu items are currently visible
#         #
#         visible_menu_items = self.menu_range[3] = []
#
#         previous_scroll_value = 0
#         for i, menu_item in enumerate(self.menu_items):
#             scroll_value = self.menu_items_scroll[i]
#
#             # check if lower or upper edge is in menu range
#             #
#             lower = upper = False
#             if self.menu_range[1] <= previous_scroll_value < self.menu_range[2]:
#                 lower = True
#             if self.menu_range[1] < scroll_value <= self.menu_range[2]:
#                 upper = True
#
#             # based on visible edges add to visible menu items
#             #
#             if lower and upper:
#                 visible_menu_items.append((i, None, None))
#             elif lower:
#                 value = self.menu_range[2] - previous_scroll_value
#                 if value == 0:
#                     continue
#                 visible_menu_items.append((i, 0, value))
#             elif upper:
#                 value = scroll_value - self.menu_range[1] + 2
#                 visible_menu_items.append((i, value, self.menu_item_grids[menu_item].height))
#
#             previous_scroll_value = scroll_value
#
#
#     def paintEvent(self, _):
#         painter = qw.QStylePainter(self)
#         option = qw.QStyleOption()
#         option.initFrom(self)
#
#         paintImage(self.menu_title_grid, painter, 0, 2, self.data.pixel_width)
#         x = option.rect.x() + 2
#         y = option.rect.y() + 3 + self.menu_title_grid.height
#
#         # draw menu items
#         #
#         for menu_item_id, lower, upper in self.menu_range[3]:
#             menu_item_grid = self.menu_item_grids[self.menu_items[menu_item_id]]
#
#             invert = False
#             if menu_item_id == self.selected_item_index:
#                 invert = True
#
#             # paint either full or partial menu item image
#             #
#             if lower is None:
#                 paintImage(menu_item_grid, painter, x, y, self.data.pixel_width, invert)
#                 y += menu_item_grid.height
#             else:
#                 sub_image = menu_item_grid.getSubImage(0, lower, menu_item_grid.width, upper - lower)
#                 paintImage(sub_image, painter, x, y, self.data.pixel_width, invert)
#                 y += sub_image.height


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
        self.game_over_image = font.main_font.getImage('Game over!', width=102, height=17)
        self.your_score_image = font.main_font.getImage('Your score:', width=102, height=17)
        self.score_image = font.main_font.getImage('0000', width=102, height=17)

    
    def reset(self):
        self._bonus_counter = 0
        self._game_over_counter = 0
        
        self.game_mode = True
        self.running = True

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
        elif key in (qc.Qt.Key_Return, qc.Qt.Key_Enter) and not self.game_mode:
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

        self.grid.hide()
        self.score_board.hide()
        self.bonus_countdown.hide()

        self.score_image = font.main_font.getImage(self.score_board.asString(), 102, 17)

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
            x, y = 0, 10
            self.game_over_image.paint(painter, x, y, False, paintPixel)
            self.your_score_image.paint(painter, x, y + 17, False, paintPixel)
            self.score_image.paint(painter, x, y + 34, False, paintPixel)


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

# ------------------------------------------------------------------------------------------------ #

ui = None

def create():
    global ui

    if not ui:
        ui = Snake()
    
    ui.show()
    


def delete():
    global ui
    
    if ui:
        del ui
    
    ui = None


def draw(image):
    image_str = []
    for line in image.lines:
        check = 1
        line_str = []
        for _ in range(image.width):
            if line & check:
                line_str.append('#')
            else:
                line_str.append(' ')
            check = check << 1
        image_str.append(''.join(line_str)[::-1])
    print '\n'.join(image_str)

#--------------------------------------------------------------------------------------------------#

class HighScores(Menu):
    def __init__(self, data):
        super(HighScores, self).__init__(data, 'High Scores')

        self.initialize(['MIK   0020', 'DAV   0234'])


class HighScoreLine(qw.QWidget):
    def __init__(self, name='AAA', score=0):
        super(HighScoreLine, self).__init__()
        self.name = name
        self.score = score
        self.edit_mode = False
        self.edit_index = 0

    def edit(self):
        pass


    def keyPressEvent(self, event):
        if not self.edit_mode:
            return

        key = event.key()
        if key == qc.Qt.Key_Left:
            self.grid.moveLeft()
        elif key == qc.Qt.Key_Right:
            self.grid.moveRight()
        elif key == qc.Qt.Key_Up:
            self.grid.moveUp()
        elif key == qc.Qt.Key_Down:
            self.grid.moveDown()
        elif key in (qc.Qt.Key_Return, qc.Qt.Key_Enter) and not self.game_mode:
            self.switch(0)


    def scrollUp(self):
        pass


    def scrollDown(self):
        pass


    def select(self):
        pass

