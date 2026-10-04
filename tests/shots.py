import asyncio, sys, json
from playwright.async_api import async_playwright
SP='/tmp/claude-0/-home-claude/7a53ad74-232f-5ff1-a790-d3359cdb5b14/scratchpad/'
URL='http://localhost:8765/index.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True)
        pg = await ctx.new_page()
        logs=[]
        pg.on('console', lambda m: logs.append(f'{m.type}: {m.text}'))
        pg.on('pageerror', lambda e: logs.append(f'PAGEERROR: {e}'))
        await pg.goto(URL); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=SP+'p_title.png')
        # opening
        await pg.click('#btn-start'); await pg.wait_for_timeout(1800); await pg.screenshot(path=SP+'p_op1.png')
        await pg.click('#op-next'); await pg.wait_for_timeout(1300); await pg.screenshot(path=SP+'p_op2.png')
        await pg.click('#op-next'); await pg.wait_for_timeout(1000); await pg.screenshot(path=SP+'p_op3.png')
        await pg.click('#op-next'); await pg.wait_for_timeout(800); await pg.screenshot(path=SP+'p_op4.png')
        await pg.click('#op-next'); await pg.wait_for_timeout(1500); await pg.screenshot(path=SP+'p_ready.png')
        # run: press start then tap at ideal
        T = await pg.evaluate("1.8")
        await pg.dispatch_event('#btn-action','pointerdown')
        await pg.wait_for_timeout(900); await pg.screenshot(path=SP+'p_run.png')
        await pg.wait_for_timeout(int((T-0.1-0.9)*1000)-15)
        await pg.dispatch_event('#btn-action','pointerdown')
        await pg.wait_for_timeout(60); await pg.screenshot(path=SP+'p_hit.png')
        await pg.wait_for_timeout(500); await pg.screenshot(path=SP+'p_fly1.png')
        await pg.wait_for_timeout(1500); await pg.screenshot(path=SP+'p_fly2.png')
        await pg.wait_for_timeout(2500); await pg.screenshot(path=SP+'p_fly3.png')
        for i in range(30):
            st = await pg.evaluate("__harisen.G.state")
            if st=='land': break
            await pg.wait_for_timeout(200)
        await pg.wait_for_timeout(400); await pg.screenshot(path=SP+'p_land.png')
        await pg.wait_for_timeout(2600); await pg.screenshot(path=SP+'p_result.png')
        r = await pg.evaluate("({j:__harisen.G.run && __harisen.G.run.judge, d:__harisen.G.run && __harisen.G.run.L && __harisen.G.run.L.dist, rw:__harisen.G.run && __harisen.G.run.reward, save:__harisen.save})")
        print(json.dumps(r, ensure_ascii=False)[:800])
        await pg.evaluate("document.querySelector('#ov-result .scroll').scrollTop=9999"); await pg.wait_for_timeout(300); await pg.screenshot(path=SP+'p_result2.png')
        print('\n'.join(logs[:40]))
        await b.close()
asyncio.run(main())
