# Подключение csm-lit.ru

Домен приобретён владельцем в Рег.ру 23.10.2026. Хостинг сайта — GitHub Pages, репозиторий `a9252233314-dotcom/Centrspetsmetall`, ветка `main`, корень.

## Сайт

- Основной адрес: `https://csm-lit.ru/`.
- Файл `CNAME` в корне: `csm-lit.ru`.
- `canonicalBase`, canonical страниц, Open Graph, JSON-LD и Sitemap используют новый адрес без `/Centrspetsmetall/`.
- Внутренние ссылки и ресурсы относительные.
- Копия Sites и отдельный проект костровой зоны подключением домена не изменяются.

## DNS в Рег.ру

Сначала закрепить `csm-lit.ru` в настройках GitHub Pages или публикацией корневого `CNAME`. Затем открыть домен в Рег.ру → «DNS-серверы и управление зоной». При использовании бесплатных DNS Рег.ру установить `ns1.reg.ru`, `ns2.reg.ru` и добавить записи:

| Тип | Поддомен | Значение |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | a9252233314-dotcom.github.io. |

TTL оставить по умолчанию. Если для `@` или `www` присутствуют парковочные A/AAAA/CNAME, заменить только конфликтующие записи. Почтовые MX и TXT не затрагивать. Не создавать wildcard-записи. Для CNAME не указывать протокол или имя репозитория.

## Завершение

После распространения DNS проверить apex и www, включая вложенные страницы, `robots.txt` и Sitemap. В GitHub → Settings → Pages дождаться выпуска сертификата и включить Enforce HTTPS. Сам факт коммита не подтверждает готовность DNS и HTTPS; их состояние проверяется отдельно.

После запуска добавить домен в Яндекс Вебмастер и Google Search Console, подтвердить владение и отправить Sitemap. Коды подтверждения не выдумываются.

Источники: [GitHub Pages — подключение домена](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site), [Рег.ру — ресурсные записи](https://help.reg.ru/support/dns-servery-i-nastroyka-zony/nastroyka-resursnykh-zapisey-dns/nastroyka-resursnykh-zapisey-v-lichnom-kabinete).
