import datetime
import html
import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

JST = datetime.timezone(datetime.timedelta(hours=9))
OUT_FILE = Path("keiba_schedule.json")

JRA_VENUES = ["札幌","函館","福島","新潟","東京","中山","中京","京都","阪神","小倉"]

# NAR競馬場コード
LOCAL_CODES = {
    "帯広": 3,
    "門別": 36,
    "盛岡": 10,
    "水沢": 11,
    "浦和": 18,
    "船橋": 19,
    "大井": 20,
    "川崎": 21,
    "金沢": 22,
    "笠松": 23,
    "名古屋": 24,
    "園田": 27,
    "姫路": 28,
    "高知": 31,
    "佐賀": 32,
}

NANKAN = {"浦和", "船橋", "大井", "川崎"}


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tokens = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if self.skip:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if text:
            self.tokens.append(text)


def fetch_html(url, timeout=25):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
            "Cache-Control": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        raw = res.read()

    for enc in ("utf-8", "cp932", "shift_jis"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def visible_tokens(text):
    parser = VisibleTextParser()
    parser.feed(text)
    return parser.tokens


def classify_jra_race(name="", conditions=""):
    text = f"{name} {conditions}".strip()

    if "障害" in text and any(x in text for x in ["J・GⅠ","J・GI","J・GⅡ","J・GII","J・GⅢ","J・GIII"]):
        return {"race_type": "障害重賞", "icon": "🏆🚧"}

    if "障害" in text:
        return {"race_type": "障害", "icon": "🚧"}

    if "メイクデビュー" in text or "新馬" in text:
        return {"race_type": "新馬", "icon": "🆕"}

    if any(x in text for x in ["GⅠ","GI","GⅡ","GII","GⅢ","GIII"]):
        return {"race_type": "重賞", "icon": "🏆"}

    if "リステッド" in text or "(L)" in text or "（L）" in text:
        return {"race_type": "リステッド", "icon": "⭐"}

    if "オープン" in text:
        return {"race_type": "オープン", "icon": "⭐"}

    if any(x in text for x in ["特別","ステークス","カップ","賞"]):
        return {"race_type": "特別", "icon": "🏇"}

    return {"race_type": "一般", "icon": "🐎"}


def classify_local_race(name="", kind_text="", conditions=""):
    text = f"{name} {kind_text} {conditions}".strip()

    if any(x in text for x in ["JpnⅠ","JpnI","JpnⅡ","JpnII","JpnⅢ","JpnIII"]):
        return {"race_type": "ダートグレード", "icon": "🏆"}

    if "準重賞" in text:
        return {"race_type": "準重賞", "icon": "⭐"}

    if "重賞" in text:
        return {"race_type": "重賞", "icon": "🏆"}

    if any(x in text for x in ["新馬", "フレッシュチャレンジ", "スーパーフレッシュチャレンジ"]):
        return {"race_type": "新馬", "icon": "🆕"}

    if "特別" in kind_text or any(x in name for x in ["特別", "賞", "杯", "カップ"]):
        return {"race_type": "特別", "icon": "🏇"}

    return {"race_type": "一般", "icon": "🐎"}


def hm_to_minutes(hm):
    h, m = map(int, hm.split(":"))
    return h * 60 + m


def detect_jra_day_type(races):
    if not races:
        return "非開催"
    last = races[-1].get("time", "")
    if not last:
        return "通常"
    return "薄暮" if hm_to_minutes(last) >= 17 * 60 else "通常"


def detect_local_day_type(races):
    if not races:
        return "非開催"

    first = races[0].get("time", "")
    last = races[-1].get("time", "")
    if not first or not last:
        return "デイ"

    start = hm_to_minutes(first)
    end = hm_to_minutes(last)

    if end >= 19 * 60 + 30:
        return "ナイター"
    if end >= 17 * 60:
        return "薄暮"
    if start < 10 * 60:
        return "モーニング"
    return "デイ"


def race_text(race):
    return " ".join(
        str(race.get(k, ""))
        for k in ("name", "kind", "conditions")
    )


def detect_main_race(races):
    if not races:
        return races

    for r in races:
        r["main"] = False

    grade_priority = [
        "J・GⅠ","J・GI","GⅠ","GI","JpnⅠ","JpnI",
        "J・GⅡ","J・GII","GⅡ","GII","JpnⅡ","JpnII",
        "J・GⅢ","J・GIII","GⅢ","GIII","JpnⅢ","JpnIII",
    ]

    for keyword in grade_priority:
        candidates = [r for r in races if keyword in race_text(r)]
        if candidates:
            candidates[-1]["main"] = True
            return races

    candidates = [
        r for r in races
        if r.get("race_type") in
        {"重賞", "障害重賞", "ダートグレード", "準重賞", "リステッド"}
    ]
    if candidates:
        candidates[-1]["main"] = True
        return races

    candidates = [
        r for r in races
        if r.get("race", 0) >= 7
        and r.get("race_type") in {"オープン", "特別"}
    ]
    if candidates:
        candidates[-1]["main"] = True
        return races

    for r in races:
        if r.get("race") == 11:
            r["main"] = True
            return races

    (races[-2] if len(races) >= 2 else races[-1])["main"] = True
    return races


def normalize_jra_race(race_no, time_text, race_name="", conditions=""):
    kind = classify_jra_race(race_name, conditions)
    return {
        "race": int(race_no),
        "time": time_text,
        "name": race_name.strip(),
        "kind": "",
        "conditions": conditions.strip(),
        "race_type": kind["race_type"],
        "icon": kind["icon"],
        "main": False,
    }


def normalize_local_race(race_no, time_text, race_name="", kind_text="", conditions=""):
    kind = classify_local_race(race_name, kind_text, conditions)
    return {
        "race": int(race_no),
        "time": time_text,
        "name": race_name.strip(),
        "kind": kind_text.strip(),
        "conditions": conditions.strip(),
        "race_type": kind["race_type"],
        "icon": kind["icon"],
        "main": False,
    }


def prepare_venue(venue, races, category, source):
    races = sorted(races, key=lambda x: x["race"])
    races = detect_main_race(races)

    day_type = (
        detect_jra_day_type(races)
        if category == "jra"
        else detect_local_day_type(races)
    )

    return {
        "source": source,
        "day_type": day_type,
        "races": races,
    }


# =========================================================
# JRA
# =========================================================

VENUE_HEADER_RE = re.compile(
    r"\d+回(" + "|".join(map(re.escape, JRA_VENUES)) + r")\d+日"
)
RACE_RE = re.compile(r"^(\d{1,2})レース$")
TIME_RE = re.compile(r"^(\d{1,2})時(\d{2})分$")


def split_jra_name_conditions(text):
    text = html.unescape(re.sub(r"\s+", " ", text).strip())

    if re.match(r"^\d歳", text) or text.startswith("障害"):
        return text, text

    m = re.search(
        r"\s(?=\d歳(?:以上)?(?:未勝利|新馬|以上|オープン|\d勝クラス))",
        text,
    )
    if m:
        name = text[:m.start()].strip()
        cond = text[m.start():].strip()
        return name or text, cond

    return text, text


def fetch_jra(date_str):
    result = {}

    dt = datetime.datetime.strptime(date_str, "%Y%m%d")
    url = (
        f"https://www.jra.go.jp/keiba/calendar{dt.year}/"
        f"{dt.year}/{dt.month}/{dt.strftime('%m%d')}.html"
    )

    print(f"JRA公式: {url}")

    try:
        page = fetch_html(url)
    except Exception as e:
        print(f"JRA取得失敗: {e}")
        return result

    tokens = visible_tokens(page)
    current_venue = None
    current_races = []

    def flush():
        nonlocal current_venue, current_races
        if current_venue and current_races:
            info = prepare_venue(
                current_venue,
                current_races,
                "jra",
                "JRA公式",
            )
            old = result.get(current_venue)
            if not old or len(info["races"]) > len(old["races"]):
                result[current_venue] = info
        current_venue = None
        current_races = []

    i = 0
    while i < len(tokens):
        token = tokens[i]

        vm = VENUE_HEADER_RE.search(token)
        if vm:
            flush()
            current_venue = vm.group(1)
            i += 1
            continue

        rm = RACE_RE.match(token)
        if rm and current_venue:
            race_no = int(rm.group(1))
            parts = []
            time_text = None
            j = i + 1

            while j < len(tokens) and j < i + 30:
                t = tokens[j]
                if VENUE_HEADER_RE.search(t) or RACE_RE.match(t):
                    break

                tm = TIME_RE.match(t)
                if tm:
                    time_text = f"{int(tm.group(1)):02d}:{tm.group(2)}"
                    break

                if t not in {"レース番号", "レース名・条件", "発走時刻"}:
                    parts.append(t)
                j += 1

            if time_text:
                name, cond = split_jra_name_conditions(" ".join(parts))
                current_races.append(
                    normalize_jra_race(
                        race_no,
                        time_text,
                        name,
                        cond,
                    )
                )
                i = j

        i += 1

    flush()

    for venue, info in result.items():
        print(f"  {venue}: {len(info['races'])}R {info['day_type']}")

    return result


# =========================================================
# 門別：ホッカイドウ競馬公式を優先
# =========================================================

HOKKAIDO_TIME_RE = re.compile(r"発走時刻[〗】\s]*([0-2]?\d):([0-5]\d)")
HOKKAIDO_TITLE_RE = re.compile(r"第[０-９\d]+競走\s+(.+)")


def fetch_hokkaido(date_str):
    """
    門別は公式出走表を優先。
    1Rから順番に見て、存在しなくなったら終了。
    """
    races = []

    for race_no in range(1, 13):
        url = (
            "https://www.hokkaidokeiba.net/raceinfo/syuso.php?"
            + urllib.parse.urlencode(
                {
                    "p_day": date_str,
                    "p_rno": f"{race_no:03d}",
                }
            )
        )

        try:
            text = fetch_html(url, timeout=15)
        except Exception:
            if race_no == 1:
                return {}
            break

        visible = "\n".join(visible_tokens(text))

        tm = re.search(
            r"発走時刻[^0-9]*([0-2]?\d):([0-5]\d)",
            visible,
        )
        if not tm:
            if race_no == 1:
                return {}
            break

        time_text = f"{int(tm.group(1)):02d}:{tm.group(2)}"

        # 見出し例: 第８競走 カルミア特別
        title = ""
        title_match = re.search(
            r"第[０-９0-9]+競走\s+([^\n]+)",
            visible,
        )
        if title_match:
            title = title_match.group(1).strip()

        # 条件は括弧内を補助情報として保持
        condition = ""
        cond_match = re.search(
            r"（([^）]+)）",
            visible,
        )
        if cond_match:
            condition = cond_match.group(1).strip()

        races.append(
            normalize_local_race(
                race_no,
                time_text,
                title,
                "",
                condition,
            )
        )

    if not races:
        return {}

    return {
        "門別": prepare_venue(
            "門別",
            races,
            "local",
            "ホッカイドウ競馬公式",
        )
    }


# =========================================================
# NAR共通
# =========================================================

def fetch_nar_venue(venue, baba_code, date_str, source_label="NAR公式"):
    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")
    date_param = date_obj.strftime("%Y/%m/%d")

    url = (
        "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?"
        + urllib.parse.urlencode(
            {
                "k_babaCode": baba_code,
                "k_raceDate": date_param,
            }
        )
    )

    try:
        page = fetch_html(url)
    except Exception:
        return None

    tokens = visible_tokens(page)
    text = "\n".join(tokens)

    # 別場ページ等を誤認しないよう場名を確認
    if f"{venue}競馬" not in text and venue not in text:
        return None

    races = []

    # NARの当日メニューは
    # 「1R」「15:35」「特別」「競走名...」という順序で並ぶ。
    # visible textを順番に読む。
    i = 0
    while i < len(tokens):
        m = re.fullmatch(r"(\d{1,2})R", tokens[i])
        if not m:
            i += 1
            continue

        race_no = int(m.group(1))
        time_text = ""
        kind_text = ""
        race_name = ""

        # 後方10トークン以内から時刻を探す
        j = i + 1
        while j < len(tokens) and j < i + 12:
            if re.fullmatch(r"\d{1,2}R", tokens[j]):
                break

            tm = re.fullmatch(r"([0-2]?\d):([0-5]\d)", tokens[j])
            if tm and not time_text:
                time_text = f"{int(tm.group(1)):02d}:{tm.group(2)}"
                j += 1
                continue

            if time_text:
                t = tokens[j]

                if t in {"有", "変更"}:
                    j += 1
                    continue

                if t in {"特別", "重賞", "準重賞"} and not kind_text:
                    kind_text = t
                    j += 1
                    continue

                # コース・天候・ボタン類より前の最初の意味ある文字列を競走名にする
                if (
                    not race_name
                    and not re.search(r"(右|左)\d+m", t)
                    and t not in {"オッズ", "映像", "成績"}
                    and not t.isdigit()
                ):
                    race_name = t
                    break

            j += 1

        if time_text and race_name:
            races.append(
                normalize_local_race(
                    race_no,
                    time_text,
                    race_name,
                    kind_text,
                    "",
                )
            )

        i += 1

    # 同じRが重複した場合は先頭を採用
    unique = {}
    for race in races:
        unique.setdefault(race["race"], race)
    races = list(unique.values())

    if not races:
        return None

    return prepare_venue(
        venue,
        races,
        "local",
        source_label,
    )


def fetch_nankan(date_str):
    """
    南関4場。
    まずNARの共通当日メニューを使う。
    データ形式は南関公式に依存しない形に正規化しているので、
    後でnankankeiba.com専用取得へ差し替え可能。
    """
    result = {}

    for venue in ("浦和", "船橋", "大井", "川崎"):
        info = fetch_nar_venue(
            venue,
            LOCAL_CODES[venue],
            date_str,
            "NAR公式（南関フォールバック）",
        )
        if info:
            result[venue] = info

    return result


def fetch_nar(date_str):
    result = {}

    # 門別と南関は専用ルートが先なので除外
    skip = {"門別"} | NANKAN

    for venue, code in LOCAL_CODES.items():
        if venue in skip:
            continue

        info = fetch_nar_venue(
            venue,
            code,
            date_str,
            "NAR公式",
        )
        if info:
            result[venue] = info

    return result


# =========================================================
# 全取得
# =========================================================

def build_keiba_schedule(date_str=None):
    if date_str is None:
        date_str = datetime.datetime.now(JST).strftime("%Y%m%d")

    print("")
    print("============================")
    print("競馬データ取得")
    print(f"DATE: {date_str}")
    print("============================")

    data = {
        "date": date_str,
        "updated_at": datetime.datetime.now(JST).isoformat(),
        "jra": {},
        "local": {},
    }

    # JRA
    data["jra"].update(fetch_jra(date_str))
    print(f"JRA: {len(data['jra'])}場")

    # 門別公式
    hokkaido = fetch_hokkaido(date_str)
    data["local"].update(hokkaido)
    print(f"門別: {len(hokkaido)}場")

    # 南関
    nankan = fetch_nankan(date_str)
    data["local"].update(nankan)
    print(f"南関東: {len(nankan)}場")

    # その他NAR
    nar = fetch_nar(date_str)
    for venue, info in nar.items():
        if venue not in data["local"]:
            data["local"][venue] = info
    print(f"その他地方: {len(nar)}場")

    return data


def save_schedule(data):
    with OUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def show_summary(data):
    print("")
    print("============================")
    print("取得結果")
    print("============================")

    for category in ("jra", "local"):
        print("")
        print("JRA" if category == "jra" else "地方競馬")

        if not data[category]:
            print("  取得なし")
            continue

        for venue, info in data[category].items():
            print(
                f"{venue}: {info.get('day_type')} "
                f"{len(info.get('races', []))}R "
                f"[{info.get('source')}]"
            )

            for race in info.get("races", []):
                main = " 🏆MAIN" if race.get("main") else ""
                print(
                    f"  {race['icon']} "
                    f"{race['race']}R {race['time']} "
                    f"{race['name']}{main}"
                )


if __name__ == "__main__":
    schedule = build_keiba_schedule()
    save_schedule(schedule)
    show_summary(schedule)
    print("")
    print(f"保存完了: {OUT_FILE}")
