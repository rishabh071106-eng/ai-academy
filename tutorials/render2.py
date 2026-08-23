import build2, content2_a, content2_b, content2_c, content2_d, content2_e, content2_f

secs = (content2_a.sections() + content2_b.sections() + content2_c.sections()
        + content2_d.sections() + content2_e.sections() + content2_f.sections())
for i, s in enumerate(secs):
    s['num'] = '%02d' % i
html = build2.page(secs)
open('attention-worked-out.html', 'w').write(html)
print('sections:', len(secs))
print('bytes:', len(html), '=', round(len(html) / 1e6, 2), 'MB')
