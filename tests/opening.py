import asyncio
from playwright.async_api import async_playwright
SP='/tmp/claude-0/-home-claude/7a53ad74-232f-5ff1-a790-d3359cdb5b14/scratchpad/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await (await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)).new_page()
        await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(1000)
        await pg.click('#btn-start')
        for i in range(4):
            await pg.wait_for_timeout(2000); await pg.screenshot(path=f'{SP}op{i}.png')
            if i<3: await pg.click('#op-next')
        await b.close()
asyncio.run(main())
