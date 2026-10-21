// Node 22+. Run a static server in this repo and Chrome with --remote-debugging-port=9227.
// From repo root: node tools/export-bench-pdfs.mjs http://127.0.0.1:8843/ http://127.0.0.1:9227
// Uses a dedicated browser tab; closes it afterwards. Produces A4 landscape PDFs.
import fs from 'node:fs';
const base=process.argv[2]||'http://127.0.0.1:8843/';
const endpoint=process.argv[3]||'http://127.0.0.1:9227';
const models=JSON.parse(fs.readFileSync(new URL('../lamps.json',import.meta.url),'utf8'));
const tab=await fetch(endpoint+'/json/new?'+encodeURIComponent(base),{method:'PUT'}).then(r=>r.json());
const ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
let id=0;const pending=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result);}};
function send(method,params={}){return new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}));});}
try{
 await send('Page.enable');
 for(const b of models){
  const html=`<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>${b.code} — ${b.name} — габаритный эскиз и узел</title><style>@page{size:A4 landscape;margin:0}html,body{margin:0;padding:0}img{width:297mm;height:210mm;display:block;break-after:page}img:last-child{break-after:auto}</style></head><body><img src="${base}assets/lamps/${b.id}-drawing.svg"><img src="${base}assets/lamps/${b.id}-assembly.svg"></body></html>`;
  const tree=await send('Page.getFrameTree');await send('Page.setDocumentContent',{frameId:tree.frameTree.frame.id,html});
  const result=await send('Runtime.evaluate',{expression:'Promise.all([...document.images].map(i=>i.decode()))',awaitPromise:true});if(result.exceptionDetails)throw Error('Drawing failed to load');
  const pdf=await send('Page.printToPDF',{printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false,marginTop:0,marginBottom:0,marginLeft:0,marginRight:0});
  const output=new URL(`../assets/lamps/${b.id}-drawing.pdf`,import.meta.url);fs.writeFileSync(output,Buffer.from(pdf.data,'base64'));console.log(b.id+': PDF written');
 }
}finally{ws.close();await fetch(endpoint+'/json/close/'+tab.id);}
