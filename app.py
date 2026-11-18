import json
import os
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(
    page_title="재활·운동 일지",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 무채색(Slate & Gray) 미니멀 스타일 적용 및 불필요한 여백 제거
st.markdown(
    """
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        color: #1e293b;
    }
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 740px !important;
    }
    .w-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .w-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
    }
    .w-title {
        font-size: 14px;
        font-weight: 700;
        color: #0f172a;
    }
    .w-meta {
        font-size: 12px;
        font-weight: 600;
        color: #475569;
        background: #f1f5f9;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .w-feel {
        margin-top: 6px;
        padding: 6px 10px;
        background: #f8fafc;
        border-left: 2px solid #64748b;
        font-size: 12.5px;
        color: #334155;
        line-height: 1.45;
    }
    .vas-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
        margin-top: 6px;
    }
    .vas-table th, .vas-table td {
        border: 1px solid #e2e8f0;
        padding: 6px 8px;
        text-align: center;
        color: #334155;
    }
    .vas-table th {
        background: #f8fafc;
        font-weight: 700;
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "rehab_shared_data.json"
SCHEMA_VERSION = "2026-11-18-v9-minimal"

PART_META = [
    {"key": "lumbar", "name": "1. 허리(요추)", "short": "허리"},
    {"key": "leftHip", "name": "2. 왼쪽 고관절", "short": "좌고관절"},
    {"key": "leftAnteriorShoulder", "name": "3. 왼쪽 전면 어깨", "short": "좌어깨"},
    {"key": "rightWrist", "name": "4. 오른쪽 손목", "short": "우손목"},
    {"key": "rightKnee", "name": "5. 오른쪽 무릎", "short": "우무릎"},
    {"key": "cervical", "name": "6. 목(일자목)", "short": "목"},
]

WORKOUTS_1113 = [
    {"id": "w-301", "text": "무릎꿇고 골반 하늘로 올리기", "duration": "12초 × 3세트", "rpe": 6, "feeling": "1세트엔 왼쪽 고관절 앞쪽이 팽팽했으나 3세트째 둔근 수축감 잘 들어옴", "done": True},
    {"id": "w-302", "text": "플랭크 (다리 하나씩 들기)", "duration": "1분(한발 10초) × 2세트", "rpe": 8, "feeling": "왼다리 들 때 골반이 살짝 흔들리고 40초 이후 복부 떨림 강함", "done": True},
    {"id": "w-303", "text": "사이드로 누워 의자에 다리 올려 버티기", "duration": "30초 × 2세트", "rpe": 8, "feeling": "버티는 후반부에 지지하는 왼쪽 전면 어깨로 체중이 실리며 뻐근함", "done": True},
    {"id": "w-304", "text": "어깨 슈러그 (16kg)", "duration": "30회 × 3세트", "rpe": 7, "feeling": "상부 승모근 펌핑감 양호, 마지막 5회에서 목 앞쪽이 살짝 긴장됨", "done": True},
    {"id": "w-305", "text": "다리 한쪽 올려 옆으로 돌리기", "duration": "10회 × 3세트", "rpe": 6, "feeling": "크게 외회전할 때 왼쪽 고관절 깊은 곳에서 걸리는 느낌 약간 있음", "done": True},
]

WORKOUTS_1114 = [
    {"id": "w-401", "text": "무릎꿇고 골반 하늘로 올리기", "duration": "12초 × 3세트", "rpe": 6, "feeling": "어제보다 골반 앞쪽 당김이 줄고 엉덩이 힘으로 12초 버티기 수월해짐", "done": True},
    {"id": "w-402", "text": "플랭크 (다리 하나씩 들기)", "duration": "1분(한발 10초) × 2세트", "rpe": 7, "feeling": "배꼽을 등 쪽으로 당기며 버티니 요추 부담 없이 1분 유지 안정적임", "done": True},
    {"id": "w-403", "text": "사이드로 누워 의자에 다리 올려 버티기", "duration": "30초 × 2세트", "rpe": 8, "feeling": "팔꿈치로 바닥을 밀어내며 버티니 왼쪽 앞어깨 불편감이 어제보다 줄어듦", "done": True},
    {"id": "w-404", "text": "어깨 슈러그 (16kg)", "duration": "30회 × 3세트", "rpe": 7, "feeling": "오른쪽 손목 불편감 전혀 없이 덤벨 파지 안정적, 3세트 무난히 완료", "done": True},
    {"id": "w-405", "text": "다리 한쪽 올려 옆으로 돌리기", "duration": "10회 × 3세트", "rpe": 5, "feeling": "회전 반경을 조금 줄여서 돌리니 고관절 걸림 없이 부드럽게 수행됨", "done": True},
]

WORKOUTS_1115 = [
    {"id": "w-501", "text": "무릎꿇고 골반 하늘로 올리기", "duration": "12초 × 3세트", "rpe": 6, "feeling": "아침 7시 반 조기 기상으로 첫 세트엔 허리가 약간 뻣뻣했으나 2세트부터 풀림", "done": True},
    {"id": "w-502", "text": "플랭크 (다리 하나씩 들기)", "duration": "1분(한발 10초) × 2세트", "rpe": 8, "feeling": "수면이 조금 부족해 2세트 마지막 다리 들기 10초 구간에서 코어 피로도 높았음", "done": True},
    {"id": "w-503", "text": "사이드로 누워 의자에 다리 올려 버티기", "duration": "30초 × 2세트", "rpe": 8, "feeling": "내전근과 옆구리 자극 강하게 들어옴, 왼쪽 어깨 겨드랑이 지지 집중", "done": True},
    {"id": "w-504", "text": "어깨 슈러그 (16kg)", "duration": "30회 × 3세트", "rpe": 7, "feeling": "턱 당김 유지하며 30회씩 수행, 상부 승모근 자극 일정함", "done": True},
    {"id": "w-505", "text": "다리 한쪽 올려 옆으로 돌리기", "duration": "10회 × 3세트", "rpe": 6, "feeling": "고관절을 너무 크게 돌릴 때만 약간의 뻐근함이 있어 적정 각도로 조절함", "done": True},
]

DEFAULT_DATA = {
    "schemaVersion": SCHEMA_VERSION,
    "ownerPin": "0208",
    "selectedDate": "2026-11-15",
    "logs": [
        {
            "date": "2026-11-11",
            "sleep": {"score": 2, "posture": "똑바로 누울 때 찌릿함", "sittingHours": 10},
            "parts": {
                "lumbar": {"score": 7, "note": "새벽에 허리가 뻐근해 2번 깸"},
                "leftHip": {"score": 6, "note": "일어날 때 왼쪽 사타구니 앞쪽 당김"},
                "leftAnteriorShoulder": {"score": 5, "note": "타이핑 시 왼쪽 앞어깨 걸림"},
                "rightWrist": {"score": 4, "note": "마우스 클릭 시 시큰거림"},
                "rightKnee": {"score": 5, "note": "계단 내려갈 때 오른쪽 무릎 부담"},
                "cervical": {"score": 6, "note": "퇴근 무렵 뒷목과 승모근 굳음"},
            },
            "workoutList": [
                {"id": "w-101", "text": "폼롤러 흉추(등뼈) 마사지", "duration": "10분", "rpe": 4, "feeling": "등 중앙이 굳어 있어 처음엔 아팠으나 롤링 후 호흡이 편해짐", "done": True},
                {"id": "w-102", "text": "런지 자세 좌측 장요근 스트레칭", "duration": "30초 × 3세트", "rpe": 6, "feeling": "왼쪽 사타구니 앞쪽이 강하게 당김, 30초 버틴 후 허리 가벼움", "done": True},
            ],
            "patientWorkoutNote": "무릎 아래 베개 받치고 취침 시도, 등 마사지 후 호흡이 편해짐",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "assessment": "VAS는 외부 요인 영향을 많이 받으므로 보조지표로 두고, 각 운동별 RPE와 유지시간에 따른 주관적 느낌을 최우선으로 확인하겠습니다.",
                "prescription": "무릎 꿇고 골반 올리기와 플랭크·사이드 버티기 수행 시 목표 유지시간을 채울 때의 느낌을 기록해 주세요.",
            },
        },
        {
            "date": "2026-11-12",
            "sleep": {"score": 3, "posture": "뒤척일 때 뻐근함", "sittingHours": 9},
            "parts": {
                "lumbar": {"score": 5, "note": "베개 받치고 자니 통증 줄어듦"},
                "leftHip": {"score": 5, "note": "장요근 스트레칭 후 찝히는 느낌 완화"},
                "leftAnteriorShoulder": {"score": 4, "note": "가슴 스트레칭 병행 중"},
                "rightWrist": {"score": 4, "note": "버티컬 마우스 사용 시작"},
                "rightKnee": {"score": 4, "note": "테이핑 후 보행 시 편안함"},
                "cervical": {"score": 5, "note": "모니터 받침대 10cm 높임"},
            },
            "workoutList": [
                {"id": "w-201", "text": "런지 장요근 스트레칭", "duration": "30초 × 4세트", "rpe": 5, "feeling": "어제보다 30초 유지할 때 사타구니 당김 강도가 부드러워짐", "done": True},
                {"id": "w-202", "text": "흉추 가동성 오픈북", "duration": "좌우 15회 × 3세트", "rpe": 5, "feeling": "왼쪽 가슴 앞쪽이 열리면서 어깨 회전이 시원하게 됨", "done": True},
            ],
            "patientWorkoutNote": "장요근과 오픈북 완료, 모니터 높인 뒤 목 피로도 감소",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "assessment": "장요근 이완과 흉추 가동성이 확보되면서 버티기 훈련으로 넘어가기 좋은 상태입니다.",
                "prescription": "다음 루틴부터는 플랭크(다리 들기)와 사이드 의자 다리 올려 버티기를 추가해 유지시간과 RPE를 체크해 주세요.",
            },
        },
        {
            "date": "2026-11-13",
            "sleep": {"score": 4, "posture": "뒤척일 때 뻐근함", "sittingHours": 8},
            "parts": {
                "lumbar": {"score": 3, "note": "중간에 깨지 않고 숙면함, 아침 강직만 약간 있음"},
                "leftHip": {"score": 3, "note": "고관절이 심하게 회전될때"},
                "leftAnteriorShoulder": {"score": 3, "note": "왼쪽으로 몸이 기울때, 아픔"},
                "rightWrist": {"score": 2, "note": "체중 싣고 땅짚을때"},
                "rightKnee": {"score": 1, "note": "스쿼트 할때"},
                "cervical": {"score": 2, "note": "가끔 컴퓨터할때 뻐근함"},
            },
            "workoutList": json.loads(json.dumps(WORKOUTS_1113)),
            "patientWorkoutNote": "낮 동안 50:3 루틴과 장요근·소흉근 이완 완료, 저녁에 브릿지 추가 예정",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "assessment": "5대 개인 운동 루틴 수행이 안정적입니다. 보조지표인 VAS도 1~3점대로 낮아졌습니다.",
                "prescription": "골반 올리기 12초, 플랭크 1분, 사이드 버티기의 유지시간과 주관적 느낌을 계속 기록해 주세요.",
            },
        },
        {
            "date": "2026-11-14",
            "sleep": {"score": 4, "posture": "뒤척일 때 뻐근함", "sittingHours": 8},
            "parts": {
                "lumbar": {"score": 2, "note": "중간에 깨지 않고 숙면함, 아침 강직만 약간 있음"},
                "leftHip": {"score": 2, "note": "고관절이 심하게 회전될때"},
                "leftAnteriorShoulder": {"score": 1, "note": "왼쪽으로 몸이 기울때, 아픔"},
                "rightWrist": {"score": 0, "note": "체중 싣고 땅짚을때"},
                "rightKnee": {"score": 1, "note": "스쿼트 할때"},
                "cervical": {"score": 2, "note": "가끔 컴퓨터할때 뻐근함"},
            },
            "workoutList": json.loads(json.dumps(WORKOUTS_1114)),
            "patientWorkoutNote": "5대 개인 재활 운동 루틴 전체 완료! 오른쪽 손목 통증은 0점으로 소실됨",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "assessment": "동일한 유지시간 대비 RPE(체감 난이도)가 안정화되면서 근육 동원 효율이 좋아지고 있습니다.",
                "prescription": "다리 옆으로 돌리기 운동은 걸리는 느낌이 없는 각도 내에서만 컨트롤하며 10회 3세트를 유지합니다.",
            },
        },
        {
            "date": "2026-11-15",
            "sleep": {"score": 3, "posture": "뒤척일 때 뻐근함", "sittingHours": 0},
            "parts": {
                "lumbar": {"score": 3, "note": "중간에 깨지 않고 숙면함, 아침 강직만 약간 있음"},
                "leftHip": {"score": 3, "note": "고관절이 심하게 회전될때"},
                "leftAnteriorShoulder": {"score": 1, "note": "왼쪽으로 몸이 기울때, 아픔"},
                "rightWrist": {"score": 0, "note": "체중 싣고 땅짚을때"},
                "rightKnee": {"score": 1, "note": "스쿼트 할때"},
                "cervical": {"score": 2, "note": "가끔 컴퓨터할때 뻐근함"},
            },
            "workoutList": json.loads(json.dumps(WORKOUTS_1115)),
            "patientWorkoutNote": "일요일이여서 오래자고 싶었는데 7시반에 깨서 잠 만족도가 별로임.",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "assessment": "일요일 조기 기상으로 컨디션이 아쉬웠음에도 5가지 운동의 목표 유지시간과 세트를 모두 완수하셨습니다.",
                "prescription": "방문 수업 시 사이드 버티기 어깨 지지 자세와 고관절 회전 각도를 함께 잡아보겠습니다.",
            },
        },
    ],
}


def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if saved.get("schemaVersion") == SCHEMA_VERSION:
                return saved
        except Exception:
            pass
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=2)
    return json.loads(json.dumps(DEFAULT_DATA))


def save_db(data):
    data["schemaVersion"] = SCHEMA_VERSION
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


db = load_db()

if "is_owner" not in st.session_state:
    st.session_state.is_owner = False
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# --- 상단 헤더 및 날짜/잠금 컨트롤 ---
col_title, col_date, col_add, col_auth = st.columns([3.2, 2.2, 1.3, 1.8])
with col_title:
    st.markdown("#### 재활·운동 일지")
with col_date:
    dates = [l["date"] for l in db["logs"]]
    sel_idx = dates.index(db["selectedDate"]) if db["selectedDate"] in dates else len(dates) - 1
    chosen_date = st.selectbox("날짜", dates, index=sel_idx, label_visibility="collapsed")
    if chosen_date != db["selectedDate"]:
        db["selectedDate"] = chosen_date
        save_db(db)
        st.rerun()
with col_add:
    if st.button("+ 새 일지", disabled=not st.session_state.is_owner, use_container_width=True):
        last_log = db["logs"][-1]
        next_dt = (datetime.strptime(last_log["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        if next_dt not in dates:
            new_log = json.loads(json.dumps(last_log))
            new_log["date"] = next_dt
            for i, w in enumerate(new_log.get("workoutList", [])):
                w["id"] = f"w-{int(datetime.now().timestamp())}-{i}"
                w["feeling"] = ""
                w["done"] = False
            new_log["patientWorkoutNote"] = ""
            new_log["directorOpinion"]["assessment"] = ""
            new_log["directorOpinion"]["prescription"] = ""
            db["logs"].append(new_log)
            db["selectedDate"] = next_dt
            save_db(db)
            st.rerun()
with col_auth:
    if st.session_state.is_owner:
        if st.button("본인 모드 (잠금)", use_container_width=True):
            st.session_state.is_owner = False
            st.rerun()
    else:
        with st.popover("잠금 해제", use_container_width=True):
            pin_in = st.text_input("PIN 입력", type="password", key="pin_in")
            if st.button("확인", use_container_width=True):
                if pin_in == db.get("ownerPin", "0208"):
                    st.session_state.is_owner = True
                    st.rerun()
                else:
                    st.error("PIN 불일치")

current_log = next((l for l in db["logs"] if l["date"] == db["selectedDate"]), db["logs"][-1])
is_owner = st.session_state.is_owner

tab1, tab2, tab3 = st.tabs([
    "운동 요약 (첫 화면)",
    f"기록·수정 {'(열림)' if is_owner else '(잠김)'}",
    "원장님 소견",
])

# --- TAB 1: 운동 요약 최우선 배치 + 방문일 근황 + 보조지표(VAS) ---
with tab1:
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    avg_rpe = round(sum(int(w.get("rpe", 7)) for w in workouts) / len(workouts), 1) if workouts else 0.0

    st.markdown(f"**오늘 수행한 개인 운동 요약 ({current_log['date']})** — 완료 {done_cnt}/{len(workouts)} · 평균 RPE {avg_rpe}")

    if not workouts:
        st.caption("등록된 운동이 없습니다.")
    else:
        cards_html = ""
        for idx, w in enumerate(workouts):
            mark = "✓" if w.get("done") else "-"
            feel = w.get("feeling") or "기록된 주관적 느낌 없음"
            cards_html += (
                f"<div class='w-card'>"
                f"<div class='w-header'>"
                f"<span class='w-title'>[{mark}] {idx + 1}. {w['text']}</span>"
                f"<span class='w-meta'>유지/수행: {w.get('duration', '-')} | RPE {w.get('rpe', 7)}/10</span>"
                f"</div>"
                f"<div class='w-feel'>느낌: {feel}</div>"
                f"</div>"
            )
        st.markdown(cards_html, unsafe_allow_html=True)

    if current_log.get("patientWorkoutNote"):
        st.caption(f"컨디션 메모: {current_log['patientWorkoutNote']}")

    d_op = current_log.get("directorOpinion", {})
    if d_op.get("assessment") or d_op.get("prescription"):
        with st.container(border=True):
            st.markdown(f"**{d_op.get('directorName', '담당 원장님')} 코멘트**")
            if d_op.get("assessment"):
                st.write(f"- 평가: {d_op['assessment']}")
            if d_op.get("prescription"):
                st.write(f"- 가이드: {d_op['prescription']}")

    st.markdown("---")
    st.markdown("**일자별 운동 근황 모아보기 (방문일 확인용)**")
    for l in reversed(db["logs"]):
        lw = l.get("workoutList", [])
        ldone = sum(1 for w in lw if w.get("done"))
        lrpe = round(sum(int(w.get("rpe", 7)) for w in lw) / len(lw), 1) if lw else 0.0
        with st.expander(f"{l['date']}  |  운동 {ldone}/{len(lw)} 완료 · 평균 RPE {lrpe} · 수면 {l['sleep']['score']}점", expanded=(l["date"] == current_log["date"])):
            if l.get("patientWorkoutNote"):
                st.caption(f"메모: {l['patientWorkoutNote']}")
            for w in lw:
                st.markdown(f"- **{w['text']}** (`{w.get('duration', '-')}` | RPE {w.get('rpe', 7)})  \n  ↳ 느낌: {w.get('feeling') or '-'}")

    with st.expander("보조지표: 날짜별 6대 부위 통증(VAS) 추이 표 보기", expanded=False):
        th = "<tr><th>부위</th>" + "".join([f"<th>{l['date'][5:]}</th>" for l in db["logs"]]) + "<th>선택일 메모</th></tr>"
        trs = ""
        for m in PART_META:
            k = m["key"]
            tds = "".join([f"<td>{l['parts'][k]['score']}</td>" for l in db["logs"]])
            note = current_log["parts"][k].get("note") or "-"
            trs += f"<tr><td style='font-weight:600;'>{m['short']}</td>{tds}<td style='text-align:left;'>{note}</td></tr>"
        st.markdown(f"<table class='vas-table'>{th}{trs}</table>", unsafe_allow_html=True)

# --- TAB 2: 운동 및 보조지표 기록·수정 ---
with tab2:
    if not is_owner:
        st.caption("우측 상단 [잠금 해제] 후 수정할 수 있습니다.")

    st.markdown("**1. 개인 운동 추가 및 수정**")
    with st.expander("+ 새 운동 추가", expanded=is_owner):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            nw_title = st.text_input("운동명", disabled=not is_owner, key=f"nt_{db['selectedDate']}")
        with c2:
            nw_dur = st.text_input("유지시간/세트", placeholder="예: 12초 × 3세트", disabled=not is_owner, key=f"nd_{db['selectedDate']}")
        with c3:
            nw_rpe = st.number_input("RPE", 1, 10, 7, disabled=not is_owner, key=f"nr_{db['selectedDate']}")
        nw_feel = st.text_input("유지시간에 따른 주관적 느낌", disabled=not is_owner, key=f"nf_{db['selectedDate']}")
        if st.button("추가", disabled=not is_owner, use_container_width=True):
            if nw_title.strip():
                current_log.setdefault("workoutList", []).append({
                    "id": f"w-{int(datetime.now().timestamp()*1000)}",
                    "text": nw_title.strip(),
                    "duration": nw_dur.strip() or "-",
                    "rpe": int(nw_rpe),
                    "feeling": nw_feel.strip(),
                    "done": True,
                })
                save_db(db)
                st.rerun()

    for w in list(current_log.get("workoutList", [])):
        wid = w["id"]
        with st.container(border=True):
            if st.session_state.edit_id == wid and is_owner:
                ec1, ec2, ec3 = st.columns([3, 2, 1])
                with ec1:
                    et = st.text_input("운동명", value=w["text"], key=f"et_{wid}")
                with ec2:
                    ed = st.text_input("유지시간/세트", value=w.get("duration", ""), key=f"ed_{wid}")
                with ec3:
                    er = st.number_input("RPE", 1, 10, int(w.get("rpe", 7)), key=f"er_{wid}")
                ef = st.text_input("주관적 느낌", value=w.get("feeling", ""), key=f"ef_{wid}")
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("저장", key=f"sv_{wid}", use_container_width=True):
                        w["text"], w["duration"], w["rpe"], w["feeling"] = et.strip(), ed.strip(), int(er), ef.strip()
                        st.session_state.edit_id = None
                        save_db(db)
                        st.rerun()
                with b2:
                    if st.button("취소", key=f"cn_{wid}", use_container_width=True):
                        st.session_state.edit_id = None
                        st.rerun()
            else:
                wc1, wc2, wc3 = st.columns([6, 1, 1])
                with wc1:
                    chk = st.checkbox(
                        f"{w['text']} ({w.get('duration', '-')} | RPE {w.get('rpe', 7)})",
                        value=bool(w.get("done")),
                        disabled=not is_owner,
                        key=f"ck_{wid}_{db['selectedDate']}",
                    )
                    if chk != bool(w.get("done")) and is_owner:
                        w["done"] = chk
                        save_db(db)
                        st.rerun()
                with wc2:
                    if st.button("수정", key=f"eb_{wid}", disabled=not is_owner, use_container_width=True):
                        st.session_state.edit_id = wid
                        st.rerun()
                with wc3:
                    if st.button("삭제", key=f"db_{wid}", disabled=not is_owner, use_container_width=True):
                        current_log["workoutList"] = [i for i in current_log["workoutList"] if i["id"] != wid]
                        save_db(db)
                        st.rerun()
                st.caption(f"느낌: {w.get('feeling') or '-'}")

    cond_in = st.text_input("오늘의 컨디션 한줄 메모", value=current_log.get("patientWorkoutNote", ""), disabled=not is_owner)
    if is_owner and st.button("컨디션 메모 저장", use_container_width=True):
        current_log["patientWorkoutNote"] = cond_in
        save_db(db)
        st.rerun()

    with st.expander("2. 보조지표 (수면 만족도 및 6대 부위 VAS) 수정", expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            sl_sc = st.selectbox("수면 만족도(1~5)", [1, 2, 3, 4, 5], index=current_log["sleep"]["score"] - 1, disabled=not is_owner)
        with sc2:
            p_opts = ["뒤척일 때 뻐근함", "똑바로 누울 때 찌릿함", "새벽·기상 직후 강직", "수면 중 불편감 없음"]
            cp = current_log["sleep"].get("posture", p_opts[0])
            sl_po = st.selectbox("수면 중 요추 상태", p_opts, index=p_opts.index(cp) if cp in p_opts else 0, disabled=not is_owner)
        with sc3:
            sl_st = st.number_input("좌식 시간", 0, 24, int(current_log["sleep"].get("sittingHours", 8)), disabled=not is_owner)

        up_parts = {}
        for m in PART_META:
            k = m["key"]
            it = current_log["parts"][k]
            pc1, pc2 = st.columns([1, 1])
            with pc1:
                v_sc = st.slider(f"{m['name']} (VAS)", 0, 10, int(it["score"]), disabled=not is_owner, key=f"v_{k}_{db['selectedDate']}")
            with pc2:
                v_nt = st.text_input(f"{m['short']} 메모", value=it["note"], disabled=not is_owner, key=f"n_{k}_{db['selectedDate']}")
            up_parts[k] = {"score": v_sc, "note": v_nt}

        if is_owner and st.button("보조지표 저장", use_container_width=True):
            current_log["sleep"] = {"score": sl_sc, "posture": sl_po, "sittingHours": sl_st}
            current_log["parts"] = up_parts
            save_db(db)
            st.rerun()

# --- TAB 3: 원장님 소견 (전체 개방) ---
with tab3:
    d_op = current_log.get("directorOpinion", {})
    d_name = st.text_input("담당 전문가", value=d_op.get("directorName", "황인준 대표 (피지컬그라운드)"))
    d_ass = st.text_area("운동 수행(RPE·유지시간·느낌) 평가 소견", value=d_op.get("assessment", ""), height=80)
    d_pre = st.text_area("다음 루틴 및 가이드", value=d_op.get("prescription", ""), height=80)

    if st.button("소견 저장", use_container_width=True):
        current_log["directorOpinion"] = {"directorName": d_name, "assessment": d_ass, "prescription": d_pre}
        save_db(db)
        st.toast("저장되었습니다.")
        st.rerun()
