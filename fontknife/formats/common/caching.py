import base64
import csv
import hashlib
import json
import tempfile
from collections import UserDict
from dataclasses import dataclass, astuple, field
from pathlib import Path
from typing import Callable, Dict, Optional, Union, BinaryIO, Set, Any, Tuple

from PIL import ImageFont

from fontknife.custom_types import PathLike, HasReadline, HasRead, PathLikeOrHasRead
from fontknife.iohelpers import ensure_folder_exists, load_binary_source, get_resource_filesystem_path, absolute_path


def hash_binary_stream(source: BinaryIO, hash_algo: Callable = hashlib.sha1, block_size: int = 2 ** 16):
    hash_instance = hash_algo()
    buffer = bytearray(block_size)
    buffer_view = memoryview(buffer)

    # This should be replaced with the := operator once 3.7 is EOL
    running = True
    while running:
        num_bytes_read = source.readinto(buffer_view)
        if not num_bytes_read:
            running = False
            break
        hash_instance.update(buffer_view[:num_bytes_read])

    return hash_instance


def hash_file(
        source: Union[PathLike, BinaryIO],
        hash_algo: Callable = hashlib.sha1,
        block_size: int = 2 ** 16
):
    """
    Naive overall file-content based hashing

    :param source: A stream or path to read data from.
    :hash_algo: An object that behaves like a hash algorithm from hashlib
    :param block_size: The maximum size of reads.
    :return: the hash object
    """


    if hasattr(source, 'readinto'):
        hash = hash_binary_stream(source)
    else:
        with open(source, "rb", buffering=0) as file:
            hash = hash_binary_stream(file)

    return hash


def deserialize_optional(raw: str, converter: Optional[Callable] = None) -> Any:
    if raw == 'None':
        return None
    elif converter is not None:
        return converter(raw)
    return raw


def glyph_sequence_to_string(raw: Tuple[str, ...]) -> str:
    json_encode = json.dumps(raw)
    bytes_encode = json_encode.encode('utf-8')
    b64 = base64.b64encode(bytes_encode)
    out = b64.decode('ascii')
    return out


def glyph_sequence_from_string(raw: str) -> Tuple[str, ...]:
    raw_bytes = raw.encode('ascii')
    utf8_bytes = base64.b64decode(raw_bytes)
    json_string = utf8_bytes.decode('utf-8')
    sequence_list = json.loads(json_string)
    return tuple(sequence_list)


@dataclass
class MetadataCacheEntry:
    """
    Metadata for a specific font file.

    This makes an assumption that the hash won't collide. It is
    theoretically possible for the hash and modification time of
    two fonts to be the same despite containing different data.
    """
    modified_time_nanoseconds: int = field(hash=True)
    file_hash: str = field(hash=True)
    provided_glyphs: Tuple[str, ...] = field(hash=False, compare=False, default_factory=tuple)

    @classmethod
    def generate_for_source(cls, source: PathLikeOrHasRead):
        source_file_path = Path(get_resource_filesystem_path(source))
        modified_time_ns = source_file_path.stat().st_mtime_ns
        file_hash = hash_file(source_file_path).hexdigest()

        return cls(modified_time_ns, file_hash)

    @classmethod
    def from_string_tuple(cls, *args):
        modified_time_ns = int(args[0])
        file_hash = args[1]
        glyph_membership = glyph_sequence_from_string(args[2])

        return cls(modified_time_ns, file_hash, glyph_membership)

    def to_string_tuple(self) -> Tuple[str, ...]:
        return (
            str(self.modified_time_nanoseconds),
            str(self.file_hash),
            glyph_sequence_to_string(self.provided_glyphs)
        )

    def detect_provided_glyphs(
        self,
        pilfont_metadata_file: Path,
        value_length_byes: int = 2,
        num_values_per_glyph: int = 10
    ):
        """
        Return the glyphs present in a cached pil font.

        This is a very nasty workaround for PIL's lack of support for
        access to font metadata.

        Must be called *after* the font is actually cached.

        :param pilfont_metadata_file: The file holding PIL metadata
        :param value_length_byes: the length of each metrics table value in bytes
        :param num_values_per_glyph: how many values there are per glyph metrics table group
        :return:
        """
        with open(pilfont_metadata_file, "rb") as fp:
            glyph_length_bytes = value_length_byes * num_values_per_glyph

            # Skip header lines to get to the metrics data
            while line := fp.readline():
                if line == b"DATA\n":
                    break

            # Read the metrics block
            all_metrics = fp.read(256 * glyph_length_bytes)

        included_glyphs = []

        # Append every glyph character that is presented by the font
        for glyph_index in range(256):

            # Extract the metrics block for the current glyph index
            glyph_start = glyph_index * glyph_length_bytes
            glyph_end = glyph_start + glyph_length_bytes
            glyph_metrics = all_metrics[glyph_start:glyph_end]

            # Only glyphs provided by the font have non-zero metrics blocks
            if any(glyph_metrics):
                included_glyphs.append(chr(glyph_index))

        self.provided_glyphs = tuple(included_glyphs)


class FileMetadataCache(UserDict):
    """
    Keeps track of source files and which have already been processed.

    It uses source path, modification time, and file content hash.
    """

    def __init__(
        self,
        cache_folder: PathLike = None,
        initialdata: Dict[Path, MetadataCacheEntry] = None,
        cache_metadata_file_path: Optional[PathLike] = None,
        has_changes_unwritten: bool = False
    ):
        super().__init__({} if initialdata is None else initialdata)
        self._has_changes_unwritten = has_changes_unwritten

        # generate config folder paths without doing
        # anything with them until write time.

        self.cache_folder_path = cache_folder
        self.cache_metadata_file_path = cache_metadata_file_path or self.cache_folder_path / "cache_metadata"

    @property
    def has_changes_unwritten(self) -> bool:
        return  self._has_changes_unwritten

    def __contains__(self, item: PathLike):
        return super().__contains__(Path(item))

    def __getitem__(self, item: PathLike):
        return super().__getitem__(Path(item))

    def __setitem__(self, key: PathLike, value: MetadataCacheEntry):
        key_path = Path(key)
        if key_path not in self or self[key_path] != value:
            super().__setitem__(key_path, value)
            self._has_changes_unwritten = True

    @classmethod
    def load_from_disk(
        cls,
        cache_folder: PathLike,
        cache_metadata_filename: str = "cache_metadata"
    ) -> "FileMetadataCache":

        cache_folder = Path(cache_folder)
        cache_metadata_file_path = cache_folder / cache_metadata_filename
        raw_cache = dict()

        if cache_metadata_file_path.is_file():
            with open(cache_metadata_file_path, "r") as csvfile:
                reader = csv.reader(csvfile, dialect=csv.excel_tab)

                for raw_path, *raw_data in reader:
                    path = Path(raw_path)
                    cache_entry_data = MetadataCacheEntry.from_string_tuple(*raw_data)
                    raw_cache[path] = cache_entry_data

        return cls(
            cache_folder=cache_folder,
            cache_metadata_file_path=cache_metadata_file_path,
            initialdata=raw_cache
        )

    def save_to_disk(self, force_write: bool = False) -> None:
        if not (force_write or self._has_changes_unwritten):
            # print("skipping write, neither forced nor dirty")
            return

        # print("writing cache to disk...")

        # sort by last modified time
        data_rows = [(key, data) for key, data in self.items()]
        data_rows.sort(key=lambda t: t[1].modified_time_nanoseconds)

        with open(self.cache_metadata_file_path, "w") as csvfile:
            writer = csv.writer(csvfile, dialect=csv.excel_tab)
            # print(list(self.data.items()))
            # print(list(self.items()))
            for path, data_elements in self.items():
                # print(path, data_elements)
                writer.writerow((str(path), *data_elements.to_string_tuple()))

    def __del__(self):
        self.save_to_disk()


default_cache: Optional[FileMetadataCache] = None


def get_cache(cache_directory: Optional[PathLike] = None) -> FileMetadataCache[Path, MetadataCacheEntry]:
    creating_temp_cache = cache_directory is None

    if creating_temp_cache:
        temp_dir = Path(tempfile.gettempdir())
        cache_directory = temp_dir / 'fontknife'

    ensure_folder_exists(cache_directory)
    cache = FileMetadataCache.load_from_disk(cache_directory)
    return cache


default_cache = get_cache()


def load_and_cache_bitmap_font(
    source: PathLikeOrHasRead[bytes],
    raw_loader: Callable,
    cache: Optional[FileMetadataCache] = None
) -> ImageFont:

    current_metadata = MetadataCacheEntry.generate_for_source(source)
    if isinstance(source, (HasReadline, HasRead)):
        source_path = get_resource_filesystem_path(source)
    else:
        source_path = absolute_path(source)

    pil_font_cache_dir = cache.cache_folder_path
    pil_cached_font_base_name = pil_font_cache_dir / current_metadata.file_hash
    pil_cached_font_metadata_name = pil_cached_font_base_name.with_suffix('.pil')

    if source_path not in cache or current_metadata != cache[source_path]:
        # print("updating cache...")
        raw_font = load_binary_source(source, raw_loader)

        # todo: fix this naming scheme, just hashes is hard to use
        # todo: check if pillow caches fonts anywhere...
        raw_font.save(pil_cached_font_base_name)
        current_metadata.detect_provided_glyphs(pil_cached_font_metadata_name)
        cache[source_path] = current_metadata

    pil_font = ImageFont.load(str(pil_cached_font_metadata_name))
    return pil_font
