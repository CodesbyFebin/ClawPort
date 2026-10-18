import json,urllib.request,concurrent.futures,pathlib,datetime
root=pathlib.Path(__file__).resolve().parents[1]
base=json.loads((root/'dist/catalog.json').read_text())
for p in base:
 p.setdefault('category','Claw ecosystem');p.setdefault('source','Original collection')
existing={p['repo'].lower() for p in base if p['repo']}
extra=json.loads((root/'scripts/extra-projects.json').read_text())
def get(url):
 try:return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ClawPort-research'}),timeout=20))
 except Exception:return {}
def inspect(pair):
 category,repo=pair
 if repo.lower() in existing:return None
 m=get('https://api.github.com/repos/'+repo)
 if not m.get('full_name'):return None
 release=get('https://api.github.com/repos/'+m['full_name']+'/releases/latest')
 return dict(name=m['name'],repo=m['full_name'],category=category,source='Expanded primary-source research',language=m.get('language') or 'Community',description=m.get('description') or 'See upstream documentation.',license=(m.get('license') or {}).get('spdx_id','Unverified'),archived=m['archived'],release=release.get('tag_name'),releaseUrl=release.get('html_url'),assets=[dict(name=a['name'],url=a['browser_download_url'],size=a['size'],digest=a.get('digest')) for a in release.get('assets',[])],checked=datetime.datetime.now(datetime.timezone.utc).isoformat())
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool: found=list(pool.map(inspect,[(c,r) for c,rs in extra.items() for r in rs]))
seen={p['repo'].lower() for p in base if p['repo']}
for p in found:
 if p and p['repo'].lower() not in seen:
  placeholder=next((x for x in base if not x['repo'] and x['name'].lower()==p['name'].lower()),None)
  if placeholder:base.remove(placeholder)
  base.append(p);seen.add(p['repo'].lower())
(root/'dist/catalog.json').write_text(json.dumps(base,indent=2))
print(len(base),'entries;',len(seen),'verified repo links')
print('Unresolved:',[r for r,p in zip([r for rs in extra.values() for r in rs],found) if not p])
