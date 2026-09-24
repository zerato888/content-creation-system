# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Optional Metricool connector: Instagram posts/reels of the last 30 days for one brand.

Account ids come from the brand's config (`metrics.account.blog_id` / `user_id`);
the API key comes from the OS credential store via engines/kit_secrets.py
(`METRICOOL_API_KEY`), read at call time and never stored or logged. Sends only
the brand's own ids and key to app.metricool.com.
"""
import datetime as dt
import json
import urllib.parse
import urllib.request

BASE = "https://app.metricool.com/api"
SECRET = "METRICOOL_API_KEY"


def _get(path, key, account, frm, to, tz, fetch):
    query = {"blogId": account["blog_id"], "userId": account["user_id"], "from": frm, "to": to,
             "timezone": tz, "start": frm, "end": to}
    request = urllib.request.Request(f"{BASE}{path}?{urllib.parse.urlencode(query)}",
                                     headers={"X-Mc-Auth": key, "Accept": "application/json"})
    return fetch(request)


def _urlopen(request):
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


def rows(obj):
    if isinstance(obj, dict):
        return next((obj[k] for k in ("data", "items", "results", "posts", "reels") if isinstance(obj.get(k), list)), [])
    return obj if isinstance(obj, list) else []


def num(d, *keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, dict):
            v = v.get("value")
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return v
    return 0


def _published(r):
    for k in ("publishedAt", "published", "date", "dateTime", "createdAt"):
        v = r.get(k)
        v = v.get("dateTime") or v.get("date") if isinstance(v, dict) else v
        if isinstance(v, str) and len(v) >= 7:
            return v
    return ""


def fetch(brand, key, tz="UTC", now=None, fetch=_urlopen):
    account = (brand.get("metrics") or {}).get("account") or {}
    if not account.get("blog_id") or not account.get("user_id"):
        raise ValueError("faltan blog_id y user_id de Metricool en la config de la marca")
    if not key:
        raise ValueError(f"falta la clave {SECRET} en el llavero del sistema")
    now = now or dt.datetime.now()
    frm, to = (now - dt.timedelta(days=30)).strftime("%Y-%m-%dT00:00:00"), now.strftime("%Y-%m-%dT23:59:59")
    posts = []
    for path in ("/v2/analytics/reels/instagram", "/v2/analytics/posts/instagram"):
        for r in rows(_get(path, key, account, frm, to, tz, fetch)):
            posts.append({"caption": str(r.get("text") or r.get("caption") or "").replace("\n", " ")[:120],
                          "reach": num(r, "reach", "impressions", "views"),
                          "likes": num(r, "likes"), "comments": num(r, "comments"), "saves": num(r, "saved", "saves"),
                          "url": r.get("url") or r.get("permalink") or "", "published_at": _published(r)})
    posts.sort(key=lambda p: p["reach"], reverse=True)
    reach = sum(p["reach"] for p in posts)
    interactions = sum(p["likes"] + p["comments"] + p["saves"] for p in posts)
    return {"brand": brand["id"], "source": "metricool", "fetched_at": now.isoformat(), "window_days": 30,
            "posts": len(posts), "top": posts[:6],
            "totals": {"reach": reach, "likes": sum(p["likes"] for p in posts),
                       "comments": sum(p["comments"] for p in posts), "saves": sum(p["saves"] for p in posts),
                       "engagement_pct": round(interactions / reach * 100, 2) if reach else 0}}
