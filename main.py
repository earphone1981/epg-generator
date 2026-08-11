import datetime
import json
import urllib.request
import xml.etree.ElementTree as ET

KEIRIN_MAP = {
    "函館": "keirin.hakodate", "青森": "keirin.aomori", "いわき平": "keirin.iwakitaira", "弥彦": "keirin.yahiko",
    "前橋": "keirin.maebashi", "取手": "keirin.toride", "宇都宮": "keirin.utsunomiya", "大宮": "keirin.omiya",
    "西武園": "keirin.seibuen", "京王閣": "keirin.keiogatsu", "立川": "keirin.tachikawa", "松戸": "keirin.matsudo",
    "川崎": "keirin.kawasaki", "平塚": "keirin.hiratsuka", "小田原": "keirin.odawara", "伊東": "keirin.ito",
    "静岡": "keirin.shizuoka", "名古屋": "keirin.nagoya", "岐阜": "keirin.gifu", "大垣": "keirin.ogaki",
    "豊橋": "keirin.toyohashi", "松阪": "keirin.matsusaka", "四日市": "keirin.yokkaichi", "富山": "keirin.toyama",
    "福井": "keirin.fukui", "奈良": "keirin.nara", "岸和田": "keirin.kishiwada", "和歌山": "keirin.wakayama",
    "玉野": "keirin.tamano", "広島": "keirin.hiroshima", "防府": "keirin.hofu", "小松島": "keirin.komatsushima",
    "松山": "keirin.matsuyama", "高知": "keirin.kochi", "高松": "keirin.takamatsu", "向日町": "keirin.mukomachi",
    "小倉": "keirin.kokura", "久留米": "keirin.kurume", "武雄": "keirin.takeo", "佐世保": "keirin.sasebo",
    "別府": "keirin.beppu", "熊本": "keirin.kumamoto", "千葉": "keirin.pist6"
}
KEIBA_MAP = {
    "帯広": "chihou.obihiro", "門別": "chihou.mombetsu", "盛岡": "chihou.morioka", "水沢": "chihou.mizusawa",
    "浦和": "chihou.urawa", "船橋": "chihou.funabashi", "大井": "chihou.oi", "川崎": "chihou.kawasaki_keiba",
    "金沢": "chihou.kanazawa", "名古屋": "chihou.nagoya_keiba", "笠松": "chihou.kasamatsu", "園田": "chihou.sonoda",
    "姫路": "chihou.himeji", "高知": "chihou.kochi_keiba", "佐賀": "chihou.saga", "札幌": "jra.sapporo",
    "新潟": "jra.niigata", "中京": "jra.chukyo", "ＪＲＡ公式": "jra.official", "ＪＲＡグリーン": "jra.green"
}
AUTO_MAP = {"川口": "auto.kawaguchi", "伊勢崎": "auto.isesaki", "浜松": "auto.hamamatsu", "飯塚": "auto.iizuka", "山陽": "auto.sanyo"}


BOAT_MAP = {
    "01 桐生": "boat.kiryu",
    "02 戸田": "boat.toda",
    "03 江戸川": "boat.edogawa",
    "04 平和島": "boat.heiwajima",
    "05 多摩川": "boat.tamagawa",
    "06 浜名湖": "boat.hamanako",
    "07 蒲郡": "boat.gamagori",
    "08 常滑": "boat.tokoname",
    "09 津": "boat.tsu",
    "10 三国": "boat.mikuni",
    "11 びわこ": "boat.biwako",
    "12 住之江": "boat.suminoe",
    "13 尼崎": "boat.amagasaki",
    "14 鳴門": "boat.naruto",
    "15 丸亀": "boat.marugame",
    "16 児島": "boat.kojima",
    "17 宮島": "boat.miyajima",
    "18 徳山": "boat.tokuyama",
    "19 下関": "boat.shimonoseki",
    "20 若松": "boat.wakamatsu",
    "21 芦屋": "boat.ashiya",
    "22 福岡": "boat.fukuoka",
    "23 唐津": "boat.karatsu",
    "24 大村": "boat.omura",
}

BOAT_TODAY_URL = (
    "https://raw.githubusercontent.com/"
    "earphone1981/ganble/main/boatrace_today.json"
)

SCHEDULES = {
    "20260811": {
        "keirin": {
            "松山": {"desc": "GI オールスター競輪 初日", "start": "15:15", "end": "20:50", "is_girls": True, "day_type": "ナイター"},
            "弥彦": {"desc": "FI KEIRINライジングスターズ 初日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "熊本": {"desc": "FI KEIRINライジングスターズ 初日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "富山": {"desc": "FI 仲間と繋がるTIPSTAR杯 2日目", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "前橋": {"desc": "FII ティーネットエンタープライズC 最終日", "start": "15:00", "end": "20:25", "is_girls": False, "day_type": "ナイター"},
            "川崎": {"desc": "FII チャリロト杯 最終日", "start": "20:40", "end": "23:40", "is_girls": True, "day_type": "ミッドナイト"},
            "平塚": {"desc": "FII 楽天Kドリームス杯 最終日", "start": "08:30", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "四日市": {"desc": "FII 前検日コメならウィンチケット杯 最終日", "start": "20:40", "end": "23:40", "is_girls": False, "day_type": "ミッドナイト"}
        },
        "keiba": {
            "帯広": {"desc": "ナイター", "start": "14:20", "end": "20:40", "day_type": "ナイター"},
            "門別": {"desc": "ナイター", "start": "14:00", "end": "20:40", "day_type": "ナイター"},
            "盛岡": {"desc": "クラスターカップ JpnⅢ", "start": "11:40", "end": "18:10", "day_type": "薄暮"},
            "浦和": {"desc": "ルーキーズサマーC", "start": "13:30", "end": "19:30", "day_type": "薄暮"},
            "金沢": {"desc": "読売レディス杯", "start": "15:05", "end": "20:50", "day_type": "ナイター"},
            "笠松": {"desc": "薄暮", "start": "11:15", "end": "18:00", "day_type": "薄暮"}
        },
        "auto": {"伊勢崎": {"desc": "SG オートレースグランプリ 初日", "start": "18:00", "end": "21:30", "day_type": "ナイター"}}
    },
    "20260812": {
        "keirin": {
            "松山": {"desc": "GI オールスター競輪 2日目", "start": "15:15", "end": "20:50", "is_girls": True, "day_type": "ナイター"},
            "弥彦": {"desc": "FI KEIRINライジングスターズ 2日目", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "熊本": {"desc": "FI KEIRINライジングスターズ 2日目", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "青森": {"desc": "FII AI競輪も大人気チャリロト杯 初日", "start": "20:40", "end": "23:40", "is_girls": False, "day_type": "ミッドナイト"},
            "岐阜": {"desc": "FII 前検日コメならウィンチケット杯 初日", "start": "08:50", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "富山": {"desc": "FI 仲間と繋がるTIPSTAR杯 最終日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "武雄": {"desc": "FII 前検日コメならウィンチケット杯 初日", "start": "20:40", "end": "23:40", "is_girls": True, "day_type": "ミッドナイト"}
        },
        "keiba": {
            "帯広": {"desc": "ナイター", "start": "14:20", "end": "20:40", "day_type": "ナイター"},
            "浦和": {"desc": "薄暮", "start": "13:30", "end": "19:30", "day_type": "薄暮"},
            "大井": {"desc": "ナイター", "start": "14:25", "end": "20:50", "day_type": "ナイター"},
            "笠松": {"desc": "薄暮", "start": "11:15", "end": "18:00", "day_type": "薄暮"},
            "園田": {"desc": "薄暮", "start": "13:30", "end": "19:30", "day_type": "薄暮"},
            "金沢": {"desc": "ナイター", "start": "15:05", "end": "20:50", "day_type": "ナイター"}
        },
        "auto": {"伊勢崎": {"desc": "SG 2日目", "start": "18:00", "end": "21:30", "day_type": "ナイター"}}
    },
    "20260813": {
        "keirin": {
            "松山": {"desc": "GI オールスター競輪 3日目", "start": "15:15", "end": "20:50", "is_girls": True, "day_type": "ナイター"},
            "弥彦": {"desc": "FI KEIRINライジングスターズ 最終日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "熊本": {"desc": "FI KEIRINライジングスターズ 最終日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "青森": {"desc": "FII AI競輪も大人気チャリロト杯 2日目", "start": "20:40", "end": "23:40", "is_girls": False, "day_type": "ミッドナイト"},
            "西武園": {"desc": "FII オッズパーク杯 初日", "start": "08:30", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "岐阜": {"desc": "FII 前検日コメならウィンチケット杯 2日目", "start": "08:50", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "武雄": {"desc": "FII 前検日コメならウィンチケット杯 2日目", "start": "20:40", "end": "23:40", "is_girls": True, "day_type": "ミッドナイト"}
        },
        "keiba": {
            "帯広": {"desc": "ナイター", "start": "14:20", "end": "20:40", "day_type": "ナイター"},
            "門別": {"desc": "北海道スプリントC JpnⅢ", "start": "14:00", "end": "20:40", "day_type": "ナイター"},
            "大井": {"desc": "ナイター", "start": "14:25", "end": "20:50", "day_type": "ナイター"},
            "笠松": {"desc": "薄暮", "start": "11:15", "end": "18:00", "day_type": "薄暮"},
            "園田": {"desc": "薄暮", "start": "13:30", "end": "19:30", "day_type": "薄暮"},
            "金沢": {"desc": "ナイター", "start": "15:05", "end": "20:50", "day_type": "ナイター"}
        },
        "auto": {"伊勢崎": {"desc": "SG 3日目", "start": "18:00", "end": "21:30", "day_type": "ナイター"}}
    },
    "20260814": {
        "keirin": {
            "松山": {"desc": "GI オールスター競輪 4日目", "start": "15:15", "end": "20:50", "is_girls": True, "day_type": "ナイター"},
            "京王閣": {"desc": "FI KEIRINライジングスターズ 初日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "奈良": {"desc": "FI KEIRINライジングスターズ 初日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "青森": {"desc": "FII AI競輪も大人気チャリロト杯 最終日", "start": "20:40", "end": "23:40", "is_girls": False, "day_type": "ミッドナイト"},
            "西武園": {"desc": "FII オッズパーク杯 2日目", "start": "08:30", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "岐阜": {"desc": "FII 前検日コメならウィンチケット杯 最終日", "start": "08:50", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "武雄": {"desc": "FII 前検日コメならウィンチケット杯 最終日", "start": "20:40", "end": "23:40", "is_girls": True, "day_type": "ミッドナイト"}
        },
        "keiba": {
            "帯広": {"desc": "ナイター", "start": "14:20", "end": "20:40", "day_type": "ナイター"},
            "門別": {"desc": "ナイター", "start": "14:00", "end": "20:40", "day_type": "ナイター"},
            "大井": {"desc": "ナイター", "start": "14:25", "end": "20:50", "day_type": "ナイター"},
            "笠松": {"desc": "薄暮", "start": "11:15", "end": "18:00", "day_type": "薄暮"},
            "園田": {"desc": "その金ナイター (摂津盃)", "start": "15:00", "end": "20:30", "day_type": "ナイター"}
        },
        "auto": {
            "伊勢崎": {"desc": "SG 4日目", "start": "18:00", "end": "21:30", "day_type": "ナイター"},
            "飯塚": {"desc": "ミッドナイト", "start": "20:20", "end": "23:45", "day_type": "ミッドナイト"}
        }
    },
    "20260815": {
        "keirin": {
            "松山": {"desc": "GI オールスター競輪 5日目", "start": "15:15", "end": "20:50", "is_girls": True, "day_type": "ナイター"},
            "京王閣": {"desc": "FI KEIRINライジングスターズ 2日目", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "奈良": {"desc": "FI KEIRINライジングスターズ 2日目", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "前橋": {"desc": "FII 前検日コメならウィンチケット杯 初日", "start": "20:40", "end": "23:40", "is_girls": True, "day_type": "ミッドナイト"},
            "西武園": {"desc": "FII オッズパーク杯 最終日", "start": "08:30", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "静岡": {"desc": "FII オッズパーク杯 初日", "start": "20:40", "end": "23:40", "is_girls": False, "day_type": "ミッドナイト"}
        },
        "keiba": {
            "札幌": {"desc": "JRA 札幌開催", "start": "09:40", "end": "17:00", "day_type": "デイ"},
            "新潟": {"desc": "JRA 新潟ジャンプS", "start": "09:40", "end": "17:00", "day_type": "デイ"},
            "中京": {"desc": "JRA 中京開催", "start": "09:40", "end": "17:00", "day_type": "デイ"},
            "ＪＲＡ公式": {"desc": "JRA公式中継", "start": "09:00", "end": "17:00", "day_type": "デイ"},
            "ＪＲＡグリーン": {"desc": "グリーンチャンネル", "start": "09:00", "end": "21:00", "day_type": "デイ"},
            "帯広": {"desc": "ナイター", "start": "14:20", "end": "20:40", "day_type": "ナイター"},
            "大井": {"desc": "ナイター", "start": "14:25", "end": "20:50", "day_type": "ナイター"},
            "佐賀": {"desc": "ナイター", "start": "15:55", "end": "20:50", "day_type": "ナイター"}
        },
        "auto": {
            "伊勢崎": {"desc": "SG 最終日", "start": "18:00", "end": "21:30", "day_type": "ナイター"},
            "飯塚": {"desc": "ミッドナイト", "start": "20:20", "end": "23:45", "day_type": "ミッドナイト"}
        }
    },
    "20260816": {
        "keirin": {
            "松山": {"desc": "GI オールスター競輪 決勝戦", "start": "15:15", "end": "20:50", "is_girls": True, "day_type": "ナイター"},
            "京王閣": {"desc": "FI KEIRINライジングスターズ 最終日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "奈良": {"desc": "FI KEIRINライジングスターズ 最終日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "前橋": {"desc": "FII 前検日コメならウィンチケット杯 2日目", "start": "20:40", "end": "23:40", "is_girls": True, "day_type": "ミッドナイト"},
            "伊東": {"desc": "FI PayPay銀行杯 初日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "静岡": {"desc": "FII オッズパーク杯 2日目", "start": "20:40", "end": "23:40", "is_girls": False, "day_type": "ミッドナイト"},
            "別府": {"desc": "FI CTCは3分前杯 初日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"}
        },
        "keiba": {
            "札幌": {"desc": "札幌記念 GⅡ", "start": "09:40", "end": "17:00", "day_type": "デイ"},
            "新潟": {"desc": "JRA 新潟開催", "start": "09:40", "end": "17:00", "day_type": "デイ"},
            "中京": {"desc": "JRA 中京開催", "start": "09:40", "end": "17:00", "day_type": "デイ"},
            "ＪＲＡ公式": {"desc": "JRA公式中継", "start": "09:00", "end": "17:00", "day_type": "デイ"},
            "ＪＲＡグリーン": {"desc": "グリーンチャンネル", "start": "09:00", "end": "21:00", "day_type": "デイ"},
            "帯広": {"desc": "ナイター", "start": "14:20", "end": "20:40", "day_type": "ナイター"},
            "大井": {"desc": "ナイター", "start": "14:25", "end": "20:50", "day_type": "ナイター"},
            "佐賀": {"desc": "ナイター", "start": "15:55", "end": "20:50", "day_type": "ナイター"}
        },
        "auto": {
            "飯塚": {"desc": "ミッドナイト", "start": "20:20", "end": "23:45", "day_type": "ミッドナイト"}
        }
    },
    "20260817": {
        "keirin": {
            "前橋": {"desc": "FII 前検日コメならウィンチケット杯 最終日", "start": "20:40", "end": "23:40", "is_girls": True, "day_type": "ミッドナイト"},
            "西武園": {"desc": "FII 2日目", "start": "08:30", "end": "11:55", "is_girls": False, "day_type": "モーニング"},
            "静岡": {"desc": "FII オッズパーク杯 最終日", "start": "20:40", "end": "23:40", "is_girls": False, "day_type": "ミッドナイト"},
            "立川": {"desc": "FI 初日", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "伊東": {"desc": "FI PayPay銀行杯 2日目", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"},
            "別府": {"desc": "FI CTCは3分前杯 2日目", "start": "10:30", "end": "16:30", "is_girls": False, "day_type": "デイ"}
        },
        "keiba": {
            "盛岡": {"desc": "薄暮", "start": "11:40", "end": "18:10", "day_type": "薄暮"},
            "門別": {"desc": "ナイター", "start": "14:00", "end": "20:40", "day_type": "ナイター"},
            "金沢": {"desc": "ナイター", "start": "15:05", "end": "20:50", "day_type": "ナイター"}
        },
        "auto": {
            "飯塚": {"desc": "ミッドナイト", "start": "20:20", "end": "23:45", "day_type": "ミッドナイト"}
        }
    }
}

ICON_MAP = {
    "keirin": "🚲",
    "keiba": "🏇",
    "auto": "🏍️",
    "boat": "🚤",
}

BOAT_TODAY_URL = (
    "https://raw.githubusercontent.com/"
    "earphone1981/ganble/main/boatrace_today.json"
)

KEIBA_SCHEDULE_URL = (
    "https://raw.githubusercontent.com/"
    "earphone1981/ganble/main/keiba_schedule.json"
)


KEIRIN_SCHEDULE_URL = (
    "https://raw.githubusercontent.com/"
    "earphone1981/ganble/main/keirin_schedule.json"
)

AUTORACE_SCHEDULE_URL = (
    "https://raw.githubusercontent.com/"
    "earphone1981/ganble/main/autorace_schedule.json"
)


def format_time_xml(dt):
    return dt.strftime("%Y%m%d%H%M%S +0900")


def fetch_json(url, label):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Cache-Control": "no-cache",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            text = response.read().decode("utf-8-sig")
        data = json.loads(text)
        print(f"{label}: 取得成功")
        return data
    except Exception as e:
        print(f"{label}: 取得失敗: {e}")
        return {}


def load_boatrace_today():
    return fetch_json(BOAT_TODAY_URL, "BOAT JSON")


def load_keiba_schedule():
    return fetch_json(KEIBA_SCHEDULE_URL, "KEIBA JSON")


def load_keirin_schedule():
    return fetch_json(KEIRIN_SCHEDULE_URL, "KEIRIN JSON")


def load_autorace_schedule():
    return fetch_json(AUTORACE_SCHEDULE_URL, "AUTORACE JSON")


def add_programme(tv, channel, start_dt, stop_dt, title, desc=""):
    if stop_dt <= start_dt:
        return None

    prog = ET.SubElement(
        tv,
        "programme",
        start=format_time_xml(start_dt),
        stop=format_time_xml(stop_dt),
        channel=channel,
    )
    ET.SubElement(prog, "title", lang="ja").text = title

    if desc:
        ET.SubElement(prog, "desc", lang="ja").text = desc

    return prog


def day_emoji(day_type):
    return {
        "モーニング": "🌅",
        "通常": "☀️",
        "デイ": "☀️",
        "薄暮": "🌇",
        "サマータイム": "🌇",
        "ナイター": "🌙",
        "ミッドナイト": "⭐",
    }.get(day_type, "☀️")


def build_manual_category(
    tv,
    date_str,
    category,
    target_map,
    cat_data,
    JST,
    today_display,
):
    cat_label = {
        "keirin": "競輪",
        "keiba": "競馬",
        "auto": "オートレース",
    }.get(category, "")

    for v_name, tvg_id in target_map.items():
        day_start = datetime.datetime.strptime(
            f"{date_str} 01:00", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        day_end = datetime.datetime.strptime(
            f"{date_str} 23:59", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        if v_name not in cat_data:
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                f"💤 本日非開催 {v_name}（{cat_label}）",
                f"本日は{v_name}での開催予定はありません。",
            )
            continue

        info = cat_data[v_name]
        is_girls = info.get("is_girls", False)
        day_type = info.get("day_type", "デイ")
        emoji = day_emoji(day_type)
        girls_tag = "💛ガールズ" if is_girls else ""

        grade_list = [
            "JpnIII", "JpnII", "JpnI",
            "GIII", "GII", "GI",
            "FII", "FI", "SG",
        ]
        grade_found = next(
            (g for g in grade_list if g in info["desc"]),
            "",
        )

        day_match_str = ""
        for term in [
            "初日", "2日目", "3日目", "4日目",
            "5日目", "決勝戦", "最終日",
        ]:
            if term in info["desc"]:
                day_match_str = term
                break

        match_text = (
            "🏆 決勝戦"
            if "決勝戦" in info["desc"]
            else day_match_str
        )

        grade_prefix = f"【{grade_found}】" if grade_found else ""

        title_parts = [
            grade_prefix,
            "🔴 LIVE",
            v_name,
            f"{emoji}{day_type}",
            match_text,
            girls_tag,
            f"（{cat_label}）",
        ]
        title_live = " ".join(p for p in title_parts if p)

        start_dt = datetime.datetime.strptime(
            f"{date_str} {info['start']}", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        end_dt = datetime.datetime.strptime(
            f"{date_str} {info['end']}", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        if end_dt <= start_dt:
            end_dt += datetime.timedelta(days=1)

        pre_start = start_dt - datetime.timedelta(minutes=10)
        post_end = end_dt + datetime.timedelta(minutes=10)

        desc_text = (
            f"{ICON_MAP.get(category, '⭐')} 開催地: {v_name} ({day_type})\n"
            f"🏆 グレード: {grade_found if grade_found else '通常開催'}\n"
            f"✨ ガールズ: {'あり 💛' if is_girls else 'なし'}\n"
            f"📢 内容: {info['desc']}\n"
            f"⏰ 時間: {info['start']} - {info['end']}\n"
            f"📅 日付: {today_display}"
        )

        if day_start < pre_start:
            add_programme(
                tv,
                tvg_id,
                day_start,
                pre_start,
                f"⏳ 待機 {v_name} ({emoji}{day_type} "
                f"1R {info['start']}開始)（{cat_label}）",
                desc_text,
            )

        add_programme(
            tv,
            tvg_id,
            max(pre_start, day_start),
            post_end,
            title_live,
            desc_text,
        )

        if post_end < day_end:
            add_programme(
                tv,
                tvg_id,
                post_end,
                day_end,
                f"🏁 終了 {v_name} ({emoji}{day_type})（{cat_label}）",
                f"{v_name} ({day_type}) の放送は終了しました。",
            )


def build_keiba_race_epg(
    tv,
    date_str,
    keiba_data,
    JST,
    today_display,
):
    """
    keiba_schedule.json の各Rを1番組としてEPG化。
    その日のJSONが無い場合は False を返して手入力へフォールバック。
    """
    if not keiba_data:
        return False

    if keiba_data.get("date") != date_str:
        return False

    merged = {}

    for category_key in ("jra", "local"):
        for venue, info in keiba_data.get(category_key, {}).items():
            merged[venue] = {
                **info,
                "_category": category_key,
            }

    if not merged:
        return False

    handled = set()

    for venue, info in merged.items():
        tvg_id = KEIBA_MAP.get(venue)
        if not tvg_id:
            print(f"KEIBA: tvg-id未登録: {venue}")
            continue

        races = info.get("races", [])
        if not races:
            continue

        handled.add(venue)

        day_type = info.get("day_type", "デイ")
        emoji = day_emoji(day_type)
        category_name = "JRA" if info.get("_category") == "jra" else "地方競馬"

        day_start = datetime.datetime.strptime(
            f"{date_str} 01:00", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        day_end = datetime.datetime.strptime(
            f"{date_str} 23:59", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        race_times = []
        for race in races:
            time_text = race.get("time", "")
            try:
                dt = datetime.datetime.strptime(
                    f"{date_str} {time_text}", "%Y%m%d %H:%M"
                ).replace(tzinfo=JST)
            except Exception:
                continue
            race_times.append((race, dt))

        if not race_times:
            continue

        first_race_dt = race_times[0][1]
        pre_start = max(
            day_start,
            first_race_dt - datetime.timedelta(minutes=20),
        )

        if day_start < pre_start:
            add_programme(
                tv,
                tvg_id,
                day_start,
                pre_start,
                f"⏳ 待機 {venue} {emoji}{day_type}",
                f"{category_name} {venue}\n"
                f"1R発走予定 {race_times[0][0].get('time', '')}\n"
                f"📅 {today_display}",
            )

        # 各Rを「発走10分前～次R発走10分前」で連続表示
        for idx, (race, start_time) in enumerate(race_times):
            block_start = max(
                pre_start,
                start_time - datetime.timedelta(minutes=10),
            )

            if idx + 1 < len(race_times):
                next_time = race_times[idx + 1][1]
                block_stop = next_time - datetime.timedelta(minutes=10)
            else:
                block_stop = start_time + datetime.timedelta(minutes=30)

            if block_stop <= block_start:
                block_stop = start_time + datetime.timedelta(minutes=15)

            race_no = race.get("race", "")
            race_name = race.get("name", "").strip()
            race_type = race.get("race_type", "一般")
            icon = race.get("icon", "🐎")
            main = bool(race.get("main"))
            conditions = race.get("conditions", "").strip()

            main_mark = "🏆 MAIN " if main else ""
            display_name = race_name if race_name else race_type

            title = (
                f"{main_mark}{icon} {venue} "
                f"{race_no}R {race.get('time', '')} "
                f"{display_name}"
            ).strip()

            desc_lines = [
                f"{category_name} {venue}",
                f"{emoji} 開催区分: {day_type}",
                f"⏰ 発走予定: {race.get('time', '')}",
                f"🏷️ 種別: {race_type}",
            ]

            if race_name:
                desc_lines.append(f"📢 レース名: {race_name}")

            if conditions and conditions != race_name:
                desc_lines.append(f"📋 条件: {conditions}")

            if main:
                desc_lines.append("🏆 メインレース")

            desc_lines.append(f"📅 {today_display}")

            add_programme(
                tv,
                tvg_id,
                block_start,
                min(block_stop, day_end),
                title,
                "\n".join(desc_lines),
            )

        finish_start = race_times[-1][1] + datetime.timedelta(minutes=30)

        if finish_start < day_end:
            add_programme(
                tv,
                tvg_id,
                finish_start,
                day_end,
                f"🏁 終了 {venue} {emoji}{day_type}",
                f"{venue}の本日の競馬は終了しました。",
            )

    # JSONに無い地方/JRAチャンネルは非開催表示。
    # JRA公式・グリーンは配信専用なので手入力側に任せる。
    for venue, tvg_id in KEIBA_MAP.items():
        if venue in {"ＪＲＡ公式", "ＪＲＡグリーン"}:
            continue
        if venue in handled:
            continue

        day_start = datetime.datetime.strptime(
            f"{date_str} 01:00", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        day_end = datetime.datetime.strptime(
            f"{date_str} 23:59", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        add_programme(
            tv,
            tvg_id,
            day_start,
            day_end,
            f"💤 本日非開催 {venue}（競馬）",
            f"本日は{venue}のレース情報を取得していません。",
        )

    print(f"KEIBA EPG: {len(handled)}場を各R単位で生成")
    return True



def build_keirin_race_epg(
    tv,
    date_str,
    keirin_data,
    JST,
    today_display,
):
    if not keirin_data or keirin_data.get("date") != date_str:
        return False

    venues = keirin_data.get("venues", {})
    if not venues:
        return False

    handled = set()

    for venue, info in venues.items():
        tvg_id = KEIRIN_MAP.get(venue) or info.get("tvg_id", "")
        if not tvg_id:
            print(f"KEIRIN: tvg-id未登録: {venue}")
            continue

        races = info.get("races", [])
        if not races:
            continue

        race_times = []
        for race in races:
            try:
                dt = datetime.datetime.strptime(
                    f"{date_str} {race.get('time','')}",
                    "%Y%m%d %H:%M",
                ).replace(tzinfo=JST)
            except Exception:
                continue
            race_times.append((race, dt))

        if not race_times:
            continue

        handled.add(venue)

        day_type = info.get("day_type", "デイ")
        day_icon = info.get("day_emoji", day_emoji(day_type))
        grade = info.get("grade", "")
        event_name = info.get("event_name", "")
        event_day = info.get("event_day", "")

        day_start = datetime.datetime.strptime(
            f"{date_str} 01:00", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)
        day_end = datetime.datetime.strptime(
            f"{date_str} 23:59", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        pre_start = max(
            day_start,
            race_times[0][1] - datetime.timedelta(minutes=20),
        )

        if day_start < pre_start:
            add_programme(
                tv, tvg_id, day_start, pre_start,
                f"⏳ 待機 {venue} {day_icon}{day_type}",
                "\n".join(
                    x for x in [
                        f"🚲 競輪 {venue}",
                        f"{grade} {event_name}".strip(),
                        event_day,
                        f"1R発走予定 {race_times[0][0].get('time','')}",
                        f"📅 {today_display}",
                    ] if x
                ),
            )

        for idx, (race, start_time) in enumerate(race_times):
            block_start = max(
                pre_start,
                start_time - datetime.timedelta(minutes=8),
            )

            if idx + 1 < len(race_times):
                next_time = race_times[idx + 1][1]
                block_stop = next_time - datetime.timedelta(minutes=8)
            else:
                block_stop = start_time + datetime.timedelta(minutes=25)

            if block_stop <= block_start:
                block_stop = start_time + datetime.timedelta(minutes=12)

            race_name = race.get("name", "").strip() or "競走"
            race_no = race.get("race", "")
            main = bool(race.get("main"))
            girls = bool(race.get("girls"))

            title_parts = []
            if main:
                title_parts.append("🏆 MAIN")
            if girls:
                title_parts.append("💛")
            else:
                title_parts.append("🚲")
            if grade and main:
                title_parts.append(f"【{grade}】")
            title_parts.append(f"{venue} {race_no}R")
            title_parts.append(race.get("time", ""))
            title_parts.append(race_name)

            desc_lines = [
                f"🚲 競輪 {venue}",
                f"{day_icon} 開催区分: {day_type}",
                f"⏰ 発走予定: {race.get('time','')}",
                f"🏷️ {race.get('race_class','競輪')}",
            ]
            if grade:
                desc_lines.append(f"🏆 グレード: {grade}")
            if event_name:
                desc_lines.append(f"📢 開催名: {event_name}")
            if event_day:
                desc_lines.append(f"📅 開催日次: {event_day}")
            if girls:
                desc_lines.append("💛 ガールズ")
            if race.get("is_semi"):
                desc_lines.append("🔥 準決勝")
            if race.get("is_final"):
                desc_lines.append("🏆 決勝")
            if main:
                desc_lines.append("🏆 メインレース")

            add_programme(
                tv,
                tvg_id,
                block_start,
                min(block_stop, day_end),
                " ".join(x for x in title_parts if x),
                "\n".join(desc_lines),
            )

        finish = race_times[-1][1] + datetime.timedelta(minutes=25)
        if finish < day_end:
            add_programme(
                tv, tvg_id, finish, day_end,
                f"🏁 終了 {venue} {day_icon}{day_type}",
                f"{venue}の本日の競輪は終了しました。",
            )

    print(f"KEIRIN EPG: {len(handled)}場を各R単位で生成")
    return True


def build_autorace_race_epg(
    tv,
    date_str,
    autorace_data,
    JST,
    today_display,
):
    if not autorace_data or autorace_data.get("date") != date_str:
        return False

    venues = autorace_data.get("venues", {})
    if not venues:
        return False

    handled = set()

    for venue, info in venues.items():
        tvg_id = AUTO_MAP.get(venue) or info.get("tvg_id", "")
        if not tvg_id:
            print(f"AUTORACE: tvg-id未登録: {venue}")
            continue

        races = info.get("races", [])
        if not races:
            continue

        race_times = []
        for race in races:
            try:
                dt = datetime.datetime.strptime(
                    f"{date_str} {race.get('time','')}",
                    "%Y%m%d %H:%M",
                ).replace(tzinfo=JST)
            except Exception:
                continue
            race_times.append((race, dt))

        if not race_times:
            continue

        handled.add(venue)

        day_type = info.get("day_type", "デイ")
        day_icon = info.get("day_emoji", day_emoji(day_type))
        grade = info.get("grade", "")
        event_name = info.get("event_name", "")
        event_day = info.get("event_day", "")

        day_start = datetime.datetime.strptime(
            f"{date_str} 01:00", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)
        day_end = datetime.datetime.strptime(
            f"{date_str} 23:59", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        pre_start = max(
            day_start,
            race_times[0][1] - datetime.timedelta(minutes=20),
        )

        if day_start < pre_start:
            add_programme(
                tv, tvg_id, day_start, pre_start,
                f"⏳ 待機 {venue} {day_icon}{day_type}",
                "\n".join(
                    x for x in [
                        f"🏍️ オートレース {venue}",
                        f"{grade} {event_name}".strip(),
                        event_day,
                        f"1R発走予定 {race_times[0][0].get('time','')}",
                        f"📅 {today_display}",
                    ] if x
                ),
            )

        for idx, (race, start_time) in enumerate(race_times):
            block_start = max(
                pre_start,
                start_time - datetime.timedelta(minutes=8),
            )

            if idx + 1 < len(race_times):
                next_time = race_times[idx + 1][1]
                block_stop = next_time - datetime.timedelta(minutes=8)
            else:
                block_stop = start_time + datetime.timedelta(minutes=25)

            if block_stop <= block_start:
                block_stop = start_time + datetime.timedelta(minutes=12)

            race_no = race.get("race", "")
            race_name = race.get("name", "").strip() or race.get("race_type", "競走")
            main = bool(race.get("main"))
            icon = race.get("icon", "🏍️")

            title_parts = []
            if main:
                title_parts.append("🏆 MAIN")
            title_parts.append(icon)
            if grade and main:
                title_parts.append(f"【{grade}】")
            title_parts.append(f"{venue} {race_no}R")
            title_parts.append(race.get("time", ""))
            title_parts.append(race_name)

            desc_lines = [
                f"🏍️ オートレース {venue}",
                f"{day_icon} 開催区分: {day_type}",
                f"⏰ 発走予定: {race.get('time','')}",
                f"🏷️ 種別: {race.get('race_type','')}",
            ]
            if grade:
                desc_lines.append(f"🏆 グレード: {grade}")
            if event_name:
                desc_lines.append(f"📢 開催名: {event_name}")
            if event_day:
                desc_lines.append(f"📅 開催日次: {event_day}")
            if race.get("is_semi"):
                desc_lines.append("🔥 準決勝")
            if race.get("is_final"):
                desc_lines.append("🏆 優勝戦")
            if main:
                desc_lines.append("🏆 メインレース")

            add_programme(
                tv,
                tvg_id,
                block_start,
                min(block_stop, day_end),
                " ".join(x for x in title_parts if x),
                "\n".join(desc_lines),
            )

        finish = race_times[-1][1] + datetime.timedelta(minutes=25)
        if finish < day_end:
            add_programme(
                tv, tvg_id, finish, day_end,
                f"🏁 終了 {venue} {day_icon}{day_type}",
                f"{venue}の本日のオートレースは終了しました。",
            )

    print(f"AUTORACE EPG: {len(handled)}場を各R単位で生成")
    return True


def build_boat_epg(
    tv,
    date_str,
    boat_today,
    JST,
    today_str,
    today_display,
):
    for v_name, tvg_id in BOAT_MAP.items():
        day_start = datetime.datetime.strptime(
            f"{date_str} 01:00", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        day_end = datetime.datetime.strptime(
            f"{date_str} 23:59", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        if date_str != today_str:
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                f"📅 {v_name} ボートレース",
                f"{today_display} {v_name} ボートレース",
            )
            continue

        info = boat_today.get(v_name, {})

        if not isinstance(info, dict) or not info.get("live"):
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                f"💤 本日非開催 {v_name}（ボートレース）",
                f"{v_name}のライブ配信URLは取得されていません。",
            )
            continue

        start_text = info.get("start")
        end_text = info.get("end")
        day_type = info.get("day_type", "開催")
        emoji = info.get("emoji", "🚤")

        if not start_text or not end_text:
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                f"🔴 LIVE {v_name} 🚤ボートレース",
                f"🚤 ボートレース {v_name}\n"
                f"✅ 配信URL取得済み\n"
                f"📅 {today_display}",
            )
            continue

        start_dt = datetime.datetime.strptime(
            f"{date_str} {start_text}", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        end_dt = datetime.datetime.strptime(
            f"{date_str} {end_text}", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        if end_dt <= start_dt:
            end_dt += datetime.timedelta(days=1)

        pre_start = start_dt - datetime.timedelta(minutes=10)

        desc = (
            f"🚤 ボートレース {v_name}\n"
            f"⏰ 配信予定: {start_text}～{end_text}\n"
            f"{emoji} 開催区分: {day_type}\n"
            f"📅 {today_display}"
        )

        if day_start < pre_start:
            add_programme(
                tv,
                tvg_id,
                day_start,
                pre_start,
                f"⏳ 待機 {v_name} {emoji}{day_type} {start_text}開始",
                desc,
            )

        if pre_start < start_dt:
            add_programme(
                tv,
                tvg_id,
                max(pre_start, day_start),
                start_dt,
                f"⏳ まもなく開始 {v_name} {emoji}{day_type}",
                desc,
            )

        add_programme(
            tv,
            tvg_id,
            start_dt,
            end_dt,
            f"🔴 LIVE {v_name} {emoji}{day_type} 🚤ボートレース",
            desc,
        )

        if end_dt < day_end:
            add_programme(
                tv,
                tvg_id,
                end_dt,
                day_end,
                f"🏁 終了 {v_name} {emoji}{day_type}",
                f"{v_name}の本日のライブ配信は終了しました。",
            )


def build_epg_xml():
    tv = ET.Element(
        "tv",
        {"generator-info-name": "CombinedEPGGenerator"},
    )

    JST = datetime.timezone(datetime.timedelta(hours=9))

    boat_today = load_boatrace_today()
    keiba_schedule = load_keiba_schedule()
    keirin_schedule = load_keirin_schedule()
    autorace_schedule = load_autorace_schedule()

    today_str = datetime.datetime.now(JST).strftime("%Y%m%d")

    all_channels = {
        **KEIRIN_MAP,
        **KEIBA_MAP,
        **AUTO_MAP,
        **BOAT_MAP,
    }

    for v_name, tvg_id in all_channels.items():
        channel = ET.SubElement(tv, "channel", id=tvg_id)
        ET.SubElement(channel, "display-name").text = v_name

    for date_str in SCHEDULES.keys():
        day_schedules = SCHEDULES.get(date_str, {})
        dt_obj = datetime.datetime.strptime(date_str, "%Y%m%d")
        today_display = dt_obj.strftime("%Y年%m月%d日")

        # 競輪はJSONの日付一致なら各R自動EPG。
        # JSONが無い日だけ従来手入力へフォールバック。
        used_auto_keirin = build_keirin_race_epg(
            tv,
            date_str,
            keirin_schedule,
            JST,
            today_display,
        )

        if not used_auto_keirin:
            build_manual_category(
                tv,
                date_str,
                "keirin",
                KEIRIN_MAP,
                day_schedules.get("keirin", {}),
                JST,
                today_display,
            )

        # 競馬はJSONの日付が一致すれば各R自動EPG。
        # 一致しなければ従来の手入力へフォールバック。
        used_auto_keiba = build_keiba_race_epg(
            tv,
            date_str,
            keiba_schedule,
            JST,
            today_display,
        )

        if not used_auto_keiba:
            build_manual_category(
                tv,
                date_str,
                "keiba",
                KEIBA_MAP,
                day_schedules.get("keiba", {}),
                JST,
                today_display,
            )

        # JRA公式/グリーンだけは自動JSONにチャンネルが無いので
        # 手入力がある日だけ追加
        if used_auto_keiba:
            extra_keiba = {}
            for special in ("ＪＲＡ公式", "ＪＲＡグリーン"):
                if special in day_schedules.get("keiba", {}):
                    extra_keiba[special] = day_schedules["keiba"][special]

            if extra_keiba:
                special_map = {
                    k: KEIBA_MAP[k]
                    for k in extra_keiba
                    if k in KEIBA_MAP
                }
                build_manual_category(
                    tv,
                    date_str,
                    "keiba",
                    special_map,
                    extra_keiba,
                    JST,
                    today_display,
                )

        # オートもJSONの日付一致なら各R自動EPG。
        used_auto_autorace = build_autorace_race_epg(
            tv,
            date_str,
            autorace_schedule,
            JST,
            today_display,
        )

        if not used_auto_autorace:
            build_manual_category(
                tv,
                date_str,
                "auto",
                AUTO_MAP,
                day_schedules.get("auto", {}),
                JST,
                today_display,
            )

        # ボートJSON
        build_boat_epg(
            tv,
            date_str,
            boat_today,
            JST,
            today_str,
            today_display,
        )

    tree = ET.ElementTree(tv)

    if hasattr(ET, "indent"):
        ET.indent(tree, space="    ")

    tree.write(
        "epg.xml",
        encoding="utf-8",
        xml_declaration=True,
    )

    boat_live_count = sum(
        1
        for info in boat_today.values()
        if isinstance(info, dict) and info.get("live")
    )

    print("")
    print("============================")
    print("EPG生成完了")
    print(f"ボートLIVE: {boat_live_count} / 24")
    print("競馬: keiba_schedule.json 優先")
    print("競輪: keirin_schedule.json 優先")
    print("オート: autorace_schedule.json 優先")
    print("出力: epg.xml")
    print("============================")


if __name__ == "__main__":
    build_epg_xml()
