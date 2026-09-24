# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Optional Zernio connector: post analytics for one brand's account.

The account comes from the brand's config (`metrics.account.account_id`, or
`handle` to look it up in /accounts); the key from the OS credential store
(`ZERNIO_API_KEY`) via engines/kit_secrets.py. Nothing is baked in.
"""
import datetime as dt
import json
import urllib.parse
import urllib.request

BASE = "https://api.zernio.com/v1"
SECRET = "ZERNIO_API_KEY"


def _urlopen(request):
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def _get(path, key, fetch):
    return fetch(urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {key}"}))


def _account(account, key, fetch):
    if account.get("account_id"):
        return {"_id": account["account_id"]}
    wanted = (account.get("handle") or "").lower().lstrip("@")
    if not wanted:
        raise ValueError("falta account_id o handle de Zernio en la config de la marca")
    payload = _get("/accounts", key, fetch)
    for a in payload.get("accounts", payload) if isinstance(payload, dict) else payload:
        profile = (a.get("profileUrl") or "").rstrip("/").split("/")[-1].lower().lstrip("@")
        if wanted in (profile, (a.get("displayName") or "").lower().lstrip("@")):
            return a
    raise ValueError("esa cuenta no aparece en Zernio con esta clave")


def fetch(brand, key, now=None, fetch=_urlopen):
    if not key:
        raise ValueError(f"falta la clave {SECRET} en el llavero del sistema")
    account = _account((brand.get("metrics") or {}).get("account") or {}, key, fetch)
    data = _get(f"/analytics?{urllib.parse.urlencode({'accountId': account['_id'], 'limit': 50})}", key, fetch) or {}
    totals = {"reach": 0, "impressions": 0, "likes": 0, "comments": 0, "saves": 0, "views": 0}
    rates = []
    for post in data.get("posts") or []:
        stats = post.get("analytics") or {}
        for k in totals:
            totals[k] += stats.get(k, 0) or 0
        if stats.get("engagementRate"):
            rates.append(stats["engagementRate"])
    overview = data.get("overview") or {}
    return {"brand": brand["id"], "source": "zernio", "fetched_at": (now or dt.datetime.now()).isoformat(),
            "followers": account.get("followersCount"), "posts": overview.get("publishedPosts", 0),
            "scheduled": overview.get("scheduledPosts", 0),
            "totals": {**totals, "engagement_pct": round(sum(rates) / len(rates), 2) if rates else 0}}
