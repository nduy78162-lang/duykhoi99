"""
⏳ ESCAPE TIME: PUZZLE GAMES — game thoát phòng giải đố bằng Streamlit
=====================================================================
Cài đặt:  pip install "streamlit>=1.37"
Chạy:     streamlit run escape_time.py

- 3 căn phòng, 13 vật thể để khám phá, đếm ngược theo thời gian thực
- Mỗi lần chơi: mã két, mật thư, câu đố, dãy số... đều được tạo ngẫu nhiên
- Túi đồ, hệ thống gợi ý (trừ giờ), hộp quà bất ngờ, bảng vàng điểm cao
"""

import json
import random
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Escape Time: Puzzle Games",
    page_icon="⏳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if not hasattr(st, "fragment"):
    st.error("Game cần Streamlit >= 1.37. Hãy chạy: pip install -U streamlit")
    st.stop()

# ----------------------------------------------------------------------------
# CẤU HÌNH
# ----------------------------------------------------------------------------
SCORE_FILE = Path(__file__).with_name("escape_time_scores.json")
HINT_PENALTY = 30  # giây bị trừ mỗi lần xin gợi ý

# tên độ khó: (tổng giây, số gợi ý, hệ số điểm, mô tả)
DIFFICULTY = {
    "Dễ": (15 * 60, 4, 1.0, "15 phút · 4 gợi ý"),
    "Thường": (10 * 60, 3, 1.5, "10 phút · 3 gợi ý"),
    "Khó": (6 * 60, 1, 2.0, "6 phút · 1 gợi ý"),
}

ITEMS = {
    "Chìa khóa đồng": ("🗝️", "Chiếc chìa khóa đồng nhỏ, vẫn còn âm ấm."),
    "Mật thư": ("📜", None),  # mô tả tạo động
    "Dung dịch phát sáng": ("🧪", "Chất lỏng xanh lơ, tỏa ánh sáng dịu."),
    "Thẻ từ": ("💳", "Thẻ từ có vạch đỏ, in chữ 'CỬA THÉP'."),
    "Bánh răng vàng": ("⚙️", "Bánh răng vàng nặng tay, như khớp với một cỗ máy lớn."),
}

EMOJI = ["🌸", "🐦", "⭐", "🌙"]

WORDS = ["ESCAPE", "SECRET", "PUZZLE", "HIDDEN", "ORIGIN", "SILVER"]

# (câu đố, chữ số đáp án)
RIDDLES = [
    [("Số nguyên tố chẵn duy nhất", 2), ("Số hoàn hảo nhỏ nhất", 6), ("Bình phương của 3", 9)],
    [("Số ngày trong một tuần", 7), ("Số cạnh của hình tam giác", 3), ("Số mặt của một con xúc xắc", 6)],
    [("Số chân của con nhện", 8), ("Số ngón tay trên một bàn tay", 5), ("Số màu trong cầu vồng", 7)],
]

# (dãy số, đáp án 2 chữ số, quy luật)
SEQ1 = [
    ("2, 6, 12, 20, ?", 30, "các tích n×(n+1)"),
    ("3, 8, 15, 24, ?", 35, "bình phương trừ 1"),
    ("1, 4, 9, 16, 25, ?", 36, "các số chính phương"),
    ("5, 10, 20, 40, ?", 80, "nhân đôi mỗi bước"),
    ("4, 7, 11, 16, ?", 22, "hiệu tăng dần 3, 4, 5…"),
]
SEQ2 = [
    ("1, 1, 2, 3, 5, 8, ?", 13, "mỗi số bằng tổng hai số liền trước"),
    ("1, 2, 4, 7, 11, 16, ?", 22, "hiệu tăng dần 1, 2, 3…"),
    ("2, 3, 5, 7, 11, 13, ?", 17, "các số nguyên tố"),
    ("100, 91, 82, 73, ?", 64, "giảm 9 mỗi bước"),
    ("3, 6, 12, 24, ?", 48, "nhân đôi mỗi bước"),
]

# Thứ tự đổ đúng của 4 lọ hóa chất
POTION_OPTIONS = ["🔴 Đỏ", "🟢 Lục", "🟡 Vàng", "🔵 Xanh dương"]
POTION_SOLUTION = ["🔵 Xanh dương", "🟡 Vàng", "🔴 Đỏ", "🟢 Lục"]

ROOMS = [
    {
        "name": "📚 Thư phòng cổ",
        "intro": (
            "Bạn tỉnh dậy trong một thư phòng cổ. Đèn dầu leo lét, mùi giấy cũ phảng phất. "
            "Cánh cửa gỗ phía sau lưng đã bị khóa chặt. 🕯️"
        ),
        "objs": [
            ("painting", "🖼️ Bức tranh"),
            ("shelf", "📚 Giá sách"),
            ("safe", "🔐 Két sắt"),
            ("desk", "🗄️ Bàn làm việc"),
            ("door0", "🚪 Cửa gỗ"),
        ],
    },
    {
        "name": "🧪 Phòng thí nghiệm",
        "intro": (
            "Phía sau cánh cửa là một phòng thí nghiệm bỏ hoang. Ống nghiệm sủi bọt lách tách, "
            "đèn huỳnh quang nhấp nháy. Ở góc phòng có một hộp quà lạ lẫm. 🎁"
        ),
        "objs": [
            ("bottles", "🧪 Bàn hóa chất"),
            ("wall", "🧱 Bức tường"),
            ("cabinet", "🗃️ Tủ khóa số"),
            ("gift", "🎁 Hộp quà"),
            ("door1", "🚪 Cửa thép"),
        ],
    },
    {
        "name": "🕰️ Phòng đồng hồ",
        "intro": (
            "Căn phòng cuối cùng. Tiếng tích tắc vang khắp nơi, nhưng chiếc đồng hồ khổng lồ giữa phòng "
            "lại đứng im. Cánh cửa thoát hiểm ở ngay đó… chỉ còn thiếu mật mã. ⏰"
        ),
        "objs": [
            ("clock", "🕰️ Đồng hồ cổ"),
            ("board", "📝 Bảng phấn"),
            ("exit", "🚪 Cửa thoát hiểm"),
        ],
    },
]

CSS = """
<style>
.title{text-align:center;font-size:2.4rem;font-weight:900;margin:0;line-height:1.2}
.sub{text-align:center;opacity:.75;margin-top:.2rem}
.timer{font-size:2.2rem;font-weight:800;text-align:center;border-radius:14px;
       padding:.2rem 0;letter-spacing:2px;font-variant-numeric:tabular-nums}
.timer.ok{background:rgba(46,204,113,.15);color:#2ecc71}
.timer.warn{background:rgba(241,196,15,.15);color:#f1c40f}
.timer.danger{background:rgba(231,76,60,.18);color:#e74c3c;animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.55}}
.big{font-size:1.7rem;letter-spacing:4px;line-height:2.3rem;margin:.1rem 0}
.stars{text-align:center;font-size:2.4rem}
</style>
"""


# ----------------------------------------------------------------------------
# TIỆN ÍCH
# ----------------------------------------------------------------------------
def fmt(sec):
    sec = max(0, int(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def norm(text):
    return "".join(text.split()).upper()


def time_left(g):
    ref = g.get("end") or time.time()
    return g["duration"] - (ref - g["start"]) - g["penalty"]


def say(g, msg):
    g["log"].append(msg)


def has(g, item):
    return item in g["inv"]


def give(g, item, msg):
    if item not in g["inv"]:
        g["inv"].append(item)
    say(g, msg)


def make_puzzle():
    """Sinh toàn bộ câu đố ngẫu nhiên cho một lượt chơi."""
    counts = [random.randint(1, 9) for _ in range(4)]
    word = random.choice(WORDS)
    shift = random.randint(2, 5)
    cipher = "".join(chr((ord(c) - 65 + shift) % 26 + 65) for c in word)
    riddle = random.choice(RIDDLES)
    s1, s2 = random.choice(SEQ1), random.choice(SEQ2)
    return {
        "counts": counts,
        "safe": "".join(map(str, counts)),
        "word": word,
        "shift": shift,
        "cipher": cipher,
        "riddle": riddle,
        "keypad": "".join(str(d) for _, d in riddle),
        "seq1": s1,
        "seq2": s2,
        "final": f"{s1[1]}{s2[1]}",
        "surprise": random.choice(["time", "hint", "joke"]),
    }


def start_game(diff, name):
    secs, hints, _, _ = DIFFICULTY[diff]
    st.session_state.g = {
        "phase": "play",
        "gid": int(time.time() * 1000),
        "name": name.strip() or "Người bí ẩn",
        "diff": diff,
        "duration": secs,
        "start": time.time(),
        "end": None,
        "penalty": 0,
        "hints": hints,
        "used_hints": 0,
        "room": 0,
        "inv": [],
        "flags": set(),
        "log": ["⏳ Cánh cửa sập lại sau lưng bạn. **Đồng hồ bắt đầu chạy!** Hãy khám phá căn phòng."],
        "P": make_puzzle(),
    }


def calc_score(g):
    left = max(0, time_left(g))
    mult = DIFFICULTY[g["diff"]][2]
    bonus = g["hints"] * 100 + (500 if g["used_hints"] == 0 else 0)
    return int((left * 10 + bonus) * mult)


def calc_stars(g):
    ratio = max(0, time_left(g)) / g["duration"]
    return 3 if ratio >= 0.5 else 2 if ratio >= 0.25 else 1


def load_scores():
    try:
        return json.loads(SCORE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_score(entry):
    scores = load_scores()
    scores.append(entry)
    scores.sort(key=lambda e: -e["score"])
    try:
        SCORE_FILE.write_text(json.dumps(scores[:50], ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        pass  # môi trường chỉ đọc: bỏ qua
    return scores.index(entry) + 1


def win(g):
    g["phase"] = "win"
    g["end"] = time.time()
    g["score"] = calc_score(g)
    g["stars"] = calc_stars(g)
    g["rank"] = save_score(
        {
            "name": g["name"],
            "diff": g["diff"],
            "score": g["score"],
            "left": int(max(0, time_left(g))),
        }
    )


def code_form(key, label, placeholder=""):
    """Form nhập mã. Trả về None nếu chưa bấm nút, ngược lại là chuỗi đã chuẩn hóa."""
    with st.form(key, clear_on_submit=True):
        val = st.text_input(label, placeholder=placeholder, max_chars=12, key=f"{key}_in")
        sub = st.form_submit_button("Thử", use_container_width=True)
    return norm(val) if sub else None


# ----------------------------------------------------------------------------
# PHÒNG 1 — THƯ PHÒNG CỔ
# ----------------------------------------------------------------------------
def o_painting(g, P):
    g["flags"].add("seen_painting")
    st.write("Bức tranh vẽ một khu vườn ban đêm, từng thứ được vẽ rất rõ ràng, như thể ai đó muốn bạn đếm chúng:")
    for emo, c in zip(EMOJI, P["counts"]):
        st.markdown(f"<div class='big'>{emo * c}</div>", unsafe_allow_html=True)
    st.caption("Ở góc tranh có dòng chữ nhỏ: “Đếm theo thứ tự: hoa, chim, sao, trăng.”")


def o_shelf(g, P):
    g["flags"].add("seen_shelf")
    st.write("Giữa những gáy sách bụi bặm, cuốn **“Julius Caesar”** kẹp một mẩu giấy:")
    st.info(f"“Muốn đọc mật thư, hãy **lùi {P['shift']} bước** trong bảng chữ cái cho mỗi chữ cái.”")
    st.caption("Ví dụ lùi 1 bước: C → B, B → A. Lùi quá A thì quay vòng về Z.")


def o_safe(g, P):
    if "safe" in g["flags"]:
        st.success("Két sắt đã mở. Bên trong trống rỗng.")
        return
    st.write("Một chiếc két sắt nặng nề với bàn phím **4 chữ số**.")
    code = code_form("f_safe", "Mật mã (4 số)", "____")
    if code is None:
        return
    if code == P["safe"]:
        g["flags"].add("safe")
        give(g, "Chìa khóa đồng", "🔓 *Cạch!* Két sắt bật mở. Bên trong có một **chìa khóa đồng**.")
        st.rerun()
    else:
        st.error("Két sắt kêu bíp bíp. Sai mã rồi!")


def o_desk(g, P):
    if "drawer" in g["flags"]:
        st.write("Ngăn kéo đã mở, chỉ còn lại bụi.")
        return
    st.write("Chiếc bàn gỗ sồi có một ngăn kéo khóa kín, ổ khóa hình bông hoa.")
    if has(g, "Chìa khóa đồng"):
        if st.button("🗝️ Dùng chìa khóa đồng", key="u_key", use_container_width=True):
            g["flags"].add("drawer")
            give(g, "Mật thư", "📂 Ngăn kéo mở ra! Bạn tìm thấy một **mật thư** viết bằng mật mã.")
            st.rerun()
    else:
        st.caption("Bạn cần một chiếc chìa khóa phù hợp.")


def o_door0(g, P):
    if "door0" in g["flags"]:
        st.success("Cánh cửa gỗ đã mở!")
        if st.button("➡️ Bước sang phòng tiếp theo", key="go1", type="primary", use_container_width=True):
            g["room"] = 1
            say(g, "🧪 Bạn bước vào **phòng thí nghiệm**. Mùi hóa chất xộc lên mũi.")
            st.rerun()
        return
    st.write("Cánh cửa gỗ có một bàn phím chữ cái với **6 ô**. Hãy nhập mật khẩu.")
    pw = code_form("f_door0", "Mật khẩu (6 chữ cái)", "______")
    if pw is None:
        return
    if pw == P["word"]:
        g["flags"].add("door0")
        say(g, "🚪 *Click!* Cánh cửa gỗ bật mở. Phía sau là một hành lang sáng đèn.")
        st.rerun()
    else:
        st.error("Bàn phím chớp đỏ. Sai mật khẩu!")


# ----------------------------------------------------------------------------
# PHÒNG 2 — PHÒNG THÍ NGHIỆM
# ----------------------------------------------------------------------------
def o_bottles(g, P):
    if "potion" in g["flags"]:
        st.success("Bình thủy tinh đã sáng lên với dung dịch phát sáng. Bạn đã giữ nó trong túi.")
        return
    st.write("Bốn lọ màu nằm trên bàn, cạnh một bình thủy tinh trống. Tờ ghi chú dán trên bàn viết:")
    st.info(
        "• Lọ 🟢 Lục được đổ **ngay sau** lọ 🔴 Đỏ.\n\n"
        "• Lọ 🔴 Đỏ **không** được đổ đầu tiên.\n\n"
        "• Lọ 🟡 Vàng **không** đứng đầu và phải đứng **cạnh** lọ 🔵 Xanh dương.\n\n"
        "• Lọ 🔵 Xanh dương **không** đứng cuối."
    )
    with st.form("f_bottles"):
        cols = st.columns(2)
        picks = []
        for i in range(4):
            with cols[i % 2]:
                picks.append(
                    st.selectbox(
                        f"Lần đổ thứ {i + 1}",
                        POTION_OPTIONS,
                        index=None,
                        placeholder="Chọn lọ…",
                        key=f"b{g['gid']}_{i}",
                    )
                )
        sub = st.form_submit_button("⚗️ Đổ vào bình", use_container_width=True)
    if not sub:
        return
    if None in picks or len(set(picks)) < 4:
        st.warning("Hãy chọn đủ 4 lọ, mỗi lọ một lần.")
    elif picks == POTION_SOLUTION:
        g["flags"].add("potion")
        give(g, "Dung dịch phát sáng", "✨ Bình sủi bọt rồi tỏa sáng xanh lơ! Bạn nhận được **dung dịch phát sáng**.")
        st.rerun()
    else:
        st.error("Bình sủi bọt, khói tím bốc lên rồi lặng im. Sai thứ tự!")


def o_wall(g, P):
    f = g["flags"]
    if "potion" not in f:
        st.write("Bức tường trắng trơn, nhưng có mùi hóa chất thoang thoảng, như thể có thứ gì đó vô hình trên đó.")
        return
    if "wall" not in f:
        st.write("Bức tường trắng trơn… nhưng dung dịch trong tay bạn đang rung nhẹ.")
        if st.button("🧪 Rưới dung dịch lên tường", key="u_potion", use_container_width=True):
            f.add("wall")
            say(g, "✨ Chữ phát sáng hiện lên trên tường! Đó là **ba câu đố**.")
            st.rerun()
        return
    st.write("Những dòng chữ phát sáng hiện ra trên tường:")
    for i, (text, _) in enumerate(P["riddle"], 1):
        st.markdown(f"**{i}.** {text}")
    st.caption("Ba đáp án (mỗi đáp án một chữ số), ghép theo thứ tự, tạo thành mật mã.")


def o_cabinet(g, P):
    if "cabinet" in g["flags"]:
        st.success("Tủ đã mở. Bạn đã lấy hết đồ bên trong.")
        return
    st.write("Một chiếc tủ kim loại với bảng số **3 chữ số**.")
    code = code_form("f_cab", "Mật mã (3 số)", "___")
    if code is None:
        return
    if code == P["keypad"]:
        g["flags"].add("cabinet")
        for item in ("Thẻ từ", "Bánh răng vàng"):
            if item not in g["inv"]:
                g["inv"].append(item)
        say(g, "🔓 Tủ bật mở! Bên trong có một **thẻ từ** và một **bánh răng vàng**.")
        st.rerun()
    else:
        st.error("Bảng số kêu bíp bíp. Sai mã!")


def o_gift(g, P):
    if "gift" in g["flags"]:
        st.write("Hộp quà đã trống rỗng.")
        return
    st.write("Một hộp quà thắt ruy băng bạc nằm lẻ loi trên sàn. Có thẻ ghi: *“Dành cho kẻ dám mở.”*")
    if st.button("🎁 Mở hộp quà", key="u_gift", use_container_width=True):
        g["flags"].add("gift")
        kind = P["surprise"]
        if kind == "time":
            g["penalty"] -= 45
            say(g, "🎁 **BẤT NGỜ!** Một chiếc đồng hồ cát phép thuật tan vào không khí: bạn được **cộng 45 giây**!")
        elif kind == "hint":
            g["hints"] += 1
            say(g, "🎁 **BẤT NGỜ!** Một con đom đóm giấy bay ra và để lại cho bạn **thêm 1 lượt gợi ý**.")
        else:
            say(g, "🎁 **BẤT NGỜ!** Một chú hề lò xo bật ra: *“Bạn có biết vì sao đồng hồ hay đi muộn? Vì nó… tích tắc quá nhiều!”* Không có phần thưởng, chỉ có tiếng cười.")
        st.rerun()


def o_door1(g, P):
    if "door1" in g["flags"]:
        st.success("Cửa thép đã mở!")
        if st.button("➡️ Bước sang phòng tiếp theo", key="go2", type="primary", use_container_width=True):
            g["room"] = 2
            say(g, "🕰️ Bạn bước vào **phòng đồng hồ**. Tiếng tích tắc vang khắp nơi.")
            st.rerun()
        return
    st.write("Cánh cửa thép nặng nề, bên cạnh có một khe quẹt thẻ.")
    if has(g, "Thẻ từ"):
        if st.button("💳 Quẹt thẻ từ", key="u_card", use_container_width=True):
            g["flags"].add("door1")
            say(g, "💚 Đèn xanh bật sáng. Cửa thép trượt mở!")
            st.rerun()
    else:
        st.caption("Bạn cần một tấm thẻ từ.")


# ----------------------------------------------------------------------------
# PHÒNG 3 — PHÒNG ĐỒNG HỒ
# ----------------------------------------------------------------------------
def o_clock(g, P):
    if "clock" in g["flags"]:
        st.success("Chiếc đồng hồ đã chạy! Chuông gõ vang và một ngăn bí mật bật mở, bên trong có tờ giấy:")
        st.info(f"**Phần 1 của mã:**  `{P['seq1'][0]}`")
        return
    st.write("Chiếc đồng hồ cao ba mét, kim đứng im. Sau mặt kính, một trục trống đang chờ một bánh răng.")
    if has(g, "Bánh răng vàng"):
        if st.button("⚙️ Lắp bánh răng vàng", key="u_gear", use_container_width=True):
            g["flags"].add("clock")
            say(g, "⚙️ Bánh răng khớp vào! Đồng hồ **bắt đầu chạy**, chuông gõ vang và một ngăn bí mật bật mở.")
            st.rerun()
    else:
        st.caption("Thiếu một bánh răng…")


def o_board(g, P):
    st.write("Trên bảng phấn có dòng chữ: *“Mã mở cửa gồm hai phần ghép nối.”*")
    st.info(f"**Phần 2 của mã:**  `{P['seq2'][0]}`")
    st.caption("Phần 1 nằm đâu đó bên trong chiếc đồng hồ…")


def o_exit(g, P):
    st.write(
        "Cánh cửa thoát hiểm có ô nhập **4 chữ số**: hai số đầu là đáp án dãy số ở **đồng hồ**, "
        "hai số sau là đáp án dãy số trên **bảng phấn**."
    )
    code = code_form("f_exit", "Mã thoát hiểm (4 số)", "____")
    if code is None:
        return
    if code == P["final"]:
        win(g)
        st.rerun()
    else:
        st.error("Cánh cửa rung lên rồi im lìm. Sai mã!")


HANDLERS = {
    "painting": o_painting, "shelf": o_shelf, "safe": o_safe, "desk": o_desk, "door0": o_door0,
    "bottles": o_bottles, "wall": o_wall, "cabinet": o_cabinet, "gift": o_gift, "door1": o_door1,
    "clock": o_clock, "board": o_board, "exit": o_exit,
}


# ----------------------------------------------------------------------------
# GỢI Ý THEO TIẾN TRÌNH
# ----------------------------------------------------------------------------
def current_hint(g, P):
    f, r = g["flags"], g["room"]
    if r == 0:
        if "safe" not in f:
            if "seen_painting" not in f:
                return "Hãy nhìn thật kỹ **bức tranh**, có thứ để đếm."
            return "Đếm từng loại hình trong tranh, ghép 4 số theo thứ tự hoa–chim–sao–trăng để mở **két sắt**."
        if "drawer" not in f:
            return "Chìa khóa đồng hợp với ổ khóa của **bàn làm việc**."
        if "door0" not in f:
            if "seen_shelf" not in f:
                return "Hãy xem **giá sách**, có thứ giúp bạn đọc được mật thư."
            return f"Lùi {P['shift']} bước mỗi chữ cái. Chữ đầu '{P['cipher'][0]}' sẽ thành '{P['word'][0]}'."
        return "Cửa đã mở, hãy bước sang phòng tiếp theo."
    if r == 1:
        if "potion" not in f:
            return "Lục luôn đứng ngay sau Đỏ, và Đỏ không đứng đầu. Đáp án bắt đầu bằng 🔵 Xanh dương."
        if "wall" not in f:
            return "Dung dịch phát sáng có thể làm hiện chữ vô hình trên **bức tường**."
        if "cabinet" not in f:
            return "Giải ba câu đố trên tường rồi ghép ba chữ số theo thứ tự cho **tủ khóa số**."
        if "door1" not in f:
            return "**Thẻ từ** dùng cho cánh cửa thép."
        return "Cửa đã mở, hãy bước sang phòng tiếp theo."
    if "clock" not in f:
        return "**Bánh răng vàng** thuộc về chiếc đồng hồ."
    return (
        f"Quy luật dãy ở đồng hồ: {P['seq1'][2]}. Quy luật dãy trên bảng: {P['seq2'][2]}. "
        "Mã = đáp án dãy đồng hồ rồi đến đáp án dãy bảng phấn."
    )


# ----------------------------------------------------------------------------
# MÀN HÌNH
# ----------------------------------------------------------------------------
def show_leaderboard():
    scores = load_scores()[:5]
    if not scores:
        st.caption("Bảng vàng còn trống. Hãy là người đầu tiên! 🏆")
        return
    st.subheader("🏆 Bảng vàng")
    st.table(
        [
            {"#": i + 1, "Tên": e["name"], "Điểm": e["score"], "Độ khó": e["diff"], "Còn lại": fmt(e["left"])}
            for i, e in enumerate(scores)
        ]
    )


def screen_menu():
    st.markdown("<p class='title'>⏳ Escape Time</p><p class='sub'>Puzzle Games · Bất ngờ mới mỗi lần chơi</p>", unsafe_allow_html=True)
    st.write(
        "Bạn bị nhốt trong một dinh thự cổ có **ba căn phòng**. Giải mọi câu đố, "
        "gom vật phẩm và tìm đường thoát ra trước khi hết giờ!"
    )
    name = st.text_input("Tên người chơi", value="Người bí ẩn", max_chars=16)
    diff = st.radio(
        "Độ khó",
        list(DIFFICULTY),
        index=1,
        format_func=lambda d: f"{d} — {DIFFICULTY[d][3]}",
    )
    if st.button("▶️ Bắt đầu thoát hiểm", type="primary", use_container_width=True):
        start_game(diff, name)
        st.rerun()
    with st.expander("📖 Cách chơi"):
        st.markdown(
            "- Chọn một **vật thể** trong phòng để quan sát, nhập mã hoặc dùng vật phẩm.\n"
            "- Vật phẩm tìm được nằm trong **🎒 Túi đồ**.\n"
            f"- Bí quá? Dùng **💡 Gợi ý**, mỗi lần bị trừ {HINT_PENALTY} giây.\n"
            "- Mã két, mật thư, câu đố và dãy số **khác nhau ở mỗi lượt chơi**.\n"
            "- Điểm = thời gian còn lại + thưởng không dùng gợi ý, nhân hệ số độ khó."
        )
    show_leaderboard()


@st.fragment(run_every=1)
def timer_box():
    g = st.session_state.g
    left = time_left(g)
    if g["phase"] == "play" and left <= 0:
        g["phase"] = "lose"
        g["end"] = time.time()
        st.rerun()
    left = max(0, left)
    cls = "danger" if left < 60 else "warn" if left < 180 else "ok"
    st.markdown(f"<div class='timer {cls}'>⏳ {fmt(left)}</div>", unsafe_allow_html=True)
    st.progress(max(0.0, min(1.0, left / g["duration"])))


def show_inventory(g, P):
    if not g["inv"]:
        st.caption("🎒 Túi đồ: trống")
        return
    with st.expander(f"🎒 Túi đồ ({len(g['inv'])})", expanded=True):
        for name in g["inv"]:
            emo, desc = ITEMS[name]
            if name == "Mật thư":
                desc = f"Tờ giấy ghi: **{P['cipher']}**"
            st.markdown(f"{emo} **{name}** — {desc}")


def screen_play(g):
    P = g["P"]
    room = ROOMS[g["room"]]
    st.markdown("<p class='title' style='font-size:1.5rem'>⏳ Escape Time</p>", unsafe_allow_html=True)
    timer_box()
    st.info(g["log"][-1])
    st.markdown(f"### {room['name']} · Phòng {g['room'] + 1}/3")
    st.write(room["intro"])

    labels = [label for _, label in room["objs"]]
    pick = st.radio(
        "Bạn muốn xem gì?",
        labels,
        index=None,
        horizontal=True,
        key=f"focus_{g['gid']}_{g['room']}",
    )
    if pick:
        oid = next(i for i, label in room["objs"] if label == pick)
        with st.container(border=True):
            st.markdown(f"#### {pick}")
            HANDLERS[oid](g, P)

    show_inventory(g, P)

    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            f"💡 Gợi ý ({g['hints']}) · −{HINT_PENALTY}s",
            disabled=g["hints"] <= 0,
            use_container_width=True,
        ):
            g["hints"] -= 1
            g["used_hints"] += 1
            g["penalty"] += HINT_PENALTY
            say(g, "💡 **Gợi ý:** " + current_hint(g, P))
            st.rerun()
    with c2:
        if st.button("🏳️ Bỏ cuộc", use_container_width=True):
            g["phase"] = "menu"
            st.rerun()

    if len(g["log"]) > 1:
        with st.expander("📜 Nhật ký"):
            for m in reversed(g["log"]):
                st.markdown(f"- {m}")


def screen_win(g):
    if not g.get("ballooned"):
        g["ballooned"] = True
        st.balloons()
    st.markdown("<p class='title'>🎉 BẠN ĐÃ THOÁT!</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='stars'>{'⭐' * g['stars']}{'☆' * (3 - g['stars'])}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Điểm", g["score"])
    c2.metric("Còn lại", fmt(max(0, time_left(g))))
    c3.metric("Gợi ý đã dùng", g["used_hints"])
    st.success(f"**{g['name']}** xếp hạng **#{g['rank']}** trên bảng vàng (độ khó {g['diff']}).")
    play_again(g)
    show_leaderboard()


def screen_lose(g):
    P = g["P"]
    st.markdown("<p class='title'>⌛ HẾT GIỜ!</p>", unsafe_allow_html=True)
    st.error("Cánh cửa sau lưng khóa lại mãi mãi… Nhưng bạn có thể thử lại với một căn phòng hoàn toàn mới.")
    with st.expander("🔍 Xem đáp án của lượt này"):
        st.markdown(
            f"- Két sắt: **{P['safe']}**\n"
            f"- Mật khẩu cửa gỗ: **{P['word']}** (mật thư: {P['cipher']}, lùi {P['shift']})\n"
            "- Thứ tự đổ lọ: " + " → ".join(POTION_SOLUTION) + "\n"
            f"- Tủ khóa số: **{P['keypad']}**\n"
            f"- Mã thoát hiểm: **{P['final']}** (dãy 1: {P['seq1'][2]}; dãy 2: {P['seq2'][2]})"
        )
    play_again(g)
    show_leaderboard()


def play_again(g):
    if st.button("🔄 Chơi lại (câu đố mới)", type="primary", use_container_width=True):
        start_game(g["diff"], g["name"])
        st.rerun()
    if st.button("🏠 Về màn hình chính", use_container_width=True):
        g["phase"] = "menu"
        st.rerun()


# ----------------------------------------------------------------------------
# CHẠY GAME
# ----------------------------------------------------------------------------
st.markdown(CSS, unsafe_allow_html=True)

if "g" not in st.session_state:
    st.session_state.g = {"phase": "menu"}
game = st.session_state.g

if game["phase"] == "play" and time_left(game) <= 0:
    game["phase"] = "lose"
    game["end"] = time.time()

if game["phase"] == "menu":
    screen_menu()
elif game["phase"] == "play":
    screen_play(game)
elif game["phase"] == "win":
    screen_win(game)
else:
    screen_lose(game)
