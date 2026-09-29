import re, glob, os
D='/home/user/Sep2026/aster-mechanism-review'
body=open('report_body.html',encoding='utf-8').read()
m={'fig1':'fig1_motion_draft','fig2':'fig2_diffusiophoresis_sign_check','fig3':'fig3_motion_proposed','fig4':'fig4_speed_scales','fig5':'fig5_force_draft','fig6':'fig6_force_proposed_contact','fig7':'fig7_force_proposed_fields'}
for k,v in m.items():
    svg=open(f'{D}/figures/{v}.svg',encoding='utf-8').read()
    svg=re.sub(r'<svg ([^>]*?) width="\d+" height="\d+"', r'<svg \1', svg, count=1)
    body=body.replace('{{'+k+'}}', svg)
css='''
@page { size: A4; margin: 15mm 14mm 16mm 14mm; }
:root{--ink:#1f2933;--muted:#52606d;--accent:#4c1d95;--line:#e2e8f0;}
body{font-family:'WenQuanYi Zen Hei','Noto Sans CJK SC',sans-serif;color:var(--ink);background:#fff;font-size:10.2pt;line-height:1.62;margin:0;}
h1{font-size:21pt;line-height:1.35;margin:6px 0 10px;color:#111827}
h2{font-size:14.5pt;margin:20px 0 8px;padding-bottom:4px;border-bottom:2px solid var(--accent);color:var(--accent);break-after:avoid}
h3{font-size:11.5pt;margin:14px 0 6px;color:#111827;break-after:avoid}
.cover{padding:6px 0 10px;border-bottom:1px solid var(--line);margin-bottom:8px}
.kicker{font-size:9pt;color:var(--muted);letter-spacing:.08em}
.sub{color:var(--muted);font-size:9.5pt;margin:0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.card{border:1px solid #ddd6fe;background:#faf5ff;border-radius:8px;padding:8px 11px;font-size:9.4pt}
.card h3{margin-top:2px;color:var(--accent)}
.card p{margin:4px 0}
.note,.caveat{font-size:9pt;color:var(--muted);background:#f8fafc;border-left:3px solid #94a3b8;padding:6px 10px;margin:8px 0}
figure{margin:12px 0 14px;break-inside:avoid;page-break-inside:avoid}
figure svg{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:6px}
figcaption{font-size:8.8pt;color:var(--muted);margin-top:4px}
ol,ul{padding-left:1.4em;margin:4px 0}
li{margin:3px 0}
ol.issues>li{margin:6px 0}
table{width:100%;border-collapse:collapse;font-size:9pt;margin:6px 0 10px;break-inside:avoid}
th,td{border:1px solid #cbd5e1;padding:4px 6px;vertical-align:top;text-align:left}
th{background:#f1f5f9}
td:first-child{white-space:nowrap;font-weight:700;color:#334155}
.refs{font-size:8.8pt;color:#334155}
em{font-style:normal;font-weight:700;color:#b91c1c}
'''
html=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>人工星状体机理评析</title><style>{css}</style></head><body>{body}</body></html>'
open(f'{D}/report.html','w',encoding='utf-8').write(html)
print('html ok')
