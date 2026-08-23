import build, content_a, content_b, content_c

secs = content_a.sections() + content_b.sections() + content_c.sections()
html = build.page(secs)
open('vacuum-world-walkthrough.html', 'w').write(html)
print('sections:', len(secs))
print('bytes:', len(html))
