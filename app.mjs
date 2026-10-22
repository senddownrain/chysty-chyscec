import {saintPrayer} from './prayers.mjs';
import {revealFragment} from './navigation.mjs';
import {imageSizes} from './image-sizes.mjs';
import data from './saints.mjs';
import {SELECTION,NAMES,choose,loadSelection,nextSelection,loadNames,publicCard} from './core.mjs';
// Resolve the web root for both GitHub project Pages and a custom domain.
const siteURL=new URL('./',location.href);
const $=id=>document.getElementById(id), cards=data.saints;
$('print-site-url').textContent=siteURL.host+siteURL.pathname.replace(/\/$/,'');
let selection=null,names=[],storageOK=true,dialogAction=null;
const warn=t=>{$('status').textContent=t};
function read(key){try{return localStorage.getItem(key)}catch{storageOK=false;return null}}
function save(key,value){try{localStorage.setItem(key,JSON.stringify(value))}catch{storageOK=false;warn('Захаванне ў браўзеры недаступнае. Даныя застануцца толькі ў гэтай адкрытай сесіі.')}}
try{selection=loadSelection(read(SELECTION),cards)}catch{warn('Захаваны выбар не ўдалося прачытаць. Можна зрабіць новы выбар.')}try{names=loadNames(read(NAMES))}catch{$('names-status').textContent='Захаваныя імёны не ўдалося прачытаць. Можна стварыць новы спіс.'}
if(!storageOK)warn('Захаванне ў браўзеры недаступнае. Даныя застануцца толькі ў гэтай адкрытай сесіі.');
const current=()=>cards.find(s=>s.id===selection?.saintId);
// Editorial status describes the source text; it does not gate draft functionality.
const pool=()=>cards;
function render(){const c=current();renderSaintPrayer(c);renderPrintCard(c);$('hero-action').textContent=c?'Мой святы ↗':'Атрымаць святога ↗';$('prayer-intention').textContent=c?c.originalIntention:'Спачатку атрымайце святога — тут з’явіцца ваша малітоўная інтэнцыя.';$('prayer-card-link').textContent=c?'Вярнуцца да маёй карткі ↗':'Атрымаць святога ↗';$('empty').hidden=!!c;$('saint-card').hidden=!c;if(!c){$('assign').disabled=!pool().length;return}$('saint-name').textContent=c.displayName;$('intention').textContent=c.originalIntention;$('biography').textContent=c.biography;$('card-state').textContent='МОЙ СВЯТЫ';$('replace').disabled=pool().filter(s=>s.id!==c.id).length===0;renderSaintImage(c)}

function assign(){const c=choose(pool(),selection?.saintId);if(!c)return;selection=nextSelection(c);save(SELECTION,selection);render();$('saint-name').setAttribute('tabindex','-1');$('saint-name').focus()}
function ask(title,copy,yes,action){$('dialog-title').textContent=title;$('dialog-copy').textContent=copy;$('dialog-yes').textContent=yes;dialogAction=action;$('confirm').returnValue='';$('confirm').showModal()}
$('confirm').addEventListener('close',()=>{if($('confirm').returnValue==='confirm')dialogAction?.();dialogAction=null});
$('assign').addEventListener('click',assign);
$('replace').addEventListener('click',()=>ask('Змяніць святога?','Новы святы заменіць цяперашняга. Папярэдні выбар не захаваецца. Працягнуць? Імёны вашых блізкіх застануцца.','Так, змяніць',assign));
function renderNames(){const list=$('names-list');list.replaceChildren();for(const n of names){const li=document.createElement('li'),t=document.createElement('span'),b=document.createElement('button');t.textContent=n.text;b.type='button';b.textContent='×';b.setAttribute('aria-label','Выдаліць імя');b.addEventListener('click',()=>{names=names.filter(x=>x.id!==n.id);save(NAMES,{version:1,names});renderNames()});li.append(t,b);list.append(li)}$('names-empty').hidden=!!names.length;$('clear-names').hidden=!names.length}
$('names-form').addEventListener('submit',e=>{e.preventDefault();const text=$('name').value.trim();if(!text){$('names-status').textContent='Увядзіце імя.';return}if(text.length>100||names.length>=50){$('names-status').textContent='Можна захаваць да 50 імёнаў, кожнае — да 100 знакаў.';return}names.push({id:crypto.randomUUID(),text});save(NAMES,{version:1,names});$('name').value='';$('names-status').textContent='Імя дададзена.';renderNames()});
$('clear-names').addEventListener('click',()=>ask('Выдаліць усе імёны?','Спіс будзе выдалены з гэтага браўзера. Выбар святога застанецца.','Так, выдаліць',()=>{names=[];save(NAMES,{version:1,names});renderNames()}));
function appendCredit(target,meta){
  target.replaceChildren();
  if(!meta)return;
  const source=document.createElement('a');source.href=meta.source;source.textContent=meta.credit;
  const license=document.createElement('a');license.href=meta.licenseURL;license.textContent=meta.license;
  target.append(source,document.createTextNode(' · '),license,document.createTextNode(' · Памяншэнне, WebP; без абрэзкі.'));
}
function renderSaintImage(card){
  const visual=document.querySelector('.saint-visual');visual.replaceChildren();
  const frame=document.createElement('div');frame.className='saint-image-frame';
  const meta=imageSizes[card.id];
  if(meta){
    const img=document.createElement('img');img.width=meta.width;img.height=meta.height;
    img.alt=card.displayName;img.className='saint-photo';img.loading='eager';img.decoding='async';
    frame.setAttribute('aria-busy','true');
    img.addEventListener('load',()=>frame.removeAttribute('aria-busy'));
    img.addEventListener('error',()=>{frame.removeAttribute('aria-busy');frame.replaceChildren();frame.textContent='✧ Выява часова недаступная'});
    // Set responsive attributes before src to avoid an unnecessary fallback request.
    img.sizes=meta.sizes;img.srcset=meta.srcset;img.src=meta.src;frame.append(img);
    const credit=document.createElement('small');appendCredit(credit,meta);visual.append(frame,credit);
  }else{
    const icon=document.createElement('span');icon.className='saint-icon';icon.textContent='✧';icon.setAttribute('aria-hidden','true');
    const note=document.createElement('small');note.textContent='Выява чакае праверкі';frame.append(icon,note);visual.append(frame);
  }
}
function renderPrintCard(card,loadImage=false){
  const image=$('print-photo');$('print-card').hidden=!card;
  if(!card){image.removeAttribute('src');image.hidden=true;$('print-credit').replaceChildren();return}
  $('print-saint-name').textContent=card.displayName;$('print-intention').textContent=card.originalIntention;
  const meta=imageSizes[card.id];appendCredit($('print-credit'),meta);
  image.alt=card.displayName;if(!meta)image.hidden=true;
  if(meta){image.width=meta.width;image.height=meta.height}
  if(loadImage&&meta){
    if(image.getAttribute('src')!==meta.print){image.hidden=false;image.src=meta.print;}
  }else{image.hidden=!meta;image.removeAttribute('src')}
}
$('print-photo').addEventListener('error',()=>{$('print-photo').hidden=true;$('print-status').textContent='Выяву не ўдалося загрузіць. Картку можна раздрукаваць без яе.'});
$('print').addEventListener('click',()=>{const card=current();if(!card)return;$('print-status').textContent='';renderPrintCard(card);renderPrintCard(card,true);$('print-preview').showModal()});
$('print-close').addEventListener('click',()=>$('print-preview').close());
$('print-confirm').addEventListener('click',async()=>{if(!current())return;const button=$('print-confirm');button.disabled=true;try{const image=$('print-photo');if(!image.hidden&&image.hasAttribute('src')&&image.decode){try{await image.decode()}catch{image.hidden=true;$('print-status').textContent='Выяву не ўдалося загрузіць. Картка будзе без яе.'}}if(document.fonts?.ready)await document.fonts.ready;window.print()}catch{$('print-status').textContent='Не ўдалося адкрыць друк. Паспрабуйце яшчэ раз.'}finally{button.disabled=false}});
$('share').addEventListener('click',async()=>{const c=current();if(!c)return;const payload=publicCard(c,siteURL.href);try{if(navigator.share){await navigator.share(payload)}else if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(`${payload.title}\n${payload.text}\n${payload.url}`);warn('Картка і спасылка скапіяваныя. Прыватныя імёны не ўключаныя.')}else{warn('Капіяванне недаступнае. Адрас сайта: '+payload.url)}}catch(e){if(e.name!=='AbortError')warn('Не ўдалося падзяліцца. Можна скапіяваць адрас сайта з радка браўзера.')}});
render();renderNames();

window.addEventListener('beforeprint',()=>renderPrintCard(current(),true));
window.addEventListener('hashchange',()=>revealFragment(document,location.hash));
document.addEventListener('click',event=>{const link=event.target.closest?.('a[href^="#"]');if(link)revealFragment(document,link.getAttribute('href'))});
revealFragment(document,location.hash);

function renderSaintPrayer(card){const text=saintPrayer(card);$('saint-prayer-text').textContent=text||'Атрымайце святога, каб маліцца разам з ім у інтэнцыі сваёй карткі.';$('saint-prayer-invite').hidden=!!text}
