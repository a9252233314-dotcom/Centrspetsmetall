'use strict';
document.documentElement.classList.add('js');
const root=document.body.dataset.root||'./';
const brandName=document.querySelector('.brand strong').innerText.replace(/\s+/g,' ').trim();
const email=document.querySelector('.footer-contacts .email').textContent.trim();
const requestDialog=document.getElementById('request-dialog');
const form=document.getElementById('request-form');
const status=document.getElementById('request-status');
let returnFocus=null,lastSuggestion='';
const field=id=>document.getElementById('request-'+id);
function openDialog(dialog){returnFocus=document.activeElement;if(!dialog.open)dialog.showModal();document.body.classList.add('dialog-open');}
function closeDialog(dialog){dialog.close();if(!document.querySelector('dialog[open]'))document.body.classList.remove('dialog-open');if(returnFocus?.isConnected)returnFocus.focus();}
const menu=document.getElementById('menu-toggle');
menu?.addEventListener('click',()=>{const nav=document.getElementById('main-nav');const opened=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(opened));menu.setAttribute('aria-label',opened?'Закрыть меню':'Открыть меню');menu.textContent=opened?'×':'☰';});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menu?.getAttribute('aria-expanded')==='true'){document.getElementById('main-nav').classList.remove('open');menu.setAttribute('aria-expanded','false');menu.textContent='☰';menu.focus();}});
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>closeDialog(document.getElementById(button.dataset.close))));
document.querySelectorAll('dialog').forEach(dialog=>{
 dialog.addEventListener('close',()=>{if(!document.querySelector('dialog[open]'))document.body.classList.remove('dialog-open');});
 dialog.addEventListener('click',event=>{if(event.target!==dialog)return;const bounds=dialog.getBoundingClientRect();if(event.clientX<bounds.left||event.clientX>bounds.right||event.clientY<bounds.top||event.clientY>bounds.bottom)closeDialog(dialog);});
});
document.querySelectorAll('[data-request]').forEach(button=>button.addEventListener('click',()=>{
 const id=button.dataset.request;
 const selected=[...field('product').options].find(o=>o.value===id);
 field('product').value=selected?id:'custom';
 status.textContent='';
 if(!field('message').value||field('message').value===lastSuggestion){lastSuggestion=button.dataset.message||(selected&&id!=='custom'?'Интересует '+selected.textContent.toLowerCase()+'. Прошу уточнить исполнение, стоимость и срок изготовления.':'');field('message').value=lastSuggestion;}
 openDialog(requestDialog);
}));
field('phone').addEventListener('input',()=>field('phone').setCustomValidity(''));
field('email').addEventListener('input',()=>field('phone').setCustomValidity(''));
function validRequest(){
 field('phone').setCustomValidity('');
 if(!field('phone').value.trim()&&!field('email').value.trim())field('phone').setCustomValidity('Укажите телефон или электронную почту для ответа.');
 return form.reportValidity();
}
function composeRequest(){
 const product=field('product').selectedOptions[0].textContent;
 const parts=[['Изделие',product],['Имя',field('name').value.trim()],['Компания',field('company').value.trim()],['Телефон',field('phone').value.trim()],['Email',field('email').value.trim()],['Количество',field('quantity').value.trim()],['Материал / размер',field('material').value.trim()]];
 const body='Здравствуйте!\n\nПрошу рассмотреть изготовление.\n\n'+parts.filter(([,v])=>v).map(([k,v])=>k+': '+v).join('\n')+'\n\nОписание задачи:\n'+field('message').value.trim()+'\n\nСтраница обращения: '+location.href+'\nЧертежи и фотографии при необходимости приложу к письму.\n\n' + brandName;
 return {subject:'Запрос на изготовление — '+product,body};
}
form?.addEventListener('submit',event=>{event.preventDefault();if(!validRequest())return;const request=composeRequest();location.href='mailto:'+email+'?subject='+encodeURIComponent(request.subject)+'&body='+encodeURIComponent(request.body);status.textContent='Открывается ваша почта. Проверьте письмо, прикрепите файлы и отправьте. Если почта не открылась — скопируйте текст или скачайте заявку.';});
document.getElementById('copy-request')?.addEventListener('click',async()=>{if(!validRequest())return;try{await navigator.clipboard.writeText(composeRequest().body);status.textContent='Текст скопирован. Отправьте его на '+email+'.';}catch{status.textContent='Не удалось скопировать автоматически. Скачайте заявку и отправьте её на '+email+'.';}});
document.getElementById('download-request')?.addEventListener('click',()=>{if(!validRequest())return;const request=composeRequest();const blob=new Blob(['\uFEFFКому: '+email+'\nТема: '+request.subject+'\n\n'+request.body],{type:'text/plain;charset=utf-8'});const href=URL.createObjectURL(blob),link=document.createElement('a');link.href=href;link.download=brandName+'-заявка.txt';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(href),1000);status.textContent='Заявка сохранена. Отправьте её на '+email+' с нужными файлами.';});
const search=document.getElementById('catalog-search');
search?.addEventListener('input',()=>{const query=search.value.toLocaleLowerCase('ru').replaceAll('ё','е').trim();let count=0;for(const card of document.querySelectorAll('[data-product-id]')){const visible=card.dataset.search.replaceAll('ё','е').includes(query);card.hidden=!visible;if(visible)count++;}document.getElementById('result-count').textContent=count+' позиций';document.getElementById('empty-state').hidden=count!==0;});
const mainImage=document.querySelector('.product-main-image');
document.querySelectorAll('[data-gallery-src]').forEach(button=>button.addEventListener('click',()=>{mainImage.src=button.dataset.gallerySrc;document.querySelectorAll('[data-gallery-src]').forEach(other=>other.setAttribute('aria-pressed',String(other===button)));}));
document.getElementById('product-zoom')?.addEventListener('click',()=>{const image=document.getElementById('lightbox-image');image.src=mainImage.currentSrc||mainImage.src;image.alt=mainImage.alt;openDialog(document.getElementById('lightbox'));});
const legacy=location.hash.match(/^#product-([a-z-]+)$/);
if(legacy){const routes={'bowl-classic':'kostrovaya-chasha','bowl-decor':'chasha-na-figurnyh-oporah','stove':'chugunnaya-pech','castings':'litye-detali-i-zagotovki','grill-ring':'koltso-stoleshnitsa-s-reshetkoy','stand':'litaya-podstavka-pod-chashu','pattern':'modelnaya-osnastka','decor-elephant':'figura-slon','decor-wolf':'figura-volk','decor-panels':'dekorativnye-paneli','mangal-relief':'mangal-s-relefom','gazebo':'besedka-s-ochagom'};if(routes[legacy[1]])location.replace(root+'products/'+routes[legacy[1]]+'/');}
