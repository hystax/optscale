import gzip
import os
import tempfile
import threading
import time
import unittest
from diworker.diworker.cache.aws_report_cache import (
    AWSReportCache,
    DEFAULT_CACHE_TTL_DAYS,
)


class AWSReportCacheTests(unittest.TestCase):
    def test_reuses_cached_report_and_links_each_importer(self):
        with tempfile.TemporaryDirectory() as directory:
            first_cache = AWSReportCache(directory)
            second_cache = AWSReportCache(directory)
            downloads = []

            def download(destination):
                downloads.append(destination.name)
                destination.write(b'report')

            report = ('bucket', 'path/report.csv.gz', 'etag')
            cached_path = first_cache.get_or_download(*report, download)
            second_path = second_cache.get_or_download(*report, download)
            first_link = os.path.join(directory, 'first')
            second_link = os.path.join(directory, 'second')

            first_cache.link(cached_path, first_link)
            second_cache.link(cached_path, second_link)

            self.assertEqual(cached_path, second_path)
            self.assertEqual(1, len(downloads))
            self.assertTrue(os.path.islink(first_link))
            self.assertTrue(os.path.islink(second_link))
            with open(second_link, 'rb') as cached_report:
                self.assertEqual(b'report', cached_report.read())

    def test_key_deterministic_and_unique(self):
        self.assertEqual(
            AWSReportCache._key('b', 'k', 'e'),
            AWSReportCache._key('b', 'k', 'e'))
        self.assertNotEqual(
            AWSReportCache._key('b', 'k', 'e1'),
            AWSReportCache._key('b', 'k', 'e2'))
        self.assertNotEqual(
            AWSReportCache._key('b1', 'k', 'e'),
            AWSReportCache._key('b2', 'k', 'e'))
        key = AWSReportCache._key('b', 'path/r.csv.gz', 'e')
        self.assertEqual(len(key), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in key))

    def test_subdirectories_created_on_init(self):
        with tempfile.TemporaryDirectory() as d:
            AWSReportCache(d)
            for sub in ('reports', 'unpacked', 'locks'):
                self.assertTrue(os.path.isdir(os.path.join(d, sub)))

    def test_reinit_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            p = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))
            AWSReportCache(d)
            self.assertTrue(os.path.exists(p))

    def test_ttl_defaults_and_overrides(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(
                AWSReportCache(d).cache_ttl_days, DEFAULT_CACHE_TTL_DAYS)
            self.assertEqual(
                AWSReportCache(d, cache_ttl_days=7).cache_ttl_days, 7)

            os.environ['AWS_REPORT_CACHE_TTL_DAYS'] = '10'
            try:
                self.assertEqual(AWSReportCache(d).cache_ttl_days, 10)
            finally:
                del os.environ['AWS_REPORT_CACHE_TTL_DAYS']

    def test_different_etag_redownloads(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            n = []

            def dl(f):
                n.append(1)
                f.write(b'x')

            c.get_or_download('b', 'k', 'e1', dl)
            c.get_or_download('b', 'k', 'e2', dl)
            self.assertEqual(len(n), 2)

    def test_failed_download_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)

            def bad(f):
                f.write(b'partial')
                raise IOError('network error')

            with self.assertRaises(IOError):
                c.get_or_download('b', 'k', 'e', bad)
            self.assertEqual(len(list(c.reports_dir.iterdir())), 0)

    def test_download_mtime_refreshed_on_hit(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            p = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))
            os.utime(p, (0, 0))
            c.get_or_download('b', 'k', 'e', lambda f: None)
            self.assertGreater(os.path.getmtime(p), 0)

    def test_link_falls_back_to_copy_on_symlink_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = AWSReportCache(directory)
            source = os.path.join(directory, 'source')
            with open(source, 'wb') as f:
                f.write(b'content')
            destination = os.path.join(directory, 'copied')

            original_symlink = os.symlink
            try:
                def fail_symlink(src, dst):
                    raise OSError("Operation not supported")
                os.symlink = fail_symlink
                cache.link(source, destination)
            finally:
                os.symlink = original_symlink

            self.assertFalse(os.path.islink(destination))
            self.assertTrue(os.path.exists(destination))
            with open(destination, 'rb') as f:
                self.assertEqual(b'content', f.read())

    def test_link_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            src = os.path.join(d, 'src')
            with open(src, 'wb') as f:
                f.write(b'x')
            lnk = os.path.join(d, 'nested', 'deep', 'lnk')
            c.link(src, lnk)
            self.assertTrue(os.path.exists(lnk))

    def test_serializes_concurrent_downloads_for_same_report(self):
        with tempfile.TemporaryDirectory() as directory:
            caches = [AWSReportCache(directory), AWSReportCache(directory)]
            barrier = threading.Barrier(2)
            downloads = []
            results = []

            def download(destination):
                downloads.append(destination.name)
                destination.write(b'report')

            def load(cache):
                barrier.wait()
                results.append(cache.get_or_download(
                    'bucket', 'path/report.csv.gz', 'etag', download))

            workers = [threading.Thread(target=load, args=(cache,))
                       for cache in caches]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()

            self.assertEqual(1, len(downloads))
            self.assertEqual(2, len(results))
            self.assertEqual(results[0], results[1])

    def test_serializes_concurrent_unpacks(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            cached = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))
            barrier = threading.Barrier(2)
            n, res = [], []

            def unp(directory):
                n.append(1)
                out = os.path.join(directory, 'r.csv')
                with open(out, 'wb') as f:
                    f.write(b'u')
                return out

            def w():
                barrier.wait()
                res.append(c.get_or_unpack(cached, unp))

            ts = [threading.Thread(target=w) for _ in range(2)]
            for t in ts:
                t.start()
            for t in ts:
                t.join(10)
            self.assertEqual(len(n), 1)
            self.assertEqual(res[0], res[1])

    def test_cleanup_waits_for_active_cache_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = AWSReportCache(directory, cache_ttl_days=1)
            cached_path = cache.get_or_download(
                'bucket', 'path/report.csv.gz', 'etag',
                lambda destination: destination.write(b'report'))
            os.utime(cached_path, (0, 0))
            cleanup_done = threading.Event()
            worker = threading.Thread(
                target=lambda: (cache.cleanup(), cleanup_done.set()))

            with cache._lock(os.path.basename(cached_path)):
                worker.start()
                self.assertFalse(cleanup_done.wait(0.5))
                os.utime(cached_path, None)

            worker.join(5)
            self.assertTrue(os.path.exists(cached_path))

    def test_cleanup_removes_expired_files(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d, cache_ttl_days=1)
            p = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))
            os.utime(p, (0, 0))
            c.cleanup()
            self.assertFalse(os.path.exists(p))

    def test_cleanup_keeps_fresh_files(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d, cache_ttl_days=1)
            p = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))
            c.cleanup()
            self.assertTrue(os.path.exists(p))

    def test_cleanup_removes_expired_unpacked(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d, cache_ttl_days=1)
            cached = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))

            def unp(directory):
                out = os.path.join(directory, 'r.csv')
                with open(out, 'wb') as f:
                    f.write(b'u')
                return out

            up = c.get_or_unpack(cached, unp)
            os.utime(up, (0, 0))
            c.cleanup()
            self.assertFalse(os.path.exists(up))

    def test_reuses_cached_unpacked_report(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = AWSReportCache(directory)
            cached_path = cache.get_or_download(
                'bucket', 'path/report.csv.gz', 'etag',
                lambda destination: destination.write(b'compressed'))
            unpacks = []

            def unpack(destination):
                unpacks.append(destination)
                unpacked_path = os.path.join(destination, 'report.csv')
                with open(unpacked_path, 'wb') as report:
                    report.write(b'unpacked')
                return unpacked_path

            first_path = cache.get_or_unpack(cached_path, unpack)
            second_path = cache.get_or_unpack(cached_path, unpack)

            self.assertEqual(first_path, second_path)
            self.assertEqual(1, len(unpacks))
            with open(second_path, 'rb') as report:
                self.assertEqual(b'unpacked', report.read())

    def test_unpack_none_return_raises_value_error(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            cached = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))
            with self.assertRaises(ValueError):
                c.get_or_unpack(cached, lambda directory: None)
            self.assertEqual(len(list(c.unpacked_dir.iterdir())), 0)

    def test_unpack_exception_propagates_and_cleans(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            cached = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))

            def bad(directory):
                raise RuntimeError('decompression error')

            with self.assertRaises(RuntimeError):
                c.get_or_unpack(cached, bad)

    def test_unpack_mtime_refreshed_on_hit(self):
        with tempfile.TemporaryDirectory() as d:
            c = AWSReportCache(d)
            cached = c.get_or_download('b', 'k', 'e', lambda f: f.write(b'x'))
            n = []

            def unp(directory):
                n.append(1)
                out = os.path.join(directory, 'r.csv')
                with open(out, 'wb') as f:
                    f.write(b'u')
                return out

            p = c.get_or_unpack(cached, unp)
            os.utime(p, (0, 0))
            c.get_or_unpack(cached, unp)
            self.assertGreater(os.path.getmtime(p), 0)

    def test_end_to_end_shared_cur_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            cache = AWSReportCache(d)
            raw_payload = gzip.compress(b'csv-row-1,csv-row-2')
            dl_calls = []

            def dl(f):
                dl_calls.append(1)
                f.write(raw_payload)

            p1 = cache.get_or_download('bucket', 'r.csv.gz', 'etag', dl)
            p2 = cache.get_or_download('bucket', 'r.csv.gz', 'etag', dl)
            self.assertEqual(p1, p2)
            self.assertEqual(len(dl_calls), 1)

            unpack_calls = []

            def unp(directory):
                unpack_calls.append(1)
                out = os.path.join(directory, 'r.csv')
                with gzip.open(p1, 'rb') as gz:
                    with open(out, 'wb') as f:
                        f.write(gz.read())
                return out

            u1 = cache.get_or_unpack(p1, unp)
            u2 = cache.get_or_unpack(p1, unp)
            self.assertEqual(u1, u2)
            self.assertEqual(len(unpack_calls), 1)

            ws1 = os.path.join(d, 'datasource_1', 'r.csv')
            ws2 = os.path.join(d, 'datasource_2', 'r.csv')
            cache.link(u1, ws1)
            cache.link(u2, ws2)

            for ws in (ws1, ws2):
                with open(ws, 'rb') as f:
                    self.assertEqual(f.read(), b'csv-row-1,csv-row-2')

            os.remove(ws1)
            os.remove(ws2)
            self.assertTrue(os.path.exists(u1))
            self.assertTrue(os.path.exists(p1))


if __name__ == '__main__':
    unittest.main()
