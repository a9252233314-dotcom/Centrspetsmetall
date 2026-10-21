'use strict';
// Presentation geometry only. The fixed downloadable sheet remains the base sketch.
(()=>{
const host=document.querySelector('[data-bench]');if(!host)return;
const stage=document.getElementById('bench-viewer'),svg=document.getElementById('bench-canvas'),fallback=document.getElementById('bench-fallback');
const request=document.getElementById('bench-request'),supply=document.getElementById('bench-supply');
const modelName=document.querySelector('.bench-summary h1').innerText.replace(/\s+/g,' ').trim();
const code=document.querySelector('.bench-summary .eyebrow').textContent.split(' · ')[0];
let faces=null,yaw=-.66,pitch=.30,length=1800,iron='#33453d',view='render',drag=null;
const ns='http://www.w3.org/2000/svg';let frame=0;
const canvas=document.getElementById('bench-gl');let renderer=null;try{renderer=window.createBenchRenderer?.(canvas);}catch{}
function projection(v){const [x,y,z]=v;const a=Math.cos(yaw),s=Math.sin(yaw),p=Math.sin(pitch),q=Math.cos(pitch);let xx=x*a-y*s,yy=x*s+y*a;return [xx,-yy*p-z*q,-yy*q+z*p];}
function markView(){document.querySelectorAll('[data-bench-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.benchView===view)));}
function liveView(){view='perspective';markView();}
function shade(face){const vs=face.v,a=vs[1].map((v,i)=>v-vs[0][i]),b=vs[2].map((v,i)=>v-vs[0][i]);const n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],ln=Math.hypot(...n)||1;let light=.70+.28*Math.abs(n[0]*-.3+n[1]*-.4+n[2]*.86)/ln;if(Math.abs(n[2])/ln>.8)light=1.12;const base=(face.m==='wood'?'#a56d42':face.m==='iron'?iron:'#8b938a').slice(1);return '#'+[0,2,4].map(i=>Math.min(255,Math.round(parseInt(base.slice(i,i+2),16)*light)).toString(16).padStart(2,'0')).join('');}
function render(){
 if(!faces)return;
 if(view==='render'||view==='joint'){fallback.src=view==='joint'?stage.dataset.joint:stage.dataset.render;fallback.hidden=false;svg.setAttribute('hidden','');canvas.hidden=true;document.querySelector('.bench-view-help').textContent=view==='joint'?'Узел 01 · Условное изображение крепежа':'Рендер базового эскиза 1,8 м · Потяните для 3D';return;}
 const active=view==='support'?faces.filter(f=>f.g==='support-right').map(f=>({...f,v:f.v.map(v=>[v[0]-650,v[1],v[2]])})):faces.map(f=>({...f,v:f.v.map(v=>[f.m==='wood'?v[0]*length/1800:v[0]+Math.sign(v[0])*(length-1800)/2,v[1],v[2]])}));
 const projected=active.map(f=>({face:f,vs:f.v.map(projection)}));const pts=projected.flatMap(f=>f.vs);const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys),scale=Math.min(1050/Math.max(1,xmax-xmin),720/Math.max(1,ymax-ymin)),cx=600-(xmin+xmax)/2*scale,cy=445-(ymin+ymax)/2*scale;
 projected.sort((a,b)=>a.vs.reduce((s,p)=>s+p[2],0)/a.vs.length-b.vs.reduce((s,p)=>s+p[2],0)/b.vs.length);
 if(renderer){renderer.draw(active,projection,scale,cx,cy,iron,yaw,pitch);canvas.hidden=false;svg.setAttribute('hidden','');fallback.hidden=true;document.querySelector('.bench-view-help').textContent='3D · Потяните, чтобы повернуть';stage.dataset.renderer='webgl';return;}
 const fragment=document.createDocumentFragment();const ellipse=document.createElementNS(ns,'ellipse');ellipse.setAttribute('cx','610');ellipse.setAttribute('cy','748');ellipse.setAttribute('rx','400');ellipse.setAttribute('ry','27');ellipse.setAttribute('fill','#24382b');ellipse.setAttribute('opacity','.08');fragment.append(ellipse);
 for(const {face,vs} of projected){const polygon=document.createElementNS(ns,'polygon');polygon.setAttribute('points',vs.map(p=>(p[0]*scale+cx).toFixed(2)+','+(p[1]*scale+cy).toFixed(2)).join(' '));const color=shade(face);polygon.setAttribute('fill',color);polygon.setAttribute('stroke',color);polygon.setAttribute('stroke-width','.65');polygon.setAttribute('stroke-linejoin','round');fragment.append(polygon);}
 svg.replaceChildren(fragment);svg.removeAttribute('hidden');fallback.hidden=true;canvas.hidden=true;stage.dataset.renderer='svg';document.querySelector('.bench-view-help').textContent='3D · Потяните, чтобы повернуть';
}
function schedule(){if(frame)return;frame=requestAnimationFrame(()=>{frame=0;render();});}
function updateRequest(){const color=document.querySelector('[data-bench-color][aria-pressed="true"]').getAttribute('aria-label');request.dataset.message='Прошу рассмотреть изготовление: '+modelName+' ('+code+'). Комплектация: '+supply.value+'. Желаемая длина: '+length+' мм. Цвет на визуализации: '+color+'. Количество: ____. Город: ____. Итоговое исполнение прошу согласовать.';document.getElementById('bench-current').textContent='Запрос: '+length+' мм · '+supply.value;}
document.querySelectorAll('[data-bench-view]').forEach(btn=>btn.addEventListener('click',()=>{view=btn.dataset.benchView;const angles={render:[-.66,.30],joint:[-.66,.30],perspective:[-.66,.30],front:[0,0],side:[-Math.PI/2,0],support:[-.66,.30]};[yaw,pitch]=angles[view];markView();schedule();}));
document.querySelectorAll('[data-bench-length]').forEach(btn=>btn.addEventListener('click',()=>{length=Number(btn.dataset.benchLength);liveView();document.querySelectorAll('[data-bench-length]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));updateRequest();schedule();}));
document.querySelectorAll('[data-bench-color]').forEach(btn=>btn.addEventListener('click',()=>{iron=btn.dataset.benchColor;liveView();document.querySelectorAll('[data-bench-color]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));updateRequest();schedule();}));
supply.addEventListener('change',updateRequest);
stage.addEventListener('pointerdown',event=>{if(!faces||event.button!==0)return;if(view==='render'||view==='joint')liveView();drag={x:event.clientX,y:event.clientY,yaw,pitch};stage.setPointerCapture(event.pointerId);stage.classList.add('dragging');schedule();});
stage.addEventListener('pointermove',event=>{if(!drag)return;yaw=drag.yaw+(event.clientX-drag.x)*.008;pitch=Math.max(-.35,Math.min(.9,drag.pitch+(event.clientY-drag.y)*.006));schedule();});
function stop(){drag=null;stage.classList.remove('dragging');}stage.addEventListener('pointerup',stop);stage.addEventListener('pointercancel',stop);stage.addEventListener('lostpointercapture',stop);
updateRequest();fetch(stage.dataset.geometry).then(r=>{if(!r.ok)throw Error('Geometry unavailable');return r.json();}).then(data=>{faces=data.faces;stage.classList.add('interactive');stage.dataset.ready='true';render();}).catch(()=>{document.querySelector('.bench-view-help').textContent='Статичная проектная визуализация';});
})();
