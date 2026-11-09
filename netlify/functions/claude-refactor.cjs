'use strict';
/* Administrative proxy: default-deny unless CLAUDE_REFACTOR_TOKEN is configured. */
const {timingSafeEqual,createHash}=require('node:crypto');
const reply=(statusCode,message)=>({statusCode,headers:{'Content-Type':'application/json','Cache-Control':'no-store'},body:JSON.stringify({error:message})});
exports.handler=async event=>{
 if(event.httpMethod!=='POST')return reply(405,'Method Not Allowed');
 const secret=process.env.CLAUDE_REFACTOR_TOKEN,provided=event.headers?.['x-admin-token']||'';
 if(!secret||!provided)return reply(403,'Endpoint administrativ indisponibil');
 const a=createHash('sha256').update(secret).digest(),b=createHash('sha256').update(provided).digest();
 if(!timingSafeEqual(a,b))return reply(403,'Acces refuzat');
 if(!event.body||event.body.length>18000)return reply(413,'Payload prea mare');
 if(!process.env.ANTHROPIC_API_KEY)return reply(503,'AI neconfigurat');
 let body;try{body=JSON.parse(event.body)}catch{return reply(400,'JSON invalid')}
 if(!Array.isArray(body?.messages)||body.messages.length>15||body.messages.some(m=>!m||!['user','assistant'].includes(m.role)||typeof m.content!=='string'||m.content.length>2000))return reply(400,'Conținut invalid');
 try{
   const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),25000);
   let res;try{res=await fetch('https://api.anthropic.com/v1/messages',{
     method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json','x-api-key':process.env.ANTHROPIC_API_KEY,'anthropic-version':'2023-06-01'},
     body:JSON.stringify({model:'claude-haiku-4-5-20251001',max_tokens:900,system:'Asistent administrativ NutriSib.',messages:body.messages})
   })}finally{clearTimeout(timer)}
   return {statusCode:res.status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'},body:await res.text()};
 }catch{return reply(503,'Serviciu indisponibil')}
};
