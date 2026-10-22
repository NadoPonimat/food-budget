import json, datetime, urllib.request, urllib.parse

API = "https://magnum.kz:1337"
Q = ("/api/products?filters[shops][address][$containsi]=г. АЛМАТЫ"
     "&populate[shops][filters][address][$containsi]=г. АЛМАТЫ"
     "&populate[shops][fields][0]=name&populate[shops][fields][1]=address&populate[shops][fields][2]=geo"
     "&pagination[pageSize]=100&pagination[page]=")


def get(p):
    u = API + urllib.parse.quote(p, safe="/?&=[]$:")
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode())


items = {}
shops = {}
page = 1
while True:
    d = get(Q + str(page))
    for x in d["data"]:
        a = x["attributes"]
        key = (a["name"], a["final_price"])
        it = items.setdefault(key, {
            "name": a["name"],
            "price": a["final_price"],
            "old": a.get("start_price") or 0,
            "discount": a.get("discount") or 0,
            "until": a.get("action_end"),
            "shops": [],
        })
        for s in (a.get("shops") or {}).get("data", []):
            sa = s["attributes"]
            if s["id"] not in it["shops"]:
                it["shops"].append(s["id"])
            shops[s["id"]] = {"id": s["id"], "name": sa["name"],
                              "address": sa["address"], "geo": sa.get("geo")}
    if page >= d["meta"]["pagination"]["pageCount"]:
        break
    page += 1

out = {"updated": datetime.date.today().isoformat(),
       "items": list(items.values()), "shops": list(shops.values())}
json.dump(out, open("magnum.json", "w", encoding="utf-8"), ensure_ascii=False)
print("pages:", page, "unique items:", len(items), "almaty shops:", len(shops))
for it in list(items.values())[:15]:
    print(it["name"], it["old"], "->", it["price"], "до", it["until"], "магазинов:", len(it["shops"]))
for s in list(shops.values())[:6]:
    print(s["name"], "|", s["address"])
