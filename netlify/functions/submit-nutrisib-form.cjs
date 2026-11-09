'use strict';
/* NutriSib submission endpoint. Requires environment configuration:
 * NUTRISIB_SHEETS_ID, GOOGLE_SERVICE_ACCOUNT_EMAIL, GOOGLE_PRIVATE_KEY
 * Sheet tabs: Programari, Wellness. No personal data stored in git/Netlify logs.
 */
const crypto=require('node:crypto');
const json=(statusCode,body)=>({statusCode,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'},body:JSON.stringify(body)});
const b64=o=>Buffer.from(JSON.stringify(o)).toString('base64url');
function validOrigin(headers){
 const origin=headers.origin,host=headers.host;
 if(!origin||!host)return false;
 try{const url=new URL(origin);return url.protocol==='https:'&&url.host.toLowerCase()===host.toLowerCase()}catch{return false}
}
async function token(){
 const email=process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
 const key=(process.env.GOOGLE_PRIVATE_KEY||'').replace(/\\n/g,'\n');
 if(!email||!key)throw Error('Sheets credentials missing');
 const now=Math.floor(Date.now()/1000);
 const header=b64({alg:'RS256',typ:'JWT'});
 const payload=b64({iss:email,scope:'https://www.googleapis.com/auth/spreadsheets',aud:'https://oauth2.googleapis.com/token',iat:now,exp:now+3500});
 const signed=header+'.'+payload;
 const signature=crypto.createSign('RSA-SHA256').update(signed).sign(key).toString('base64url');
 const params=new URLSearchParams({grant_type:'urn:ietf:params:oauth:grant-type:jwt-bearer',assertion:signed+'.'+signature});
 const res=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:params.toString()});
 if(!res.ok)throw Error('Google authorization unavailable');
 const data=await res.json();if(!data.access_token)throw Error('No Google access token');return data.access_token;
}
const basic=['name','phone','email','age','sex'];
function clean(value){
 if(Array.isArray(value))return value.filter(v=>typeof v==='string').slice(0,40).map(v=>v.slice(0,170));
 if(typeof value==='string')return value.slice(0,900).trim();
 return '';
}
const limited=new Map();
exports.handler=async event=>{
 if(event.httpMethod==='GET'){
   const configured=Boolean(process.env.NUTRISIB_FORMS_ENABLED==='true'&&process.env.NUTRISIB_SHEETS_ID&&process.env.GOOGLE_PRIVATE_KEY&&process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL);
   return json(200,{ready:configured});
 }
 if(event.httpMethod!=='POST')return json(405,{error:'Metodă neacceptată.'});
 if(!validOrigin(event.headers||{}))return json(403,{error:'Origine neacceptată.'});
 if(process.env.NUTRISIB_FORMS_ENABLED!=='true')return json(503,{error:'Formularul este temporar indisponibil pentru trimitere. Folosește pagina Contact.'});
 if(!process.env.NUTRISIB_SHEETS_ID||!process.env.GOOGLE_PRIVATE_KEY||!process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL)return json(503,{error:'Formularul este în pregătire. Contactează-ne direct.'});
 if(!event.body||event.body.length>18000)return json(413,{error:'Date prea lungi.'});
 const ip=String(event.headers['x-nf-client-connection-ip']||event.headers['client-ip']||'unknown').slice(0,100);
 const now=Date.now(),r=limited.get(ip);
 if(limited.size>2000){for(const [k,v] of limited)if(now-v.t>3600000)limited.delete(k)}
 if(r&&now-r.t<600000&&r.n>=3)return json(429,{error:'Prea multe solicitări. Reîncearcă mai târziu.'});
 if(!r||now-r.t>600000)limited.set(ip,{t:now,n:1});else r.n++;
 let body;try{body=JSON.parse(event.body)}catch{return json(400,{error:'Cerere invalidă.'})}
 if(!body||!['programare','wellness'].includes(body.form)||body.website)return json(400,{error:'Date invalide.'});
 if(!body.consentPrivacy||!body.consentSensitive)return json(422,{error:'Lipsește acordul necesar procesării.'});
 if(!basic.every(k=>typeof body[k]==='string'&&body[k].trim().length>0)&&body.form==='programare')return json(422,{error:'Completează datele obligatorii.'});
 if(typeof body.name!=='string'||body.name.length<3||typeof body.email!=='string'||!/^.+@[^@\s]+\.[^@\s]+$/.test(body.email)||typeof body.phone!=='string'||body.phone.length<7)return json(422,{error:'Numele, telefonul sau e-mailul sunt invalide.'});
 if(body.form==='programare'&&(!body.service||!body.age||!body.sex||!body.channel))return json(422,{error:'Completează datele obligatorii ale programării.'});
 if(body.form==='wellness'&&(!body.birthDate||!body.sex||!body.height||!body.weight||!body.priority||!body.occupation))return json(422,{error:'Completează câmpurile necesare profilului wellness.'});
 if(Object.keys(body).length>70)return json(413,{error:'Prea multe câmpuri.'});
 const cleaned={};for(const [key,val] of Object.entries(body))if(/^[A-Za-z][A-Za-z0-9]{0,40}$/.test(key))cleaned[key]=clean(val);
 // Avoid spreadsheet formula execution in both values and the JSON detail column.
 const safe=v=>{const value=String(v??'');return /^[=+\-@\t\r]/.test(value)?"'"+value:value};
 const id=crypto.randomUUID();
 const summary=[new Date().toISOString(),id,body.form,body.name||'',body.sex||'',body.phone||'',body.email||'',body.age||body.birthDate||'',body.service||body.priority||'',body.channel||'',String(!!body.consentSensitive),String(!!body.consentPhone),String(!!body.consentEmail),String(!!body.consentPhotoPrivate),String(!!body.consentPhotoSocial),JSON.stringify(cleaned),String(!!body.consentPrivacy),'NutriSib-formulare-v1','Nouă',''];
 const tab=body.form==='programare'?'Programari':'Wellness';
 try{
   const bearer=await token();
   const sheet=encodeURIComponent(tab)+'!A:T';
   const endpoint='https://sheets.googleapis.com/v4/spreadsheets/'+encodeURIComponent(process.env.NUTRISIB_SHEETS_ID)+'/values/'+sheet+':append?valueInputOption=RAW&insertDataOption=INSERT_ROWS';
   const response=await fetch(endpoint,{method:'POST',headers:{'Authorization':'Bearer '+bearer,'Content-Type':'application/json'},body:JSON.stringify({majorDimension:'ROWS',values:[summary.map(safe)]})});
   if(!response.ok){console.error('Sheet append error',response.status);return json(502,{error:'Înregistrarea nu a reușit. Nu retrimite imediat; contactează-ne.'})}
   return json(200,{ok:true,id});
 }catch(e){console.error('Form integration error',e?.name);return json(503,{error:'Serviciul nu este disponibil momentan. Contactează-ne.'})}
};
