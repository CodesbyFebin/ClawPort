import {test} from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const projects=JSON.parse(fs.readFileSync(new URL('../dist/catalog.json',import.meta.url)));
test('catalog has 100+ unique upstream repositories with dated source metadata',()=>{const repos=projects.filter(p=>p.repo).map(p=>p.repo.toLowerCase());assert.ok(repos.length>=100);assert.equal(new Set(repos).size,repos.length);for(const p of projects){assert.ok(p.category);assert.ok(p.checked);if(p.repo)assert.match(p.repo,/^[\w.-]+\/[\w.-]+$/);}});
test('download URLs come from GitHub release assets',()=>{for(const p of projects)for(const a of p.assets){const u=new URL(a.url);assert.equal(u.protocol,'https:');assert.equal(u.hostname,'github.com');assert.ok(u.pathname.includes('/releases/download/'));assert.ok(a.size>=0);}});

test('every repository has an installation page and four platform records',()=>{const matrix=JSON.parse(fs.readFileSync(new URL('../dist/build-matrix.json',import.meta.url)));assert.equal(matrix.length,projects.length*4);for(const p of projects)assert.ok(fs.existsSync(new URL('../dist/projects/'+p.repo.toLowerCase().replace('/','--')+'/index.html',import.meta.url)));});
