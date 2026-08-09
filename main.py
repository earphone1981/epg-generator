import datetime
import xml.etree.ElementTree as ET

KEIRIN_MAP = {
    "函館": "keirin.hakodate", "青森": "keirin.aomori", "いわき平": "keirin.iwakitaira",
    "弥彦": "keirin.yahiko", "前橋": "keirin.maebashi", "取手": "keirin.toride",
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
    "千葉PIST6": "keirin.pist6", "伊東温泉": "keirin.ito"
}

KEIBA_MAP = {
    "帯広": "chihou.obihiro", "門別": "chihou.mombetsu", "盛岡": "chihou.morioka",
    "水沢": "chihou.mizusawa", "浦和": "chihou.urawa", "船橋": "chihou.funabashi",
    "大井": "chihou.oi", "川崎": "chihou.kawasaki_keiba", "金沢": "chihou.kanazawa",
    "名古屋": "chihou.nagoya_keiba", "笠松": "chihou.kasamatsu", "園田": "chihou.sonoda",
    "姫路": "chihou.himeji", "高知": "chihou.kochi_keiba", "佐賀": "chihou.saga",
    "ＪＲＡ公式": "jra.official", "ＪＲＡグリーン": "jra.green"
}

AUTO_MAP = {
    "川口": "auto.kawaguchi", "伊勢崎": "auto.isesaki", "浜松": "auto.hamamatsu",
    "飯塚": "auto.iizuka", "山陽": "auto.sanyo"
}

SCHEDULES = {
    "20260810": {
        "keirin": {
            "前橋": {"desc": "F2 モーニング🌅 2日目", "start": "08:30", "end": "11:55"},
            "立川": {"desc": "FI デイ☀ 最終日", "start": "10:40", "end": "16:35"},
            "平塚": {"desc": "F2 ナイター🌙 2日目", "start": "15:00", "end": "20:25"},
            "川崎": {"desc": "F2 ナイター🌙 2日目", "start": "20:40", "end": "23:15"},
            "四日市": {"desc": "F2 ナイター🌙 2日目", "start": "20:50", "end": "23:25"},
            "富山": {"desc": "F2 ミッドナイト⭐ 初日", "start": "20:40", "end": "23:40"}
        },
        "keiba": {
            "盛岡": {"desc": "薄暮🌇", "start": "11:40", "end": "18:10"},
            "浦和": {"desc": "薄暮🌇", "start": "13:30", "end": "19:30"},
            "帯広": {"desc": "ナイター🌙", "start": "14:20", "end": "20:40"},
            "金沢": {"desc": "ナイター🌙", "start": "16:35", "end": "20:50"}
        },
        "auto": {
            "飯塚": {"desc": "ミッドナイト⭐ 3日目", "start": "20:19", "end": "23:45"}
        }
    }
}

def build_epg_xml():
    tv = ET.Element("tv", {"generator-info-name": "CombinedEPGGenerator"})
    JST = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(JST)
    
    today_str = (now - datetime.timedelta(days=1) if now.hour < 1 else now).strftime("%Y%m%d")
    dt_obj = datetime.datetime.strptime(today_str, "%Y%m%d")
    today_display = dt_obj.strftime("%Y年%m月%d日")
    day_schedules = SCHEDULES.get(today_str, {})

    for target_map, category in [(KEIRIN_MAP, "keirin"), (KEIBA_MAP, "keiba"), (AUTO_MAP, "auto")]:
        cat_data = day_schedules.get(category, {})
        for v_name, tvg_id in target_map.items():
            channel = ET.SubElement(tv, "channel", id=tvg_id)
            ET.SubElement(channel, "display-name").text = v_name

            if v_name in cat_data:
                info = cat_data[v_name]
                desc_text = info["desc"]
                
                start_dt = datetime.datetime.strptime(f"{today_str} {info['start']}", "%Y%m%d %H:%M").replace(tzinfo=JST)
                end_dt = datetime.datetime.strptime(f"{today_str} {info['end']}", "%Y%m%d %H:%M").replace(tzinfo=JST)
                
                pre_start = start_dt - datetime.timedelta(minutes=30)
                post_end = end_dt + datetime.timedelta(minutes=30)
                
                day_start_limit = datetime.datetime.strptime(f"{today_str} 01:00", "%Y%m%d %H:%M").replace(tzinfo=JST)

                if day_start_limit <= now < pre_start:
                    title_text = f"♦本日開催 実況中継前 第①レース{info['start']} 開始♦"
                elif pre_start <= now <= post_end:
                    title_text = f"♦{v_name} {desc_text} 実況放送♦"
                else:
                    title_text = "♦本日 全レース終了♦"
            else:
                title_text = "💎本日は開催しておりません💎"

            prog = ET.SubElement(tv, "programme", start=f"{today_str}000000 +0900", stop=f"{today_str}235959 +0900", channel=tvg_id)
            ET.SubElement(prog, "title", lang="ja").text = title_text
            ET.SubElement(prog, "desc", lang="ja").text = f"{today_display} {v_name} ステータス: {title_text}"

    tree = ET.ElementTree(tv)
    if hasattr(ET, "indent"): 
        ET.indent(tree, space="    ")
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print(f"{today_display} EPG生成完了")

if __name__ == "__main__":
    build_epg_xml()
