import csv
import hashlib
import tempfile
from collections import UserDict
from dataclasses import dataclass, astuple, field
from pathlib import Path
from typing import Callable, Dict, Optional, Union, BinaryIO, Set, Any

from PIL import ImageFont

from octofont3.custom_types import PathLike
from octofont3.utils import ensure_folder_exists


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


@dataclass
class MetadataCacheEntry:
    modified_time_nanoseconds: int
    file_hash: str
    glyph_membership: Optional[frozenset] = field(default=None)

    @classmethod
    def generate_for_file(cls, source_file_path: Path):
        modified_time_ns = source_file_path.stat().st_mtime_ns
        file_hash = hash_file(source_file_path).hexdigest()
        return cls(modified_time_ns, file_hash)

    @classmethod
    def from_string_format(cls, *args):
        modified_time_ns = int(args[0])
        file_hash = args[1]
        glyph_membership = deserialize_optional(args[2])

        return cls(modified_time_ns, file_hash, glyph_membership)


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

    def __setitem__(self, key: PathLike, value: MetadataCacheEntry):
        key_path = Path(key)
        if key_path not in self or self[key_path] != value:
            super().__setitem__(key, value)
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
                reader = csv.reader(csvfile)

                for raw_path, *raw_data in reader:
                    path = Path(raw_path)
                    cache_entry_data = MetadataCacheEntry.from_string_format(*raw_data)
                    raw_cache[path] = cache_entry_data

        return cls(
            cache_folder=cache_folder,
            cache_metadata_file_path=cache_metadata_file_path,
            initialdata=raw_cache
        )

    def save_to_disk(self, force_write: bool = False) -> None:
        if not (force_write or self._has_changes_unwritten):
            print("skipping write, neither forced nor dirty")
            return

        print("writing cache to disk...")

        # sort by last modified time
        data_rows = [(key, data) for key, data in self.items()]
        data_rows.sort(key=lambda t: t[1].modified_time_nanoseconds)

        with open(self.cache_metadata_file_path, "w") as csvfile:
            writer = csv.writer(csvfile)
            for path, data_elements in self.items():
                writer.writerow((str(path), *map(str, astuple(data_elements))))

    def __del__(self):
        self.save_to_disk()

default_cache: Optional[FileMetadataCache] = None


def get_cache(cache_directory: Optional[PathLike] = None) -> FileMetadataCache:
    creating_temp_cache = cache_directory is None

    if creating_temp_cache:
        temp_dir = Path(tempfile.gettempdir())
        cache_directory = temp_dir / 'octofont3'

    ensure_folder_exists(cache_directory)
    cache = FileMetadataCache.load_from_disk(cache_directory)
    return cache


default_cache = get_cache()


def load_and_cache_bitmap_font(
    source_path: PathLike,
    raw_loader: Callable,
    cache: Optional[FileMetadataCache] = None
) -> ImageFont:

    source_path = Path(source_path).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Couldn't find {source_path}")

    elif not source_path.is_file():
        raise FileNotFoundError(f"{source_path} is not a file")

    metadata = MetadataCacheEntry.generate_for_file(source_path)

    pil_font_cache_dir = cache.cache_folder_path
    pil_font_cache_path = pil_font_cache_dir / metadata.file_hash

    file_base_name = metadata.file_hash

    if source_path not in cache or metadata != cache[source_path]:
        print("updating cache...")
        raw_font = raw_loader(source_path)

        # todo: fix this naming scheme, just hashes is hard to use
        # todo: check if pillow caches fonts anywhere...
        raw_font.save(pil_font_cache_dir / file_base_name)

        cache[source_path] = metadata

    pil_font = ImageFont.load(f"{pil_font_cache_path}.pil")
    return pil_font
