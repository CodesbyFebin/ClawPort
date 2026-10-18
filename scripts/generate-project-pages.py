import json,pathlib,html,collections,csv
root=pathlib.Path(__file__).resolve().parents[1];data=json.loads((root/'dist/catalog.json').read_text());e=html.escape
platforms={'Android':lambda n:n.endswith('.apk'),'Windows':lambda n:n.endswith(('.exe','.msi')),'macOS':lambda n:n.endswith(('.dmg','.pkg')),'Linux':lambda n:n.endswith(('.deb','.rpm','.appimage','.sh')) or 'linux' in n and n.endswith(('.tar.gz','.tgz','.bin','.tar.xz'))}
rows=[]
for p in data:
 slug=p['repo'].lower().replace('/','--');folder=root/'dist/projects'/slug;folder.mkdir(parents=True,exist_ok=True)
 blocks=[]
 for os,match in platforms.items():
  assets=[a for a in p['assets'] if (p['repo']!='openai/codex' or __import__('re').match(r'^codex-(aarch64|x86_64|x64|arm64)[-.]',a['name']) and 'bazel' not in a['name']) and match(a['name'].lower()) and not any(s in a['name'].lower() for s in ['dsym','evidence','checksum'])]
  status='Official packages available' if assets else 'Native package not verified'
  links=''.join('<p><a class="button" href="'+e(a['url'])+'">Download ↓</a> <span class="asset-name">'+e(a['name'])+(' [DEBUG BUILD — not a production release]' if 'debug' in a['name'].lower() else '')+' · '+str(round(a['size']/1048576,1))+' MB</span>'+('<br><code style="font-size:10px;overflow-wrap:anywhere">'+e(a['digest'])+'</code>' if a.get('digest') else '')+'</p>' for a in assets)
  if not assets:links='<p>Check upstream setup. A native build or platform port may be required; no installer is supplied here.</p>'
  if os=='Linux' and p['name']=='NullClaw':links+='<p><a class="button" download href="../../install-nullclaw.sh">ClawPort Linux installer .sh ↓</a></p><p>Downloads a pinned upstream binary and checks SHA-256. Run with sh after reviewing the script. Does not configure providers.</p>'
  blocks.append('<article class="agent"><p class="eyebrow">'+os+'</p><h3>'+status+'</h3>'+links+'</article>')
  rows.append({'repo':p['repo'],'platform':os,'status':status,'packages':len(assets),'built_by_clawport':False})
 page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+e(p['name'])+''' — ClawPort installation</title><link rel="stylesheet" href="../../style.css"></head><body><nav><a class="brand" href="../../">◈ <b>clawport</b></a><a href="../../#catalog">← All projects</a></nav><main><section style="padding:60px 0 35px"><p class="eyebrow">'''+e(p['category'])+'</p><h1 style="font-size:clamp(40px,6vw,76px);overflow-wrap:anywhere">'+e(p['name'])+'</h1><p class="intro">'+e(p['description'])+'</p><p class="meta">License: '+e(p['license'])+' · '+('Archived upstream repository · ' if p.get('archived') else '')+'Checked '+e(p['checked'][:10])+'</p><a class="button" href="https://github.com/'+e(p['repo'])+'">Source & setup ↗</a> <a class="button secondary" href="https://github.com/'+e(p['repo'])+'/releases">All upstream releases ↗</a> <a class="button secondary" href="https://github.com/'+e(p['repo'])+'/archive/'+e(p.get('sourceCommit','HEAD'))+'.tar.gz">Pinned source archive ↓</a></section><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">'+''.join(blocks)+'</div><section class="note" style="margin-top:50px"><h3>Before installing</h3><p>Confirm your architecture, OS version and upstream requirements. Release filenames identify packages; they do not prove device compatibility. Your OS will ask for installation approval. These packages are published by the upstream maintainers and have not been rebuilt, executed or device-tested by ClawPort. Model weights, provider keys and services may need separate setup. Unverified means this catalog has not established availability, not that a project cannot support the platform.</p></section></main></body></html>'
 (folder/'index.html').write_text(page)
(root/'dist/build-matrix.json').write_text(json.dumps(rows,indent=2))
with (root/'BUILD-MATRIX.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
summary=collections.Counter(p['category'] for p in data)
lines=['# ClawPort catalog','',f'{len(data)} distinct upstream repositories. Metadata verification is not a source-code, license or security audit.','', '| Category | Projects |','|---|---:|']+[f'| {c} | {n} |' for c,n in summary.items()]+['','| Project | Category | License metadata | Upstream |','|---|---|---|---|']
for p in data:lines.append(f"| {p['name']} | {p['category']} | {p['license']} | https://github.com/{p['repo']} |")
(root/'CATALOG.md').write_text('\n'.join(lines)+'\n')
print('Generated',len(data),'project pages and',len(rows),'platform records')
