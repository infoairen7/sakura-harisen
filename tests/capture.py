import asyncio, sys, json, base64
from playwright.async_api import async_playwright
SP='/tmp/claude-0/-home-claude/7a53ad74-232f-5ff1-a790-d3359cdb5b14/scratchpad/'
async def main(course=1, tap=1.69, times=(0.5,1.5,1.75,1.95,2.3,3,5,7.5,8.6,10.2), vw=390, vh=844, prefix='cap', setup=None):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':vw,'height':vh}, device_scale_factor=2)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(1200)
        if setup: await pg.evaluate(setup)
        res = await pg.evaluate(f"__harisen.capture({{courseId:{course}, tapOffset:{tap}, times:{list(times)}}})")
        for i,d in enumerate(res['shots']):
            open(f'{SP}{prefix}_{i}.png','wb').write(base64.b64decode(d.split(',')[1]))
        print('dist', res['dist'], res['judge'], 'errors', errs)
        await b.close()
if __name__=='__main__':
    args = json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
    asyncio.run(main(**args))
