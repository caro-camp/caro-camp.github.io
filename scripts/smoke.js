// 실제 브라우저로 열어서 JS 오류 없이 목록이 그려지는지 확인
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];
p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+path.resolve(__dirname,'..','index.html'));await p.waitForTimeout(1500);
const n=await p.evaluate(()=>document.querySelectorAll('#list > *').length);
console.log('JS 오류',errs.length,'목록 항목',n);await b.close();
if(errs.length||n<1){console.log(errs.join('\n'));process.exit(1)}})();
