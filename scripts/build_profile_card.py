"""Build self-contained, GitHub-safe desktop/mobile SVG cards with real Shields badges."""
from html import escape
from pathlib import Path
import re
import textwrap
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
SKILLS = [
    ('ios-development','iOS Development','28313e','apple'),
    ('swift','Swift','a4422c','swift'),
    ('swiftui','SwiftUI','185780','swift'),
    ('cybersecurity','Cybersecurity','15563d',''),
    ('penetration-testing','Penetration Testing','58376b',''),
    ('python','Python','254c72','python'),
    ('javascript','JavaScript','64531c','javascript'),
    ('nodejs','Node.js','2b5734','nodedotjs'),
    ('linux','Linux','45443a','linux'),
    ('docker','Docker','165a78','docker'),
    ('github-actions','GitHub Actions','294f86','githubactions'),
]
PROJECTS = [
    ('Maruf Studio 2.0','Personal iOS Application','SwiftUI, account architecture and local media.','DEVELOPMENT','#61d3a6'),
    ('iOS IPA Builder','Automated iOS Build System','GitHub Actions, unsigned IPA artifacts and validation.','AUTOMATION','#78b7ff'),
    ('Private DNS Infrastructure','Ongoing research and development','DNS infrastructure and administration.','R&D','#c6a1f0'),
    ('Android Device Management Tools','Ongoing research and development','Android device management.','R&D','#c6a1f0'),
    ('Security Research Projects','Ongoing research and development','Application security, reverse engineering and testing.','R&D','#c6a1f0'),
]

def shield_url(skill):
    _, label, color, logo = skill
    params = {'label':'','message':label,'color':color,'style':'flat','logoColor':'white'}
    if logo: params['logo'] = logo
    return 'https://img.shields.io/static/v1?' + urlencode(params)

def download_badges():
    folder = ROOT / 'assets/shields'
    folder.mkdir(parents=True, exist_ok=True)
    for skill in SKILLS:
        path = folder / (skill[0] + '.svg')
        if not path.exists():
            for attempt in range(3):
                try:
                    with urlopen(Request(shield_url(skill),headers={'User-Agent':'arifular1f-profile-card'}),timeout=30) as response:
                        data = response.read()
                    element = ET.fromstring(data)
                    assert element.tag == '{'+NS+'}svg'
                    assert b'<script' not in data.lower() and b'foreignObject' not in data
                    path.write_bytes(data)
                    break
                except Exception:
                    if attempt == 2: raise
                    time.sleep(1)

def text(x,y,value,size=16,color='#b0b7c1',weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'

def badge_fragment(slug,x,y,scale):
    root = ET.fromstring((ROOT/'assets/shields'/f'{slug}.svg').read_bytes())
    width, height = float(root.attrib['width']), float(root.attrib['height'])
    # Shields uses repeated gradient IDs. Namespace each badge before nesting it.
    serialized = ET.tostring(root,encoding='unicode')
    ids = re.findall(r'\bid="([^"]+)"',serialized)
    for old in ids:
        new = slug+'-'+old
        serialized = serialized.replace('id="'+old+'"','id="'+new+'"').replace('url(#'+old+')','url(#'+new+')').replace('href="#'+old+'"','href="#'+new+'"')
    root = ET.fromstring(serialized)
    root.attrib.update({'x':str(x),'y':str(y),'width':str(width*scale),'height':str(height*scale),'viewBox':f'0 0 {width} {height}'})
    clip = f'pill-{slug}'
    return f'<defs><clipPath id="{clip}"><rect x="{x}" y="{y}" width="{width*scale}" height="{height*scale}" rx="{height*scale/2}"/></clipPath></defs><g clip-path="url(#{clip})">'+ET.tostring(root,encoding='unicode')+'</g>', width*scale, height*scale

def card(mobile):
    width = 340 if mobile else 900
    pad = 25 if mobile else 42
    right = width-pad
    body = ''
    body += text(pad,55 if mobile else 70,'Maruf Khan',30 if mobile else 44,'#f4f6f8',700)
    body += text(pad,81 if mobile else 100,'@arifular1f',16 if mobile else 19,'#89949d')
    bx,by = (pad,103) if mobile else (width-244,49)
    body += f'<rect x="{bx}" y="{by}" width="194" height="30" rx="15" fill="#102b21" stroke="#21593f"/><circle cx="{bx+15}" cy="{by+15}" r="4" fill="#65dfa4"/>'
    body += text(bx+27,by+20,'Developer Portfolio',14,'#91e7b8',600)
    y = 159 if mobile else 140
    body += f'<path d="M{pad} {y}H{right}" stroke="#232b2e"/>'
    y += 34
    body += text(pad,y,'ABOUT ME',12,'#6fdbab',650)
    y += 31
    roles = ['iOS Developer','Cybersecurity Researcher','Red Team Operator','Software Engineer']
    if mobile:
        for role in roles:
            body += text(pad,y,role,16,'#e3e8ec',500); y += 25
        y += 13
    else:
        body += text(pad,y,' | '.join(roles),18,'#e3e8ec',500); y += 48
    body += f'<path d="M{pad} {y}H{right}" stroke="#232b2e"/>'
    y += 34
    body += text(pad,y,'TECHNICAL EXPERTISE',12,'#6fdbab',650)
    y += 21
    x = pad
    scale = 1.2 if mobile else 1.35
    for slug,*_ in SKILLS:
        root = ET.fromstring((ROOT/'assets/shields'/f'{slug}.svg').read_bytes())
        w = float(root.attrib['width'])*scale
        if x+w > right:
            x = pad; y += 36 if mobile else 40
        fragment,w,h = badge_fragment(slug,x,y,scale)
        body += fragment; x += w+9
    y += 54 if mobile else 62
    body += f'<path d="M{pad} {y}H{right}" stroke="#232b2e"/>'
    y += 34
    body += text(pad,y,'FEATURED PROJECTS',12,'#6fdbab',650)
    y += 22
    for index,(title,subtitle,detail,status,color) in enumerate(PROJECTS):
        title_lines = textwrap.wrap(title,width=28) if mobile else [title]
        detail_lines = textwrap.wrap(detail,width=37) if mobile else [detail]
        height = 108 + (len(title_lines)-1)*22 + (len(detail_lines)-1)*19 if mobile else 111
        body += f'<rect x="{pad}" y="{y}" width="{width-2*pad}" height="{height}" rx="13" fill="#101418" stroke="#222a30"/>'
        tx = pad+16
        ty = y+28
        for line in title_lines:
            body += text(tx,ty,line,15 if mobile else 19,'#eef2f5',650); ty += 22 if mobile else 25
        body += text(tx,ty,subtitle,12 if mobile else 14,color,500); ty += 22
        for line in detail_lines:
            body += text(tx,ty,line,12 if mobile else 14,'#909ba6'); ty += 19
        if not mobile:
            statusw = len(status)*7+24
            body += f'<rect x="{right-statusw-16}" y="{y+16}" width="{statusw}" height="22" rx="11" fill="#17212a"/>'
            body += text(right-statusw-5,y+31,status,10,color,600)
        y += height+12
    y += 14
    body += f'<path d="M{pad} {y}H{right}" stroke="#232b2e"/>'
    y += 32
    if mobile:
        body += text(pad,y,'GitHub Portfolio',15,'#d3dce3',600); y += 27
        body += text(pad,y,'Open Source Projects',15,'#d3dce3',600); y += 27
        body += text(pad,y,'github.com/arifular1f',12,'#6f7f8e')
    else:
        body += text(pad,y,'GitHub Portfolio  /  Open Source Projects',15,'#d3dce3',600)
        body += text(right-183,y,'github.com/arifular1f',13,'#6f7f8e')
    height = y+34
    background = f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="22" fill="#090c0f" stroke="#30383c" stroke-width="1.2"/>'
    document = f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>Maruf Khan — Developer Portfolio</title><desc>arifular1f. iOS development, cybersecurity, red team operations and software engineering. Technical expertise and five project highlights; infrastructure and security projects are ongoing research and development.</desc>'+background+body+'</svg>\n'
    target = ROOT/'assets'/('profile-card-mobile.svg' if mobile else 'profile-card.svg')
    target.write_text(document,encoding='utf-8')
    ET.fromstring(document)
    print(f'Created {target.name}: {width} × {height}')

if __name__ == '__main__':
    download_badges()
    card(False)
    card(True)
