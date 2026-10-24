// CARO 베타 서비스워커: 화면 파일은 캐시 우선, 데이터(data.js·pub.js)는 네트워크 우선(오프라인이면 마지막 데이터)
const V='caro-v4';
const SHELL=['./','index.html','manifest.webmanifest','img/hero.jpg','img/lantern.jpg','icons/icon-192.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=='GET'||u.origin!==location.origin)return;
  const fresh=/\/(data|pub|attr)\.js$|\/$|index\.html$/.test(u.pathname);
  if(fresh){
    e.respondWith(fetch(e.request,{cache:'no-store'}).then(r=>{const c=r.clone();caches.open(V).then(x=>x.put(e.request,c));return r;}).catch(()=>caches.match(e.request)));
  }else{
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(n=>{const c=n.clone();caches.open(V).then(x=>x.put(e.request,c));return n;})));
  }
});
