import fcntl
import hashlib
import logging
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

LOG = logging.getLogger(__name__)

# ponytail: cache lives in raw-worker pod storage; mount shared storage only when deployment needs it.
DEFAULT_CACHE_DIR = '/var/cache/optscale/aws_reports'
DEFAULT_CACHE_TTL_DAYS = 2


class AWSReportCache:
    def __init__(self, cache_dir=None, cache_ttl_days=None):
        self.cache_dir = Path(cache_dir or os.environ.get(
            'AWS_REPORT_CACHE_DIR', DEFAULT_CACHE_DIR))
        self.cache_ttl_days = int(cache_ttl_days or os.environ.get(
            'AWS_REPORT_CACHE_TTL_DAYS', DEFAULT_CACHE_TTL_DAYS))
        self.reports_dir = self.cache_dir / 'reports'
        self.unpacked_dir = self.cache_dir / 'unpacked'
        self.locks_dir = self.cache_dir / 'locks'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.unpacked_dir.mkdir(parents=True, exist_ok=True)
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        self.cleanup()

    @staticmethod
    def _key(*parts):
        return hashlib.sha256('|'.join(parts).encode()).hexdigest()

    @contextmanager
    def _lock(self, key):
        with open(self.locks_dir / f'{key}.lock', 'w') as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            yield

    def get_or_download(self, bucket_name, object_key, etag, download):
        cache_key = self._key(bucket_name, object_key, etag)
        cached_path = self.reports_dir / cache_key
        with self._lock(cache_key):
            if cached_path.exists():
                LOG.info('CUR cache hit for %s (key: %s)', object_key, cache_key)
                cached_path.touch()
                return str(cached_path)
            LOG.info('CUR cache miss for %s, downloading to %s', object_key, cached_path)
            with tempfile.NamedTemporaryFile(
                    dir=self.reports_dir, delete=False) as destination:
                temporary_path = destination.name
                try:
                    download(destination)
                    os.replace(temporary_path, cached_path)
                    LOG.info('CUR successfully cached to %s', cached_path)
                except Exception:
                    os.unlink(temporary_path)
                    raise
        return str(cached_path)

    def get_or_unpack(self, cached_path, unpack):
        cached_path = Path(cached_path)
        unpacked_path = self.unpacked_dir / cached_path.name
        with self._lock(f'unpack-{cached_path.name}'):
            if unpacked_path.exists():
                LOG.info('CUR unpack cache hit for %s', cached_path.name)
                unpacked_path.touch()
                return str(unpacked_path)
            LOG.info('CUR unpack cache miss for %s, extracting', cached_path.name)
            with tempfile.TemporaryDirectory(dir=self.unpacked_dir) as directory:
                source_path = unpack(directory)
                if source_path is None:
                    raise ValueError(f'Could not unpack {cached_path}')
                os.replace(source_path, unpacked_path)
                LOG.info('CUR successfully unpacked to cache at %s', unpacked_path)
        return str(unpacked_path)

    @staticmethod
    def link(target_path, link_path):
        Path(link_path).parent.mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(target_path, link_path)
            LOG.debug('Linked cached CUR %s -> %s', target_path, link_path)
        except OSError as exc:
            LOG.warning('Symlink %s -> %s failed (%s), falling back to copy',
                        target_path, link_path, exc)
            shutil.copy2(target_path, link_path)

    def cleanup(self):
        cutoff = time.time() - self.cache_ttl_days * 86400
        cleaned = 0
        for directory, lock_prefix in (
                (self.reports_dir, ''), (self.unpacked_dir, 'unpack-')):
            for cached_path in directory.iterdir():
                try:
                    with self._lock(f'{lock_prefix}{cached_path.name}'):
                        if cached_path.stat().st_mtime < cutoff:
                            cached_path.unlink()
                            cleaned += 1
                except FileNotFoundError:
                    continue
        if cleaned:
            LOG.info('Cleaned %d expired file(s) from AWS CUR cache', cleaned)
