import build, content_a, content_py, content_b, content_c

a = content_a.sections()
secs = a[:1] + content_py.sections() + a[1:] + content_b.sections() + content_c.sections()
for i, sec in enumerate(secs):
    sec['num'] = '%02d' % i
html = build.page(secs)
open('vacuum-world-walkthrough.html', 'w').write(html)
print('sections:', len(secs))
print('bytes:', len(html))
