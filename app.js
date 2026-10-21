'use strict';
const companyEmail='csm-factory@bk.ru';
let products=[],activeProduct=null,lastDialogFocus=null,suggestedMessage='';
const $=id=>document.getElementById(id);
function make(tag,className,text){const element=document.createElement(tag);if(className)element.className=className;if(text!==undefined)element.textContent=text;return element}
function openDialog(id){lastDialogFocus=document.activeElement;$(id).showModal();document.body.classList.add('dialog-open')}
function closeDialog(id){$(id).close();if(!document.querySelector('dialog[open]'))document.body.classList.remove('dialog-open');lastDialogFocus?.focus()}
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>closeDialog(button.dataset.close)));
document.querySelectorAll('dialog').forEach(dialog=>{dialog.addEventListener('close',()=>{if(!document.querySelector('dialog[open]'))document.body.classList.remove('dialog-open')});dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)closeDialog(dialog.id)}})});
$('menu-button').addEventListener('click',()=>{const opened=$('main-nav').classList.toggle('open');$('menu-button').setAttribute('aria-expanded',String(opened))});
$('main-nav').querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{$('main-nav').classList.remove('open');$('menu-button').setAttribute('aria-expanded','false')}));
function renderProducts(filter='all'){
  const grid=$('product-grid');grid.replaceChildren();
  const visible=products.filter(product=>filter==='all'||product.category===filter);
  visible.forEach(product=>{
    const card=make('article','product-card');card.dataset.id=product.id;
    const imageButton=make('button','product-image-button');imageButton.type='button';imageButton.setAttribute('aria-label','Открыть: '+product.name);imageButton.addEventListener('click',()=>showProduct(product.id));
    const image=make('img');image.src=product.image;image.alt=product.name;image.loading='lazy';image.width=650;image.height=480;
    imageButton.append(image,make('span','card-tag',product.tag));
    const body=make('div','product-card-body'),title=make('h3'),titleButton=make('button','',product.name);titleButton.type='button';titleButton.addEventListener('click',()=>showProduct(product.id));title.append(titleButton);
    const bottom=make('div','card-bottom'),details=make('button','','Подробнее ↗');details.type='button';details.addEventListener('click',()=>showProduct(product.id));bottom.append(make('span','',product.category==='projects'?'Обсудить проект':'Расчёт по запросу'),details);
    body.append(make('p','category',product.categoryLabel),title,make('p','',product.subtitle),bottom);card.append(imageButton,body);grid.append(card);
  });
  $('product-count').textContent=visible.length+' / '+products.length+' ПОЗИЦИЙ';
}
function showProduct(id){
  const product=products.find(item=>item.id===id);if(!product)return;
  activeProduct=product;
  $('product-title').textContent=product.name;$('product-category').textContent=product.categoryLabel.toUpperCase();$('product-status').textContent=product.tag;$('product-description').textContent=product.description;$('product-note').textContent=product.note;
  $('product-main-image').src=product.image;$('product-main-image').alt=product.name;
  const thumbnails=$('product-thumbnails');thumbnails.replaceChildren();
  product.gallery.forEach((src,i)=>{const button=make('button',i===0?'active':'');button.type='button';button.setAttribute('aria-label','Фото '+(i+1));const img=make('img');img.src=src;img.alt='';button.append(img);button.addEventListener('click',()=>{$('product-main-image').src=src;thumbnails.querySelectorAll('button').forEach(b=>b.classList.toggle('active',b===button))});thumbnails.append(button)});
  $('product-features').replaceChildren();product.features.forEach(([label,value])=>{const row=make('div');row.append(make('dt','',label),make('dd','',value));$('product-features').append(row)});
  $('product-project').hidden=!product.projectUrl;if(product.projectUrl)$('product-project').href=product.projectUrl;
  openDialog('product-dialog');
}
function requestProduct(id='custom'){
  if($('product-dialog').open)$('product-dialog').close();
  const product=products.find(item=>item.id===id);$('request-product').value=product?id:'custom';$('request-status').textContent='';
  if(!$('request-message').value||$('request-message').value===suggestedMessage){suggestedMessage=product?'Интересует '+product.name.toLowerCase()+'. Прошу уточнить возможность изготовления, комплектацию, стоимость и сроки.':'';$('request-message').value=suggestedMessage;}
  openDialog('request-dialog');
}
document.querySelectorAll('[data-request]').forEach(button=>button.addEventListener('click',()=>requestProduct(button.dataset.request)));
document.querySelectorAll('[data-product]').forEach(button=>button.addEventListener('click',()=>showProduct(button.dataset.product)));
$('product-request').addEventListener('click',()=>requestProduct(activeProduct?.id));
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(item=>{const selected=item===button;item.classList.toggle('active',selected);item.setAttribute('aria-pressed',String(selected))});renderProducts(button.dataset.filter)}));
function composeRequest(){
  const selected=products.find(product=>product.id===$('request-product').value),name=selected?.name||'Изделие по чертежу / своя задача';
  const fields=[['Изделие',name],['Имя',$('request-name').value.trim()],['Компания',$('request-company').value.trim()],['Телефон',$('request-phone').value.trim()],['Email',$('request-email').value.trim()],['Количество',$('request-quantity').value.trim()],['Материал / размер',$('request-material').value.trim()]];
  const body='Здравствуйте!\n\nПрошу рассмотреть заявку на изготовление.\n\n'+fields.filter(([,value])=>value).map(([key,value])=>key+': '+value).join('\n')+'\n\nОписание задачи:\n'+$('request-message').value.trim()+'\n\nЧертежи и фотографии при необходимости приложу к письму.\n\nЗаявка подготовлена на сайте ЦЕНТРСПЕЦМЕТАЛЛ.';
  return {subject:'Запрос на изготовление — '+name,body};
}
function validRequest(){return $('request-form').reportValidity()}
$('request-form').addEventListener('submit',event=>{event.preventDefault();if(!validRequest())return;const request=composeRequest();window.location.href='mailto:'+companyEmail+'?subject='+encodeURIComponent(request.subject)+'&body='+encodeURIComponent(request.body);$('request-status').textContent='Открывается ваша почта. Проверьте письмо, прикрепите файлы и отправьте. Если почта не открылась — скопируйте текст или скачайте заявку.'});
$('copy-request').addEventListener('click',async()=>{if(!validRequest())return;try{await navigator.clipboard.writeText(composeRequest().body);$('request-status').textContent='Текст скопирован. Отправьте его на '+companyEmail+'.'}catch{$('request-status').textContent='Автоматическое копирование недоступно. Скачайте текст заявки и отправьте на '+companyEmail+'.'}});
$('download-request').addEventListener('click',()=>{if(!validRequest())return;const request=composeRequest(),blob=new Blob(['\uFEFFКому: '+companyEmail+'\nТема: '+request.subject+'\n\n'+request.body],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=make('a');a.href=url;a.download='ЦЕНТРСПЕЦМЕТАЛЛ-заявка.txt';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);$('request-status').textContent='Текст заявки сохранён. Отправьте его на '+companyEmail+' с нужными файлами.'});
async function loadProducts(){
  try{const response=await fetch('products.json');if(!response.ok)throw new Error('Catalog unavailable');products=await response.json();renderProducts();products.forEach(product=>{const option=make('option','',product.name);option.value=product.id;$('request-product').append(option)});const productHash=location.hash.match(/^#product-([a-z-]+)$/);if(productHash)showProduct(productHash[1]);return products.length;}
  catch(error){const box=make('div','error-state','Каталог временно не загрузился. Напишите нам: '),link=make('a','',companyEmail);link.href='mailto:'+companyEmail;box.append(link);$('product-grid').replaceChildren(box);$('product-count').textContent='';return 0;}
}
window.catalogReady=loadProducts();
