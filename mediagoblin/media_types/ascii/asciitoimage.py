# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Python IRC ASCII to image script by e (e@tr0ll.in)
 - Found at https://gist.github.com/791868
"""

import Image, ImageFont, ImageDraw
import time, re

_strip_colors_regex = re.compile('(\x03([0-9]{1,2})(,[0-9]{1,2})?)|[\x0f\x02\x1f\x03\x16]').sub
def strip_colors(string):
    return _strip_colors_regex('', string)
    
_colorRegex = re.compile('(([0-9]{1,2})(,([0-9]{1,2}))?)')

colors = [16777215, 0, 8323072, 2788394, 255, 127, 10223772, 32764, 65535, 64512, 9671424, 16776960, 16515072, 16711935, 8355711, 13816530]

IGNORE_CHRS = ('\x16','\x1f','\x02', '\x03', '\x0f')
def renderImage(text, size=15, utf8 = False, defaultBg = 1, defaultFg = 0, defaultFont = '/usr/share/fonts/truetype/ttf-inconsolata/Inconsolata.otf'):
    try:
        if utf8 and not isinstance(text, unicode):
            text = text.decode('utf-8')
    except:
        pass
    
    lineLens = [len(line) for line in strip_colors(text).split('\n')]
    maxWidth, height = max(lineLens), len(lineLens)
    font = ImageFont.truetype(defaultFont, size)
    fontX, fontY = font.getsize('.')
    imageX, imageY = maxWidth * fontX, height * fontY
    image = Image.new('RGB', (imageX, imageY), colors[defaultBg])
    draw = ImageDraw.Draw(image)
    dtext, drect, match, x, y, fg, bg = draw.text, draw.rectangle, _colorRegex.match, 0, 0, defaultFg, defaultBg
    start = time.time()
    for text in text.split('\n'):
        ll, i = len(text), 0
        while i < ll:
            chr = text[i]
            if chr == "\x03":
                m = match(text[i+1:i+6])
                if m:
                    i+= len(m.group(1))
                    fg = int(m.group(2), 10) % 16
                    if m.group(4) is not None:
                        bg = int(m.group(4), 10) % 16
                else:
                    bg, fg = defaultBg, defaultFg
                    
            elif chr == "\x0f":
                fg, bg = defaultFg, defaultBg
            elif chr not in IGNORE_CHRS:
                if bg != defaultBg: # bg is not white, render it
                    drect((x, y, x+fontX, y+fontY), fill=colors[bg])
                if bg != fg: # text will show, render it. this saves a lot of time!
                    dtext((x, y), chr, font=font, fill=colors[fg])
                x += fontX
            i += 1
        y += fontY
        fg, bg, x = defaultFg, defaultBg, 0
    return image, imageX, imageY, time.time()-start

import logging

_log = logging.getLogger(__name__)

class AsciiToImage(object):
    '''
    Converter of ASCII art into image files, preserving whitespace
    '''

    # TODO: Be more portable. (include an OTF in the GMG dist?)
    _font = '/usr/share/fonts/truetype/ttf-inconsolata/Inconsolata.otf'

    _font_size = 11

    # ImageFont instance
    _if = None

    # ImageFont
    _if_dims = None

    # Image instance
    _im = None

    def __init__(self, **kw):
        if kw.get('font'):
            self._font = kw.get('font')

        if kw.get('font_size'):
            self._font_size = kw.get('font_size')

        _log.debug('Setting font to {0}, size {1}'.format(
                self._font,
                self._font_size))

        self._if = ImageFont.truetype(
            self._font,
            self._font_size)

        #      (I am a wall socket!)Oo,  ___
        #                               '   `
        # Get the size, in pixels of the '.' character
        self._if_dims = self._if.getsize('.')
        #                               `---'

    def convert(self, text, destination):
        # TODO: Detect if text is a file-like, if so, act accordingly
        im = self._create_image(text)

        # PIL's Image.save will handle both file-likes and paths
        if im.save(destination):
            _log.debug('Saved image in {0}'.format(
                    destination))

    def _create_image(self, text):
        '''
        Write characters to a PIL image canvas.

        TODO:
        - Character set detection and decoding,
          http://pypi.python.org/pypi/chardet
        '''
        # TODO: Account for alternative line endings
        lines = text.split('\n')

        line_lengths = [len(i) for i in lines]

        # Calculate destination size based on text input and character size
        im_dims = (
            max(line_lengths) * self._if_dims[0],
            len(line_lengths) * self._if_dims[1])

        _log.debug('Destination image dimensions will be {0}'.format(
                im_dims))

        im = Image.new(
            'RGBA',
            im_dims,
            (255, 255, 255, 0))

        draw = ImageDraw.Draw(im)

        char_pos = [0, 0]

        for line in lines:
            line_length = len(line)

            _log.debug('Writing line at {0}'.format(char_pos))

            for _pos in range(0, line_length):
                char = line[_pos]

                px_pos = self._px_pos(char_pos)

                _log.debug('Writing character "{0}" at {1} (px pos {2}'.format(
                        char,
                        char_pos,
                        px_pos))

                draw.text(
                    px_pos,
                    char,
                    font=self._if,
                    fill=0)

                char_pos[0] += 1

            # Reset X position, increment Y position
            char_pos[0] = 0
            char_pos[1] += 1

        return im

    def _px_pos(self, char_pos):
        '''
        Helper function to calculate the pixel position based on
        character position and character dimensions
        '''
        px_pos = [0, 0]
        for index, val in zip(range(0, len(char_pos)), char_pos):
                px_pos[index] = char_pos[index] * self._if_dims[index]

        return px_pos


if __name__ == "__main__":
    import urllib
    txt = urllib.urlopen('file:///home/joar/Dropbox/ascii/install-all-the-dependencies.txt')

    _log.setLevel(logging.DEBUG)
    logging.basicConfig()

    converter = AsciiToImage()

    converter.convert(txt.read(), '/tmp/test.png')

    '''
    im, x, y, duration = renderImage(h, 10)
    print "Rendered image in %.5f seconds" % duration
    im.save('tldr.png', "PNG")
    '''
