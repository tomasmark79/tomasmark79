#!/usr/bin/env python3
"""Render a self-contained animated README illustration from public activity."""
import argparse
from datetime import date
from html import escape
from pathlib import Path
import json
import math
import re

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data', type=Path, default=ROOT / 'assets/factory/activity.json')
parser.add_argument('--output', type=Path, default=ROOT / 'assets/factory')
args = parser.parse_args()
OUT = args.output
snapshot = json.loads(args.data.read_text())
if snapshot['schema_version'] != 1:
    raise ValueError('Unsupported activity schema')
owner = snapshot['owner']
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', owner):
    raise ValueError('Invalid owner')
rows = snapshot['repositories']
if len(rows) > 5 or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', row['name'])
                        or type(row['commits']) is not int or row['commits'] < 0 for row in rows):
    raise ValueError('Invalid repository activity')
colors = ['#80cbc4', '#b6a0de', '#f0ba68', '#8ab9e9', '#e5948c']
REPOS = [(row['name'], row['commits'], colors[i]) for i, row in enumerate(rows)]
REPOS += [(None, 0, '#aebcc7')] * (5 - len(REPOS))
total = sum(commits for _, commits, _ in REPOS)
active_count = sum(commits > 0 for _, commits, _ in REPOS)
idle = total == 0
start, end = date.fromisoformat(snapshot['start']), date.fromisoformat(snapshot['end'])
if (end - start).days != 29:
    raise ValueError('Expected a 30-day inclusive window')

BELT_SPEED = 90  # Drawing units per second, identical on every delivery route.
CYCLE = 18
# Allocate the 18 delivery slots proportionally using largest remainders.
quotas = [CYCLE * commits / total if total else 0 for _, commits, _ in REPOS]
slot_counts = [math.floor(q) for q in quotas]
for i in sorted(range(len(REPOS)), key=lambda i: quotas[i] - slot_counts[i], reverse=True)[:CYCLE - sum(slot_counts) if total else 0]:
    slot_counts[i] += 1
# Smooth weighted round robin spreads each source across the common timeline.
credits = [0] * len(REPOS)
deliveries = [[] for _ in REPOS]
for slot in range(CYCLE if total else 0):
    credits = [credit + weight for credit, weight in zip(credits, slot_counts)]
    source = max(range(len(REPOS)), key=lambda i: credits[i])
    credits[source] -= CYCLE
    deliveries[source].append(slot)

# Length of one rounded corner: quadratic Bezier (0,0), (r,0), (r,r).
CORNER_LENGTH = 27 * (1 + math.asinh(1) / math.sqrt(2))

parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="640" viewBox="0 0 1120 640" role="img" aria-labelledby="workshop-title workshop-desc">
<title id="workshop-title">The package workshop</title>
<desc id="workshop-desc">Five public projects send packages to a NixOS snowflake assembler. Traffic reflects indexed authored commits from September 20 through October 19, 2026. Assembly is illustrative and does not represent CI results.</desc>
<defs>
 <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#cdd5db"/></pattern>
 <pattern id="rollers" width="18" height="18" patternUnits="userSpaceOnUse"><path d="M4 0v18" stroke="#9caab8" stroke-width="2"/></pattern>
 <linearGradient id="metal" x2="0" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#e4e9ed"/></linearGradient>
 <linearGradient id="glass" x2="1" y2="1"><stop stop-color="#e4f0fc"/><stop offset="1" stop-color="#f6faff"/></linearGradient>
 <filter id="shadow" x="-30%" y="-30%" width="160%" height="180%"><feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#243849" flood-opacity=".09"/></filter>
 <g id="parcel"><path d="M-10-7 0-12 10-7 10 6 0 12-10 6Z" fill="currentColor" stroke="#243849" stroke-width="1.3" stroke-linejoin="round"/><path d="m-10-7 10 6 10-6M0-1v13M-5-10 5-4v5" fill="none" stroke="#243849" stroke-width="1.1"/><path d="m-7 3 3 2" stroke="#fff" stroke-width="1.3"/></g>
 <g id="gear"><path d="M-4-15h8l1 5 4 2 5-2 4 7-4 3v4l4 3-4 7-5-2-4 2-1 5h-8l-1-5-4-2-5 2-4-7 4-3v-4l-4-3 4-7 5 2 4-2Z" fill="#cad5df" stroke="#536a7b" stroke-width="1.4"/><circle r="6" fill="#f7f9fa" stroke="#536a7b" stroke-width="1.4"/></g>
</defs>
<style>
 text{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#243849}
 .mono{font-family:ui-monospace,"DejaVu Sans Mono",monospace}
 .muted{fill:#647986}.tiny{font-size:10px;letter-spacing:1.6px;font-weight:650}
 .cog{animation:turn 8s linear infinite;transform-box:fill-box;transform-origin:center}
 .roller{animation:roll .8s linear infinite}
 .lamp{animation:blink 1.7s ease-in-out infinite}
 .press{animation:press 2.4s ease-in-out infinite}
 .completed{animation:complete 18s linear infinite;opacity:0}
 .working{animation:working 18s linear infinite}
 @keyframes turn{to{transform:rotate(360deg)}}
 @keyframes roll{to{stroke-dashoffset:-18}}
 @keyframes blink{0%,100%{opacity:.35}50%{opacity:1}}
 @keyframes press{0%,30%,75%,100%{transform:translateY(0)}50%,60%{transform:translateY(6px)}}
 @keyframes complete{0%,76%{opacity:0}79%,94%{opacity:1}100%{opacity:0}}
 @keyframes working{0%,76%{opacity:1}79%,94%{opacity:0}100%{opacity:1}}
 @media(prefers-reduced-motion:reduce){*{animation:none!important}animateMotion{display:none}.flake{opacity:1!important}.completed{opacity:1}.working{opacity:0}.moving{display:none}}
</style>
<rect width="1120" height="640" rx="20" fill="#f5f7f9"/>
<rect x="24" y="120" width="1072" height="450" rx="16" fill="url(#grid)"/>
<text x="48" y="43" class="tiny muted">TOMASMARK79 / OPEN SOURCE, IN MOTION</text>
<text x="48" y="87" font-size="34" font-weight="750" letter-spacing="-1.2">The package workshop<tspan fill="#5277c3">.</tspan></text>
<rect x="865" y="40" width="207" height="30" rx="15" fill="#e7edf3"/>
<circle cx="883" cy="55" r="3" fill="#5277c3"/>
<text x="895" y="59" font-size="11" class="mono">20 SEP — 19 OCT 2026</text>
<text x="48" y="156" class="tiny muted">A MONTH OF WORK, MADE TANGIBLE</text>
<text x="48" y="191" font-size="18" font-weight="550">Commits in. Packages out.</text>
<text x="48" y="217" font-size="13" class="muted">Five projects keep the workshop moving.</text>
<text x="48" y="237" font-size="13" class="muted">One snowflake, assembled piece by piece.</text>
<text x="49" y="287" font-size="30" font-weight="700">98<tspan dx="10" font-size="12" font-weight="400" class="muted">authored commits</tspan></text>
<path d="M250 260v35" stroke="#ccd5dc"/>
<text x="273" y="287" font-size="30" font-weight="700">05<tspan dx="10" font-size="12" font-weight="400" class="muted">public projects</tspan></text>
<!-- The delivery belt turns up and back into the assembly chamber. -->
<path d="M78 350H1003Q1030 350 1030 323V260Q1030 233 1003 233H967" fill="none" stroke="#c6d1db" stroke-width="30"/>
<path d="M78 350H1003Q1030 350 1030 323V260Q1030 233 1003 233H967" fill="none" stroke="#ecf0f3" stroke-width="24"/>
<path class="roller" d="M78 350H1003Q1030 350 1030 323V260Q1030 233 1003 233H967" fill="none" stroke="#a9b8c5" stroke-width="19" stroke-dasharray="2 16"/>
<circle cx="78" cy="350" r="13" fill="#d7e0e7" stroke="#94a7b5"/><circle cx="78" cy="350" r="4" fill="#758c9e"/>
<path d="M88 371v11m280-11v11m280-11v11m280-11v11" stroke="#aebcc7" stroke-width="5"/>
<!-- Assembly chamber and service robot. -->
<path d="M598 294h93" stroke="#c4d0da" stroke-width="7" stroke-linecap="round"/>
<rect x="603" y="279" width="67" height="23" rx="4" fill="#e4eaf0" stroke="#8194a4"/>
<path d="M636 278v-45l45-34 38 22" fill="none" stroke="#344f65" stroke-width="12" stroke-linejoin="round"/>
<path d="M636 273v-40l45-34 38 22" fill="none" stroke="#d4dfe7" stroke-width="7" stroke-linejoin="round"/>
<circle cx="636" cy="233" r="8" fill="#f0ba68" stroke="#344f65" stroke-width="2"/>
<circle cx="681" cy="199" r="8" fill="#f0ba68" stroke="#344f65" stroke-width="2"/>
<path class="press" d="m712 215 8 6-5 13m5-13 13-1" fill="none" stroke="#344f65" stroke-width="4" stroke-linecap="round"/>
<g filter="url(#shadow)"><rect x="739" y="128" width="228" height="187" rx="14" fill="url(#metal)" stroke="#9cabb8" stroke-width="1.5"/></g>
<rect x="751" y="139" width="204" height="160" rx="9" fill="url(#glass)" stroke="#c1d3e3"/>
<path d="M762 149h24m-24 0v24m182-24h-24m24 0v24m-182 113h24m-24 0v-24m182 24h-24m24 0v-24" fill="none" stroke="#afc3d4"/>
<path d="m766 147 174 143" stroke="#fff" stroke-width="16" style="opacity:var(--glass-reflection)"/>
<text x="852" y="119" text-anchor="middle" class="tiny muted">NIXOS ASSEMBLER</text>
''']

logo = (ROOT / 'assets/icons/nixos.svg').read_text()
path = re.search(r'<path d="([^"]+)"', logo).group(1)
segments = re.split('[zZ]', path)
last = (0., 0.)
for i, segment in enumerate(s for s in segments if s.strip()):
    match = re.match(r'([Mm])(-?[\d.]+)[ ,]+(-?[\d.]+)', segment)
    cmd, x, y = match.groups()
    x, y = float(x), float(y)
    if cmd == 'm':
        x, y = x + last[0], y + last[1]
    last = x, y
    segment = f'M{x:g} {y:g}' + segment[match.end():] + 'z'
    threshold = 18 + i * 10
    parts.append(f'''<style>@keyframes piece{i}{{0%,{threshold}%{{opacity:.09;transform:translateY(-3px)}}{threshold+4}%,94%{{opacity:1;transform:translateY(0)}}100%{{opacity:.09;transform:translateY(-3px)}}}}</style>
<g transform="translate(778 150) scale(6.2)"><path class="flake" d="{segment}" fill="{'#5277c3' if i%2 else '#7eb4dd'}" style="animation:piece{i} 18s ease-in-out infinite"/></g>''')

parts.append('''<rect x="780" y="303" width="146" height="23" rx="5" fill="#243849"/>
<g class="working"><circle cx="793" cy="315" r="3" fill="#f0ba68" class="lamp"/><text x="806" y="318" fill="#fff" style="fill:#fff" font-size="9" class="mono">assembling flake…</text></g>
<g class="completed"><circle cx="793" cy="315" r="3" fill="#80cbc4"/><text x="806" y="318" style="fill:#fff" font-size="9" class="mono">snowflake complete</text></g>
''')

for i, (name, commits, color) in enumerate(REPOS):
    x = 51 + i * 194
    cx = x + 78
    rate = 5.8 * max(r[1] for r in REPOS) / commits if commits else 8
    display_name = name if name else f'Station {i+1:02}'
    link_open = f'<a href="https://github.com/{owner}/{escape(name)}">' if name else '<g>'
    link_close = '</a>' if name else '</g>'
    parts.append(f'''<!-- {escape(display_name)}: {commits} indexed authored commits. -->
{link_open}
<path d="M{cx} 424v-62" stroke="#bbc9d4" stroke-width="22"/>
<path d="M{cx} 424v-62" stroke="#e7edf2" stroke-width="16"/>
<path class="roller" d="M{cx} 424v-62" stroke="#9bafbf" stroke-width="12" stroke-dasharray="2 16"/>
<ellipse cx="{cx}" cy="514" rx="82" ry="7" fill="#243849" opacity=".07"/>
<path d="M{x+16} 487v24m122-24v24" stroke="#536d80" stroke-width="7"/>
<rect x="{x}" y="422" width="157" height="77" rx="9" fill="url(#metal)" stroke="#8298aa" stroke-width="1.5"/>
<path d="M{x+8} 422v-28q0-8 8-8h125q8 0 8 8v28" fill="{color}" stroke="#536d80" stroke-width="1.5"/>
<rect x="{x+51}" y="391" width="55" height="41" rx="4" fill="#263f52"/>
<path class="press" d="M{x+58} 393h41v10h-41z" fill="#90a6b7"/>
<path d="M{x+55} 425h47" stroke="#e3edf3" stroke-width="3"/>
<circle cx="{x+20}" cy="405" r="4" fill="#f8faff" class="lamp" style="animation-duration:{rate/3:.2f}s"/>
<circle cx="{x+137}" cy="405" r="3" fill="#243849" opacity=".5"/>
<rect x="{x+12}" y="440" width="78" height="39" rx="4" fill="#243849"/>
<text x="{x+21}" y="455" class="mono" font-size="9" style="fill:{color}">repo_{i+1:02}</text>
<text x="{x+21}" y="470" class="mono" font-size="9" style="fill:#e8eff5">working<tspan class="lamp">...</tspan></text>
<g transform="translate({x+121} 459)"><use href="#gear" class="cog" style="animation-duration:{rate:.2f}s"/></g>
<path d="M{x+12} 489h133" stroke="#b5c4cf"/>
<text x="{cx}" y="543" text-anchor="middle" font-size="{min(12, 160 / max(1, len(display_name)) / .62):.2f}" font-weight="650">{escape(display_name)}</text>
<text x="{cx}" y="564" text-anchor="middle" font-size="11" class="mono muted">{commits} commits</text>
{link_close}''')
    if not commits:
        # Only this station sleeps when other projects are still active.
        parts[-1] = parts[-1].replace('class="press"', '').replace('class="cog"', '').replace('class="lamp"', '')
        parts[-1] = parts[-1].replace('working<tspan >...</tspan>', 'idle')
        parts[-1] = parts[-1].replace('working<tspan>...</tspan>', 'idle')
    # Reserve equally spaced arrival slots at the assembler. Compute departure
    # backwards from route length: every shared belt has the same speed, and
    # merges leave a full slot of space, including across the loop boundary.
    route = f'M{cx} 420V350H1003Q1030 350 1030 323V260Q1030 233 1003 233H969'
    route_length = 70 + (1003 - cx) + 2 * CORNER_LENGTH + 63 + 34
    duration = route_length / BELT_SPEED
    for arrival in deliveries[i]:
        delay = (arrival - duration) % CYCLE - CYCLE
        period = CYCLE
        motion_end = duration / period
        parts.append(f'''<g class="moving" color="{color}"><g><use href="#parcel"/>
<animateMotion dur="{period}s" begin="{delay:.8f}s" repeatCount="indefinite" path="{route}" keyPoints="0;1;1" keyTimes="0;{motion_end:.9f};1" calcMode="linear"/>
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.005;{motion_end-.005:.9f};{motion_end:.9f};1" dur="{period}s" begin="{delay:.8f}s" repeatCount="indefinite"/>
</g></g>''')

parts.append('''<path d="M48 589h1024" stroke="#d7e0e7"/>
<circle cx="52" cy="612" r="3" fill="#5277c3"/>
<text x="64" y="616" font-size="11" class="muted">Public commit activity · illustrative assembly, not CI status</text>
<text x="1072" y="616" text-anchor="end" font-size="11" class="mono muted">PROTOTYPE / 001</text>
</svg>''')

svg = '\n'.join(parts)
# Substitute the current data into the approved composition.
months = 'JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split()
date_label = f'{start.day:02} {months[start.month-1]} — {end.day:02} {months[end.month-1]} {end.year}'
svg = svg.replace('20 SEP — 19 OCT 2026', date_label)
svg = svg.replace('September 20 through October 19, 2026', f'{start.isoformat()} through {end.isoformat()}')
svg = svg.replace('TOMASMARK79 /', escape(owner.upper()) + ' /')
svg = svg.replace('>98<tspan', f'>{total}<tspan')
svg = svg.replace('>05<tspan', f'>{active_count:02}<tspan')
svg = svg.replace('>public projects<', '>active projects<')
svg = svg.replace('PROTOTYPE / 001', 'LAST 30 DAYS')
svg = svg.replace('The package workshop — prototype', 'The package workshop')
svg = svg.replace('Five public projects send packages', f'{active_count} active public projects send packages')
if idle:
    svg = svg.replace('0 active public projects send packages to a NixOS snowflake assembler.', 'Public project stations and the NixOS assembler are idle.')
    svg = svg.replace('Commits in. Packages out.', 'The workshop is taking a breather.')
    svg = svg.replace('Five projects keep the workshop moving.', 'No commits in the last 30 days.')
    svg = svg.replace('One snowflake, assembled piece by piece.', 'Ready when the next idea arrives.')
    svg = svg.replace('assembling flake…', 'workshop idle')
    svg = svg.replace('</svg>', '<style>*{animation:none!important}.flake{opacity:.12!important}.completed{opacity:0}.working{opacity:1}.lamp{opacity:.35}</style></svg>')
elif active_count < 5:
    noun = 'project keeps' if active_count == 1 else 'projects keep'
    svg = svg.replace('Five projects keep the workshop moving.', f'{active_count} {noun} the workshop moving.')
# Keep displays dark in both themes; other neutral surfaces follow the theme.
svg = svg.replace('fill="#243849"', 'fill="#203648"')
svg = svg.replace('<stop stop-color="#fff"/>', '<stop stop-color="var(--metal-top)"/>')
svg = svg.replace('flood-color="#243849"', 'flood-color="#08121c"')
palette = {
    '#243849': '#dbe8f3',  # text and small foreground strokes
    '#647986': '#a0b5c7',
    '#f5f7f9': '#101b28',
    '#cdd5db': '#2e4257',
    '#e4e9ed': '#293e52',
    '#e4f0fc': '#182f46',
    '#f6faff': '#203a53',
    '#e7edf3': '#22384d',
    '#ccd5dc': '#3c536a',
    '#c6d1db': '#4a6278',
    '#ecf0f3': '#23394d',
    '#a9b8c5': '#688298',
    '#d7e0e7': '#2e475d',
    '#94a7b5': '#7892a6',
    '#758c9e': '#a0b7ca',
    '#aebcc7': '#4e687e',
    '#c4d0da': '#4a6378',
    '#e4eaf0': '#30495f',
    '#8194a4': '#728ba0',
    '#344f65': '#9bb3c7',
    '#d4dfe7': '#536e86',
    '#9cabb8': '#617e96',
    '#c1d3e3': '#3e607c',
    '#afc3d4': '#486b89',
    '#bbc9d4': '#4a647b',
    '#e7edf2': '#243b50',
    '#9bafbf': '#6c879e',
    '#536d80': '#728ea5',
    '#8298aa': '#68849c',
    '#536a7b': '#88a1b7',
    '#cad5df': '#4c6b85',
    '#f7f9fa': '#253c51',
    '#b5c4cf': '#48657e',
}
light = ['--metal-top:#fff', '--glass-reflection:.35']
dark = ['--metal-top:#354d63', '--glass-reflection:.055']
for i, (original, themed) in enumerate(palette.items()):
    key = f'--tone-{i}'
    svg = svg.replace(original, f'var({key})')
    light.append(f'{key}:{original}')
    dark.append(f'{key}:{themed}')
theme = ('<style>:root{' + ';'.join(light) + '}'
         '@media(prefers-color-scheme:dark){:root{' + ';'.join(dark) + '}}</style>')
svg = svg.replace('</svg>', theme + '</svg>')
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'workshop.svg').write_text(svg)
for name, declarations in [('light', light), ('dark', dark)]:
    fixed = svg.replace(theme, '<style>:root{' + ';'.join(declarations) + '}</style>')
    (OUT / f'workshop-{name}.svg').write_text(fixed)
# A local artwork viewer, with the SVG inline for deterministic frame capture.
(OUT / 'preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The package workshop</title><style>html,body{margin:0;background:#e9eef2}body{display:grid;place-items:center;min-height:100vh}svg{display:block;width:min(1120px,100vw);height:auto}a{cursor:pointer}@media(prefers-color-scheme:dark){html,body{background:#0b1420}}</style>''' + svg + '</html>')
print(f'Generated {OUT / "workshop.svg"}')
