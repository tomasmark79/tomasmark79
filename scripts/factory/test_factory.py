"""Check external API boundaries, quiet periods and generated delivery safety."""
from datetime import date
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fetch_activity', HERE / 'fetch_activity.py')
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)
NS = {'s': 'http://www.w3.org/2000/svg'}


def repo(name, private=False, owner='demo'):
    return {'name': name, 'full_name': f'{owner}/{name}', 'private': private,
            'owner': {'login': owner}}


def item(name, sha, **kw):
    return {'repository': repo(name, **kw), 'sha': sha, 'author': {'type': 'User'}}


def result(items, total=None, incomplete=False):
    return {'items': items, 'total_count': len(items) if total is None else total,
            'incomplete_results': incomplete}


class ActivityTests(unittest.TestCase):
    def test_paginated_public_only_and_deterministic_ties(self):
        rows = [item('zeta', str(i)) for i in range(50)]
        rows += [item('alpha', str(i)) for i in range(50)]
        rows += [item('secret', 'x', private=True), item('foreign', 'x', owner='other')]
        def api(endpoint):
            if endpoint.startswith('users/'):
                return [repo('quiet')]
            query = parse_qs(urlparse(endpoint).query)
            self.assertIn('is:public', query['q'][0])
            page = int(query['page'][0])
            return result(rows[(page-1)*100:page*100], total=102)
        data = fetch.collect('demo', date(2026, 10, 19), api)
        self.assertEqual(data['total_commits'], 100)
        self.assertEqual(data['repositories'], [
            {'name': 'alpha', 'commits': 50}, {'name': 'zeta', 'commits': 50},
            {'name': 'quiet', 'commits': 0}])
        self.assertEqual(data['start'], '2026-09-20')

    def test_zero_is_valid_and_keeps_public_stations(self):
        def api(endpoint):
            return [repo('quiet'), repo('secret', private=True)] if endpoint.startswith('users/') else result([])
        data = fetch.collect('demo', date(2027, 1, 1), api)
        self.assertEqual(data['start'], '2026-12-03')
        self.assertEqual(data['repositories'], [{'name': 'quiet', 'commits': 0}])
        self.assertEqual(data['total_commits'], 0)

    def test_incomplete_results_fail_instead_of_returning_zero(self):
        with self.assertRaisesRegex(RuntimeError, 'incomplete'):
            fetch.collect('demo', date(2026, 10, 19), lambda _: result([], incomplete=True))

    def test_search_limit_splits_dates_without_double_counting(self):
        def api(endpoint):
            if endpoint.startswith('users/'):
                return []
            query = parse_qs(urlparse(endpoint).query)['q'][0]
            if '2026-09-20..2026-10-19' in query:
                return result([], total=1001)
            if '2026-09-20..2026-10-04' in query:
                return result([item('first', 'a')])
            self.assertIn('2026-10-05..2026-10-19', query)
            return result([item('second', 'b')])
        self.assertEqual(fetch.collect('demo', date(2026, 10, 19), api)['total_commits'], 2)

    def test_duplicate_pages_fail(self):
        with self.assertRaisesRegex(RuntimeError, 'duplicated'):
            fetch.collect('demo', date(2026, 10, 19), lambda _: result([item('r', 'same')]*2))

    def test_api_error_propagates(self):
        def api(_):
            raise RuntimeError('API unavailable')
        with self.assertRaisesRegex(RuntimeError, 'API unavailable'):
            fetch.collect('demo', date(2026, 10, 19), api)

    def test_failed_refresh_preserves_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'activity.json'
            output.write_text('previous successful snapshot')
            with patch.object(sys, 'argv', ['fetch_activity.py', '--output', str(output)]), \
                    patch.object(fetch, 'collect', side_effect=RuntimeError('API unavailable')):
                with self.assertRaisesRegex(RuntimeError, 'API unavailable'):
                    fetch.main()
            self.assertEqual(output.read_text(), 'previous successful snapshot')


class RenderTests(unittest.TestCase):
    def render(self, rows):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        data = {'schema_version': 1, 'owner': 'demo', 'start': '2026-12-03',
                'end': '2027-01-01', 'repositories': rows}
        (folder / 'activity.json').write_text(json.dumps(data))
        subprocess.run([sys.executable, str(HERE/'generate.py'), '--data',
                        str(folder/'activity.json'), '--output', str(folder)],
                       check=True, capture_output=True, text=True)
        svg = (folder/'workshop.svg').read_text()
        for filename in ['workshop.svg', 'workshop-dark.svg', 'workshop-light.svg']:
            ET.parse(folder/filename)
        return svg, ET.fromstring(svg), folder

    def test_empty_window_sleeps_without_fake_packages(self):
        for rows in [[], [{'name': 'quiet', 'commits': 0}]]:
            with self.subTest(rows=rows):
                svg, root, _ = self.render(rows)
                self.assertIn('Public project stations and the assembler are idle.', svg)
                self.assertIn('workshop idle', svg)
                self.assertIn('*{animation:none!important}', svg)
                self.assertEqual(root.findall('.//s:animateMotion', NS), [])
                self.assertEqual(root.findall('.//s:g[@class="arrival-flash"]', NS), [])
                self.assertNotIn('working<tspan', svg)

    def test_one_active_project_and_no_activity_in_other_stations(self):
        svg, root, _ = self.render([{'name': 'active', 'commits': 1}, {'name': 'quiet', 'commits': 0}])
        self.assertEqual(len(root.findall('.//s:animateMotion', NS)), 18)
        self.assertIn('>1 commits</text>', svg)

    def test_arrival_flash_matches_delivery_time_and_project_color(self):
        _, root, _ = self.render([{'name': 'first', 'commits': 3}, {'name': 'second', 'commits': 2}])
        deliveries = {}
        for parcel in root.findall('.//s:g[@class="moving"]', NS):
            motion = parcel.find('.//s:animateMotion', NS)
            period = float(motion.get('dur').removesuffix('s'))
            travel = period * float(motion.get('keyTimes').split(';')[1])
            arrival = (float(motion.get('begin').removesuffix('s')) + travel) % period
            deliveries[round(arrival) % 18] = parcel.get('color')
        flashes = {}
        for flash in root.findall('.//s:g[@class="arrival-flash"]', NS):
            animation = flash.find('s:animate', NS)
            period = float(animation.get('dur').removesuffix('s'))
            arrival = float(animation.get('begin').removesuffix('s')) % period
            flashes[arrival] = flash.get('fill')
        self.assertEqual(len(flashes), 18)
        self.assertEqual(flashes, deliveries)

    def test_shared_belt_arrivals_have_fixed_spacing(self):
        rows = [{'name': f'repo-{i}', 'commits': n} for i, n in enumerate([26,20,19,17,16])]
        svg, root, folder = self.render(rows)
        arrivals = []
        for motion in root.findall('.//s:animateMotion', NS):
            period = float(motion.attrib['dur'].removesuffix('s'))
            travel = period * float(motion.attrib['keyTimes'].split(';')[1])
            begin = float(motion.attrib['begin'].removesuffix('s'))
            arrivals.append((begin + travel) % period)
        arrivals.sort()
        gaps = [(arrivals[(i+1)%18] - arrivals[i]) % 18 for i in range(18)]
        for gap in gaps:
            self.assertAlmostEqual(gap, 1, places=6)
        self.assertIn('2026-12-03 through 2027-01-01', svg)
        self.assertNotIn('@media(prefers-color-scheme:dark)', (folder/'workshop-light.svg').read_text())
        self.assertNotIn('@media(prefers-color-scheme:dark)', (folder/'workshop-dark.svg').read_text())


if __name__ == '__main__':
    unittest.main()
