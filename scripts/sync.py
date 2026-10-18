import urllib.request,json,re,concurrent.futures,pathlib,datetime
root=pathlib.Path(__file__).resolve().parents[1]
raw=(root/'vendor/awesome-openclaw-alternatives/README.md').read_text()
def get(url):
 try:
  return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ClawPort-catalog'}),timeout=20))
 except Exception:return {}
def project(section):
 name=section.splitlines()[0]; match=re.search(r'https://github.com/([\w.-]+/[\w.-]+)',section)
 repo=match[1] if match else None
 meta=get('https://api.github.com/repos/'+repo) if repo else {}
 release=get('https://api.github.com/repos/'+repo+'/releases/latest') if repo else {}
 return dict(name=name,repo=repo,language=meta.get('language') or 'Community',description=meta.get('description') or 'Community agent implementation. See upstream documentation for requirements.',license=(meta.get('license') or {}).get('spdx_id','Unverified'),release=release.get('tag_name'),releaseUrl=release.get('html_url'),assets=[dict(name=a['name'],url=a['browser_download_url'],size=a['size'],digest=a.get('digest')) for a in release.get('assets',[])],checked=datetime.datetime.now(datetime.timezone.utc).isoformat())
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool: data=list(pool.map(project,raw.split('### ')[1:]))
catalog_path=root/'dist/catalog.json'
previous=json.loads(catalog_path.read_text()) if catalog_path.exists() else []
for p in data:p['category']='Claw ecosystem';p['source']='Original collection'
original_names={p['name'].lower() for p in data}
data.extend(p for p in previous if p['name'].lower() not in original_names)
catalog_path.write_text(json.dumps(data,indent=2))
print('Catalog:',len(data),'projects;',sum(len(x['assets']) for x in data),'release assets')
