"""Shared Yandex.Metrika installation for published HTML and future builds."""
import re

COUNTER_ID = 113775985
SCRIPT = '''<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=113775985', 'ym');

    ym(113775985, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
'''
NOSCRIPT = '''<noscript><div><img src="https://mc.yandex.ru/watch/113775985" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->'''

def with_metrika(html):
    if 'https://mc.yandex.ru/metrika/tag.js?id=113775985' in html:
        if html.count("ym(113775985, 'init'") != 1 or html.count('https://mc.yandex.ru/watch/113775985') != 1:
            raise ValueError('Duplicate or incomplete Metrika counter')
        return html
    if '</head>' not in html or not re.search(r'<body\b[^>]*>', html, re.I):
        raise ValueError('Metrika requires a complete HTML head and body')
    html = html.replace('</head>', SCRIPT + '</head>', 1)
    return re.sub(r'(<body\b[^>]*>)', lambda match:match[0] + NOSCRIPT, html, count=1, flags=re.I)
