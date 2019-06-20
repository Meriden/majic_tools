import PySide2.QtCore as qc
import PySide2.QtWidgets as qw

# ------------------------------------------------------------------------------------------------ #

class GameData(dict):
    title = 'GAME'
    pause = False

    width = 500
    height = 500

    background_color = (100, 100, 100)

# ------------------------------------------------------------------------------------------------ #

class Game(qw.QDialog):
    """Main Game Window. Has functions for adding and connection levels."""

    data = GameData()

    def __init__(self):
        super(Game, self).__init__()

        self.setWindowTitle(self.data.title)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)

        self.setBackgroundColor(*self.data.background_color)

        self.setLayout(qw.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.setFixedWidth(self.data.width)
        self.setFixedHeight(self.data.height)

        self.widget_stack = qw.QStackedWidget()
        self.layout().addWidget(self.widget_stack)

        self.installEventFilter(self)

        # level information
        #
        self._levels = {}
        self._types = {}
        self._connections = {}


    def setBackgroundColor(self, r, g, b):
        """Set background color to give rgb value."""
        self.setStyleSheet('background-color: rgb({}, {}, {});'.format(r, g, b))


    def register(self, type_name, level_class):
        """Register a new level type."""

        self._types[type_name] = level_class
        level_class.data = Game.data


    def addLevel(self, level_class, *args, **kwargs):
        """Add a new level to the game. Creates the level based on type, add and connects."""
        # get level class from registered level types
        #
        new_level = level_class(self.data, *args, **kwargs)

        self.widget_stack.addWidget(new_level)
        self.connect(new_level, qc.SIGNAL('switchLevel(int, int)'), self._switch)

        # store new level against level id for reference
        #
        self._levels[new_level.id] = new_level

        return new_level


    @staticmethod
    def addConnection(src_level, dst_level):
        """Define connections between levels."""
        # add new connection
        #
        src_level.connections.append(dst_level.id)

        return len(src_level.connections) - 1


    def _switch(self, current_level_id, signal_id):
        """Switch to another level based on predefined connections."""
        # end current level
        #
        current_level = self._levels[current_level_id]

        # get next level from connections
        #
        num_connections = len(current_level.connections)
        if num_connections == 0:
            return

        signal_id = min(signal_id, (num_connections - 1))
        next_level_id = current_level.connections[signal_id]

        # display next level and start
        #
        next_level = self._levels[next_level_id]
        self.widget_stack.setCurrentWidget(next_level)

        # switch levels
        #
        current_level.end()
        next_level.start()


    def keyPressEvent(self, event):
        """
        Feed key press events to current widget. Otherwise signal goes to main window and is lost.
        Feed key press events to current widget. Otherwise signal goes to main window and is lost.
        """
        current_widget = self.widget_stack.currentWidget()
        return current_widget.keyPressEvent(event)


    def focusOutEvent(self, event):
        print 'focus out'
        super(Game, self).focusOutEvent(event)


    def eventFilter(self, object, event):
        if event.type() == qc.QEvent.WindowDeactivate:
            self.data.pause = True
        elif event.type() == qc.QEvent.WindowActivate:
            self.data.pause = False
        return False

# ------------------------------------------------------------------------------------------------ #

class Level(qw.QWidget):
    id = 0

    def __init__(self, data):
        qw.QWidget.__init__(self)
        self.id = Level.id
        Level.id += 1

        self.data = data
        self.connections = []

        self.setLayout(qw.QHBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)


    def reset(self):
        pass


    def start(self):
        pass


    def end(self):
        pass


    def switch(self, index):
        self.emit(qc.SIGNAL('switchLevel(int, int)'), self.id, index)