"""Generate profile artwork and statistics using only unauthenticated public GitHub data."""
import json
import math
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USERNAME = 'arifular1f'

def svg_document(width, height, body, title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title>{body}</svg>\n'

def write_assets():
    assets = ROOT / 'assets'
    badges = assets / 'badges'
    badges.mkdir(parents=True, exist_ok=True)
    body = '''<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0b1220"/><stop offset="1" stop-color="#142b3c"/></linearGradient></defs>
<rect width="1200" height="270" rx="22" fill="url(#bg)"/>
<path d="M895 0v270M995 0v270M1095 0v270M795 0v270M695 0v270M695 55h505M695 135h505M695 215h505" stroke="#2a4859" opacity=".42"/>
<rect x="46" y="45" width="5" height="178" rx="2" fill="#64dfc1"/>
<text x="76" y="78" fill="#64dfc1" font-family="Segoe UI,Arial,sans-serif" font-size="14" letter-spacing="3">DEVELOPER PORTFOLIO</text>
<text x="74" y="142" fill="#f4f8fc" font-family="Segoe UI,Arial,sans-serif" font-weight="700" font-size="55">arifular1f</text>
<text x="76" y="183" fill="#c1d0dc" font-family="Segoe UI,Arial,sans-serif" font-size="22">iOS development · Automation · Security research</text>
<text x="76" y="222" fill="#91a9bc" font-family="Segoe UI,Arial,sans-serif" font-size="15">SwiftUI interfaces. Practical tooling. Continuous learning.</text>
<path d="m1000 70-65 65 65 65m60-130 65 65-65 65" fill="none" stroke="#64dfc1" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>'''
    (assets / 'profile-banner.svg').write_text(svg_document(1200,270,body,'arifular1f developer portfolio'),encoding='utf-8')
    labels = [('swift','Swift','#ed795d'),('swiftui','SwiftUI','#77bafa'),('python','Python','#f0cf77'),('javascript','JavaScript','#ecd869'),('nodejs','Node.js','#8ac787'),('github-actions','GitHub Actions','#80b6ff'),('git','Git','#f69780'),('linux','Linux','#d8dfeb'),('docker','Docker','#77c9fb'),('virtualization','Virtualization','#baa4f2')]
    for slug, label, color in labels:
        width = max(76, math.ceil(len(label)*7.7)+34)
        badge = f'<rect width="{width}" height="30" rx="7" fill="#142333"/><circle cx="15" cy="15" r="3" fill="{color}"/><text x="26" y="20" fill="#e2eaf4" font-family="Segoe UI,Arial,sans-serif" font-size="12" font-weight="600">{escape(label)}</text>'
        (badges / (slug+'.svg')).write_text(svg_document(width,30,badge,label),encoding='utf-8')
    # No auth header: this script cannot query any private account data.
    request = Request(f'https://api.github.com/users/{USERNAME}',headers={'Accept':'application/vnd.github+json','User-Agent':'arifular1f-public-profile-assets'})
    with urlopen(request,timeout=30) as response:
        public = json.load(response)
    assert public['login'].lower() == USERNAME
    date = datetime.now(timezone(timedelta(hours=8))).date().isoformat()
    stats = [('PUBLIC REPOSITORIES',str(public['public_repos'])),('FOLLOWERS',str(public['followers'])),('FOLLOWING',str(public['following'])),('ON GITHUB SINCE',public['created_at'][:7])]
    stats_body = '<rect width="1200" height="190" rx="20" fill="#0f1b2a"/>'
    for index, (label,value) in enumerate(stats):
        x = 34+index*295
        if index: stats_body += f'<path d="M{x-18}35v92" stroke="#2b3e51"/>'
        stats_body += f'<text x="{x}" y="55" fill="#95adbf" font-family="Segoe UI,Arial,sans-serif" font-size="12" letter-spacing="1">{label}</text><text x="{x}" y="105" fill="#e9f5fa" font-family="Segoe UI,Arial,sans-serif" font-size="34" font-weight="700">{escape(value)}</text>'
    stats_body += f'<text x="34" y="159" fill="#7b94a8" font-family="Segoe UI,Arial,sans-serif" font-size="12">Public profile snapshot · Updated {date} (Asia/Kuala_Lumpur)</text>'
    (assets/'github-stats.svg').write_text(svg_document(1200,190,stats_body,'Public GitHub statistics for '+USERNAME),encoding='utf-8')
    print(f'Generated banner, {len(labels)} badges and public-only statistics for {date}')

if __name__ == '__main__': write_assets()
