"""Defensive helpers for reading untrusted source archives."""
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

from backend.config import MAX_COMPRESSION_RATIO, MAX_UNCOMPRESSED_BYTES


class SourceFileError(Exception):
    """Raised when a raw source file is missing, malformed or unsafe to read."""


def check_member_name(name):
    p = PurePosixPath(name.replace('\\', '/'))
    if p.is_absolute() or '..' in p.parts or ':' in name:
        raise SourceFileError(f'Unsafe path inside archive: {name!r}')


def open_zip_member(path, suffix='.xml', expected_name=None):
    """Open one member of a ZIP for streaming after validating the archive.

    Rejects unsafe member paths, oversized or suspiciously compressed content (zip bombs),
    and archives without exactly one matching member (unless expected_name picks one).
    Members are streamed; nothing is extracted to disk.
    """
    try:
        archive = ZipFile(path)
    except BadZipFile as exc:
        raise SourceFileError(f'Not a valid ZIP archive: {path.name}') from exc
    infos = archive.infolist()
    for info in infos:
        check_member_name(info.filename)
    total = sum(i.file_size for i in infos)
    if total > MAX_UNCOMPRESSED_BYTES:
        archive.close()
        raise SourceFileError(f'Archive expands to {total:,} bytes, above the {MAX_UNCOMPRESSED_BYTES:,} byte limit')
    candidates = [i for i in infos if i.filename.lower().endswith(suffix) and not i.is_dir()]
    if expected_name:
        candidates = [i for i in candidates if i.filename == expected_name]
    if len(candidates) != 1:
        archive.close()
        names = [i.filename for i in candidates]
        raise SourceFileError(f'Expected exactly one {suffix} member in {path.name}, found {len(candidates)}: {names}')
    info = candidates[0]
    if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
        archive.close()
        raise SourceFileError(f'Compression ratio of {info.filename} is suspiciously high')
    return archive, archive.open(info)
