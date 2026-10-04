import asyncio
from playwright.async_api import async_playwright
SP='/tmp/claude-0/-home-claude/7a53ad74-232f-5ff1-a790-d3359cdb5b14/scratchpad/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs=[]
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(1200)
        # give some progress
        await pg.evaluate("""(()=>{const s=__harisen.save; s.seenOpening=true; s.cleared=[1,2,3]; s.best={1:224.6,2:281.3,3:250.2,4:120.5}; s.totalXp=400; s.coins=260; s.fanLv=3; s.costumeLv=4; })()""")
        await pg.evaluate("__harisen.show('courses')"); await pg.wait_for_timeout(700); await pg.screenshot(path=SP+'s_courses.png')
        await pg.click('.course >> nth=3'); await pg.wait_for_timeout(700); await pg.screenshot(path=SP+'s_sheet.png')
        await pg.click('#sh-equip-btn'); await pg.wait_for_timeout(800); await pg.screenshot(path=SP+'s_equip.png', full_page=False)
        await pg.evaluate("document.querySelector('#scr-equip .scroll').scrollTop=600"); await pg.wait_for_timeout(300); await pg.screenshot(path=SP+'s_equip2.png')
        await pg.evaluate("__harisen.show('reward')"); await pg.wait_for_timeout(600); await pg.screenshot(path=SP+'s_reward.png')
        await pg.evaluate("__harisen.show('dev')"); await pg.wait_for_timeout(1500); await pg.screenshot(path=SP+'s_dev.png')
        await pg.evaluate("__harisen.show('title')"); await pg.wait_for_timeout(600); await pg.screenshot(path=SP+'s_title.png')
        # landscape phone
        await pg.set_viewport_size({'width':844,'height':390}); await pg.evaluate("__harisen.enterReady(4,false)"); await pg.wait_for_timeout(1200); await pg.screenshot(path=SP+'s_land_ready.png')
        await pg.dispatch_event('#btn-action','pointerdown'); await pg.wait_for_timeout(1000); await pg.screenshot(path=SP+'s_land_run.png')
        # desktop
        await pg.set_viewport_size({'width':1280,'height':800}); await pg.wait_for_timeout(2500); await pg.screenshot(path=SP+'s_desk.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
