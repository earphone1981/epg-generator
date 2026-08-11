import json
import datetime
from pathlib import Path


JST = datetime.timezone(
    datetime.timedelta(hours=9)
)

OUT_FILE = Path("keiba_schedule.json")


# =========================================================
# 競馬場
# =========================================================

JRA_VENUES = [
    "札幌",
    "函館",
    "福島",
    "新潟",
    "東京",
    "中山",
    "中京",
    "京都",
    "阪神",
    "小倉",
]

LOCAL_VENUES = [
    "帯広",
    "門別",
    "盛岡",
    "水沢",
    "浦和",
    "船橋",
    "大井",
    "川崎",
    "金沢",
    "笠松",
    "名古屋",
    "園田",
    "姫路",
    "高知",
    "佐賀",
]


# =========================================================
# JRA レース種別判定
# =========================================================

def classify_jra_race(name="", conditions=""):

    text = f"{name} {conditions}".strip()

    # 障害重賞を先に判定
    if "障害" in text and any(
        x in text
        for x in [
            "J・GⅠ",
            "J・GI",
            "J・GⅡ",
            "J・GII",
            "J・GⅢ",
            "J・GIII",
        ]
    ):
        return {
            "race_type": "障害重賞",
            "icon": "🏆🚧"
        }

    if "障害" in text:
        return {
            "race_type": "障害",
            "icon": "🚧"
        }

    if (
        "メイクデビュー" in text
        or "新馬" in text
    ):
        return {
            "race_type": "新馬",
            "icon": "🆕"
        }

    if any(
        x in text
        for x in [
            "GⅠ",
            "GI",
            "GⅡ",
            "GII",
            "GⅢ",
            "GIII",
        ]
    ):
        return {
            "race_type": "重賞",
            "icon": "🏆"
        }

    if (
        "リステッド" in text
        or "(L)" in text
        or "（L）" in text
    ):
        return {
            "race_type": "リステッド",
            "icon": "⭐"
        }

    if "オープン" in text:
        return {
            "race_type": "オープン",
            "icon": "⭐"
        }

    if any(
        x in text
        for x in [
            "特別",
            "ステークス",
            "カップ",
            "賞",
        ]
    ):
        return {
            "race_type": "特別",
            "icon": "🏇"
        }

    return {
        "race_type": "一般",
        "icon": "🐎"
    }


# =========================================================
# 地方競馬 レース種別判定
# =========================================================

def classify_local_race(name="", conditions=""):

    text = f"{name} {conditions}".strip()

    if any(
        x in text
        for x in [
            "JpnⅠ",
            "JpnI",
            "JpnⅡ",
            "JpnII",
            "JpnⅢ",
            "JpnIII",
        ]
    ):
        return {
            "race_type": "ダートグレード",
            "icon": "🏆"
        }

    if "重賞" in text:
        return {
            "race_type": "重賞",
            "icon": "🏆"
        }

    if "準重賞" in text:
        return {
            "race_type": "準重賞",
            "icon": "⭐"
        }

    if (
        "新馬" in text
        or "フレッシュチャレンジ" in text
    ):
        return {
            "race_type": "新馬",
            "icon": "🆕"
        }

    if any(
        x in text
        for x in [
            "特別",
            "賞",
            "杯",
            "カップ",
        ]
    ):
        return {
            "race_type": "特別",
            "icon": "🏇"
        }

    return {
        "race_type": "一般",
        "icon": "🐎"
    }


# =========================================================
# 開催区分判定
# =========================================================

def detect_jra_day_type(races):

    if not races:
        return "非開催"

    last_time = races[-1].get(
        "time",
        ""
    )

    if not last_time:
        return "通常"

    hour, minute = map(
        int,
        last_time.split(":")
    )

    end_minutes = (
        hour * 60
        + minute
    )

    if end_minutes >= 17 * 60:
        return "薄暮"

    return "通常"


def detect_local_day_type(races):

    if not races:
        return "非開催"

    first_time = races[0].get(
        "time",
        ""
    )

    last_time = races[-1].get(
        "time",
        ""
    )

    if not first_time or not last_time:
        return "デイ"

    sh, sm = map(
        int,
        first_time.split(":")
    )

    eh, em = map(
        int,
        last_time.split(":")
    )

    start_minutes = (
        sh * 60
        + sm
    )

    end_minutes = (
        eh * 60
        + em
    )

    if end_minutes >= 19 * 60 + 30:
        return "ナイター"

    if end_minutes >= 17 * 60:
        return "薄暮"

    if start_minutes < 10 * 60:
        return "モーニング"

    return "デイ"


# =========================================================
# メインレース判定
# =========================================================

def detect_main_race(races):

    if not races:
        return races

    for race in races:
        race["main"] = False

    # 最優先：最高格
    grade_priority = [
        "GⅠ",
        "GI",
        "JpnⅠ",
        "JpnI",
        "J・GⅠ",
        "J・GI",

        "GⅡ",
        "GII",
        "JpnⅡ",
        "JpnII",
        "J・GⅡ",
        "J・GII",

        "GⅢ",
        "GIII",
        "JpnⅢ",
        "JpnIII",
        "J・GⅢ",
        "J・GIII",
    ]

    for keyword in grade_priority:

        candidates = [
            r
            for r in races
            if keyword
            in (
                r.get("name", "")
                + " "
                + r.get("conditions", "")
            )
        ]

        if candidates:
            candidates[-1]["main"] = True
            return races


    # 地方重賞・主要競走
    major_types = [
        "重賞",
        "ダートグレード",
        "リステッド",
        "オープン",
    ]

    candidates = [
        r
        for r in races
        if r.get("race_type")
        in major_types
    ]

    if candidates:
        candidates[-1]["main"] = True
        return races


    # 名前付き特別は後半Rを優先
    named_candidates = [
        r
        for r in races
        if r.get("name", "").strip()
        and r.get("race", 0) >= 8
    ]

    if named_candidates:
        named_candidates[-1]["main"] = True
        return races


    # 11R
    for race in races:
        if race.get("race") == 11:
            race["main"] = True
            return races


    # 12Rしかない場合など
    if len(races) >= 2:
        races[-2]["main"] = True
    else:
        races[-1]["main"] = True

    return races


# =========================================================
# レース情報正規化
# =========================================================

def normalize_race(
    race_no,
    time_text,
    race_name="",
    conditions="",
    category="local",
):

    if category == "jra":

        kind = classify_jra_race(
            race_name,
            conditions
        )

    else:

        kind = classify_local_race(
            race_name,
            conditions
        )

    return {
        "race": int(race_no),
        "time": time_text,
        "name": race_name.strip(),
        "conditions": conditions.strip(),
        "race_type": kind["race_type"],
        "icon": kind["icon"],
        "main": False,
    }


# =========================================================
# 開催場整形
# =========================================================

def prepare_venue(
    venue,
    races,
    category,
    source
):

    races = sorted(
        races,
        key=lambda x: x["race"]
    )

    races = detect_main_race(
        races
    )

    if category == "jra":

        day_type = detect_jra_day_type(
            races
        )

    else:

        day_type = detect_local_day_type(
            races
        )

    return {
        "source": source,
        "day_type": day_type,
        "races": races,
    }


# =========================================================
# JRA取得
# =========================================================

def fetch_jra(date_str):

    result = {}

    # ここにJRA公式取得処理を入れる

    return result


# =========================================================
# ホッカイドウ競馬
# =========================================================

def fetch_hokkaido(date_str):

    result = {}

    # ここに門別公式取得処理

    return result


# =========================================================
# 南関東
# =========================================================

def fetch_nankan(date_str):

    result = {}

    # 浦和
    # 船橋
    # 大井
    # 川崎

    return result


# =========================================================
# その他地方競馬
# =========================================================

def fetch_nar(date_str):

    result = {}

    # 帯広
    # 盛岡
    # 水沢
    # 金沢
    # 笠松
    # 名古屋
    # 園田
    # 姫路
    # 高知
    # 佐賀

    return result


# =========================================================
# 全競馬取得
# =========================================================

def build_keiba_schedule(
    date_str=None
):

    if date_str is None:

        date_str = datetime.datetime.now(
            JST
        ).strftime("%Y%m%d")

    print("")
    print("============================")
    print("競馬データ取得")
    print(f"DATE: {date_str}")
    print("============================")

    data = {
        "date": date_str,
        "updated_at": datetime.datetime.now(
            JST
        ).isoformat(),
        "jra": {},
        "local": {},
    }

    try:

        jra_data = fetch_jra(
            date_str
        )

        data["jra"].update(
            jra_data
        )

        print(
            f"JRA: "
            f"{len(jra_data)} 場"
        )

    except Exception as e:

        print(
            f"JRA取得失敗: "
            f"{e}"
        )

    try:

        hokkaido_data = fetch_hokkaido(
            date_str
        )

        data["local"].update(
            hokkaido_data
        )

        print(
            f"門別: "
            f"{len(hokkaido_data)} 場"
        )

    except Exception as e:

        print(
            f"門別取得失敗: "
            f"{e}"
        )

    try:

        nankan_data = fetch_nankan(
            date_str
        )

        data["local"].update(
            nankan_data
        )

        print(
            f"南関東: "
            f"{len(nankan_data)} 場"
        )

    except Exception as e:

        print(
            f"南関東取得失敗: "
            f"{e}"
        )

    try:

        nar_data = fetch_nar(
            date_str
        )

        for venue, info in (
            nar_data.items()
        ):

            if (
                venue
                not in data["local"]
            ):

                data["local"][
                    venue
                ] = info

        print(
            f"NAR: "
            f"{len(nar_data)} 場"
        )

    except Exception as e:

        print(
            f"NAR取得失敗: "
            f"{e}"
        )

    return data


# =========================================================
# 保存
# =========================================================

def save_schedule(data):

    with OUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


# =========================================================
# 確認表示
# =========================================================

def show_summary(data):

    print("")
    print("============================")
    print("取得結果")
    print("============================")

    for category in [
        "jra",
        "local"
    ]:

        print("")
        print(
            "JRA"
            if category == "jra"
            else "地方競馬"
        )

        for venue, info in (
            data[category].items()
        ):

            races = info.get(
                "races",
                []
            )

            print(
                f"{venue}: "
                f"{info.get('day_type')} "
                f"{len(races)}R"
            )

            for race in races:

                main_mark = (
                    "【MAIN】"
                    if race.get("main")
                    else ""
                )

                print(
                    f" {race['icon']} "
                    f"{race['race']}R "
                    f"{race['time']} "
                    f"{race['name']} "
                    f"{main_mark}"
                )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    schedule = build_keiba_schedule()

    save_schedule(
        schedule
    )

    show_summary(
        schedule
    )

    print("")
    print(
        f"保存完了: "
        f"{OUT_FILE}"
    )
