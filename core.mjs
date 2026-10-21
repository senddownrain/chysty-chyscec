export const SELECTION='chysty_chyscec.selection.v1', NAMES='chysty_chyscec.names.v1';
export function choose(cards,current=null,rng=crypto){const pool=cards.filter(s=>s.id!==current);if(!pool.length)return null;const max=2**32,limit=max-max%pool.length;let n;do{n=rng.getRandomValues(new Uint32Array(1))[0]}while(n>=limit);return pool[n%pool.length]}
export function loadSelection(raw,cards){if(!raw)return null;const s=JSON.parse(raw);if(s.version!==1||!cards.some(c=>c.id===s.saintId)||!Number.isFinite(Date.parse(s.assignedAt)))throw Error('invalid');return s}
export function nextSelection(card){return {version:1,saintId:card.id,assignedAt:new Date().toISOString()}}
export function loadNames(raw){if(!raw)return [];const v=JSON.parse(raw);if(v.version!==1||!Array.isArray(v.names)||v.names.length>50||v.names.some(n=>typeof n.id!=='string'||typeof n.text!=='string'||!n.text.trim()||n.text.length>100))throw Error('invalid');return v.names}
export function publicCard(card,url){return {title:'Чысты чысцец',text:`${card.displayName}\n${card.originalIntention}`,url}}
