import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await (await b.new_context()).new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""(async()=>{const H=__harisen; H.save.fanLv=1; H.save.costumeLv=1; H.save.totalXp=0; H.save.seenOpening=true; await H.enterReady(1,false); H.Clock.virtual=1000; H.Clock.pausedTotal=0; H.onAction(1000);
          let t=1000; const step=()=>{t+=1000/60;H.Clock.virtual=t;H.tick(1/60)}; while(t<2700)step(); H.onAction(2700); while(t<3500)step();
          const g=H.G; const s1=g.state;
          Object.defineProperty(document,'hidden',{configurable:true,get:()=>true}); document.dispatchEvent(new Event('visibilitychange'));
          const paused=g.paused, overlay=!document.querySelector('#ov-pause').hidden; const n1=H.Clock.now(); t+=5000; H.Clock.virtual=t; H.tick(1/60); const n2=H.Clock.now();
          Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});
          H.G.paused=false; H.Clock.resume(); const n3=H.Clock.now(); while(!g.run.done) step(); const d=g.run.L.dist; H.Clock.virtual=null; return {s1,paused,overlay,frozen:n2===n1, resumedFrom:n3-n1, d}})()""")
        print(r); ok = r['paused'] and r['overlay'] and r['frozen'] and abs(r['resumedFrom'])<1e-6 and abs(r['d']-224.611)<0.01
        print('PASS 一時停止・時刻凍結・復帰後も同距離' if ok else 'FAIL pause', errs)
        await b.close()
asyncio.run(main())
