import re, html, json, time, datetime, urllib.request

BASE = "https://arbuz.kz/ru/almaty/catalog/cat/"
CATS = {
    "Мясо": "19907-myaso_steiki_farsh",
    "Колбасы": "19855-kolbasy",
    "Молочка": "19986-moloko_slivki_sgush_nnoe_moloko",
    "Хлеб": "20118-hleb",
    "Сыр": "20160-syr",
    "Консервы": "20205-konservaciya",
    "Крупы": "224398-krupy_bobovye",
    "Макароны": "224399-makarony_i_lapsha",
    "Сахар и соль": "224402-sahar_sol_specii",
    "Завтраки": "224533-suhie_zavtraki",
    "Здоровое питание": "224645-zdorovoe_pitanie",
    "Полуфабрикаты": "224663-polufabrikaty_i_gotovye_blyuda",
    "Овощи": "225178-ovoshi",
    "Фрукты": "225177-frukty",
    "Птица": "225173-kurica_indeika_i_ptica",
    "Рыба": "225175-ryba",
    "Яйца и масло": "225245-yaica_maslo_margarin",
    "Масло растительное": "225448-maslo_rastitelnoe",
    "Орехи": "225304-orehi_i_suhofrukty",
    "Готовая еда": "225253-gotovaya_eda",
}


def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    t = html.unescape(urllib.request.urlopen(req, timeout=30).read().decode())
    t = t.replace("\\/", "/")
    out = []
    for m in re.finditer(r'"uri":"(/ru/almaty/catalog/item/[^"]+)"', t):
        seg = t[m.end():m.end() + 900]
        pre = t[max(0, m.start() - 900):m.start()]
        p = re.search(r'"priceActual":(\d+)', seg)
        n = re.findall(r'"name":"([^"]*)"', pre)
        if p and n:
            out.append({"name": n[-1], "price": int(p.group(1)),
                        "url": "https://arbuz.kz" + m.group(1)})
    return out


items = []
for cat, slug in CATS.items():
    seen = set()
    for pg in range(1, 16):
        try:
            r = get(BASE + slug + "?page=" + str(pg))
        except Exception as e:
            print("error", cat, pg, e)
            break
        new = [x for x in r if x["url"] not in seen]
        if not new:
            break
        for x in new:
            seen.add(x["url"])
            x["cat"] = cat
            x["store"] = "Arbuz"
            items.append(x)
        time.sleep(1)
    print(cat, len(seen))

data = {"updated": datetime.date.today().isoformat(), "items": items}
json.dump(data, open("prices.json", "w", encoding="utf-8"), ensure_ascii=False)
print("total", len(items))
