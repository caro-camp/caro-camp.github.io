"""CARO 배포 전 검사. 하나라도 실패하면 exit 1 → 배포 중단(지금 사이트 유지)."""
import json, re, sys, datetime, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
bad = []
def need(ok, msg):
    print(("OK   " if ok else "FAIL ") + msg)
    if not ok: bad.append(msg)

def load(name, var):
    t = (R / name).read_text(encoding="utf-8").strip()
    pre = f"window.{var}="
    need(t.startswith(pre) and t.endswith(";"), f"{name} 형식")
    try: return json.loads(t[len(pre):-1])
    except Exception as e: need(False, f"{name} JSON 오류: {e}"); return None

D = load("data.js", "CARO_D"); P = load("pub.js", "CARO_PUB")
if D:
    camps, ev = D.get("camps", []), D.get("events", [])
    need(len(camps) >= 800, f"캠핑장 수 {len(camps)} (최소 800)")
    need(len(ev) >= 400, f"오픈 일정 수 {len(ev)} (최소 400)")
    need(all(isinstance(c, list) and len(c) >= 10 and str(c[4]).startswith("https://") for c in camps), "캠핑장 행 구조·링크")
    try:
        a = datetime.datetime.fromisoformat(D["asOf"])
        age = datetime.datetime.now(a.tzinfo) - a
        need(age < datetime.timedelta(days=4), f"데이터 기준시각 {D['asOf']} (4일 이내)")
    except Exception as e: need(False, f"asOf 오류: {e}")
    m = D.get("meta", {})
    need(len(m.get("popReview", [])) >= 50, "인기 캠핑장 목록 50곳 이상")
if P:
    need(len(P.get("camps", [])) >= 80, f"공공 캠핑장 {len(P.get('camps', []))} (최소 80)")

h = (R / "index.html").read_text(encoding="utf-8")
for i in ["v-pop", "v-find", "v-board", "v-mine", "list", "ready", "r-open", "r-cal"]:
    need(f'id="{i}"' in h, f"화면 요소 #{i}")
need('src="data.js"' in h and 'src="pub.js"' in h, "데이터 파일 연결")
need("const D = window.CARO_D;" in h, "데이터 연결 코드")
need("Content-Security-Policy" in h, "보안 설정(CSP)")
for f in ["manifest.webmanifest", "sw.js", "icons/icon-192.png", "icons/icon-512.png", "img/hero.jpg"]:
    need((R / f).exists(), f"파일 {f}")
print("\n실패 %d건" % len(bad) if bad else "\n모두 통과")
sys.exit(1 if bad else 0)
