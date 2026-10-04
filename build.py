"""src/ と public/ から配信物を作る。

  python3 build.py [公開URL]

  dist/                 : GitHub Pages などに置く完全なサイト（index.html・assets・config）
  build/web/index.html  : claude.ai の公開ページ用（ページ本文のみ。公開時に骨組みが付く）
公開URLは結果画像と投稿文に入るゲームのURL（省略時は表示中のページのURL）。
"""
import pathlib, shutil, sys
root = pathlib.Path(__file__).parent
css = (root / 'src/style.css').read_text()
body = (root / 'src/body.html').read_text()
js = (root / 'src/game.js').read_text()
game_url = sys.argv[1] if len(sys.argv) > 1 else ''
if game_url:
    js = js.replace("const GAME_URL = '';", f"const GAME_URL = '{game_url}';", 1)
head = ('<title>サクラの定時退社！ぶっとびハリセン</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=Martian+Mono:wght@500;700&display=swap">\n')
page = f"{head}<style>\n{css}</style>\n{body}\n<script>\n{js}</script>\n"
meta = ('<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="description" content="オフィスの屋上から、仕事を押し付ける部長を紙ハリセンでぶっ飛ばす。全10コースの飛距離ゲーム。">'
        '<meta name="theme-color" content="#17162C">')
full = f'<!doctype html><html lang="ja"><head>{meta}</head><body>{page}</body></html>\n'
# サイト一式
dist = root / 'dist'
if dist.exists(): shutil.rmtree(dist)
shutil.copytree(root / 'public', dist)
(dist / 'index.html').write_text(full)
(dist / '.nojekyll').write_text('')
# claude.ai 公開ページ用
web = root / 'build/web'; web.mkdir(parents=True, exist_ok=True)
(web / 'index.html').write_text(page)
print('built', len(page) // 1024, 'KB', '/ GAME_URL =', game_url or '(現在のURL)')
