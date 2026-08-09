import datetime
import xml.etree.ElementTree as ET

KEIRIN_MAP = {
    "函館": "keirin.hakodate", "青森": "keirin.aomori", "いわき平": "keirin.iwakitaira",
    "弥彦": "keirin.yahiko", "前橋": "keirin.matsusaka", "取手": "keirin.toride",
    "宇都宮": "keirin.utsunomiya", "大宮": "keirin.omiya", "西武園": "keirin.seibuen",
    "京王閣": "keirin.keiogatsu", "立川": "keirin.tachikawa", "松戸": "keirin.matsudo",
    "川崎": "keirin.kawasaki", "平塚": "keirin.hiratsuka", "小田原": "keirin.odawara",
    "伊東": "keirin.ito", "静岡": "keirin.shizuoka", "名古屋": "keirin.nagoya",
    "岐阜": "keirin.gifu", "大垣": "keirin.ogaki", "豊橋": "keirin.toyohashi",
    "松阪": "keirin.matsusaka", "四日市": "keirin.yokkaichi", "富山": "keirin.toyama",
    "福井": "keirin.fukui", "奈良": "keirin.nara", "岸和田": "keirin.kishiwada",
    "和歌山": "keirin.wakayama", "玉野": "keirin.tamano", "広島": "keirin.hiroshima",
    "防府": "keirin.hofu", "小松島": "keirin.komatsushima", "松山": "keirin.matsuyama",
    "高知": "keirin.kochi", "高松": "keirin.takamatsu", "向日町": "keirin.mukomachi",
    "小倉": "keirin.kokura", "久留米": "keirin.kurume", "武雄": "keirin.takeo", 
    "佐世保": "keirin.sasebo", "別府": "keirin.beppu", "熊本": "keirin.kumamoto", 
    "千葉PIST6": "keirin.pist6"
}

KEIBA_MAP = {
    "帯広": "chihou.obihiro", "門別": "chihou.mombetsu", "盛岡": "chihou.morioka",
    "浦和": "chihou.urawa", "大井": "chihou.oi", "金沢": "chihou.kanazawa",
    "笠松": "chihou.kasamatsu", "園田": "chihou.sonoda", "佐賀": "chihou.saga",
    "札幌": "jra.sapporo", "新潟": "jra.niigata", "中京": "jra.chukyo"
}

AUTO_MAP = {
    "伊勢崎": "auto.isesaki", "飯塚": "auto.iizuka"
}

SCHEDULES = {
    "20260810": {
        "keirin": {
            "前橋": {"desc": "FII モーニング🌅 2日目", "start": "08:30", "end": "11:55"},
            "立川": {"desc": "FI デイ☀ 最終日", "start": "10:40", "end": "16:35"},
            "平塚": {"desc": "FII ナイター🌙 2日目", "start": "15:00", "end": "20:25"},
            "川崎": {"desc": "FII ナイター🌙 2日目", "start": "15:00", "end": "20:25"},
            "四日市": {"desc": "FII ナイター🌙 2日目", "start": "15:00", "end": "20:25"},
            "富山": {"desc": "FII ミッドナイト⭐ 初日", "start": "20:40", "end": "23:40"}
        },
        "keiba": {
            "盛岡": {"desc": "薄暮🌇", "start": "11:40", "end": "18:10"},
            "浦和": {"desc": "薄暮🌇", "start": "13:30", "end": "19:30"},
            "帯広": {"desc": "ナイター🌙", "start": "14:20", "end": "20:40"},
            "金沢": {"desc": "ナイター🌙", "start": "16:35", "end": "20:50"}
        },
        "auto": {"飯塚": {"desc": "ミッドナイト⭐ 3日目", "start": "20:19", "end": "23:45"}}
    },
    "20260811": {
        "keirin": {
            "熊本": {"desc": "FI デイ☀ 初日", "start": "10:30", "end": "16:30"},
            "弥彦": {"desc": "FI デイ☀ 初日", "start": "10:30", "end": "16:30"},
            "前橋": {"desc": "FII モーニング🌅 最終日", "start": "08:30", "end": "11:55"},
            "平塚": {"desc": "FII ナイター🌙 💛 最終日", "start": "15:00", "end": "20:25"},
            "川崎": {"desc": "FII ナイター🌙 💛 最終日", "start": "15:00", "end": "20:25"},
            "四日市": {"desc": "FII ナイター🌙 💛 最終日", "start": "15:00", "end": "20:25"},
            "松山": {"desc": "GI オールスター競輪ナイター🌙 💛 初日", "start": "15:15", "end": "20:50"},
            "富山": {"desc": "FII ミッドナイト⭐ 💛 2日目", "start": "20:40", "end": "23:40"}
        },
        "keiba": {
            "盛岡": {"desc": "クラスターカップ JpnⅢ (17:05発走) デイ☀", "start": "11:40", "end": "18:10"},
            "浦和": {"desc": "ルーキーズサマーカップ (18:55発走) 薄暮🌇", "start": "13:30", "end": "19:30"},
            "金沢": {"desc": "読売レディス杯 (20:00発走) ナイター🌙", "start": "15:05", "end": "20:50"},
            "帯広": {"desc": "ナイター🌙", "start": "14:20", "end": "20:40"}
        },
        "auto": {"伊勢崎": {"desc": "SG オートレースグランプリ 初日🌙", "start": "18:00", "end": "21:30"}}
    },
    "20260812": {
        "keirin": {
            "青森": {"desc": "FII ミッドナイト⭐ 💛 初日", "start": "20:40", "end": "23:40"},
            "弥彦": {"desc": "FI デイ☀ 2日目", "start": "10:30", "end": "16:30"},
            "岐阜": {"desc": "FII モーニング🌅 初日", "start": "08:50", "end": "11:55"},
            "富山": {"desc": "FII ミッドナイト⭐ 💛 最終日", "start": "20:40", "end": "23:40"},
            "松山": {"desc": "GI オールスター競輪ナイター🌙 💛 2日目", "start": "15:15", "end": "20:50"},
            "武雄": {"desc": "FII ミッドナイト⭐ 💛 初日", "start": "20:40", "end": "23:40"},
            "熊本": {"desc": "FI デイ☀ 2日目", "start": "10:30", "end": "16:30"}
        },
        "keiba": {
            "笠松": {"desc": "くろゆり賞 (16:35発走) デイ☀", "start": "11:15", "end": "17:00"},
            "浦和": {"desc": "薄暮🌇", "start": "13:30", "end": "19:30"},
            "金沢": {"desc": "ナイター🌙", "start": "15:05", "end": "20:50"},
            "帯広": {"desc": "ナイター🌙", "start": "14:20", "end": "20:40"}
        },
        "auto": {"伊勢崎": {"desc": "SG オートレースグランプリ 2日目🌙", "start": "18:00", "end": "21:30"}}
    },
    "20260813": {
        "keirin": {
            "青森": {"desc": "FII ミッドナイト⭐ 💛 最終日", "start": "20:40", "end": "23:40"},
            "弥彦": {"desc": "FI デイ☀ 最終日", "start": "10:30", "end": "16:30"},
            "岐阜": {"desc": "FII モーニング🌅 2日目", "start": "08:50", "end": "11:55"},
            "松山": {"desc": "GI オールスター競輪ナイター🌙 💛 3日目", "start": "15:15", "end": "20:50"},
            "武雄": {"desc": "FII ミッドナイト⭐ 💛 2日目", "start": "20:40", "end": "23:40"},
            "熊本": {"desc": "FI デイ☀ 最終日", "start": "10:30", "end": "16:30"}
        },
        "keiba": {
            "門別": {"desc": "北海道スプリントカップ JpnⅢ (19:55発走) ナイター🌙", "start": "14:00", "end": "20:40"},
            "大井": {"desc": "ナイター🌙", "start": "14:25", "end": "20:50"},
            "笠松": {"desc": "デイ☀", "start": "11:15", "end": "16:30"},
            "園田": {"desc": "薄暮🌇", "start": "13:30", "end": "19:30"}
        },
        "auto": {
            "伊勢崎": {"desc": "SG オートレースグランプリ 3日目🌙", "start": "18:00", "end": "21:30"},
            "飯塚": {"desc": "ミッドナイト⭐ 初日", "start": "20:20", "end": "23:45"}
        }
    },
    "20260814": {
        "keirin": {
            "青森": {"desc": "FII ミッドナイト⭐ 💛 最終日", "start": "20:40", "end": "23:40"},
            "西武園": {"desc": "FII モーニング🌅 💛 2日目", "start": "08:30", "end": "11:55"},
            "京王閣": {"desc": "FI デイ☀ 初日", "start": "10:30", "end": "16:30"},
            "岐阜": {"desc": "FII モーニング🌅 最終日", "start": "08:50", "end": "11:55"},
            "奈良": {"desc": "FI デイ☀ 初日", "start": "10:30", "end": "16:30"},
            "松山": {"desc": "GI オールスター競輪ナイター🌙 💛 4日目", "start": "15:15", "end": "20:50"},
            "武雄": {"desc": "FII ミッドナイト⭐ 💛 最終日", "start": "20:40", "end": "23:40"}
        },
        "keiba": {
            "園田": {"desc": "その金ナイター🌇 (摂津盃 19:55発走)", "start": "15:00", "end": "20:30"},
            "門別": {"desc": "ナイター🌙", "start": "14:00", "end": "20:40"},
            "大井": {"desc": "ナイター🌙", "start": "14:25", "end": "20:50"},
            "笠松": {"desc": "デイ☀", "start": "11:15", "end": "16:30"}
        },
        "auto": {"伊勢崎": {"desc": "SG オートレースグランプリ 4日目🌙", "start": "18:00", "end": "21:30"}}
    },
    "20260815": {
        "keirin": {
            "前橋": {"desc": "FII ミッドナイト⭐ 💛 初日", "start": "20:40", "end": "23:40"},
            "西武園": {"desc": "FII モーニング🌅 💛 最終日", "start": "08:30", "end": "11:55"},
            "京王閣": {"desc": "FI デイ☀ 2日目", "start": "10:30", "end": "16:30"},
            "静岡": {"desc": "FII ミッドナイト⭐ 💛 初日", "start": "20:40", "end": "23:40"},
            "奈良": {"desc": "FI デイ☀ 2日目", "start": "10:30", "end": "16:30"},
            "松山": {"desc": "GI オールスター競輪ナイター🌙 💛 5日目", "start": "15:15", "end": "20:50"}
        },
        "keiba": {
            "新潟": {"desc": "新潟ジャンプS (15:45発走) デイ☀", "start": "09:40", "end": "18:15"},
            "中京": {"desc": "デイ☀", "start": "09:40", "end": "18:15"},
            "札幌": {"desc": "デイ☀", "start": "09:40", "end": "18:15"},
            "帯広": {"desc": "ナイター🌙", "start": "14:20", "end": "20:40"},
            "大井": {"desc": "ナイター🌙", "start": "14:25", "end": "20:50"},
            "佐賀": {"desc": "ナイター🌙", "start": "15:55", "end": "20:50"}
        },
        "auto": {"伊勢崎": {"desc": "SG オートレースグランプリ 最終日🌙", "start": "18:00", "end": "21:30"}}
    },
    "20260816": {
        "keirin": {
            "前橋": {"desc": "FII ミッドナイト⭐ 💛 2日目", "start": "20:40", "end": "23:40"},
            "西武園": {"desc": "FII モーニング🌅 💛 初日", "start": "08:30", "end": "11:55"},
            "京王閣": {"desc": "FI デイ☀ 最終日", "start": "10:30", "end": "16:30"},
            "静岡": {"desc": "FII ミッドナイト⭐ 💛 2日目", "start": "20:40", "end": "23:40"},
            "奈良": {"desc": "FI デイ☀ 最終日", "start": "10:30", "end": "16:30"},
            "松山": {"desc": "GI オールスター競輪ナイター🌙 💛 決勝戦", "start": "15:15", "end": "20:50"}
        },
        "keiba": {
            "札幌": {"desc": "札幌記念 (GⅡ 15:45発走) デイ☀", "start": "09:40", "end": "18:15"},
            "新潟": {"desc": "デイ☀", "start": "09:40", "end": "18:15"},
            "中京": {"desc": "デイ☀", "start": "09:40", "end": "18:15"},
            "帯広": {"desc": "ナイター🌙", "start": "14:20", "end": "20:40"},
            "大井": {"desc": "ナイター🌙", "start": "14:25", "end": "20:50"},
            "佐賀": {"desc": "ナイター🌙", "start": "15:55", "end": "20:50"}
        },
        "auto": {"飯塚": {"desc": "ミッドナイト⭐ 2日目", "start": "20:20", "end": "23:45"}}
    }
}

def build_epg_xml():
    tv = ET.Element("tv", {"generator-info-name": "CombinedEPGGenerator"})
    JST = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(JST)
    today_str = now.strftime("%Y%m%d")
    today_display = now.strftime("%Y年%m月%d日")
    day_schedules = SCHEDULES.get(today_str, {})

    for target_map, category in [(KEIRIN_MAP, "keirin"), (KEIBA_MAP, "keiba"), (AUTO_MAP, "auto")]:
        cat_data = day_schedules.get(category, {})
        for v_name, tvg_id in target_map.items():
            channel = ET.SubElement(tv, "channel", id=tvg_id)
            ET.SubElement(channel, "display-name").text = v_name
            if v_name in cat_data:
                info = cat_data[v_name]
                prog = ET.SubElement(tv, "programme", start=f"{today_str}000000 +0900", stop=f"{today_str}235959 +0900", channel=tvg_id)
                ET.SubElement(prog, "title", lang="ja").text = f"♦{v_name} {info['desc']} 実況放送♦"
                ET.SubElement(prog, "desc", lang="ja").text = f"{today_display} {v_name} ステータス: {info['desc']}"
            else:
                prog = ET.SubElement(tv, "programme", start=f"{today_str}000000 +0900", stop=f"{today_str}235959 +0900", channel=tvg_id)
                ET.SubElement(prog, "title", lang="ja").text = "💎本日は開催しておりません💎"

    tree = ET.ElementTree(tv)
    if hasattr(ET, "indent"): ET.indent(tree, space="    ")
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    build_epg_xml()
