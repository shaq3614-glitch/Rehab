import json
import os
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="매일 튼튼 재활·운동 일지",
    page_icon="🏋️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_FILE = "rehab_shared_data.json"
SCHEMA_VERSION = "2026-11-17-v8-clean"

PART_META = [
    {"key": "lumbar", "name": "1. 허리 (요추)", "short": "허리", "side": "중앙 코어", "color": "#ef4444", "desc": "수면 시 불편감 및 좌식 하중"},
    {"key": "leftHip", "name": "2. 왼쪽 고관절", "short": "좌고관절", "side": "좌측 하체", "color": "#f97316", "desc": "장요근 단축 및 회전 시 집임"},
    {"key": "leftAnteriorShoulder", "name": "3. 왼쪽 전면 어깨", "short": "좌어깨", "side": "좌측 상체", "color": "#eab308", "desc": "측면 지지 및 기울 때 불편"},
    {"key": "rightWrist", "name": "4. 오른쪽 손목", "short": "우손목", "side": "우측 상체", "color": "#10b981", "desc": "마우스 사용 및 땅 짚을 때"},
    {"key": "rightKnee", "name": "5. 오른쪽 무릎", "short": "우무릎", "side": "우측 하체", "color": "#06b6d4", "desc": "스쿼트 시 대각선 보상 하중"},
    {"key": "cervical", "name": "6. 목 (일자목)", "short": "목", "side": "상부 코어", "color": "#6366f1", "desc": "컴퓨터 작업 시 경추 피로"},
]

WORKOUTS_1113 = [
    {
        "id": "w-301",
        "text": "무릎꿇고 골반 하늘로 올리기",
        "duration": "12초 × 3세트",
        "rpe": 6,
        "feeling": "1세트엔 왼쪽 고관절 앞쪽이 팽팽했으나 3세트째 둔근 수축감 잘 들어옴",
        "done": True,
    },
    {
        "id": "w-302",
        "text": "플랭크 (다리 하나씩 들기)",
        "duration": "1분(한발 10초) × 2세트",
        "rpe": 8,
        "feeling": "왼다리 들 때 골반이 살짝 흔들리고 40초 이후 복부 떨림 강함",
        "done": True,
    },
    {
        "id": "w-303",
        "text": "사이드로 누워 의자에 다리 올려 버티기",
        "duration": "30초 × 2세트",
        "rpe": 8,
        "feeling": "버티는 후반부에 지지하는 왼쪽 전면 어깨로 체중이 실리며 뻐근함",
        "done": True,
    },
    {
        "id": "w-304",
        "text": "어깨 슈러그 (16kg)",
        "duration": "30회 × 3세트",
        "rpe": 7,
        "feeling": "상부 승모근 펌핑감 양호, 마지막 5회에서 목 앞쪽이 살짝 긴장됨",
        "done": True,
    },
    {
        "id": "w-305",
        "text": "다리 한쪽 올려 옆으로 돌리기",
        "duration": "10회 × 3세트",
        "rpe": 6,
        "feeling": "크게 외회전할 때 왼쪽 고관절 깊은 곳에서 걸리는 느낌 약간 있음",
        "done": True,
    },
]

WORKOUTS_1114 = [
    {
        "id": "w-401",
        "text": "무릎꿇고 골반 하늘로 올리기",
        "duration": "12초 × 3세트",
        "rpe": 6,
        "feeling": "어제보다 골반 앞쪽 당김이 줄고 엉덩이 힘으로 12초 버티기 수월해짐",
        "done": True,
    },
    {
        "id": "w-402",
        "text": "플랭크 (다리 하나씩 들기)",
        "duration": "1분(한발 10초) × 2세트",
        "rpe": 7,
        "feeling": "배꼽을 등 쪽으로 당기며 버티니 요추 부담 없이 1분 유지 안정적임",
        "done": True,
    },
    {
        "id": "w-403",
        "text": "사이드로 누워 의자에 다리 올려 버티기",
        "duration": "30초 × 2세트",
        "rpe": 8,
        "feeling": "팔꿈치로 바닥을 밀어내며 버티니 왼쪽 앞어깨 불편감이 어제보다 줄어듦",
        "done": True,
    },
    {
        "id": "w-404",
        "text": "어깨 슈러그 (16kg)",
        "duration": "30회 × 3세트",
        "rpe": 7,
        "feeling": "오른쪽 손목 불편감 전혀 없이 덤벨 파지 안정적, 3세트 무난히 완료",
        "done": True,
    },
    {
        "id": "w-405",
        "text": "다리 한쪽 올려 옆으로 돌리기",
        "duration": "10회 × 3세트",
        "rpe": 5,
        "feeling": "회전 반경을 조금 줄여서 돌리니 고관절 걸림 없이 부드럽게 수행됨",
        "done": True,
    },
]

WORKOUTS_1115 = [
    {
        "id": "w-501",
        "text": "무릎꿇고 골반 하늘로 올리기",
        "duration": "12초 × 3세트",
        "rpe": 6,
        "feeling": "아침 7시 반 조기 기상으로 첫 세트엔 허리가 약간 뻣뻣했으나 2세트부터 풀림",
        "done": True,
    },
    {
        "id": "w-502",
        "text": "플랭크 (다리 하나씩 들기)",
        "duration": "1분(한발 10초) × 2세트",
        "rpe": 8,
        "feeling": "수면이 조금 부족해 2세트 마지막 다리 들기 10초 구간에서 코어 피로도 높았음",
        "done": True,
    },
    {
        "id": "w-503",
        "text": "사이드로 누워 의자에 다리 올려 버티기",
        "duration": "30초 × 2세트",
        "rpe": 8,
        "feeling": "내전근과 옆구리 자극 강하게 들어옴, 왼쪽 어깨 겨드랑이 지지 집중",
        "done": True,
    },
    {
        "id": "w-504",
        "text": "어깨 슈러그 (16kg)",
        "duration": "30회 × 3세트",
        "rpe": 7,
        "feeling": "턱 당김 유지하며 30회씩 수행, 상부 승모근 자극 일정함",
        "done": True,
    },
    {
        "id": "w-505",
        "text": "다리 한쪽 올려 옆으로 돌리기",
        "duration": "10회 × 3세트",
        "rpe": 6,
        "feeling": "고관절을 너무 크게 돌릴 때만 약간의 뻐근함이 있어 적정 각도로 조절함",
        "done": True,
    },
]

DEFAULT_DATA = {
    "schemaVersion": SCHEMA_VERSION,
    "ownerPin": "0208",
    "selectedDate": "2026-11-15",
    "logs": [
        {
            "date": "2026-11-11",
            "sleep": {"score": 2, "posture": "똑바로 누울 때 찌릿함", "wakeUpCount": 2, "sittingHours": 10},
            "parts": {
                "lumbar": {"score": 7, "note": "새벽에 허리가 뻐근해 2번 깸"},
                "leftHip": {"score": 6, "note": "오래 앉아있다가 일어날 때 왼쪽 사타구니 앞쪽이 당김"},
                "leftAnteriorShoulder": {"score": 5, "note": "벤치프레스 및 타이핑 시 왼쪽 앞어깨 걸림"},
                "rightWrist": {"score": 4, "note": "오후 업무 중 마우스 클릭 시 시큰거림"},
                "rightKnee": {"score": 5, "note": "계단 내려갈 때 오른쪽 무릎 앞쪽 부담"},
                "cervical": {"score": 6, "note": "퇴근 무렵 뒷목과 승모근이 돌처럼 굳음"},
            },
            "workoutList": [
                {
                    "id": "w-101",
                    "text": "폼롤러 흉추(등뼈) 마사지",
                    "duration": "10분",
                    "rpe": 4,
                    "feeling": "등 중앙이 많이 굳어 있어 처음엔 아팠으나 롤링 후 호흡이 편해짐",
                    "done": True,
                },
                {
                    "id": "w-102",
                    "text": "런지 자세 좌측 장요근 스트레칭",
                    "duration": "30초 × 3세트",
                    "rpe": 6,
                    "feeling": "왼쪽 사타구니 앞쪽이 강하게 당김, 30초 버틴 후 일어설 때 허리 가벼움",
                    "done": True,
                },
            ],
            "patientWorkoutNote": "무릎 아래 베개 받치고 취침 시도, 등 마사지 후 호흡이 한결 편해짐",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "focusTarget": "버티기(등척성) 훈련 시 RPE·유지시간 및 주관적 느낌 중심 기록",
                "inquiry": "각 운동별 유지시간 동안 어느 부위에 자극이나 피로가 먼저 오는지 느낌을 적어주세요.",
                "assessment": "VAS는 외부 요인 영향을 많이 받으므로 보조지표로 두고, 각 운동별 RPE와 유지시간에 따른 주관적 느낌을 최우선 지표로 확인하겠습니다.",
                "prescription": "무릎 꿇고 골반 올리기와 플랭크·사이드 버티기 수행 시 목표 유지시간을 채울 때의 느낌을 기록해 주세요.",
            },
        },
        {
            "date": "2026-11-12",
            "sleep": {"score": 3, "posture": "뒤척일 때 뻐근함", "wakeUpCount": 1, "sittingHours": 9},
            "parts": {
                "lumbar": {"score": 5, "note": "베개 받치고 자니 똑바로 누울 때 통증은 줄어듦"},
                "leftHip": {"score": 5, "note": "장요근 스트레칭 후 찝히는 느낌 소폭 완화"},
                "leftAnteriorShoulder": {"score": 4, "note": "가슴 스트레칭 병행 중"},
                "rightWrist": {"score": 4, "note": "버티컬 마우스로 교체 사용 시작"},
                "rightKnee": {"score": 4, "note": "우측 무릎 테이핑 후 보행 시 한결 편안함"},
                "cervical": {"score": 5, "note": "모니터 받침대 10cm 높임"},
            },
            "workoutList": [
                {
                    "id": "w-201",
                    "text": "런지 장요근 스트레칭",
                    "duration": "30초 × 4세트",
                    "rpe": 5,
                    "feeling": "어제보다 30초 유지할 때 사타구니 당김 강도가 한결 부드러워짐",
                    "done": True,
                },
                {
                    "id": "w-202",
                    "text": "흉추 가동성 오픈북",
                    "duration": "좌우 15회 × 3세트",
                    "rpe": 5,
                    "feeling": "왼쪽 가슴 앞쪽이 열리면서 어깨 회전이 시원하게 됨",
                    "done": True,
                },
            ],
            "patientWorkoutNote": "장요근과 오픈북 완료! 모니터 높인 뒤 목 피로도 감소",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "focusTarget": "코어 및 고관절 등척성 버티기 유지시간 단계적 확대",
                "inquiry": "센터 오시는 날에 날짜별 운동 요약과 적어주신 주관적 느낌을 함께 체크하겠습니다.",
                "assessment": "장요근 이완과 흉추 가동성이 확보되면서 버티기 훈련으로 넘어가기 좋은 상태입니다.",
                "prescription": "다음 루틴부터는 플랭크(다리 들기)와 사이드 의자 다리 올려 버티기를 추가해 유지시간과 RPE를 체크해 주세요.",
            },
        },
        {
            "date": "2026-11-13",
            "sleep": {"score": 4, "posture": "뒤척일 때 뻐근함", "wakeUpCount": 0, "sittingHours": 8},
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
                "focusTarget": "버티기 계열 훈련 시 RPE 및 유지시간별 주관적 느낌 모니터링",
                "inquiry": "사이드 버티기 30초 유지 시 옆구리·내전근 자극과 왼쪽 어깨 부담 비율이 어떤지 적어주세요.",
                "assessment": "5대 개인 운동 루틴 수행이 매우 안정적입니다. 보조지표인 VAS도 1~3점대로 낮아졌습니다.",
                "prescription": "골반 올리기 12초, 플랭크 1분, 사이드 버티기의 유지시간과 주관적 느낌을 계속 기록해 주세요.",
            },
        },
        {
            "date": "2026-11-14",
            "sleep": {"score": 4, "posture": "뒤척일 때 뻐근함", "wakeUpCount": 0, "sittingHours": 8},
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
                "focusTarget": "등척성 유지시간 동안의 코어·둔근 동원 감각 정착",
                "inquiry": "플랭크 한 발 들기 10초 버틸 때 골반 수평이 잘 유지되는지 느낌을 남겨주세요.",
                "assessment": "동일한 유지시간 대비 RPE(체감 난이도)가 안정화되면서 근육 동원 효율이 좋아지고 있습니다.",
                "prescription": "다리 옆으로 돌리기 운동은 걸리는 느낌이 없는 각도 내에서만 컨트롤하며 10회 3세트를 유지합니다.",
            },
        },
        {
            "date": "2026-11-15",
            "sleep": {"score": 3, "posture": "뒤척일 때 뻐근함", "wakeUpCount": 0, "sittingHours": 0},
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
                "focusTarget": "센터 방문일 근황 확인 — 운동별 RPE·유지시간·주관적 느낌 종합 점검",
                "inquiry": "오시는 날에 각 운동 밑에 적어주신 주관적인 느낌과 RPE 변화를 바탕으로 다음 진도를 설정하겠습니다!",
                "assessment": "일요일 조기 기상으로 컨디션이 아쉬웠음에도 5가지 운동의 목표 유지시간과 세트를 모두 완수하셨습니다.",
                "prescription": "방문 수업 시 사이드 버티기 어깨 지지 자세와 고관절 회전 각도를 함께 디테일하게 잡아보겠습니다.",
            },
        },
    ],
}


def normalize_workout_items(db_data):
    for log in db_data.get("logs", []):
        for w in log.get("workoutList", []):
            w.setdefault("rpe", 7)
            w.setdefault("duration", "목표 세트 완수")
            w.setdefault("feeling", "")
    return db_data


def load_shared_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if saved.get("schemaVersion") == SCHEMA_VERSION:
                return normalize_workout_items(saved)
        except Exception:
            pass
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=2)
    return normalize_workout_items(json.loads(json.dumps(DEFAULT_DATA)))


def save_shared_db(data):
    data["schemaVersion"] = SCHEMA_VERSION
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_rpe_badge_style(rpe_val):
    if rpe_val <= 5:
        return "background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;"
    if rpe_val <= 7:
        return "background:#f0fdfa;color:#0f766e;border:1px solid #99f6e4;"
    return "background:#fffbeb;color:#b45309;border:1px solid #fde68a;"


def get_vas_badge_style(score):
    if score <= 3:
        return "background:#dcfce7;color:#166534;"
    if score <= 6:
        return "background:#fef3c7;color:#92400e;"
    return "background:#fee2e2;color:#991b1b;"


def render_clean_workout_summary(current_log, all_logs):
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    total_cnt = len(workouts)
    avg_rpe = round(sum(int(w.get("rpe", 7)) for w in workouts) / total_cnt, 1) if total_cnt > 0 else 0.0

    p = current_log["parts"]
    s = current_log["sleep"]
    avg_vas = round(sum(p[m["key"]]["score"] for m in PART_META) / len(PART_META), 1)

    workout_rows = ""
    if not workouts:
        workout_rows = "<div style='padding:14px;text-align:center;color:#64748b;font-size:13px;'>등록된 운동이 없습니다.</div>"
    else:
        for idx, w in enumerate(workouts):
            is_done = bool(w.get("done"))
            rpe_v = int(w.get("rpe", 7))
            dur = w.get("duration") or "-"
            feel = w.get("feeling") or "작성된 주관적 느낌이 없습니다."
            icon = "✅" if is_done else "⬜"
            row_border = "#99f6e4" if is_done else "#e2e8f0"

            workout_rows += f"""
            <div style="border:1px solid {row_border};background:#ffffff;border-radius:12px;padding:11px 14px;margin-bottom:8px;">
              <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px;">
                <div style="font-size:14px;font-weight:800;color:#0f172a;">
                  {icon} {idx + 1}. {w['text']}
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                  <span style="font-size:11.5px;font-weight:700;padding:2px 8px;border-radius:6px;background:#f1f5f9;color:#334155;">⏱️ {dur}</span>
                  <span style="font-size:11.5px;font-weight:800;padding:2px 8px;border-radius:6px;{get_rpe_badge_style(rpe_v)}">RPE {rpe_v}</span>
                </div>
              </div>
              <div style="margin-top:6px;padding:7px 10px;background:#f8fafc;border-left:3px solid #0d9488;border-radius:4px 8px 8px 4px;font-size:12.5px;color:#334155;line-height:1.45;">
                <strong style="color:#0f766e;">느낌:</strong> {feel}
              </div>
            </div>
            """

    # Accordion History for Visit Days (Compact & Easy to Scan)
    visit_accordions = ""
    for l in reversed(all_logs):
        lw = l.get("workoutList", [])
        ldone = sum(1 for w in lw if w.get("done"))
        lrpe = round(sum(int(w.get("rpe", 7)) for w in lw) / len(lw), 1) if lw else 0.0
        is_open = "open" if l["date"] == current_log["date"] else ""
        items_li = "".join([
            f"<li style='margin-bottom:5px;'><strong>{w['text']}</strong> "
            f"<span style='color:#0f766e;font-weight:700;'>({w.get('duration', '-')} · RPE {w.get('rpe', 7)})</span><br/>"
            f"<span style='color:#475569;'>↳ {w.get('feeling') or '-'}</span></li>"
            for w in lw
        ])
        visit_accordions += f"""
        <details {is_open} style="border:1px solid #e2e8f0;border-radius:10px;background:#ffffff;margin-bottom:7px;padding:8px 12px;">
          <summary style="cursor:pointer;font-size:13px;font-weight:800;color:#0f172a;display:flex;justify-content:space-between;align-items:center;">
            <span>📅 {l['date']} ({ldone}/{len(lw)} 완료 · 평균 RPE {lrpe})</span>
            <span style="font-size:11.5px;font-weight:600;color:#64748b;">수면 ★{l['sleep']['score']} · 클릭하여 펼치기</span>
          </summary>
          <div style="margin-top:8px;padding-top:8px;border-top:1px dashed #e2e8f0;font-size:12px;">
            <div style="margin-bottom:6px;color:#0f766e;font-weight:700;">📝 컨디션 메모: {l.get('patientWorkoutNote') or '-'}</div>
            <ul style="margin:0;padding-left:18px;line-height:1.45;">{items_li}</ul>
          </div>
        </details>
        """

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{
          font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
          margin: 0;
          padding: 2px;
          background: transparent;
          color: #1e293b;
        }}
        .summary-strip {{
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 8px;
          margin-bottom: 12px;
        }}
        @media (max-width: 600px) {{
          .summary-strip {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        .strip-box {{
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 10px;
          padding: 9px 11px;
        }}
        .card-container {{
          background: #f8fafc;
          border: 1.5px solid #0f766e;
          border-radius: 14px;
          padding: 14px;
          margin-bottom: 12px;
        }}
        summary::-webkit-details-marker {{ display: none; }}
      </style>
    </head>
    <body>
      <!-- 1. 오늘 수행한 개인 운동 요약 (최상단 & 한눈에 보기) -->
      <div class="card-container">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:6px;margin-bottom:10px;">
          <div>
            <span style="font-size:15.5px;font-weight:800;color:#0f172a;">🏋️ 오늘 수행한 개인 운동 요약 ({current_log['date']})</span>
            <span style="margin-left:6px;font-size:11.5px;font-weight:800;color:#0f766e;background:#ccfbf1;padding:2px 8px;border-radius:999px;">
              {done_cnt}/{total_cnt} 완료 · 평균 RPE {avg_rpe}
            </span>
          </div>
        </div>

        {workout_rows}

        <div style="margin-top:8px;padding:8px 11px;background:#ffffff;border:1px solid #cbd5e1;border-radius:8px;font-size:12px;color:#334155;">
          <strong>📝 오늘 컨디션 한줄:</strong> {current_log.get('patientWorkoutNote') or '-'}
        </div>
      </div>

      <!-- 2. 컴팩트 4대 지표 요약 바 -->
      <div class="summary-strip">
        <div class="strip-box" style="background:#f0fdfa;border-color:#99f6e4;">
          <div style="font-size:11px;color:#0f766e;font-weight:700;">운동 수행 (주지표)</div>
          <div style="font-size:17px;font-weight:800;color:#115e59;margin-top:2px;">{done_cnt}/{total_cnt} 완료</div>
        </div>
        <div class="strip-box" style="background:#eff6ff;border-color:#bfdbfe;">
          <div style="font-size:11px;color:#1d4ed8;font-weight:700;">평균 운동자각도</div>
          <div style="font-size:17px;font-weight:800;color:#1e3a8a;margin-top:2px;">RPE {avg_rpe} <span style="font-size:11px;font-weight:500;">/10</span></div>
        </div>
        <div class="strip-box">
          <div style="font-size:11px;color:#64748b;font-weight:700;">수면 만족도 · 좌식</div>
          <div style="font-size:15px;font-weight:800;color:#d97706;margin-top:2px;">★{s['score']}점 <span style="font-size:11px;color:#475569;">({s['sittingHours']}h 좌식)</span></div>
        </div>
        <div class="strip-box">
          <div style="font-size:11px;color:#64748b;font-weight:700;">보조지표 (평균 VAS)</div>
          <div style="font-size:17px;font-weight:800;color:#475569;margin-top:2px;">{avg_vas}점 <span style="font-size:11px;font-weight:500;">/10</span></div>
        </div>
      </div>

      <!-- 3. 방문일 근황 아코디언 (클릭 시 펼쳐보기) -->
      <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:13px;">
        <div style="font-size:14px;font-weight:800;color:#0f172a;margin-bottom:3px;">📋 날짜별 운동 근황 모아보기 (센터 방문일 확인용)</div>
        <div style="font-size:11.5px;color:#64748b;margin-bottom:9px;">날짜를 클릭하면 그날 수행한 운동의 유지시간·RPE·주관적 느낌이 펼쳐집니다.</div>
        {visit_accordions}
      </div>
    </body>
    </html>
    """
    dynamic_height = min(820, max(540, 290 + len(workouts) * 78 + len(all_logs) * 44))
    components.html(html_code, height=dynamic_height, scrolling=True)


def render_compact_vas_auxiliary(current_log, all_logs):
    logs_json = json.dumps(all_logs, ensure_ascii=False)
    meta_json = json.dumps(PART_META, ensure_ascii=False)
    selected_date_str = current_log["date"]

    vas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{
          font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
          margin: 0;
          padding: 2px;
          color: #1e293b;
        }}
        .filter-btn {{
          padding: 4px 9px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 700;
          border: 1px solid #cbd5e1;
          background: #f8fafc;
          color: #475569;
          cursor: pointer;
        }}
        .filter-btn.active {{
          background: #0f172a;
          color: #ffffff;
          border-color: #0f172a;
        }}
        .matrix-table {{
          width: 100%;
          border-collapse: collapse;
          font-size: 11.5px;
          margin-top: 8px;
        }}
        .matrix-table th, .matrix-table td {{
          border: 1px solid #e2e8f0;
          padding: 5px 4px;
          text-align: center;
        }}
        .matrix-table th {{ background: #f1f5f9; font-weight: 800; }}
      </style>
    </head>
    <body>
      <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:12px;">
        <div id="partFilterBar" style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px;"></div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:8px;">
          <svg id="multiLineSvg" viewBox="0 0 660 200" style="width:100%;height:auto;"></svg>
        </div>
        <table class="matrix-table" id="painMatrixTable"></table>
      </div>

      <script>
        const ALL_LOGS = {logs_json};
        const PART_META = {meta_json};
        let selectedPartFilter = 'ALL';
        let focusedDateIdx = ALL_LOGS.findIndex(l => l.date === '{selected_date_str}');
        if (focusedDateIdx < 0) focusedDateIdx = ALL_LOGS.length - 1;

        function getCellStyle(sc) {{
          if (sc <= 3) return 'background:#dcfce7;color:#166534;font-weight:800;';
          if (sc <= 6) return 'background:#fef3c7;color:#92400e;font-weight:800;';
          return 'background:#fee2e2;color:#991b1b;font-weight:800;';
        }}

        function setPartFilter(key) {{ selectedPartFilter = key; renderVas(); }}
        function setFocusedDate(idx) {{ focusedDateIdx = idx; renderVas(); }}

        function renderVas() {{
          const bar = document.getElementById('partFilterBar');
          let btns = `<button class="filter-btn ${{selectedPartFilter === 'ALL' ? 'active' : ''}}" onclick="setPartFilter('ALL')">전체 부위</button>`;
          PART_META.forEach(m => {{
            const act = selectedPartFilter === m.key;
            const st = act ? `background:${{m.color}};color:#fff;border-color:${{m.color}};` : `border-left:4px solid ${{m.color}};`;
            btns += `<button class="filter-btn" style="${{st}}" onclick="setPartFilter('${{m.key}}')">${{m.short}}</button>`;
          }});
          bar.innerHTML = btns;

          const svg = document.getElementById('multiLineSvg');
          const W = 660, H = 200, padL = 32, padR = 20, padT = 18, padB = 30;
          const plotW = W - padL - padR, plotH = H - padT - padB;
          const n = ALL_LOGS.length;
          const xPos = (i) => n === 1 ? padL + plotW / 2 : padL + (i * plotW) / (n - 1);
          const yPos = (v) => padT + plotH - (Math.min(10, Math.max(0, v)) / 10) * plotH;

          let out = '';
          [0, 2, 4, 6, 8, 10].forEach(v => {{
            const y = yPos(v);
            out += `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="#e2e8f0" stroke-width="1"/>`;
            out += `<text x="${{padL - 6}}" y="${{y + 4}}" text-anchor="end" font-size="9.5" fill="#64748b">${{v}}</text>`;
          }});

          ALL_LOGS.forEach((l, i) => {{
            const x = xPos(i);
            const sel = i === focusedDateIdx;
            out += `<text x="${{x}}" y="${{H - 8}}" text-anchor="middle" font-size="10.5" font-weight="${{sel ? '800' : '600'}}" fill="${{sel ? '#0f766e' : '#475569'}}" style="cursor:pointer;" onclick="setFocusedDate(${{i}})">${{l.date.slice(5)}}</text>`;
          }});

          PART_META.forEach((m, idx) => {{
            const hi = selectedPartFilter === 'ALL' || selectedPartFilter === m.key;
            const op = hi ? '1' : '0.15';
            const off = selectedPartFilter === 'ALL' ? (idx - 2.5) * 0.9 : 0;
            const pts = ALL_LOGS.map((l, i) => `${{xPos(i)}},${{yPos(l.parts[m.key].score) + off}}`).join(' ');
            out += `<polyline fill="none" stroke="${{m.color}}" stroke-width="2" opacity="${{op}}" points="${{pts}}"/>`;
            ALL_LOGS.forEach((l, i) => {{
              const sc = l.parts[m.key].score;
              out += `<circle cx="${{xPos(i)}}" cy="${{yPos(sc) + off}}" r="4" fill="${{m.color}}" stroke="#fff" stroke-width="1" opacity="${{op}}"/>`;
            }});
          }});
          svg.innerHTML = out;

          const tbl = document.getElementById('painMatrixTable');
          let th = `<tr><th>부위</th>` + ALL_LOGS.map(l => `<th>${{l.date.slice(5)}}</th>`).join('') + `<th>첫날 대비</th><th>선택일 특이점</th></tr>`;
          let tr = PART_META.map(m => {{
            const d = ALL_LOGS[ALL_LOGS.length - 1].parts[m.key].score - ALL_LOGS[0].parts[m.key].score;
            const dTxt = d < 0 ? `<span style="color:#0d9488;font-weight:800;">▼${{d}}</span>` : (d > 0 ? `<span style="color:#e11d48;">▲+${{d}}</span>` : '-');
            const note = ALL_LOGS[focusedDateIdx].parts[m.key].note || '-';
            return `<tr><td style="font-weight:700;">${{m.short}}</td>` +
              ALL_LOGS.map(l => `<td style="${{getCellStyle(l.parts[m.key].score)}}">${{l.parts[m.key].score}}</td>`).join('') +
              `<td>${{dTxt}}</td><td style="text-align:left;padding-left:6px;color:#475569;">${{note}}</td></tr>`;
          }}).join('');
          tbl.innerHTML = th + tr;
        }}
        renderVas();
      </script>
    </body>
    </html>
    """
    components.html(vas_html, height=420, scrolling=False)


db = load_shared_db()

if "is_owner" not in st.session_state:
    st.session_state.is_owner = False
if "editing_workout_id" not in st.session_state:
    st.session_state.editing_workout_id = None

# --- COMPACT TOP HEADER ---
h_col1, h_col2 = st.columns([3, 2])
with h_col1:
    st.markdown("#### 🏋️ 매일 튼튼 개인 운동 · 재활 일지")
    st.caption("만 31세 남 · 189cm · 93kg | 운동(RPE·유지시간·느낌) 중심 & VAS 보조지표")

with h_col2:
    if st.session_state.is_owner:
        if st.button("🔓 본인 모드 (클릭 시 잠금)", use_container_width=True):
            st.session_state.is_owner = False
            st.rerun()
    else:
        with st.popover("🔒 본인 잠금 해제 (일지 수정)", use_container_width=True):
            pin_input = st.text_input("PIN 입력", type="password", key="pin_box")
            if st.button("잠금 해제", type="primary", use_container_width=True):
                if pin_input == db.get("ownerPin", "0208"):
                    st.session_state.is_owner = True
                    st.rerun()
                else:
                    st.error("PIN 불일치")

# --- COMPACT DATE BAR ---
dates = [log["date"] for log in db["logs"]]
selected_idx = dates.index(db["selectedDate"]) if db["selectedDate"] in dates else len(dates) - 1

d_col1, d_col2 = st.columns([3, 1])
with d_col1:
    chosen_date = st.selectbox("📅 날짜 선택", dates, index=selected_idx, label_visibility="collapsed")
    if chosen_date != db["selectedDate"]:
        db["selectedDate"] = chosen_date
        save_shared_db(db)
        st.rerun()

with d_col2:
    if st.button("+ 새 일지", disabled=not st.session_state.is_owner, use_container_width=True):
        last_log = db["logs"][-1]
        next_dt = (datetime.strptime(last_log["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        if next_dt not in dates:
            new_log = json.loads(json.dumps(last_log))
            new_log["date"] = next_dt
            new_log["workoutList"] = [
                {
                    "id": f"w-{int(datetime.now().timestamp())}-{i}",
                    "text": w["text"],
                    "rpe": w.get("rpe", 7),
                    "duration": w.get("duration", ""),
                    "feeling": "",
                    "done": False,
                }
                for i, w in enumerate(last_log.get("workoutList", []))
            ]
            new_log["directorOpinion"]["inquiry"] = ""
            new_log["directorOpinion"]["assessment"] = ""
            new_log["directorOpinion"]["prescription"] = ""
            db["logs"].append(new_log)
            db["selectedDate"] = next_dt
            save_shared_db(db)
            st.rerun()

current_idx = next((i for i, l in enumerate(db["logs"]) if l["date"] == db["selectedDate"]), len(db["logs"]) - 1)
current_log = db["logs"][current_idx]
is_owner = st.session_state.is_owner

# --- 3 CLEAN TABS ---
tab1, tab2, tab3 = st.tabs([
    "🏋️ 오늘의 운동 요약",
    f"✍️ 기록·수정 {'🔓' if is_owner else '🔒'}",
    "💬 원장님 소견 (OPEN)",
])

with tab1:
    # 1. 최상단: 오늘 수행한 개인 운동 요약 + 방문일 아코디언 브리핑
    render_clean_workout_summary(current_log, db["logs"])

    # 2. 원장님 한줄 코멘트
    d_op = current_log["directorOpinion"]
    if d_op.get("assessment") or d_op.get("prescription"):
        st.info(
            f"**💬 {d_op.get('directorName', '황인준 원장님')} 피드백**\n\n"
            f"- **소견:** {d_op.get('assessment') or '-'}\n"
            f"- **가이드:** {d_op.get('prescription') or '-'}"
        )

    # 3. 보조지표(VAS)는 기본 접힘(expanded=False)으로 화면 복잡도 최소화
    with st.expander("📉 [보조지표] 날짜별 6대 부위 VAS 통증 추이 그래프 & 표 보기", expanded=False):
        render_compact_vas_auxiliary(current_log, db["logs"])

with tab2:
    if not is_owner:
        st.warning("🔒 우측 상단의 **[🔒 본인 잠금 해제]** 버튼을 눌러야 운동 및 일지를 수정할 수 있습니다.")

    st.markdown("##### 🏋️ 1. 오늘 수행한 개인 운동 (유지시간 · RPE · 주관적 느낌)")
    with st.expander("➕ 새 개인 운동 추가하기", expanded=is_owner):
        a_col1, a_col2, a_col3 = st.columns([3, 2, 1])
        with a_col1:
            new_w_title = st.text_input("운동명", placeholder="예: 무릎꿇고 골반 올리기", disabled=not is_owner, key=f"t_{db['selectedDate']}")
        with a_col2:
            new_w_dur = st.text_input("유지시간/세트", placeholder="예: 12초 × 3세트", disabled=not is_owner, key=f"d_{db['selectedDate']}")
        with a_col3:
            new_w_rpe = st.number_input("RPE(1~10)", 1, 10, 7, disabled=not is_owner, key=f"r_{db['selectedDate']}")
        new_w_feel = st.text_input("주관적인 느낌", placeholder="예: 3세트 마지막에 둔근 자극 강함, 허리 개입 없음", disabled=not is_owner, key=f"f_{db['selectedDate']}")

        if st.button("+ 목록에 추가", type="primary", disabled=not is_owner, use_container_width=True):
            if new_w_title.strip():
                current_log.setdefault("workoutList", []).append({
                    "id": f"w-{int(datetime.now().timestamp()*1000)}",
                    "text": new_w_title.strip(),
                    "duration": new_w_dur.strip() or "-",
                    "rpe": int(new_w_rpe),
                    "feeling": new_w_feel.strip(),
                    "done": True,
                })
                save_shared_db(db)
                st.rerun()

    for idx, w in enumerate(list(current_log.get("workoutList", []))):
        wid = w["id"]
        with st.container(border=True):
            if st.session_state.editing_workout_id == wid and is_owner:
                ec1, ec2, ec3 = st.columns([3, 2, 1])
                with ec1:
                    ed_title = st.text_input("운동명", value=w["text"], key=f"ed_t_{wid}")
                with ec2:
                    ed_dur = st.text_input("유지시간/세트", value=w.get("duration", ""), key=f"ed_d_{wid}")
                with ec3:
                    ed_rpe = st.number_input("RPE", 1, 10, int(w.get("rpe", 7)), key=f"ed_r_{wid}")
                ed_feel = st.text_input("주관적인 느낌", value=w.get("feeling", ""), key=f"ed_f_{wid}")
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾 저장", key=f"s_{wid}", type="primary", use_container_width=True):
                        w["text"] = ed_title.strip()
                        w["duration"] = ed_dur.strip()
                        w["rpe"] = int(ed_rpe)
                        w["feeling"] = ed_feel.strip()
                        st.session_state.editing_workout_id = None
                        save_shared_db(db)
                        st.rerun()
                with b2:
                    if st.button("취소", key=f"c_{wid}", use_container_width=True):
                        st.session_state.editing_workout_id = None
                        st.rerun()
            else:
                wc1, wc2, wc3 = st.columns([6, 1, 1])
                with wc1:
                    checked = st.checkbox(
                        f"**{w['text']}** (`{w.get('duration', '-')}` · **RPE {w.get('rpe', 7)}**)",
                        value=bool(w.get("done")),
                        disabled=not is_owner,
                        key=f"chk_{wid}_{db['selectedDate']}",
                    )
                    if checked != bool(w.get("done")) and is_owner:
                        w["done"] = checked
                        save_shared_db(db)
                        st.rerun()
                with wc2:
                    if st.button("수정", key=f"eb_{wid}", disabled=not is_owner, use_container_width=True):
                        st.session_state.editing_workout_id = wid
                        st.rerun()
                with wc3:
                    if st.button("삭제", key=f"db_{wid}", disabled=not is_owner, use_container_width=True):
                        current_log["workoutList"] = [item for item in current_log["workoutList"] if item["id"] != wid]
                        save_shared_db(db)
                        st.rerun()
                st.caption(f"↳ **느낌:** {w.get('feeling') or '-'}")

    new_cond_note = st.text_input("📝 오늘 전체 컨디션 한줄 메모", value=current_log.get("patientWorkoutNote", ""), disabled=not is_owner)
    if is_owner and st.button("💾 컨디션 메모 저장", use_container_width=True):
        current_log["patientWorkoutNote"] = new_cond_note
        save_shared_db(db)
        st.toast("저장 완료!")
        st.rerun()

    # 보조지표 입력란도 접기/펼치기(Expander)로 깔끔하게 정리
    with st.expander("📊 2. 보조지표 (수면 만족도 & 6대 부위 VAS 점수) 수정하기", expanded=False):
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            new_sleep_score = st.selectbox("수면 만족도(1~5)", [1, 2, 3, 4, 5], index=current_log["sleep"]["score"] - 1, disabled=not is_owner)
        with s_col2:
            posture_opts = ["뒤척일 때 뻐근함", "똑바로 누울 때 찌릿함", "새벽·기상 직후 강직", "수면 중 불편감 없음"]
            curr_p = current_log["sleep"]["posture"]
            new_posture = st.selectbox("수면 중 요추 상태", posture_opts, index=posture_opts.index(curr_p) if curr_p in posture_opts else 0, disabled=not is_owner)
        with s_col3:
            new_sit = st.number_input("일일 좌식(시간)", 0, 24, int(current_log["sleep"]["sittingHours"]), disabled=not is_owner)

        updated_parts = {}
        for m in PART_META:
            key = m["key"]
            item = current_log["parts"][key]
            c1, c2 = st.columns([1, 1])
            with c1:
                sc = st.slider(f"{m['name']} (VAS)", 0, 10, int(item["score"]), disabled=not is_owner, key=f"sl_{key}_{db['selectedDate']}")
            with c2:
                nt = st.text_input(f"{m['short']} 메모", value=item["note"], disabled=not is_owner, key=f"nt_{key}_{db['selectedDate']}")
            updated_parts[key] = {"score": sc, "note": nt}

        if is_owner and st.button("💾 보조지표 저장", type="primary", use_container_width=True):
            current_log["sleep"]["score"] = new_sleep_score
            current_log["sleep"]["posture"] = new_posture
            current_log["sleep"]["sittingHours"] = new_sit
            current_log["parts"] = updated_parts
            save_shared_db(db)
            st.toast("보조지표 저장 완료!")
            st.rerun()

with tab3:
    st.caption("💬 황인준 대표님께서 센터 방문일에 확인하시고 코멘트를 남기시는 공간입니다. (비밀번호 없이 즉시 저장)")
    d_op = current_log["directorOpinion"]
    d_name = st.text_input("담당 전문가", value=d_op.get("directorName", "황인준 대표 (피지컬그라운드)"))
    d_target = st.text_input("중점 타겟", value=d_op.get("focusTarget", ""))
    d_ass = st.text_area("운동 수행(RPE·유지시간·느낌) 평가 소견", value=d_op.get("assessment", ""), height=80)
    d_pre = st.text_area("다음 루틴 & 유지시간·RPE 처방 가이드", value=d_op.get("prescription", ""), height=80)

    if st.button("💾 원장님 소견 저장", type="primary", use_container_width=True):
        current_log["directorOpinion"] = {
            "directorName": d_name,
            "focusTarget": d_target,
            "inquiry": d_op.get("inquiry", ""),
            "assessment": d_ass,
            "prescription": d_pre,
        }
        save_shared_db(db)
        st.toast("소견이 저장되었습니다!")
        st.rerun()

    with st.expander("📋 카카오톡 공유용 텍스트 복사하기", expanded=False):
        p = current_log["parts"]
        workouts = current_log.get("workoutList", [])
        done_cnt = sum(1 for w in workouts if w.get("done"))
        w_lines = "\n".join([
            f"• {'✅' if w.get('done') else '⬜'} {w['text']} ({w.get('duration', '-')} | RPE {w.get('rpe', 7)})\n  ↳ 느낌: {w.get('feeling') or '-'}"
            for w in workouts
        ]) or "- 운동 기록 없음"
        share_txt = (
            f"[{current_log['date']} 운동 요약 ({done_cnt}/{len(workouts)} 완료)]\n"
            f"{w_lines}\n"
            f"📝 컨디션: {current_log.get('patientWorkoutNote') or '-'}\n\n"
            f"📊 [보조지표 VAS] 허리({p['lumbar']['score']}) 좌고관절({p['leftHip']['score']}) 좌어깨({p['leftAnteriorShoulder']['score']}) 우손목({p['rightWrist']['score']}) 우무릎({p['rightKnee']['score']}) 목({p['cervical']['score']})"
        )
        st.code(share_txt, language="markdown")
