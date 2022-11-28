from PIL.PcfFontFile import PcfFontFile

from fontknife.formats.common import CachingReader


class PCFReader(CachingReader):
    format_name = 'pcf'
    wrapped_callable = PcfFontFile
