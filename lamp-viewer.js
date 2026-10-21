'use strict';
(()=>{
const host=document.querySelector('[data-lamp]');if(!host)return;
const stage=document.getElementById('lamp-viewer'),fallback=document.getElementById('lamp-fallback'),canvas=document.getElementById('lamp-gl'),svg=document.getElementById('lamp-canvas'),request=document.getElementById('lamp-request'),supply=document.getElementById('lamp-supply'),help=stage.querySelector('.bench-view-help');
const title=document.querySelector('.bench-summary h1').textContent.replace(/\s+/g,' ').trim(),code=document.querySelector('.bench-summary .eyebrow').textContent.split(' · ')[0];
let faces=null,height=3000,fins=Number(host.dataset.fins),view='render',iron='#33453d',yaw=-.58,pitch=.12,frame=0,drag=null,token=0;
let renderer=null;try{renderer=window.createLampRenderer(canvas);}catch{}
function project(v){const [x,y,z]=v,a=Math.cos(yaw),s=Math.sin(yaw),p=Math.sin(pitch),q=Math.cos(pitch),xx=x*a-y*s,yy=x*s+y*a;return [xx,-yy*p-z*q,-yy*q+z*p];}
function marked(){document.querySelectorAll('[data-lamp-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lampView===view)));}
function live(){if(!['head','base'].includes(view))view='perspective';marked();}
function updateRequest(){const color=document.querySelector('[data-lamp-color][aria-pressed="true"]').getAttribute('aria-label');request.dataset.message='Прошу рассмотреть изготовление: '+title+' ('+code+'). Желаемая высота: '+height+' мм. Комплектация: '+supply.value+'. Цвет на визуализации: '+color+'. '+(fins?'Рёбер плафона: '+fins+'. ':'')+'Количество: ____. Территория и задача освещения: ____. Город: ____. Исполнение и светотехнику прошу согласовать.';document.getElementById('lamp-current').textContent='Запрос: '+height+' мм'+(fins?' · Рёбер: '+fins:'')+' · '+supply.value;const qty=document.getElementById('lamp-fin-quantity');if(qty)qty.textContent=fins+' в выбранном эскизе';}
function render(){
 if(!faces)return;
 if(['render','head-render','assembly'].includes(view)){fallback.src=view==='assembly'?stage.dataset.assembly:view==='head-render'?stage.dataset.headRender:stage.dataset.render;fallback.hidden=false;canvas.hidden=true;svg.setAttribute('hidden','');help.textContent=view==='assembly'?'Конструктивная схема · Базовый вариант':view==='head-render'?'Плафон · Рендер базового варианта':'Рендер базового эскиза 3 м · Потяните для 3D';return;}
 let active=faces.map(f=>({...f,v:f.v.map(v=>[v[0],v[1],v[2]+(f.s==='head'||(f.s==='post'&&v[2]>360)?height-3000:0)])}));
 if(view==='head')active=active.filter(f=>f.s==='head');
 if(view==='base')active=active.filter(f=>f.s==='base'||f.s==='post').map(f=>({...f,v:f.v.map(v=>[v[0],v[1],Math.min(v[2],460)])}));
 const projected=active.map(f=>({face:f,vs:f.v.map(project)})),pts=projected.flatMap(f=>f.vs);let xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;for(const p of pts){xmin=Math.min(xmin,p[0]);xmax=Math.max(xmax,p[0]);ymin=Math.min(ymin,p[1]);ymax=Math.max(ymax,p[1]);}
 const scale=Math.min(760/Math.max(1,xmax-xmin),1010/Math.max(1,ymax-ymin)),cx=450-(xmin+xmax)*scale/2,cy=605-(ymin+ymax)*scale/2;
 if(renderer){renderer.draw(active,project,scale,cx,cy,iron,yaw,pitch);canvas.hidden=false;svg.setAttribute('hidden','');stage.dataset.renderer='webgl';}
 else{const ns='http://www.w3.org/2000/svg',fragment=document.createDocumentFragment();projected.sort((a,b)=>a.vs.reduce((s,p)=>s+p[2],0)/a.vs.length-b.vs.reduce((s,p)=>s+p[2],0)/b.vs.length);for(const {face,vs} of projected){const polygon=document.createElementNS(ns,'polygon');polygon.setAttribute('points',vs.map(v=>(v[0]*scale+cx).toFixed(2)+','+(v[1]*scale+cy).toFixed(2)).join(' '));polygon.setAttribute('fill',face.m==='light'?'#e8eddb':face.m==='metal'?'#77827a':iron);polygon.setAttribute('stroke',face.m==='light'?'#d4dcc8':iron);polygon.setAttribute('stroke-width','.4');fragment.append(polygon);}svg.replaceChildren(fragment);svg.removeAttribute('hidden');canvas.hidden=true;stage.dataset.renderer='svg';}
 fallback.hidden=true;help.textContent=view==='base'?'Цоколь и стойка · Фундамент разрабатывается отдельно':'3D · Потяните, чтобы повернуть';
}
function schedule(){if(frame)return;frame=requestAnimationFrame(()=>{frame=0;render();});}
document.querySelectorAll('[data-lamp-view]').forEach(btn=>btn.addEventListener('click',()=>{view=btn.dataset.lampView;[yaw,pitch]=view==='front'?[0,0]:view==='base'?[-.58,.3]:[-.58,.12];marked();schedule();}));
document.querySelectorAll('[data-lamp-height]').forEach(btn=>btn.addEventListener('click',()=>{height=Number(btn.dataset.lampHeight);document.querySelectorAll('[data-lamp-height]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));live();updateRequest();schedule();}));
document.querySelectorAll('[data-lamp-color]').forEach(btn=>btn.addEventListener('click',()=>{iron=btn.dataset.lampColor;document.querySelectorAll('[data-lamp-color]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));live();updateRequest();schedule();}));
document.querySelectorAll('[data-lamp-fins]').forEach(btn=>btn.addEventListener('click',async()=>{const latest=++token;request.disabled=true;stage.setAttribute('aria-busy','true');try{const response=await fetch(btn.dataset.geometry);if(!response.ok)throw Error();const data=await response.json();if(token!==latest)return;faces=data.faces;fins=Number(btn.dataset.lampFins);stage.dataset.finCount=String(fins);stage.dataset.ready='true';stage.classList.add('interactive');document.querySelectorAll('[data-lamp-fins]').forEach(b=>b.setAttribute('aria-pressed',String(b===btn)));view='head';marked();updateRequest();schedule();}catch{if(token===latest)help.textContent='Вариант не загрузился. Выберите его ещё раз.';}finally{if(token===latest){request.disabled=false;stage.removeAttribute('aria-busy');}}}));
supply.addEventListener('change',updateRequest);
stage.addEventListener('pointerdown',event=>{if(!faces||event.button!==0)return;if(['render','assembly'].includes(view))view='perspective';else if(view==='head-render')view='head';marked();drag={x:event.clientX,y:event.clientY,yaw,pitch};stage.setPointerCapture(event.pointerId);stage.classList.add('dragging');schedule();});
stage.addEventListener('pointermove',event=>{if(!drag)return;yaw=drag.yaw+(event.clientX-drag.x)*.008;pitch=Math.max(-.35,Math.min(.9,drag.pitch+(event.clientY-drag.y)*.006));schedule();});
for(const event of ['pointerup','pointercancel','lostpointercapture'])stage.addEventListener(event,()=>{drag=null;stage.classList.remove('dragging');});
updateRequest();fetch(stage.dataset.geometry).then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{if(token)return;faces=data.faces;stage.dataset.ready='true';stage.dataset.finCount=String(fins);stage.classList.add('interactive');render();}).catch(()=>{help.textContent='Статичная проектная визуализация';});
})();
