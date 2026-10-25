"""Public company identity and requisites copied from the supplied company card."""
from html import escape
from analytics import with_metrika

def company_fields(site):
    c=site['CONFIG']['legalEntity']
    return [('Организация',c['name']),('Адрес организации',c['address']),('ИНН',c['inn']),('КПП',c['kpp']),('ОГРН',c['ogrn']),('Расчётный счёт',c['account']),('Банк',c['bank']),('БИК',c['bik']),('Корреспондентский счёт',c['correspondentAccount'])]

def company_summary(site,r):
    c=site['CONFIG']['legalEntity'];e=site['e']
    return f'<p class="legal-footer">{e(c["name"])} · ИНН {e(c["inn"])}<br><a href="{r}requisites/">Реквизиты организации ↗</a></p>'

def build_company_page(site):
    root=site['ROOT'];config=site['CONFIG'];e=site['e'];r='../'
    rows=''.join(f'<div><dt>{e(label)}</dt><dd>{e(value)}</dd></div>' for label,value in company_fields(site))
    content=site['heading']('Реквизиты организации',config['name']+' — бренд '+config['legalEntity']['name']+'. Контакты для обсуждения заказа и данные организации.','Компания')
    content+=f'<section class="container company-requisites"><div class="company-card"><p class="eyebrow">{e(config["name"])}</p><h2>{e(config["legalEntity"]["name"])}</h2><dl class="company-data">{rows}</dl><div class="documents"><a class="document-link" href="{r}assets/tlm-requisites.pdf" download>Скачать реквизиты · PDF ↓</a></div></div><aside class="company-contact"><h2>Обсудить заказ</h2><p>Роберт — обращения по изготовлению изделий и литью.</p>{site["contact_phones"]()}<a href="mailto:{config["email"]}">{e(config["email"])}</a><p>Пришлите описание изделия, размеры, материал, количество и имеющиеся чертежи.</p>{site["button"]("Подготовить заявку")}</aside></section>'
    site['page']('requisites/','Реквизиты ООО «Сфералит» — '+config['name'],'Реквизиты ООО «Сфералит»: ИНН '+config['legalEntity']['inn']+', ОГРН '+config['legalEntity']['ogrn']+', адрес в Туле, банковские данные и контакты для заказов.',content,[('Контакты','contacts/'),('Реквизиты',None)])
    standalone='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Реквизиты ООО «Сфералит» — Тульская литейная мануфактура</title><style>@page{size:A4;margin:20mm}body{font:14px/1.5 Arial,sans-serif;color:#25372b;margin:0}header{display:flex;align-items:center;gap:22px;border-bottom:2px solid #25372b;padding-bottom:22px;margin-bottom:27px}header img{width:92px;height:98px;object-fit:contain}h1{font-size:25px;line-height:1.2;margin:0 0 8px}p{margin:10px 0;color:#53675a}table{width:100%;border-collapse:collapse;margin-top:22px;font-size:13px}th,td{border-bottom:1px solid #d8e0d8;text-align:left;vertical-align:top;padding:12px 8px}th{width:37%;font-weight:500;color:#53675a}td{overflow-wrap:anywhere}.contacts{margin-top:25px}</style></head><body>'''
    standalone+=f'<header><img src="tlm-logo.svg" alt=""><div><h1>{e(config["name"])}</h1><p>Литьё и изделия из металла · Тула</p></div></header><h2>Реквизиты {e(config["legalEntity"]["name"])}</h2><table>'+''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k,v in company_fields(site))+'</table>'
    standalone+=f'<div class="contacts"><strong>Контакт для интернет-заказов — Роберт</strong><p>{e(config["phones"][0])} · {e(config["email"])}</p></div></body></html>'
    (root/'assets/tlm-requisites-print.html').write_text(with_metrika(standalone),encoding='utf-8')
