from pathlib import Path
from textwrap import dedent
from typing import List

from pytest import fixture

from nikola import Nikola


@fixture
def basic_compile_test(tmp_site_path):
    def f(ext: str, data: str, extra_plugins_dirs: List[Path] = None, metadata: str = None) -> CompileResult:
        data = dedent(data)
        (tmp_site_path / 'pages' / 'test').with_suffix(ext).write_text(data, encoding='utf8')

        metadata = metadata or '.. title: test'
        (tmp_site_path / 'pages' / 'test').with_suffix('.meta').write_text(metadata, encoding='utf8')

        config = {
            'EXTRA_PLUGINS_DIRS': map(str, extra_plugins_dirs or []),
            'PAGES': (
                ('pages/*' + ext, 'pages', 'page.tmpl'),
            ),
        }

        site = Nikola(**config)
        site.init_plugins()
        site.scan_posts()

        site.timeline[0].compile('en')

        return CompileResult(tmp_site_path / 'cache' / 'pages' / 'test.html')

    return f


class CompileResult:
    def __init__(self, path: Path):
        dep_file = path.with_suffix(path.suffix + '.dep')
        self.deps = set(dep_file.read_text(encoding='utf8').split()) if dep_file.exists() else set()
        self.raw_html = path.read_text(encoding='utf8')


@fixture
def tmp_site_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'pages').mkdir()
    return tmp_path