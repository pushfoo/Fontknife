from PIL.PcfFontFile import PcfFontFile

from octofont3.formats.common import CachingReader


class PCFReader(CachingReader):
    format_name = 'pcf'
    wrapped_callable = PcfFontFile
