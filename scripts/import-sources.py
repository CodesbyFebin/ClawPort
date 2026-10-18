"""Download source only. Does not execute imported builds or install dependencies."""
import argparse,concurrent.futures,hashlib,json,pathlib,subprocess,tarfile,urllib.request,shutil,time
root=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=0);p.add_argument('--jobs',type=int,default=6);args=p.parse_args()
items=json.loads((root/'sources/manifest.json').read_text());items=items[:args.limit] if args.limit else items
out=root/'imported-sources';out.mkdir(exist_ok=True)
results=[]
def fetch(item):
 repo=item['repo'];dest=out/repo.replace('/','--');archive=out/(repo.replace('/','--')+'.tar.gz');started=time.monotonic()
 try:
  result=subprocess.run(['git','ls-remote','https://github.com/'+repo+'.git','HEAD'],capture_output=True,text=True,timeout=40,check=True)
  sha=result.stdout.split()[0];url='https://codeload.github.com/'+repo+'/tar.gz/'+sha
  h=hashlib.sha256();total=0
  with urllib.request.urlopen(url,timeout=30) as source,archive.open('wb') as target:
   while chunk:=source.read(1024*256):
    total+=len(chunk)
    if total>100*1024*1024:raise RuntimeError('Source archive exceeds 100 MiB per-repository limit')
    if time.monotonic()-started>100:raise RuntimeError('Source download exceeded time limit')
    h.update(chunk);target.write(chunk)
  with tarfile.open(archive) as tar:
   members=tar.getmembers()
   if sum(m.size for m in members)>350*1024*1024:raise RuntimeError('Extracted source exceeds 350 MiB limit')
   dest.mkdir(exist_ok=True);tar.extractall(dest,filter='data')
  archive.unlink();return dict(repo=repo,status='extracted',commit=sha,archive_sha256=h.hexdigest(),source_url=url,path=str(dest.relative_to(root)))
 except Exception as e:
  archive.unlink(missing_ok=True)
  if dest.exists():shutil.rmtree(dest)
  return dict(repo=repo,status='blocked',reason=str(e)[:240])
with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
 for result in pool.map(fetch,items):
  results.append(result);print(result['status'],result['repo'],flush=True)
  (root/'sources/import-results.json').write_text(json.dumps(results,indent=2))
print('Extracted',sum(x['status']=='extracted' for x in results),'of',len(results),flush=True)
