# SIDES
#
LEFT = 'L'
CENTER = 'C'
RIGHT = 'R'
SIDES = [LEFT, CENTER, RIGHT]

# TRANSFORM NAMES
#
GROUP = 'GRP'
ZERO = 'ZERO'
OFFSET = 'OFFSET'
NEGATE = 'NEGATE'
GUIDE = 'GUIDE'
RIVET = 'RIVET'
MIRROR = 'MIRROR'
NULL = 'NULL'
CONTROL = 'CTRL'
JOINT = 'JNT'
SPACE_SWITCH = 'SPACE_SWITCH'

INPUT = 'IN'
OUTPUT = 'OUT'

# SHAPE NAMES
#
GEO = 'GEO'
CURVE = 'CRV'

TAG = 'tag'

# CONTROL TAGS
#
CTRL_SHAPE = 'CTRL_SHAPE'
CTRL_OFFSET = 'CTRL_OFFSET'
CTRL_DEPENDENCY = 'CTRL_DEPENDENCY'
CTRL_SNAP = 'CTRL_SNAP'
CTRL_SIDE = 'CTRL_SIDE'

# COLOURS
#
DEFAULT         = 0
BLACK           = 1
DARK_GRAY       = 2
LIGHT_GRAY      = 3
SCARLET         = 4
INDIGO          = 5
BLUE            = 6
FORREST_GREEN   = 7
DARK_PURPLE     = 8
MAGENTA         = 9
BROWN           = 10
DARK_BROWN      = 11
RED_ORANGE      = 12
RED             = 13
COMPUTER_GREEN  = 14
GRAY_BLUE       = 15
WHITE           = 16
YELLOW          = 17
LIGHT_BLUE      = 18
LIGHT_GREEN     = 19
PINK            = 20
PEACH           = 21
LIGHT_YELLOW    = 22
TEAL_GREEN      = 23
TAN             = 24
DULL_YELLOW     = 25
GREEN_YELLOW    = 26
TEAL            = 27
TEAL_BLUE       = 28
DULL_BLUE       = 29
PURPLE          = 30
RED_PURPLE      = 31

COLOURS = {'default'        : DEFAULT,
           'black'          : BLACK,
           'dark_gray'      : DARK_GRAY,
           'light_gray'     : LIGHT_GRAY,
           'scarlet'        : SCARLET,
           'indigo'         : INDIGO,
           'blue'           : BLUE,
           'forrest_green'  : FORREST_GREEN,
           'dark_purple'    : DARK_PURPLE,
           'magenta'        : MAGENTA,
           'brown'          : BROWN,
           'dark_brown'     : DARK_BROWN,
           'red_orange'     : RED_ORANGE,
           'red'            : RED,
           'computer_green' : COMPUTER_GREEN,
           'gray_blue'      : GRAY_BLUE,
           'white'          : WHITE,
           'yellow'         : YELLOW,
           'light_blue'     : LIGHT_BLUE,
           'light_green'    : LIGHT_GREEN,
           'pink'           : PINK,
           'peach'          : PEACH,
           'light_yellow'   : LIGHT_YELLOW,
           'teal_green'     : TEAL_GREEN,
           'tan'            : TAN,
           'dull_yellow'    : DULL_YELLOW,
           'green_yellow'   : GREEN_YELLOW,
           'teal'           : TEAL,
           'teal_blue'      : TEAL_BLUE,
           'dull_blue'      : DULL_BLUE,
           'purple'         : PURPLE,
           'red_purple'     : RED_PURPLE}


# COLOUR SCHEMES
#
SCHEME_1 = {LEFT : RED ,       RIGHT : YELLOW,       CENTER : LIGHT_BLUE}
SCHEME_2 = {LEFT : PINK,       RIGHT : LIGHT_YELLOW, CENTER : BLUE}
SCHEME_3 = {LEFT : SCARLET,    RIGHT : DULL_YELLOW,  CENTER : GRAY_BLUE}
SCHEME_4 = {LEFT : PURPLE,     RIGHT : TAN,          CENTER : TEAL_GREEN}
SCHEME_5 = {LEFT : RED_PURPLE, RIGHT : DULL_YELLOW,  CENTER : TEAL_BLUE}
SCHEMES = [SCHEME_1, SCHEME_2, SCHEME_3, SCHEME_4, SCHEME_5]


# COLOR RGB VALUES
#
COLOURS_RGB = {0 : (180, 180, 180),
               1 : (0, 0, 0),
               2 : (64, 64, 64),
               3 : (153, 153, 153),
               4 : (155, 0, 40),
               5 : (0, 5, 95),
               6 : (0, 0, 255),
               7 : (0, 70, 25),
               8 : (38, 0, 67),
               9 : (200, 0, 200),
               10: (138, 72, 51),
               11: (63, 35, 31),
               12: (153, 38, 0),
               13: (255, 0, 0),
               14: (0, 255, 0),
               15: (0, 65, 153),
               16: (255, 255, 255),
               17: (255, 255, 0),
               18: (100, 220, 255),
               19: (67, 255, 163),
               20: (255, 176, 176),
               21: (228, 172, 121),
               22: (255, 255, 99),
               23: (0, 153, 84),
               24: (161, 105, 48),
               25: (159, 161, 48 ),
               26: (104, 161, 48),
               27: (48, 161, 93),
               28: (48, 161, 161),
               29: (48, 143, 161),
               30: (111, 48, 161),
               31: (161, 48, 105)}


# COMPONENT SPACES
#
OBJECT_SPACE = 'os'
WORLD_SPACE = 'ws'

# DEFORMERS
#
BLENDSHAPE = 'BS'
CLUSTER = 'CLS'
SKINCLUSTER = 'SCLS'
LATTICE = 'LAT'
WRAP = 'WRAP'

# FILE FORMATS
#
MAYA_BINARY = 'mayaBinary'
MAYA_ASCII  = 'mayaAscii'

MAYA_BINARY_EXT = 'mb'
MAYA_ASCII_EXT = 'ma'

MAYA_FILE_EXTS = {MAYA_BINARY:MAYA_BINARY_EXT, MAYA_ASCII:MAYA_ASCII_EXT}
MAYA_FILE_TYPES = {MAYA_BINARY_EXT:MAYA_BINARY, MAYA_ASCII_EXT:MAYA_ASCII}

# DAG SUFFIXES
#
SET = 'SET'
MULT = 'MULT'
DIV = 'DIV'
INV = 'INV'
PLUS = 'PLUS'
SUB = 'SUB'




