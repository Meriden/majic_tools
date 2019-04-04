from majic_tools.maya.apps.games.snake.images import Image

class Font(object):
    ALIGN_LEFT = 1
    ALIGN_CENTER = 2
    ALIGN_RIGHT = 3

    def __init__(self, data, height):
        self.height = height

        # process symbols
        #
        self._data = {}
        for letter, grid in data.items():
            bin_str = bin(grid)[3:]
            width = len(bin_str) / self.height
            self._data[letter] = [bin_str[i * width:(i + 1) * width] for i in range(height)]


    def getImage(self, text, width=None, height=None, alignment=None):
        # compose new gris from text
        #
        grid = ['' for _ in range(self.height)]
        for letter_index, letter in enumerate(text):
            # get letter grid from data. Use ' ' grid if not defined.
            #
            letter_grid = self._data.get(letter, None)
            if letter_grid is None:
                letter_grid = self._data.get(' ', None)
            if letter_grid is None:
                continue

            # add row to grid
            #
            for i, row in enumerate(letter_grid):
                grid[i] += row

                # add a space between letters
                #
                if letter_index != len(text)-1:
                    grid[i] += '0'

        # modify grid to match specified height
        #
        base_offset = 0
        if isinstance(height, int):
            if height < self.height:
                grid = grid[:height]

            else:
                top_offset = base_offset = (height - self.height) / 2
                if (top_offset + base_offset + self.height) != height:
                    top_offset += 1

                for _ in range(top_offset):
                    grid.insert(0, '0')
                for _ in range(base_offset):
                    grid.append('0')
        else:
            height = self.height

        # modify grid to match specified width with given alignment
        #
        if isinstance(width, int):
            grid_width = max([len(row) for row in grid])
            if width < grid_width:
                for i, row in enumerate(grid):
                    grid[i] = row[:width]
            else:
                left_offset = right_offset = (width - grid_width) / 2
                if grid_width + left_offset + right_offset < width:
                    right_offset += 1

                if grid_width + (2 * base_offset) > width:
                    pass

                elif alignment == self.ALIGN_LEFT:
                    left_offset = base_offset
                    right_offset = width - (grid_width + left_offset)

                elif alignment == self.ALIGN_RIGHT:
                    right_offset = base_offset
                    left_offset = width - (grid_width + right_offset)

                for i, row in enumerate(grid):
                    grid[i] = ('0' * left_offset) + row + ('0' * right_offset)

        # create image
        #
        new_image = Image()
        new_image.lines = [int(i, 2) for i in grid]
        new_image.width = max([len(row) for row in grid])
        new_image.height = height

        return new_image



symbols = {' ': 0x100000000000,
           '!': 0x7ffcf0,
           '"': 0x7d0000,
           '\'': 0x7d0000,
           '(': 0x17ccccccc700,
           ')': 0x1e3333333e00,
           ',': 0x4000f0,
           '.': 0x4000f4,
           '/': 0x8c633198cc6000,
           '0': 0x5ecf3cf3cf3cde000,
           '1': 0x16e666666f00,
           '2': 0x5ecf3cc739ce3f000,
           '3': 0x5ecf30ce0f3cde000,
           '4': 0x21871e6c9b366fe18000,
           '5': 0x7fc30f830f3cde000,
           '6': 0x5ecf0fb3cf3cde000,
           '7': 0x7fcc30c638c30c000,
           '8': 0x5ecf3cdecf3cde000,
           '9': 0x5ecf3cf37c3cde000,
           ':': 0x43c3c0,
           ';': 0x43c3d0,
           '?': 0x5ecf30ce30030c000,
           'A': 0x5ecf3cffcf3cf3000,
           'B': 0x7ecf3cfecf3cfe000,
           'C': 0x5ecf0c30c30cde000,
           'D': 0x7ecf3cf3cf3cfe000,
           'E': 0xff18f6318c7c00,
           'F': 0xff18f6318c6000,
           'G': 0x5ecf0c30df3cde000,
           'H': 0x73cf3cffcf3cf3000,
           'I': 0x7ffff0,
           'J': 0x133333333e00,
           'K': 0x73cf3cfecf3cf3000,
           'L': 0x1ccccccccf00,
           'M': 0x3071f7ffaf1e3c78c000,
           'N': 0x30f1f3f7ff7e7c784000,
           'O': 0x5ecf3cf3cf3cde000,
           'P': 0x7ecf3cfec30c30000,
           'Q': 0x5ecf3cf3cf3dde0c0,
           'R': 0x7ecf3cfecf3cf3000,
           'S': 0x5ecf0c1e0c3cde000,
           'T': 0x7f30c30c30c30c000,
           'U': 0x73cf3cf3cf3cde000,
           'V': 0x73cf3cf3cde78c000,
           'W': 0x38f1e3d7affbe7cd8000,
           'X': 0x73cde78c79ecf3000,
           'Y': 0x73cf3cde30c30c000,
           'Z': 0xfc633198cc7c00,
           '[': 0x17ccccccc700,
           '\\': 0xe318630c618c00,
           ']': 0x1e3333333e00,
           'a': 0x4001e0dfcf3cdf000,
           'b': 0x70c3ecf3cf3cfe000,
           'c': 0x4001ecf0c30cde000,
           'd': 0x430dfcf3cf3cdf000,
           'e': 0x4001ecf3ff0cde000,
           'f': 0x136f66666600,
           'g': 0x4001ecf3cf3cdf0de,
           'h': 0x70c3ecf3cf3cf3000,
           'i': 0x73fff0,
           'j': 0x2c36db780,
           'k': 0x70c33dbce3cdb3000,
           'l': 0x7ffff0,
           'm': 0x10000fedbdbdbdbdbdb0000,
           'n': 0x4003ecf3cf3cf3000,
           'o': 0x4001ecf3cf3cde000,
           'p': 0x4003ecf3cf3cfec30,
           'q': 0x4001ecf3cf3cdf0c3,
           'r': 0x801bfe318c6000,
           's': 0x800fc61c31f800,
           't': 0x166f66666300,
           'u': 0x40033cf3cf3cdf000,
           'v': 0x40033cf3cd278c000,
           'w': 0x200063c78f5eb7cd8000,
           'x': 0x40033cf37bfcf3000,
           'y': 0x40033cf3cf3cdf0de,
           'z': 0x100f3366cf00,
           '{': 0x17ccccccc700,
           '|': 0x7ffff0,
           '}': 0x1e3333333e00}

main_font = Font(symbols, 11)

symbols = {' ': 0x100000,
           '0': 0x176f7bdedc0,
           '1': 0x17db6d8,
           '2': 0x1f0c6ec63e0,
           '3': 0x1f0c6e18fc0,
           '4': 0x119d73f8c60,
           '5': 0x1f43c318fc0,
           '6': 0x1763dbdedc0,
           '7': 0x3f198cc6300,
           '8': 0x176f6ededc0,
           '9': 0x176f7b70dc0,
           '!': 0x1ffcc,
           '"': 0x1b40000,
           '#': 0x157feaffd40,
           '$': 0x153f5e7afca,
           '%': 0x1cb610c21b4c0,
           '&': 0x173673ddf7740,
           '\'': 0x1c0,
           '(': 0x12b6d91,
           ')': 0x189b6d4,
           '*': 0x1257eefd480,
           '+': 0x10109f21000,
           ',': 0x1001e,
           '-': 0x1000f0000,
           '.': 0x1003c,
           '/': 0x125ad20,
           ':': 0x10f3c,
           ';': 0x10f1d,
           '<': 0x1136c6310,
           '=': 0x1000f0f00,
           '>': 0x18c636c80,
           '?': 0x1f0ccc60180,
           '@': 0x17b3ff7ff0780,
           'A': 0x176f7bfef60,
           'B': 0x1f6fdbdefc0,
           'C': 0x17e318c61e0,
           'D': 0x1f6f7bdefc0,
           'E': 0x1fe3d8c63e0,
           'F': 0x1fe3d8c6300,
           'G': 0x17631bdede0,
           'H': 0x1deffbdef60,
           'I': 0x1fffc,
           'J': 0x1333333e0,
           'K': 0x1cf6f38f36cc0,
           'L': 0x1ccccccf0,
           'M': 0x1838fbffd78f180,
           'N': 0x18f3effdf3c40,
           'O': 0x17b3cf3cf3780,
           'P': 0x1f6f7bf6300,
           'Q': 0x17b3cf3cf7783,
           'R': 0x1f6f7bf6b60,
           'S': 0x17cc633e0,
           'T': 0x1fcc30c30c300,
           'U': 0x1def7bdedc0,
           'V': 0x1cf3cde78c300,
           'W': 0x1c78f5ff7cf9b00,
           'X': 0x1cf378c7b3cc0,
           'Y': 0x1cf378c30c300,
           'Z': 0x1f8ceee63e0,
           '[': 0x1fb6db8,
           '\\': 0x1932648,
           ']': 0x1edb6f8,
           'a': 0x1001c37ede0,
           'b': 0x1c63dbdefc0,
           'c': 0x1007ccc70,
           'd': 0x118dfbdede0,
           'e': 0x1001dbfe1e0,
           'f': 0x17bedb0,
           'g': 0x1001fbdbc7e,
           'h': 0x1c63dbdef60,
           'i': 0x1cffc,
           'j': 0x161b6de,
           'k': 0x1c637ee7b60,
           'l': 0x1fffc,
           'm': 0x10000fedbdbdbdb00,
           'n': 0x1003dbdef60,
           'o': 0x1001dbdedc0,
           'p': 0x1003dbdfb18,
           'q': 0x1001fbdbc63,
           'r': 0x100dfccc0,
           's': 0x1007cf3e0,
           't': 0x1dbed98,
           'u': 0x10037bdede0,
           'v': 0x10037b73880,
           'w': 0x100031ebd6f9b00,
           'x': 0x10037b76f60,
           'y': 0x10037bdbc6e,
           'z': 0x1003e6663e0,
           '|': 0x1fffc}

small_font = Font(symbols, 8)

# {'a': '0000000000011100001101111110110111100000',
# 'b': '1100011000111101101111011110111111000000',
# 'c': '00000000011111001100110001110000',
# 'd': '0001100011011111101111011110110111100000',
# 'e': '0000000000011101101111111110000111100000',
# 'f': '011110111110110110110000',
# 'g': '0000000000011111101111011011110001111110',
# 'h': '1100011000111101101111011110111101100000',
# 'i': '1100111111111100',
# 'j': '011000011011011011011110',
# 'k': '1100011000110111111011100111101101100000',
# 'l': '1111111111111100',
# 'm': '0000000000000000111111101101101111011011110110111101101100000000',
# 'n': '0000000000111101101111011110111101100000',
# 'o': '0000000000011101101111011110110111000000',
# 'p': '0000000000111101101111011111101100011000',
# 'q': '0000000000011111101111011011110001100011',
# 'r': '00000000110111111100110011000000',
# 's': '00000000011111001111001111100000',
# 't': '110110111110110110011000',
# 'u': '0000000000110111101111011110110111100000',
# 'v': '0000000000110111101101110011100010000000',
# 'w': '00000000000000110001111010111101011011111001101100000000',
# 'x': '0000000000110111101101110110111101100000',
# 'y': '0000000000110111101111011011110001101110',
# 'z': '0000000000111110011001100110001111100000',
# 'A': '0111011011110111101111111110111101100000',
# 'B': '1111011011111101101111011110111111000000',
# 'C': '0111111000110001100011000110000111100000',
# 'D': '1111011011110111101111011110111111000000',
# 'E': '1111111000111101100011000110001111100000',
# 'F': '1111111000111101100011000110001100000000',
# 'G': '0111011000110001101111011110110111100000',
# 'H': '1101111011111111101111011110111101100000',
# 'I': '1111111111111100',
# 'J': '00110011001100110011001111100000',
# 'K': '110011110110111100111000111100110110110011000000',
# 'L': '11001100110011001100110011110000',
# 'M': '10000011100011111011111111111101011110001111000110000000',
# 'N': '100011110011111011111111110111110011110001000000',
# 'O': '011110110011110011110011110011110011011110000000',
# 'P': '1111011011110111101111110110001100000000',
# 'Q': '011110110011110011110011110011110111011110000011',
# 'R': '1111011011110111101111110110101101100000',
# 'S': '01111100110001100011001111100000',
# 'T': '111111001100001100001100001100001100001100000000',
# 'U': '1101111011110111101111011110110111000000',
# 'V': '110011110011110011011110011110001100001100000000',
# 'W': '11000111100011110101111111110111110011111001101100000000',
# 'X': '110011110011011110001100011110110011110011000000',
# 'Y': '110011110011011110001100001100001100001100000000',
# 'Z': '1111100011001110111011100110001111100000',
# '!': '1111111111001100',
# '"': '101101000000000000000000',
# '#': '0101011111111110101011111111110101000000',
# '$': '0101001111110101111001111010111111001010',
# '%': '110010110110000100001100001000011011010011000000',
# '&': '011100110110011100111101110111110111011101000000',
# '\'': '11000000',
# '(': '001010110110110110010001',
# ')': '100010011011011011010100',
# '*': '0010010101111110111011111101010010000000',
# '+': '0000000100001001111100100001000000000000',
# ',': '0000000000011110',
# '-': '00000000000011110000000000000000',
# '.': '0000000000111100',
# '/': '001001011010110100100000',
# '?': '1111000011001100110001100000000110000000',
# '@': '011110110011111111110111111111110000011110000000',
# ':': '0000111100111100',
# ';': '0000111100011101',
# '<': '00010011011011000110001100010000',
# '=': '00000000000011110000111100000000',
# '>': '10001100011000110110110010000000',
# '[': '111110110110110110111000',
# ']': '111011011011011011111000',
# '|': '1111111111111100',
# '\\': '100100110010011001001000',}
























