from PIL.BdfFontFile import BdfFontFile

from octofont3.formats.common import CachingReader


class BDFReader(CachingReader):
    format_name = 'bdf'
    wrapped_creation_func = BdfFontFile
