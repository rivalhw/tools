import requests

url = 'https://cultural.cityline.com/api/cityline_check_tk.do'
headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "cookie": "cl-font-size=16px; CL_uid=22746458; cl-theme-color=default; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=zh_CN; CL_TK=4a888009de692cc88c74d342c3f6e506a8848a556a15a3c1|c3acd3bddcde3a8d|61efa6a6aab0d7005721cdc06a50c0f97d1ef8058de2629c|57b58187f859c9fbd04a91c8125eff0f2778d318; _ga_3DXLK9N5DR=GS1.1.1739868464.17.1.1739876535.0.0.0; _ga_K0T1R01WMW=GS1.1.1739868464.18.1.1739876535.60.0.0; _gid=GA1.2.1604117075.1740017603; _gat_gtag_UA_111662758_1=1; cto_bundle=SSSgcV9ZTHU0UGJjdUdESzEyVDZaTElGcDgzYzVOZWQ0WWFUSXg3MmRnaVFSSFA2N05ETWpMMWhlM01KSGgyb01UcmUyektqZlZteiUyRjZxS1RJYWpUS1F6RFJoclcyZDBWdzFvMllseXZEZ0xMZzNYU3pTWCUyRldmZ0xweWQwQzVZcFdxb0JkcXRQM21RQTF3S0hwVnNmaUVKcm1nJTNEJTNE; cl-lang=zh-CN; lang=Sc; _ga=GA1.1.628173136.1738727815; _ga_0M1K5NPYZE=GS1.1.1740020648.30.1.1740020670.38.0.0; _ga_BD9VNGC0M6=GS1.1.1740020648.31.1.1740020670.0.0.0",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://cultural.cityline.com/sc/2025/complexcon20252122.html",
    "sec-ch-ua": "",
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Mobile/9B176 MicroMessenger/4.3.2",
    "x-requested-with": "XMLHttpRequest"
}

response = requests.get(url, headers=headers)
print(response.text)