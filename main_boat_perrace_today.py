import datetime
import html as html_lib
import json
import re
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


BOAT_OFFICIAL_INDEX_URL = (
    "https://www.boatrace.jp/owpc/pc/race/index?hd={date}"
)

BOAT_OFFICIAL_RACEINDEX_URL = (
    "https://www.boatrace.jp/owpc/pc/race/raceindex?hd={date}&jcd={code}"
)

BOAT_CODE_BY_NAME = {
    "01 桐生": "01",
    "02 戸田": "02",
    "03 江戸川": "03",
    "04 平和島": "04",
    "05 多摩川": "05",
    "06 浜名湖": "06",
    "07 蒲郡": "07",
    "08 常滑": "08",
    "09 津": "09",
    "10 三国": "10",
    "11 びわこ": "11",
    "12 住之江": "12",
    "13 尼崎": "13",
    "14 鳴門": "14",
    "15 丸亀": "15",
    "16 児島": "16",
    "17 宮島": "17",
    "18 徳山": "18",
    "19 下関": "19",
    "20 若松": "20",
    "21 芦屋": "21",
    "22 福岡": "22",
    "23 唐津": "23",
    "24 大村": "24",
}

BOAT_NAME_BY_CODE = {code: name for name, code in BOAT_CODE_BY_NAME.items()}

# EPG generation window.
# Always generate from today through the next 6 days.
EPG_DAYS = 7

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

            # Visible EPG title:
            # venue / R / start / official race title / class or conditions.
            title_parts = [
                f"{main_mark}{icon}".strip(),
                venue,
                f"{race_no}R",
                f"{race.get('time', '')}発走",
                display_name,
            ]

            if race_type and race_type not in {"一般", display_name}:
                title_parts.append(f"【{race_type}】")

            if (
                conditions
                and conditions != race_name
                and conditions != race_type
                and conditions not in display_name
            ):
                title_parts.append(conditions)

            title = " ".join(x for x in title_parts if x).strip()

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
        event_name = clean_epg_meta_text(info.get("event_name", ""))
        event_day = clean_epg_meta_text(info.get("event_day", ""))

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
            title_parts.append(f"{race.get('time', '')}発走")
            # Keep the exact source race name, e.g. A級予選 / 一次予選 / 準決勝 / 決勝.
            title_parts.append(race_name)

            race_class = race.get("race_class", "").strip()
            if race_class and race_class not in race_name:
                title_parts.append(f"【{race_class}】")

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
            is_semi = bool(race.get("is_semi")) or "準決" in race_name
            is_final = bool(race.get("is_final")) and not is_semi

            if is_semi:
                desc_lines.append("🔥 準決勝")
            if is_final:
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


def clean_epg_meta_text(value):
    """Drop broken metadata such as a lone Japanese parenthesis from EPG."""
    s = re.sub(r"\s+", " ", str(value or "")).strip()
    if not s:
        return ""
    s = s.strip(" \t\r\n-|｜()（）[]【】『』「」・:：,，.。")
    if not s:
        return ""
    if not re.search(r"[0-9A-Za-zぁ-んァ-ヶ一-龠々〆ヶ]", s):
        return ""
    return s


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
            raw_main = bool(race.get("main"))
            is_semi = bool(race.get("is_semi")) or "準決" in race_name
            is_final = (
                bool(race.get("is_final"))
                or "優勝" in race_name
                or "決勝" in race_name
            ) and not is_semi
            is_special_main = any(
                word in race_name
                for word in ("特選", "特別選抜", "選抜戦")
            )
            main = raw_main and (is_final or is_special_main)
            icon = race.get("icon", "🏍️")

            title_parts = []
            if main:
                title_parts.append("🏆 MAIN")
            title_parts.append(icon)
            if grade and main:
                title_parts.append(f"【{grade}】")
            title_parts.append(f"{venue} {race_no}R")
            title_parts.append(f"{race.get('time', '')}発走")
            # Keep the exact source race title/stage, e.g. 一次予選 / 準決勝 / 優勝戦.
            title_parts.append(race_name)

            race_type = race.get("race_type", "").strip()
            if race_type and race_type not in race_name:
                title_parts.append(f"【{race_type}】")

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
            if is_semi:
                desc_lines.append("🔥 準決勝")
            if is_final:
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


def fetch_text(url, label="URL"):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Cache-Control": "no-cache",
                "Accept-Language": "ja-JP,ja;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"{label}: 取得失敗: {e}")
        return ""


def strip_html_tags(source):
    if not source:
        return ""
    source = re.sub(r"(?is)<script.*?</script>", " ", source)
    source = re.sub(r"(?is)<style.*?</style>", " ", source)
    source = re.sub(r"(?s)<[^>]+>", " ", source)
    source = html_lib.unescape(source)
    source = re.sub(r"\s+", " ", source)
    return source.strip()


def extract_boat_active_codes(index_html):
    # Official daily index links contain jcd=01 ... jcd=24.
    found = set(
        re.findall(r"(?:[?&]|&amp;)jcd=(\d{2})", index_html or "")
    )
    return sorted(code for code in found if code in BOAT_NAME_BY_CODE)


def extract_boat_race_times(race_html):
    """Return [(race_no, HH:MM), ...] from official raceindex HTML."""
    if not race_html:
        return []

    compact = re.sub(r"\s+", " ", html_lib.unescape(race_html))
    found = {}

    # Works with both visible table text and link-heavy HTML:
    # 1R ... 15:28, 2R ... 16:02, ...
    for race_no in range(1, 13):
        patterns = [
            rf">\s*{race_no}R\s*<.*?([0-2]?\d:[0-5]\d)",
            rf"\b{race_no}R\b.{{0,1200}}?([0-2]?\d:[0-5]\d)",
        ]
        for pat in patterns:
            m = re.search(pat, compact, flags=re.I | re.S)
            if m:
                found[race_no] = m.group(1)
                break

    # Fallback on stripped text.
    if len(found) < 2:
        plain = strip_html_tags(race_html)
        for race_no in range(1, 13):
            if race_no in found:
                continue
            m = re.search(
                rf"\b{race_no}R\b.{{0,150}}?([0-2]?\d:[0-5]\d)",
                plain,
                flags=re.I,
            )
            if m:
                found[race_no] = m.group(1)

    return [(n, found[n]) for n in sorted(found)]


def infer_boat_day_type(race_times):
    if not race_times:
        return "開催", "🚤"

    first = race_times[0][1]
    try:
        hour = int(first.split(":")[0])
    except Exception:
        return "開催", "🚤"

    if hour < 10:
        return "モーニング", "🌅"
    if hour >= 14:
        return "ナイター", "🌙"
    return "デイ", "☀️"


def fetch_boat_week_schedule(today_date, days):
    """
    Official BOAT RACE pages:
      index?hd=YYYYMMDD -> active venues for that date
      raceindex?hd=YYYYMMDD&jcd=XX -> 1R..12R race times
    """
    week = {}

    for offset in range(days):
        d = today_date + datetime.timedelta(days=offset)
        date_str = d.strftime("%Y%m%d")
        print(f"BOAT 週間予定: {date_str} ...", end="", flush=True)

        index_url = BOAT_OFFICIAL_INDEX_URL.format(date=date_str)
        index_html = fetch_text(index_url, f"BOAT index {date_str}")

        if not index_html:
            week[date_str] = {
                "ok": False,
                "venues": {},
            }
            print(" 取得失敗")
            continue

        active_codes = extract_boat_active_codes(index_html)
        venues = {}

        for code in active_codes:
            v_name = BOAT_NAME_BY_CODE.get(code)
            if not v_name:
                continue

            race_url = BOAT_OFFICIAL_RACEINDEX_URL.format(
                date=date_str,
                code=code,
            )
            race_html = fetch_text(race_url, f"BOAT {date_str} {code}")
            race_times = extract_boat_race_times(race_html)
            day_type, emoji = infer_boat_day_type(race_times)

            # Race title = first H2-like heading from the race page when available.
            title = ""
            if race_html:
                m = re.search(r"(?is)<h2[^>]*>(.*?)</h2>", race_html)
                if m:
                    title = strip_html_tags(m.group(1))

            venues[v_name] = {
                "code": code,
                "title": title,
                "day_type": day_type,
                "emoji": emoji,
                "races": [
                    {"race": str(race_no), "time": hhmm}
                    for race_no, hhmm in race_times
                ],
            }

        week[date_str] = {
            "ok": True,
            "venues": venues,
        }
        print(f" {len(venues)}場")

    return week


def build_boat_race_epg(
    tv,
    date_str,
    boat_week,
    JST,
    today_display,
):
    """
    Build BOAT EPG for one date from official schedule.
    Returns True if the daily official index was available.
    """
    day_info = boat_week.get(date_str, {})
    if not day_info.get("ok"):
        return False

    venues = day_info.get("venues", {})

    for v_name, tvg_id in BOAT_MAP.items():
        day_start = datetime.datetime.strptime(
            f"{date_str} 01:00", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)
        day_end = datetime.datetime.strptime(
            f"{date_str} 23:59", "%Y%m%d %H:%M"
        ).replace(tzinfo=JST)

        info = venues.get(v_name)
        if not info:
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                f"💤 本日非開催 {v_name}（ボートレース）",
                f"BOAT RACE公式の{today_display}開催一覧に"
                f"{v_name}は掲載されていません。",
            )
            continue

        races = info.get("races", [])
        day_type = info.get("day_type", "開催")
        emoji = info.get("emoji", "🚤")
        event_title = info.get("title", "")

        # Future cards can exist before individual race times are published.
        if not races:
            title = f"📅 開催予定 {v_name} {emoji}{day_type} 🚤ボートレース"
            desc_lines = [
                f"🚤 ボートレース {v_name}",
                f"{emoji} 開催区分: {day_type}",
                f"📅 {today_display}",
                "BOAT RACE公式の開催一覧で開催を確認済み。",
                "1R～12Rの発走予定時刻は公開後に自動反映します。",
            ]
            if event_title:
                desc_lines.insert(1, f"📢 {event_title}")
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                title,
                "\n".join(desc_lines),
            )
            continue

        race_dts = []
        for race in races:
            try:
                dt = datetime.datetime.strptime(
                    f"{date_str} {race.get('time','')}",
                    "%Y%m%d %H:%M",
                ).replace(tzinfo=JST)
            except Exception:
                continue
            race_dts.append((race, dt))

        if not race_dts:
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                f"📅 開催予定 {v_name} {emoji}{day_type} 🚤ボートレース",
                f"🚤 ボートレース {v_name}\n📅 {today_display}",
            )
            continue

        pre_start = max(
            day_start,
            race_dts[0][1] - datetime.timedelta(minutes=20),
        )

        if day_start < pre_start:
            add_programme(
                tv,
                tvg_id,
                day_start,
                pre_start,
                f"⏳ 待機 {v_name} {emoji}{day_type}",
                "\n".join(
                    x for x in [
                        f"🚤 ボートレース {v_name}",
                        f"📢 {event_title}" if event_title else "",
                        f"1R {race_dts[0][0].get('time','')} 発走予定",
                        f"📅 {today_display}",
                    ] if x
                ),
            )

        # Continuous race blocks:
        # from 10 min before each deadline until 10 min before next race.
        for idx, (race, race_dt) in enumerate(race_dts):
            block_start = max(
                pre_start,
                race_dt - datetime.timedelta(minutes=10),
            )

            if idx + 1 < len(race_dts):
                next_dt = race_dts[idx + 1][1]
                block_stop = next_dt - datetime.timedelta(minutes=10)
            else:
                block_stop = race_dt + datetime.timedelta(minutes=30)

            if block_stop <= block_start:
                block_stop = race_dt + datetime.timedelta(minutes=15)

            race_no = race.get("race", "")
            race_time = race.get("time", "")

            title_parts = [
                "🚤",
                v_name,
                f"{race_no}R",
                f"{race_time}発走",
                f"{emoji}{day_type}",
            ]
            if event_title:
                title_parts.append(event_title)
            title = " ".join(x for x in title_parts if x).strip()

            desc_lines = [
                f"🚤 ボートレース {v_name}",
                f"{emoji} 開催区分: {day_type}",
                f"⏰ 発走予定: {race_time}",
                f"📅 {today_display}",
            ]
            if event_title:
                desc_lines.insert(1, f"📢 {event_title}")

            add_programme(
                tv,
                tvg_id,
                block_start,
                min(block_stop, day_end),
                title,
                "\n".join(desc_lines),
            )

        finish = race_dts[-1][1] + datetime.timedelta(minutes=30)
        if finish < day_end:
            add_programme(
                tv,
                tvg_id,
                finish,
                day_end,
                f"🏁 終了 {v_name} {emoji}{day_type}",
                f"{v_name}の本日のボートレースは終了しました。",
            )

    return True



def build_boat_epg(
    tv,
    date_str,
    boat_today,
    JST,
    today_str,
    today_display,
):
    """
    boatrace_today.json の当日レース毎データを、そのままEPGへ反映する。

    優先するJSON項目:
      races[].title
      races[].epg_start
      races[].epg_end
      finish_title / finish_start / finish_end
      status_title
    """
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
        if not isinstance(info, dict):
            info = {}

        races = info.get("races", [])
        held = bool(info.get("held")) or bool(races)
        day_type = info.get("day_type", "開催")
        emoji = info.get("emoji", "🚤")

        # -------------------------------------------------
        # 非開催
        # -------------------------------------------------
        if not held:
            title = info.get("status_title") or f"⛔ {v_name} 本日非開催"
            add_programme(
                tv,
                tvg_id,
                day_start,
                day_end,
                title,
                f"本日は{v_name}でのボートレース開催予定はありません。",
            )
            continue

        # -------------------------------------------------
        # レース毎EPG
        # -------------------------------------------------
        valid_races = []

        for race in races:
            try:
                epg_start_text = race.get("epg_start", "")
                epg_end_text = race.get("epg_end", "")

                start_dt = datetime.datetime.strptime(
                    epg_start_text,
                    "%Y-%m-%d %H:%M",
                ).replace(tzinfo=JST)

                stop_dt = datetime.datetime.strptime(
                    epg_end_text,
                    "%Y-%m-%d %H:%M",
                ).replace(tzinfo=JST)

                if stop_dt <= start_dt:
                    continue

                valid_races.append((race, start_dt, stop_dt))
            except Exception:
                continue

        if valid_races:
            first_start = valid_races[0][1]

            if day_start < first_start:
                first_race = valid_races[0][0]
                add_programme(
                    tv,
                    tvg_id,
                    day_start,
                    first_start,
                    f"⏳ 待機 {v_name} {emoji}{day_type} "
                    f"1R【{first_race.get('time', '')}】",
                    f"🚤 ボートレース {v_name}\n"
                    f"{emoji} 開催区分: {day_type}\n"
                    f"📅 {today_display}",
                )

            for race, start_dt, stop_dt in valid_races:
                race_no = race.get("rno", race.get("race", ""))
                race_time = race.get("time", "")
                race_name = race.get("race_name", "").strip()

                # PowerShell側で作ったタイトルを最優先。
                title = race.get("title", "").strip()
                if not title:
                    if race_name:
                        title = (
                            f"{emoji} {v_name} {race_no}R "
                            f"{race_name}【{race_time}】"
                        )
                    else:
                        title = (
                            f"{emoji} {v_name} {race_no}R"
                            f"【{race_time}】"
                        )

                desc_lines = [
                    f"🚤 ボートレース {v_name}",
                    f"{emoji} 開催区分: {day_type}",
                    f"⏰ 締切予定: {race_time}",
                    f"📅 {today_display}",
                ]
                if race_name:
                    desc_lines.insert(2, f"📢 レース名: {race_name}")

                add_programme(
                    tv,
                    tvg_id,
                    max(start_dt, day_start),
                    min(stop_dt, day_end),
                    title,
                    "\n".join(desc_lines),
                )

            # -------------------------------------------------
            # 最終R後
            # -------------------------------------------------
            last_stop = valid_races[-1][2]

            finish_start = last_stop
            finish_end = day_end

            try:
                if info.get("finish_start"):
                    finish_start = datetime.datetime.strptime(
                        info["finish_start"],
                        "%Y-%m-%d %H:%M",
                    ).replace(tzinfo=JST)
            except Exception:
                pass

            try:
                if info.get("finish_end"):
                    finish_end = datetime.datetime.strptime(
                        info["finish_end"],
                        "%Y-%m-%d %H:%M",
                    ).replace(tzinfo=JST)
            except Exception:
                pass

            finish_start = max(finish_start, last_stop)

            # finish_end が早すぎても、当日23:59までは「終了」を表示。
            # EPG上で空白時間を作らない。
            if finish_start < day_end:
                add_programme(
                    tv,
                    tvg_id,
                    finish_start,
                    day_end,
                    info.get("finish_title")
                    or f"🏁 {v_name} 本日開催終了",
                    f"{v_name}の本日のボートレースは終了しました。",
                )

            continue

        # -------------------------------------------------
        # 開催は確認できたが races が取れなかった場合の保険
        # -------------------------------------------------
        start_text = info.get("start")
        end_text = info.get("end")

        if start_text and end_text:
            try:
                start_dt = datetime.datetime.strptime(
                    f"{date_str} {start_text}", "%Y%m%d %H:%M"
                ).replace(tzinfo=JST)
                end_dt = datetime.datetime.strptime(
                    f"{date_str} {end_text}", "%Y%m%d %H:%M"
                ).replace(tzinfo=JST)

                if end_dt <= start_dt:
                    end_dt += datetime.timedelta(days=1)

                if day_start < start_dt:
                    add_programme(
                        tv,
                        tvg_id,
                        day_start,
                        start_dt,
                        f"⏳ 待機 {v_name} {emoji}{day_type}",
                        f"🚤 ボートレース {v_name}\n📅 {today_display}",
                    )

                add_programme(
                    tv,
                    tvg_id,
                    max(start_dt, day_start),
                    min(end_dt, day_end),
                    f"🔴 LIVE {v_name} {emoji}{day_type} 🚤ボートレース",
                    f"🚤 ボートレース {v_name}\n"
                    f"⏰ 配信予定: {start_text}～{end_text}\n"
                    f"📅 {today_display}",
                )

                if end_dt < day_end:
                    add_programme(
                        tv,
                        tvg_id,
                        end_dt,
                        day_end,
                        f"🏁 {v_name} 本日開催終了",
                        f"{v_name}の本日のボートレースは終了しました。",
                    )
                continue
            except Exception:
                pass

        add_programme(
            tv,
            tvg_id,
            day_start,
            day_end,
            f"📅 開催予定 {v_name} {emoji}{day_type}",
            f"🚤 ボートレース {v_name}\n📅 {today_display}",
        )



def build_future_placeholder(
    tv,
    date_str,
    target_map,
    category_label,
    category_icon,
    JST,
    today_display,
):
    """Future dates without race JSON: show a neutral schedule placeholder."""
    day_start = datetime.datetime.strptime(
        f"{date_str} 01:00", "%Y%m%d %H:%M"
    ).replace(tzinfo=JST)
    day_end = datetime.datetime.strptime(
        f"{date_str} 23:59", "%Y%m%d %H:%M"
    ).replace(tzinfo=JST)

    for v_name, tvg_id in target_map.items():
        add_programme(
            tv,
            tvg_id,
            day_start,
            day_end,
            f"📅 {v_name}（{category_label}）",
            f"{category_icon} {category_label} {v_name}\n"
            f"📅 {today_display}\n"
            "当日データ取得時に詳細EPGへ自動更新します。",
        )


def build_stream_channel_placeholder(
    tv,
    date_str,
    channel_names,
    JST,
    today_display,
):
    """Channels such as JRA official/Green Channel that have no race JSON."""
    day_start = datetime.datetime.strptime(
        f"{date_str} 01:00", "%Y%m%d %H:%M"
    ).replace(tzinfo=JST)
    day_end = datetime.datetime.strptime(
        f"{date_str} 23:59", "%Y%m%d %H:%M"
    ).replace(tzinfo=JST)

    for v_name in channel_names:
        tvg_id = KEIBA_MAP.get(v_name)
        if not tvg_id:
            continue
        add_programme(
            tv,
            tvg_id,
            day_start,
            day_end,
            f"📺 {v_name}",
            f"📺 {v_name}\n📅 {today_display}",
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

    today_date = datetime.datetime.now(JST).date()
    # 今日分は ganble の boatrace_today.json をそのまま使用。
    # 公式サイトの週間取得は明日以降6日分だけにして重複取得を避ける。
    boat_week = fetch_boat_week_schedule(
        today_date + datetime.timedelta(days=1),
        EPG_DAYS - 1,
    )

    for day_offset in range(EPG_DAYS):
        target_date = today_date + datetime.timedelta(days=day_offset)
        date_str = target_date.strftime("%Y%m%d")
        today_display = target_date.strftime("%Y年%m月%d日")
        is_today = (day_offset == 0)

        # -------------------------------------------------
        # 競輪
        # 今日: 各R単位だけを生成。旧「1日LIVE枠」は絶対に追加しない。
        # 未来: 詳細JSONが当日用のため、開催予定プレースホルダーのみ。
        # -------------------------------------------------
        if is_today:
            used_auto_keirin = build_keirin_race_epg(
                tv,
                date_str,
                keirin_schedule,
                JST,
                today_display,
            )
            if not used_auto_keirin:
                # 当日のJSON取得に失敗した場合だけ、ニュートラルな待機表示。
                # 旧LIVE一括枠は作らない。
                build_future_placeholder(
                    tv,
                    date_str,
                    KEIRIN_MAP,
                    "競輪",
                    "🚲",
                    JST,
                    today_display,
                )
        else:
            build_future_placeholder(
                tv,
                date_str,
                KEIRIN_MAP,
                "競輪",
                "🚲",
                JST,
                today_display,
            )

        # -------------------------------------------------
        # 競馬
        # 今日: JSONの日付一致なら各R自動EPG。
        # 未来: 決め打ちせずプレースホルダー。
        # -------------------------------------------------
        if is_today:
            used_auto_keiba = build_keiba_race_epg(
                tv,
                date_str,
                keiba_schedule,
                JST,
                today_display,
            )
            if not used_auto_keiba:
                regular_keiba_map = {
                    k: v
                    for k, v in KEIBA_MAP.items()
                    if k not in {"ＪＲＡ公式", "ＪＲＡグリーン"}
                }
                # 当日は旧「1日LIVE枠」を作らない。
                # JSON取得失敗時はニュートラルなプレースホルダーだけにする。
                build_future_placeholder(
                    tv,
                    date_str,
                    regular_keiba_map,
                    "競馬",
                    "🏇",
                    JST,
                    today_display,
                )
        else:
            regular_keiba_map = {
                k: v
                for k, v in KEIBA_MAP.items()
                if k not in {"ＪＲＡ公式", "ＪＲＡグリーン"}
            }
            build_future_placeholder(
                tv,
                date_str,
                regular_keiba_map,
                "競馬",
                "🏇",
                JST,
                today_display,
            )

        # JRA公式 / グリーンは race JSON の対象外なので、
        # 固定時刻を持たせず毎日ニュートラルな表示を作る。
        build_stream_channel_placeholder(
            tv,
            date_str,
            ("ＪＲＡ公式", "ＪＲＡグリーン"),
            JST,
            today_display,
        )

        # -------------------------------------------------
        # オートレース
        # -------------------------------------------------
        if is_today:
            used_auto_autorace = build_autorace_race_epg(
                tv,
                date_str,
                autorace_schedule,
                JST,
                today_display,
            )
            if not used_auto_autorace:
                # 当日は旧「1日LIVE枠」を作らない。
                # JSON取得失敗時はニュートラルなプレースホルダーだけにする。
                build_future_placeholder(
                    tv,
                    date_str,
                    AUTO_MAP,
                    "オートレース",
                    "🏍️",
                    JST,
                    today_display,
                )
        else:
            build_future_placeholder(
                tv,
                date_str,
                AUTO_MAP,
                "オートレース",
                "🏍️",
                JST,
                today_display,
            )

        # -------------------------------------------------
        # ボートレース
        # BOAT RACE公式サイトの指定日開催一覧 + raceindex を使い、
        # 今日から7日先まで開催場と1R～12R発走予定を自動EPG化。
        # 公式ページ取得失敗時だけ従来JSON方式へフォールバック。
        # -------------------------------------------------
        if is_today:
            # 当日は boatrace_today.json の races[].title / epg_start / epg_end を
            # そのまま採用し、レース毎タイトルを最優先。
            build_boat_epg(
                tv,
                date_str,
                boat_today,
                JST,
                today_str,
                today_display,
            )
        else:
            used_boat_official = build_boat_race_epg(
                tv,
                date_str,
                boat_week,
                JST,
                today_display,
            )

            if not used_boat_official:
                build_boat_epg(
                    tv,
                    date_str,
                    boat_today,
                    JST,
                    today_str,
                    today_display,
                )


    # -------------------------------------------------
    # Safety cleanup:
    # For TODAY's keirin channels, keep only the new per-race model:
    #   待機 / 各R / 終了 / neutral placeholder
    # Remove legacy day-long "LIVE 松山 ... 2日目" style blocks if any
    # other code path accidentally added them.
    # -------------------------------------------------
    today_prefix = today_str
    for prog in list(tv.findall("programme")):
        ch = prog.get("channel", "")
        start_attr = prog.get("start", "")
        category = None
        if ch.startswith("keirin."):
            category = "keirin"
        elif ch.startswith("keiba.") and ch not in {"keiba.jra", "keiba.green"}:
            category = "keiba"
        elif ch.startswith("auto.") or ch.startswith("autorace."):
            category = "autorace"

        if category is None or not start_attr.startswith(today_prefix):
            continue

        title_el = prog.find("title")
        title_text = title_el.text if title_el is not None and title_el.text else ""

        # 当日は全公営競技を各R単位に統一。
        # レース名（特別、予選、準決、優勝戦など）は各Rタイトル側にそのまま残す。
        keep = (
            "R" in title_text and (
                "発走" in title_text
                or category in {"keiba", "autorace"}
            )
        ) or title_text.startswith("⏳ 待機") \
          or title_text.startswith("🏁 終了") \
          or title_text.startswith("📅") \
          or title_text.startswith("💤")

        legacy_live = "🔴 LIVE" in title_text and "R" not in title_text

        if legacy_live or not keep:
            tv.remove(prog)

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
    print(f"ボートEPG: BOAT RACE公式 7日分を自動取得")
    print("競馬: keiba_schedule.json 優先")
    print("競輪: keirin_schedule.json 優先")
    print("オート: autorace_schedule.json 優先")
    print("出力: epg.xml")
    print("============================")


if __name__ == "__main__":
    build_epg_xml()