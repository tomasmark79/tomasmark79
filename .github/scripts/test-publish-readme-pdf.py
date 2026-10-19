"""Exercise the real publication script against a temporary bare Git remote."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PUBLISH = Path(__file__).with_name('publish-readme-pdf.sh')


class PublicationTest(unittest.TestCase):
    def test_concurrent_readme_update_is_rendered_again(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            remote, seed, worker, writer = [root/name for name in ['remote.git', 'seed', 'worker', 'writer']]
            env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                       GIT_AUTHOR_NAME='Test', GIT_AUTHOR_EMAIL='test@example.invalid',
                       GIT_COMMITTER_NAME='Test', GIT_COMMITTER_EMAIL='test@example.invalid')
            def run(*args, cwd=None):
                return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=True)
            run('git', 'init', '--bare', '--initial-branch=main', str(remote))
            run('git', 'init', '--initial-branch=main', str(seed))
            (seed/'.github/scripts').mkdir(parents=True)
            (seed/'cv').mkdir()
            (seed/'README.md').write_text('old source\n')
            (seed/'cv/README.pdf').write_text('old source\n')
            shutil.copyfile(PUBLISH, seed/'.github/scripts/publish-readme-pdf.sh')
            # Simulate an expensive render: a second clone changes README on
            # the remote after the first attempt has captured its input.
            (seed/'.github/scripts/readme-pdf.sh').write_text('''#!/usr/bin/env bash
set -euo pipefail
cat README.md > cv/README.pdf
if [ ! -e "$PDF_TEST_MARKER" ]; then
  touch "$PDF_TEST_MARKER"
  printf 'new source\\n' > "$PDF_TEST_WRITER/README.md"
  git -C "$PDF_TEST_WRITER" add README.md
  git -C "$PDF_TEST_WRITER" commit -m 'Concurrent source update'
  git -C "$PDF_TEST_WRITER" push origin main
  printf 'stale rendered PDF\\n' >> cv/README.pdf
fi
''')
            run('git', 'add', '.', cwd=seed)
            run('git', 'commit', '-m', 'Initial fixture', cwd=seed)
            run('git', 'remote', 'add', 'origin', str(remote), cwd=seed)
            run('git', 'push', '-u', 'origin', 'main', cwd=seed)
            run('git', 'clone', str(remote), str(worker))
            run('git', 'clone', str(remote), str(writer))
            env.update(PDF_TEST_MARKER=str(root/'first-render'), PDF_TEST_WRITER=str(writer))
            result = run('bash', '.github/scripts/publish-readme-pdf.sh', cwd=worker)
            self.assertIn('[rejected]', result.stderr)
            self.assertIn('retrying with current sources', result.stdout)
            self.assertEqual(run('git', '--git-dir='+str(remote), 'show', 'main:cv/README.pdf').stdout, 'new source\n')
            self.assertEqual(run('git', '--git-dir='+str(remote), 'show', 'main:README.md').stdout, 'new source\n')
            # A subsequent identical render must not create an empty commit.
            before = run('git', '--git-dir='+str(remote), 'rev-parse', 'main').stdout
            run('bash', '.github/scripts/publish-readme-pdf.sh', cwd=worker)
            self.assertEqual(before, run('git', '--git-dir='+str(remote), 'rev-parse', 'main').stdout)


if __name__ == '__main__':
    unittest.main()
