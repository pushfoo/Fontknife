from PIL.BdfFontFile import BdfFontFile

from fontknife.formats.common import CachingReader


class BDFReader(CachingReader):
    format_name = 'bdf'
    wrapped_callable = BdfFontFile
