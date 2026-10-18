"""Download source only. Does not execute imported builds or install dependencies."""
import argparse,concurrent.futures,hashlib,json,pathlib,subprocess,tarfile,urllib.request,shutil,time
root=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=0);p.add_argument('--jobs',type=int,default=6);p.add_argument('--retry-blocked',action='store_true');p.add_argument('--resume',action='store_true');args=p.parse_args()
items=json.loads((root/'sources/manifest.json').read_text());items=items[:args.limit] if args.limit else items
out=root/'imported-sources';out.mkdir(exist_ok=True)
prior=json.loads((root/'sources/import-results.json').read_text()) if (args.retry_blocked or args.resume) and (root/'sources/import-results.json').exists() else []
if args.retry_blocked:
 retry={x['repo'] for x in prior if x['status']=='blocked'};items=[x for x in items if x['repo'] in retry]
if args.resume:
 completed={x['repo'] for x in prior if x['status']=='extracted'};items=[x for x in items if x['repo'] not in completed]
results=[x for x in prior if x['status']=='extracted']
def fetch(item):
 repo=item['repo'];dest=out/repo.replace('/','--');archive=out/(repo.replace('/','--')+'.tar.gz');started=time.monotonic()
 try:
  result=subprocess.run(['git','ls-remote','https://github.com/'+repo+'.git','HEAD'],capture_output=True,text=True,timeout=40,check=True)
  sha=result.stdout.split()[0];url='https://codeload.github.com/'+repo+'/tar.gz/'+sha
  h=hashlib.sha256();total=0
  with urllib.request.urlopen(url,timeout=30) as source,archive.open('wb') as target:
   while chunk:=source.read(1024*256):
    total+=len(chunk)
    if total>500*1024*1024:raise RuntimeError('Source archive exceeds 500 MiB per-repository limit')
    if time.monotonic()-started>100:raise RuntimeError('Source download exceeded time limit')
    if shutil.disk_usage(out).free<5*1024**3:raise RuntimeError('Disk reserve reached')
    h.update(chunk);target.write(chunk)
  with tarfile.open(archive) as tar:
   members=tar.getmembers()
   if sum(m.size for m in members)>1500*1024*1024:raise RuntimeError('Extracted source exceeds 1500 MiB limit')
   dest.mkdir(exist_ok=True);tar.extractall(dest,filter='data')
  archive.unlink();return dict(repo=repo,status='extracted',commit=sha,archive_sha256=h.hexdigest(),source_url=url,path=str(dest.relative_to(root)))
 except Exception as e:
  archive.unlink(missing_ok=True)
  if dest.exists():shutil.rmtree(dest)
  return dict(repo=repo,status='blocked',reason=str(e)[:240])
with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
 for future in concurrent.futures.as_completed([pool.submit(fetch,item) for item in items]):
  result=future.result()
  results.append(result);print(result['status'],result['repo'],flush=True)
  (root/'sources/import-results.json').write_text(json.dumps(results,indent=2))
print('Extracted',sum(x['status']=='extracted' for x in results),'of',len(results),flush=True)
