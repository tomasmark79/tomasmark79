#!/usr/bin/env python3
"""Collect public, owned repository activity; publish no partial snapshots."""
import argparse
from collections import Counter
from datetime import date, datetime, timedelta
import json
import math
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlencode
from zoneinfo import ZoneInfo


def github_api(endpoint):
    """Use gh's local authentication or GH_TOKEN in Actions, without logging it."""
    for attempt in range(3):
        result = subprocess.run(
            ['gh', 'api', '-H', 'Accept: application/vnd.github+json', endpoint],
            text=True, capture_output=True, check=False,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        if attempt < 2:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f'GitHub API request failed: {result.stderr.strip()}')


def collect(owner, end, api=github_api):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', owner):
        raise ValueError('Invalid GitHub owner')
    start = end - timedelta(days=29)
    # Key by repository and SHA: a commit can legitimately exist in two repos.
    commits = {}

    def search(first, last):
        query = f'author:{owner} user:{owner} is:public author-date:{first}..{last}'
        def page(number):
            data = api('search/commits?' + urlencode({
                'q': query, 'per_page': 100, 'page': number,
                'sort': 'author-date', 'order': 'asc',
            }))
            if data['incomplete_results']:
                raise RuntimeError('GitHub returned incomplete commit search results')
            return data
        data = page(1)
        total = data['total_count']
        if total > 1000:
            if first == last:
                raise RuntimeError('More than 1000 commits in one day; refusing truncated data')
            middle = first + (last - first) // 2
            search(first, middle)
            search(middle + timedelta(days=1), last)
            return
        items = list(data['items'])
        for number in range(2, math.ceil(total / 100) + 1):
            data = page(number)
            if data['total_count'] != total:
                raise RuntimeError('Search changed during pagination; try again later')
            items.extend(data['items'])
        keys = {(item['repository']['full_name'].casefold(), item['sha']) for item in items}
        if len(items) != total or len(keys) != total:
            raise RuntimeError('Commit search pagination is incomplete or duplicated')
        for item in items:
            repo = item['repository']
            if repo['private'] or repo['owner']['login'].casefold() != owner.casefold():
                continue
            if (item.get('author') or {}).get('type') == 'Bot':
                continue
            commits[(repo['full_name'], item['sha'])] = repo['name']

    search(start, end)
    counts = Counter(commits.values())
    ranked = sorted(counts, key=lambda name: (-counts[name], name.casefold(), name))[:5]
    # Quiet projects still have a station, but never produce invented traffic.
    if len(ranked) < 5:
        public = api(f'users/{owner}/repos?sort=pushed&direction=desc&per_page=100&type=owner')
        for repo in public:
            if (not repo['private'] and repo['owner']['login'].casefold() == owner.casefold()
                    and repo['name'] not in ranked):
                ranked.append(repo['name'])
                if len(ranked) == 5:
                    break
    return {
        'schema_version': 1,
        'owner': owner,
        'start': start.isoformat(),
        'end': end.isoformat(),
        'metric': 'indexed authored commits in public owned repositories',
        'total_commits': sum(counts.values()),
        'repositories': [{'name': name, 'commits': counts[name]} for name in ranked],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', default='tomasmark79')
    parser.add_argument('--end', type=date.fromisoformat,
                        default=datetime.now(ZoneInfo('Europe/Prague')).date())
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    snapshot = collect(args.owner, args.end)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(args.output)
    print(f'Collected {snapshot["total_commits"]} public authored commits; '
          f'{snapshot["start"]} through {snapshot["end"]}')


if __name__ == '__main__':
    main()
