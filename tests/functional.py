import asyncio, json
from playwright.async_api import async_playwright
URL='http://localhost:8765/index.html'
results=[]
def check(name, ok, detail=''):
    results.append((name, ok, detail)); print(('PASS ' if ok else 'FAIL ')+name+('  '+str(detail) if detail else ''))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs=[]
        ctx = await b.new_context(viewport={'width':390,'height':844})
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(1200)
        await pg.evaluate("__harisen.save.seenOpening=true")
        # 1. FPS independence (same tap offset)
        for off in [1.70, 1.62, 1.83]:
            ds=[]
            for fps in [30,45,60,120,144]:
                r = await pg.evaluate(f"__harisen.simulate({{courseId:1,tapOffset:{off},fps:{fps},practice:true}})")
                ds.append((fps, r['judge'], r['dist']))
            spread = max(d for _,_,d in ds)-min(d for _,_,d in ds)
            check(f'fps独立 tap={off}s', spread < 0.1 and len(set(j for _,j,_ in ds))==1, f'{ds[0][1]} {ds[0][2]:.3f}m spread={spread:.6f}')
        # 2. boundaries (practice false). ideal tap = T - 0.1 = 1.7 (costume Lv1)
        T = 1.8; delay=0.1
        cases=[(0.040,'PERFECT'),(0.0401,'GREAT'),(-0.085,'GREAT'),(0.0851,'GOOD'),(-0.140,'GOOD'),(0.1401,'GRAZE'),(0.210,'GRAZE'),(-0.2101,'MISS'),(0.2101,'MISS')]
        for e,exp in cases:
            r = await pg.evaluate(f"__harisen.simulate({{courseId:1,tapOffset:{T-delay+e},fps:60,practice:true}})")
            # practice windows are 1.5x -> use non-practice for boundary
            r = await pg.evaluate(f"(async()=>{{const s=JSON.stringify(__harisen.save); const out=await __harisen.simulate({{courseId:1,tapOffset:{T-delay+e},fps:60,practice:false}}); localStorage.setItem('sakura-harisen-v1', s); Object.assign(__harisen.save, JSON.parse(s)); return out}})()")
            check(f'判定境界 e={e*1000:+.1f}ms', r['judge']==exp, r['judge'])
        # practice 1.5x: 0.06 -> PERFECT
        r = await pg.evaluate(f"__harisen.simulate({{courseId:1,tapOffset:{T-delay+0.06},fps:60,practice:true}})")
        check('練習モード 判定1.5倍 (60ms→PERFECT)', r['judge']=='PERFECT' and r['reward'] is None, r['judge'])
        # 3. no input -> MISS, XP8 coin10
        before = await pg.evaluate("({xp:__harisen.save.totalXp, c:__harisen.save.coins})")
        r = await pg.evaluate("__harisen.simulate({courseId:1,tapOffset:null,fps:60})")
        check('無入力→MISS(XP8/coin10)', r['miss']=='none' and r['reward']['xp']==8 and r['reward']['coins']==10, r['reward'])
        # 4. early tap within guard ignored, and multi-tap ignored
        r = await pg.evaluate("""(async()=>{const H=__harisen; await H.enterReady(1,true); H.Clock.virtual=1000; H.Clock.pausedTotal=0; H.onAction(1000);
            H.onAction(1100); const g1 = H.G.run.tapT; // within 0.3s guard -> ignored
            const ideal=1000+1700; for(let t=1000;t<ideal;t+=1000/60){H.Clock.virtual=t;H.tick(1/60);}
            H.onAction(ideal); H.onAction(ideal+5); H.onAction(ideal+30); const r=H.G.run; const out={g1, tap:r.tapT, judge:r.judge.label}; H.Clock.virtual=null; return out})()""")
        check('走り出し直後の二度押しを無視', r['g1'] is None, r)
        check('多重タップは最初の1回だけ', abs(r['tap']-2.7)<1e-9 and r['judge']=='PERFECT', r)
        # 5. too early (outside guard) -> MISS early
        r = await pg.evaluate("__harisen.simulate({courseId:1,tapOffset:1.2,fps:60,practice:true})")
        check('早すぎ→MISS', r['judge']=='MISS' and r['miss']=='early', r['miss'])
        # 6. first clear bonus once + persistence
        await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(1000); await pg.evaluate("__harisen.save.seenOpening=true")
        r1 = await pg.evaluate("__harisen.simulate({courseId:1,tapOffset:1.7,fps:60})")
        r2 = await pg.evaluate("__harisen.simulate({courseId:1,tapOffset:1.7,fps:60})")
        exp1_xp = 20 + int(r1['dist']//50) + 60; exp1_c = 30 + int(r1['dist']*0.1) + 80
        check('初回クリアボーナス1回目のみ', r1['reward']['firstClear'] and r1['reward']['xp']==exp1_xp and r1['reward']['coins']==exp1_c and not r2['reward']['firstClear'], (r1['reward']['xp'], r1['reward']['coins'], r2['reward']['xp']))
        saved = await pg.evaluate("__harisen.save")
        await pg.reload(); await pg.wait_for_timeout(1200)
        after = await pg.evaluate("__harisen.save")
        check('リロード後も進行が残る', after['totalXp']==saved['totalXp'] and after['coins']==saved['coins'] and after['cleared']==[1] and abs(after['best']['1']-r1['dist'])<1e-9, (after['totalXp'], after['coins'], after['cleared']))
        # 7. corrupt save -> confirm modal shown
        await pg.evaluate("localStorage.setItem('sakura-harisen-v1','{broken')"); await pg.reload(); await pg.wait_for_timeout(1200)
        vis = await pg.evaluate("!document.querySelector('#ov-modal').hidden && document.querySelector('#md-title').textContent")
        check('壊れたセーブは確認してから初期化', bool(vis), vis)
        await pg.click('#md-ok'); await pg.wait_for_timeout(300)
        ok = await pg.evaluate("JSON.parse(localStorage.getItem('sakura-harisen-v1')).totalXp===0")
        check('初期化を選ぶと新規データ', ok)
        # 8. full progression with PERFECT taps and greedy upgrades (no dev tools)
        prog = await pg.evaluate("""(async()=>{const H=__harisen; const S=H.save; S.seenOpening=true; const C=H.CFG; let plays=0; const log=[];
          const cap=()=>C.equipmentCapByPlayerLevel[(()=>{let l=0;C.playerXpThresholds.forEach(t=>{if(S.totalXp>=t)l++});return Math.min(l,5)})()-1];
          const cost=L=>C.economy.upgradeBaseCost+C.economy.upgradeCostPerExistingLevel*(L-1);
          const buy=()=>{let ch=true; while(ch){ch=false; for(const k of (S.fanLv<=S.costumeLv?['fanLv','costumeLv']:['costumeLv','fanLv'])){ if(S[k]<10&&S[k]<cap()&&S.coins>=cost(S[k])){S.coins-=cost(S[k]);S[k]++;ch=true;} } } };
          for(let id=1; id<=10 && plays<400; ){
            const c=C.courses[id-1]; const unlocked = id===1 || (S.cleared.includes(id-1) && (()=>{let l=0;C.playerXpThresholds.forEach(t=>{if(S.totalXp>=t)l++});return l})()>=c.requiredPlayerLevel);
            const target = unlocked ? id : id-1;
            const T = C.run.baseDurationSeconds - C.run.durationDecreasePerCostumeLevel*(S.costumeLv-1);
            const r = await H.simulate({courseId:target, tapOffset:T-0.1, fps:60}); plays++; buy();
            if (target===id && r.dist>=c.targetMeters) { log.push(`C${id}:${plays}`); id++; }
          }
          // keep playing course 10 to max out
          while((S.fanLv<10||S.costumeLv<10||S.totalXp<1200) && plays<600){ const T = C.run.baseDurationSeconds - C.run.durationDecreasePerCostumeLevel*(S.costumeLv-1); await H.simulate({courseId:10, tapOffset:T-0.1, fps:60}); plays++; buy(); }
          return {plays, log, cleared:S.cleared, fan:S.fanLv, cos:S.costumeLv, xp:S.totalXp, coins:S.coins};})()""")
        check('全10コースを通常プレイでクリア可能', prog['cleared']==list(range(1,11)), prog['log'])
        check('装備Lv10・PLAYER Lv5に到達', prog['fan']==10 and prog['cos']==10 and prog['xp']>=1200, f"{prog['plays']}プレイ fan{prog['fan']} cos{prog['cos']} xp{prog['xp']}")
        # 9. pause during flight freezes clock
        r = await pg.evaluate("""(async()=>{const H=__harisen; H.save.fanLv=1; H.save.costumeLv=1; H.save.totalXp=0; await H.enterReady(1,false); H.Clock.virtual=1000; H.Clock.pausedTotal=0; H.onAction(1000);
          let t=1000; const step=()=>{t+=1000/60;H.Clock.virtual=t;H.tick(1/60)}; while(t<2700)step(); H.onAction(2700); while(t<3500)step();
          const g=H.G; const x1 = g.run.flightStart; const s1=g.state; document.dispatchEvent(new Event('visibilitychange'));
          // simulate hidden
          Object.defineProperty(document,'hidden',{configurable:true,get:()=>true}); document.dispatchEvent(new Event('visibilitychange'));
          const paused=g.paused; const n1=H.Clock.now(); t+=5000; H.Clock.virtual=t; H.tick(1/60); const n2=H.Clock.now();
          Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});
          H.G.paused=false; H.Clock.resume(); const n3=H.Clock.now(); while(!g.run.done) step(); const d=g.run.L.dist; H.Clock.virtual=null; return {s1,paused,frozen:n2===n1, resumedFrom:n3-n1, done:g.run.done, d}})()""")
        check('タブ離脱で一時停止・時刻凍結', r['paused'] and r['frozen'] and abs(r['resumedFrom'])<1e-6, r)
        check('復帰後も距離は同じ', abs(r['d']-224.611)<0.01, r['d'])
        print('page errors:', errs)
        await b.close()
    fails=[r for r in results if not r[1]]; print(f'\n{len(results)-len(fails)}/{len(results)} passed')
asyncio.run(main())
