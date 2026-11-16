import json
import os
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="매일 튼튼 재활·운동 일지 (피지컬그라운드 공유용)",
    page_icon="🏋️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_FILE = "rehab_shared_data.json"
SCHEMA_VERSION = "2026-11-16-v7-rpe"

PART_META = [
    {"key": "lumbar", "name": "1. 허리 (요추 부위)", "short": "허리(요추)", "side": "중앙 코어", "color": "#ef4444", "desc": "수면 시 불편감 및 좌식 디스크 하중"},
    {"key": "leftHip", "name": "2. 왼쪽 고관절", "short": "왼쪽 고관절", "side": "좌측 하체", "color": "#f97316", "desc": "장요근 단축 및 골반 전면 집임"},
    {"key": "leftAnteriorShoulder", "name": "3. 왼쪽 전면 어깨", "short": "왼쪽 전면 어깨", "side": "좌측 상체", "color": "#eab308", "desc": "소흉근 단축 및 라운드 숄더"},
    {"key": "rightWrist", "name": "4. 오른쪽 손목", "short": "오른쪽 손목", "side": "우측 상체", "color": "#10b981", "desc": "마우스 과사용 및 신경 포착 주의"},
    {"key": "rightKnee", "name": "5. 오른쪽 무릎", "short": "오른쪽 무릎", "side": "우측 하체", "color": "#06b6d4", "desc": "좌측 고관절 제한에 따른 대각선 과부하"},
    {"key": "cervical", "name": "6. 목 (일자목)", "short": "목(일자목)", "side": "상부 코어", "color": "#6366f1", "desc": "모니터 높이에 따른 경추 전만 소실"},
]

CAPTURED_WORKOUTS_1113 = [
    {
        "id": "w-cap-1",
        "text": "무릎꿇고 골반 하늘로 올리기 12초씩 3세트",
        "rpe": 6,
        "duration": "12초 × 3세트",
        "feeling": "처음 1세트 때는 왼쪽 고관절 앞쪽이 팽팽했으나 3세트째에 둔근 수축감이 잘 들어옴",
        "done": True,
    },
    {
        "id": "w-cap-2",
        "text": "플랭크 1분씩( 다리 하나씩 10초씩 들기) 2세트",
        "rpe": 8,
        "duration": "1분(한발 10초) × 2세트",
        "feeling": "왼다리 들 때 골반이 살짝 흔들리고 40초 이후 복부 코어 떨림 강함",
        "done": True,
    },
    {
        "id": "w-cap-3",
        "text": "사이드로 누워서 팔로 바닥 버티면서 의자 다리올려서 버티기 2세트",
        "rpe": 8,
        "duration": "30초 × 2세트",
        "feeling": "버티는 후반부에 지지하는 왼쪽 전면 어깨 쪽으로 체중이 실리며 뻐근함 느껴짐",
        "done": True,
    },
    {
        "id": "w-cap-4",
        "text": "어깨 슈러그 30회 3세트 (16kg)",
        "rpe": 7,
        "duration": "30회 × 3세트 (16kg)",
        "feeling": "승모근 상부 펌핑감 양호, 마지막 5회에서 목 앞쪽이 살짝 긴장됨",
        "done": True,
    },
    {
        "id": "w-cap-5",
        "text": "다리한쪽 올려서 옆으로 돌리기 10회씩 3세트",
        "rpe": 6,
        "duration": "10회 × 3세트",
        "feeling": "왼쪽 다리를 크게 외회전할 때 고관절 깊은 곳에서 걸리는 느낌이 약간 있음",
        "done": True,
    },
]

CAPTURED_WORKOUTS_1114 = [
    {
        "id": "w-401",
        "text": "무릎꿇고 골반 하늘로 올리기 12초씩 3세트",
        "rpe": 6,
        "duration": "12초 × 3세트",
        "feeling": "어제보다 골반 앞쪽 당김이 줄고 엉덩이 근육으로 12초 버티기 수월해짐",
        "done": True,
    },
    {
        "id": "w-402",
        "text": "플랭크 1분씩( 다리 하나씩 10초씩 들기) 2세트",
        "rpe": 7,
        "duration": "1분(한발 10초) × 2세트",
        "feeling": "배꼽을 등 쪽으로 당기며 버티니 요추 부담 없이 1분 유지 안정적임",
        "done": True,
    },
    {
        "id": "w-403",
        "text": "사이드로 누워서 팔로 바닥 버티면서 의자 다리올려서 버티기 2세트",
        "rpe": 8,
        "duration": "30초 × 2세트",
        "feeling": "팔꿈치로 바닥을 밀어내며 버티니 왼쪽 앞어깨 불편감이 어제보다 줄어듦",
        "done": True,
    },
    {
        "id": "w-404",
        "text": "어깨 슈러그 30회 3세트 (16kg)",
        "rpe": 7,
        "duration": "30회 × 3세트 (16kg)",
        "feeling": "오른쪽 손목 통증 전혀 없이 덤벨 파지 안정적, 30회 3세트 무난히 완료",
        "done": True,
    },
    {
        "id": "w-405",
        "text": "다리한쪽 올려서 옆으로 돌리기 10회씩 3세트",
        "rpe": 5,
        "duration": "10회 × 3세트",
        "feeling": "회전 반경을 조금 줄여서 돌리니 고관절 걸림 없이 부드럽게 수행됨",
        "done": True,
    },
]

CAPTURED_WORKOUTS_1115 = [
    {
        "id": "w-501",
        "text": "무릎꿇고 골반 하늘로 올리기 12초씩 3세트",
        "rpe": 6,
        "duration": "12초 × 3세트",
        "feeling": "아침 7시 반에 일찍 깨서 초기엔 허리가 약간 뻣뻣했으나 2세트부터 부드러워짐",
        "done": True,
    },
    {
        "id": "w-502",
        "text": "플랭크 1분씩( 다리 하나씩 10초씩 들기) 2세트",
        "rpe": 8,
        "duration": "1분(한발 10초) × 2세트",
        "feeling": "수면이 조금 부족해 2세트 마지막 다리 들기 10초 구간에서 코어 피로도 높았음",
        "done": True,
    },
    {
        "id": "w-503",
        "text": "사이드로 누워서 팔로 바닥 버티면서 의자 다리올려서 버티기 2세트",
        "rpe": 8,
        "duration": "30초 × 2세트",
        "feeling": "내전근과 옆구리 자극 강하게 들어옴, 왼쪽 어깨 지지력 유지 집중",
        "done": True,
    },
    {
        "id": "w-504",
        "text": "어깨 슈러그 30회 3세트 (16kg)",
        "rpe": 7,
        "duration": "30회 × 3세트 (16kg)",
        "feeling": "턱 당김 유지하며 30회씩 수행, 상부 승모근 자극 일정함",
        "done": True,
    },
    {
        "id": "w-505",
        "text": "다리한쪽 올려서 옆으로 돌리기 10회씩 3세트",
        "rpe": 6,
        "duration": "10회 × 3세트",
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
                    "text": "폼롤러 흉추(등뼈) 마사지 10분",
                    "rpe": 4,
                    "duration": "10분",
                    "feeling": "등 중앙이 많이 굳어 있어 처음엔 아팠으나 롤링 후 호흡이 편해짐",
                    "done": True,
                },
                {
                    "id": "w-102",
                    "text": "런지 자세 좌측 장요근 스트레칭 30초×3세트",
                    "rpe": 6,
                    "duration": "30초 × 3세트",
                    "feeling": "왼쪽 사타구니 앞쪽이 강하게 당김, 30초 버틴 후 일어설 때 허리 한결 가벼움",
                    "done": True,
                },
            ],
            "patientWorkoutNote": "무릎 아래 베개 받치고 취침 시도, 등 마사지 후 호흡이 한결 편해짐",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "focusTarget": "버티기(등척성) 훈련 시 RPE·유지시간 및 주관적 느낌 중심 기록",
                "inquiry": "각 운동별 유지시간 동안 어느 부위에 자극이나 피로가 먼저 오는지 주관적인 느낌을 적어주세요.",
                "assessment": "VAS는 외부 요인 영향을 많이 받으므로 보조지표로 두고, 각 운동별 RPE(운동자각도)와 버티기 유지시간에 따른 주관적 느낌을 최우선 지표로 확인하겠습니다.",
                "prescription": "무릎 꿇고 골반 올리기와 플랭크·사이드 버티기 수행 시 목표 유지시간을 채울 때의 느낌을 운동 항목 아래에 기록해 주세요.",
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
                    "text": "런지 장요근 스트레칭 30초×4세트",
                    "rpe": 5,
                    "duration": "30초 × 4세트",
                    "feeling": "어제보다 30초 유지할 때 사타구니 당김 강도가 한결 부드러워짐",
                    "done": True,
                },
                {
                    "id": "w-202",
                    "text": "흉추 가동성 오픈북 좌우 15회×3세트",
                    "rpe": 5,
                    "duration": "15회 × 3세트",
                    "feeling": "왼쪽 가슴 앞쪽이 열리면서 어깨 회전이 시원하게 됨",
                    "done": True,
                },
            ],
            "patientWorkoutNote": "장요근과 오픈북 완료! 모니터 높인 뒤 목 피로도 감소",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "focusTarget": "코어 및 고관절 등척성 버티기 유지시간 단계적 확대",
                "inquiry": "센터 오시는 날에 날짜별 운동 요약과 적어주신 주관적 느낌을 한꺼번에 체크하겠습니다.",
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
            "workoutList": json.loads(json.dumps(CAPTURED_WORKOUTS_1113)),
            "patientWorkoutNote": "낮 동안 50:3 루틴과 장요근·소흉근 이완 완료, 저녁에 브릿지 추가 예정",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "focusTarget": "버티기 계열 훈련 시 RPE 및 유지시간별 주관적 느낌 모니터링",
                "inquiry": "사이드 버티기 30초 유지 시 옆구리(복사근)·내전근 자극과 왼쪽 어깨 부담 비율이 어떤지 적어주세요.",
                "assessment": "5대 개인 운동 루틴 수행이 매우 안정적입니다. 보조지표인 VAS 통증도 1~3점대로 크게 낮아졌습니다.",
                "prescription": "버티는 계열 훈련(골반 올리기 12초, 플랭크 1분, 사이드 버티기)의 유지시간과 운동 직후 주관적 느낌을 계속 기록해 주세요.",
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
            "workoutList": json.loads(json.dumps(CAPTURED_WORKOUTS_1114)),
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
            "workoutList": json.loads(json.dumps(CAPTURED_WORKOUTS_1115)),
            "patientWorkoutNote": "일요일이여서 오래자고 싶었는데 7시반에 깨서 잠 만족도가 별로임.",
            "directorOpinion": {
                "directorName": "황인준 대표 (피지컬그라운드)",
                "focusTarget": "센터 방문일 근황 확인용 — 운동별 RPE·유지시간·주관적 느낌 종합 점검",
                "inquiry": "오시는 날에 각 운동 밑에 적어주신 주관적인 느낌과 RPE 변화를 바탕으로 다음 진도를 설정하겠습니다!",
                "assessment": "일요일 조기 기상으로 컨디션이 살짝 아쉬웠음에도 5가지 운동의 목표 유지시간과 세트를 모두 완수하셨습니다.",
                "prescription": "방문 수업 시 사이드 버티기 어깨 지지 자세와 고관절 회전 각도를 함께 디테일하게 잡아보겠습니다.",
            },
        },
    ],
}


def normalize_workout_items(db_data):
    for log in db_data.get("logs", []):
        for w in log.get("workoutList", []):
            if "rpe" not in w:
                w["rpe"] = 7
            if "duration" not in w:
                w["duration"] = "목표 세트/유지시간 완수"
            if "feeling" not in w:
                w["feeling"] = ""
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


def get_node_color(score):
    if score <= 3:
        return "#10b981"
    if score <= 6:
        return "#f59e0b"
    return "#ef4444"


def get_badge_style(score):
    if score <= 3:
        return "background:#dcfce7;color:#166534;border:1px solid #86efac;"
    if score <= 6:
        return "background:#fef3c7;color:#92400e;border:1px solid #fde68a;"
    return "background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;"


def get_rpe_badge_style(rpe_val):
    if rpe_val <= 5:
        return "background:#dbeafe;color:#1e40af;border:1px solid #93c5fd;"
    if rpe_val <= 7:
        return "background:#ccfbf1;color:#115e59;border:1px solid #5eead4;"
    return "background:#fef3c7;color:#92400e;border:1px solid #fcd34d;"


def render_workout_first_summary(current_log, prev_log, all_logs):
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    total_cnt = len(workouts)
    pct = int(round((done_cnt / total_cnt) * 100)) if total_cnt > 0 else 0
    avg_rpe = round(sum(int(w.get("rpe", 7)) for w in workouts) / total_cnt, 1) if total_cnt > 0 else 0.0

    p = current_log["parts"]
    s = current_log["sleep"]
    vas_scores = [p[m["key"]]["score"] for m in PART_META]
    avg_vas = round(sum(vas_scores) / len(vas_scores), 1)
    stars = "★" * s["score"] + "☆" * (5 - s["score"])

    # Build Primary Section: Today's Workout Summary with RPE, Duration, and Subjective Feeling right underneath each exercise
    workout_cards_html = ""
    if not workouts:
        workout_cards_html = """
        <div style="padding:16px;text-align:center;color:#64748b;font-size:13px;border:1px dashed #cbd5e1;border-radius:12px;">
          등록된 개인 운동이 없습니다. [✍️ 운동·일지 기록] 탭에서 오늘의 운동과 주관적 느낌을 추가해 주세요.
        </div>
        """
    else:
        for idx, w in enumerate(workouts):
            is_done = bool(w.get("done"))
            rpe_val = int(w.get("rpe", 7))
            dur_txt = w.get("duration") or "세트/시간 미기재"
            feel_txt = w.get("feeling") or "작성된 주관적 느낌이 없습니다."
            status_bg = "#f0fdfa" if is_done else "#f8fafc"
            status_border = "#5eead4" if is_done else "#e2e8f0"
            check_badge = "✅ 수행 완료" if is_done else "⬜ 진행 전"

            workout_cards_html += f"""
            <div style="background:{status_bg};border:1.5px solid {status_border};border-radius:14px;padding:13px 15px;margin-bottom:10px;">
              <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="font-size:12px;font-weight:800;padding:2px 8px;border-radius:6px;background:#0f766e;color:#fff;">운동 {idx + 1}</span>
                  <span style="font-size:14.5px;font-weight:800;color:#0f172a;">{w['text']}</span>
                </div>
                <div style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;">
                  <span style="font-size:11.5px;font-weight:800;padding:2px 8px;border-radius:6px;background:#f1f5f9;color:#334155;border:1px solid #cbd5e1;">⏱️ 유지/수행: {dur_txt}</span>
                  <span style="font-size:11.5px;font-weight:800;padding:2px 8px;border-radius:6px;{get_rpe_badge_style(rpe_val)}">🔥 운동자각도 RPE {rpe_val}/10</span>
                  <span style="font-size:11.5px;font-weight:800;color:#0f766e;">{check_badge}</span>
                </div>
              </div>
              <div style="margin-top:8px;padding:9px 12px;background:#ffffff;border-radius:10px;border-left:4px solid #0d9488;font-size:13px;color:#1e293b;line-height:1.5;">
                <strong style="color:#0f766e;">💬 유지시간에 따른 주관적 느낌:</strong> {feel_txt}
              </div>
            </div>
            """

    # Build Multi-Day Workout Check-in History (For PT Director on Visit Days)
    history_html = ""
    for l in reversed(all_logs):
        l_workouts = l.get("workoutList", [])
        l_done = sum(1 for w in l_workouts if w.get("done"))
        l_rpe = round(sum(int(w.get("rpe", 7)) for w in l_workouts) / len(l_workouts), 1) if l_workouts else 0
        is_curr = l["date"] == current_log["date"]
        box_border = "border:2px solid #0d9488;background:#f0fdfa;" if is_curr else "border:1px solid #e2e8f0;background:#ffffff;"
        w_items_summary = "".join([
            f"<div style='margin-top:5px;padding:6px 10px;background:#f8fafc;border-radius:8px;font-size:12px;'>"
            f"<strong>• {w['text']}</strong> <span style='color:#0f766e;font-weight:700;'>[RPE {w.get('rpe', 7)} | {w.get('duration', '-')}]</span><br/>"
            f"<span style='color:#475569;'>↳ 느낌: {w.get('feeling') or '-'}</span></div>"
            for w in l_workouts
        ])
        history_html += f"""
        <div style="border-radius:12px;padding:12px 14px;margin-bottom:9px;{box_border}">
          <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:6px;">
            <span style="font-size:13.5px;font-weight:800;color:#0f172a;">📅 {l['date']} 운동 근황 ({l_done}/{len(l_workouts)} 완료 · 평균 RPE {l_rpe})</span>
            <span style="font-size:11.5px;color:#64748b;font-weight:600;">수면 ★{l['sleep']['score']} · 좌식 {l['sleep']['sittingHours']}h</span>
          </div>
          <div style="font-size:12px;color:#0f766e;font-weight:700;margin-top:4px;">📝 전체 컨디션 메모: {l.get('patientWorkoutNote') or '-'}</div>
          {w_items_summary}
        </div>
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
        .top-grid {{
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 10px;
          margin-bottom: 14px;
        }}
        @media (max-width: 640px) {{
          .top-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        .metric-card {{
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 14px;
          padding: 12px 14px;
          box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}
        .main-card {{
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 16px;
          padding: 16px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.04);
          margin-bottom: 14px;
        }}
      </style>
    </head>
    <body>
      <!-- 1. PRIMARY SECTION: 오늘 수행한 개인 운동 요약 (최상단 배치 - 황인준 원장님 피드백 반영) -->
      <div class="main-card" style="border:2px solid #0f766e;">
        <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;margin-bottom:12px;border-bottom:1px solid #e2e8f0;padding-bottom:10px;">
          <div>
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="background:#0f766e;color:#fff;font-size:11px;font-weight:800;padding:3px 9px;border-radius:999px;">제1 핵심 지표</span>
              <span style="font-size:16px;font-weight:800;color:#0f172a;">🏋️ 오늘 수행한 개인 운동 요약 ({current_log['date']})</span>
            </div>
            <div style="font-size:12px;color:#475569;margin-top:3px;">
              버티기 훈련의 <strong>운동자각도(RPE) · 유지시간 · 각 운동별 주관적 느낌</strong>을 최우선으로 확인합니다.
            </div>
          </div>
          <div style="text-align:right;">
            <span style="font-size:13px;font-weight:800;color:#0f766e;">달성 {done_cnt}/{total_cnt} ({pct}%) · 평균 RPE {avg_rpe}</span>
          </div>
        </div>

        {workout_cards_html}

        <div style="margin-top:10px;padding:10px 14px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:10px;font-size:12.5px;color:#334155;">
          <strong>📝 오늘의 전체 컨디션 메모:</strong> {current_log.get('patientWorkoutNote') or '기록된 컨디션 메모가 없습니다.'}
        </div>
      </div>

      <!-- 2. Top Overview Metrics (운동 지표 중심 + VAS 보조지표) -->
      <div class="top-grid">
        <div class="metric-card" style="border-color:#5eead4;background:#f0fdfa;">
          <div style="font-size:12px;color:#0f766e;font-weight:700;">운동 완수율 (주지표)</div>
          <div style="display:flex;align-items:baseline;gap:6px;margin-top:4px;">
            <span style="font-size:22px;font-weight:800;color:#115e59;">{done_cnt}/{total_cnt}</span>
            <span style="font-size:12px;font-weight:700;color:#0d9488;">({pct}%)</span>
          </div>
          <div style="font-size:11px;color:#0f766e;margin-top:4px;font-weight:600;">목표 유지시간 달성</div>
        </div>

        <div class="metric-card" style="border-color:#93c5fd;background:#eff6ff;">
          <div style="font-size:12px;color:#1e40af;font-weight:700;">평균 운동자각도 (RPE)</div>
          <div style="display:flex;align-items:baseline;gap:4px;margin-top:4px;">
            <span style="font-size:22px;font-weight:800;color:#1e3a8a;">RPE {avg_rpe}</span>
            <span style="font-size:12px;color:#64748b;">/ 10</span>
          </div>
          <div style="font-size:11px;color:#1e40af;margin-top:4px;font-weight:600;">체감 버티기 강도</div>
        </div>

        <div class="metric-card">
          <div style="font-size:12px;color:#64748b;font-weight:600;">수면 만족도 & 좌식</div>
          <div style="font-size:16px;font-weight:800;color:#f59e0b;margin-top:5px;">{stars} ({s['score']}점)</div>
          <div style="font-size:11px;color:#475569;font-weight:600;margin-top:4px;">좌식 {s['sittingHours']}시간 · 각성 {s['wakeUpCount']}회</div>
        </div>

        <div class="metric-card" style="background:#f8fafc;">
          <div style="font-size:12px;color:#64748b;font-weight:600;">평균 통증 (보조지표 VAS)</div>
          <div style="display:flex;align-items:baseline;gap:4px;margin-top:4px;">
            <span style="font-size:22px;font-weight:800;color:#475569;">{avg_vas}</span>
            <span style="font-size:12px;color:#94a3b8;">/ 10점</span>
          </div>
          <div style="font-size:11px;color:#64748b;margin-top:4px;">컨디션 참고용 보조지표</div>
        </div>
      </div>

      <!-- 3. 방문일 근황 한눈에 보기 (황인준 원장님 방문일 체크용) -->
      <div class="main-card">
        <div style="font-size:15px;font-weight:800;color:#0f172a;margin-bottom:4px;">📋 센터 방문일 근황 브리핑 (일자별 운동 RPE · 유지시간 · 주관적 느낌 모아보기)</div>
        <div style="font-size:12px;color:#64748b;margin-bottom:10px;">매일 확인하지 못하시더라도 센터 오시는 날 최근 운동 흐름과 주관적 느낌을 한눈에 파악하실 수 있습니다.</div>
        {history_html}
      </div>
    </body>
    </html>
    """
    components.html(html_code, height=960, scrolling=True)


def render_secondary_vas_section(current_log, prev_log, all_logs):
    p = current_log["parts"]
    s = current_log["sleep"]

    cards_html = ""
    for m in PART_META:
        key = m["key"]
        item = p[key]
        sc = item["score"]
        note = item["note"] or m["desc"]
        delta_badge = ""
        if prev_log:
            d = sc - prev_log["parts"][key]["score"]
            if d < 0:
                delta_badge = f"<span style='color:#0d9488;font-size:11px;font-weight:700;margin-right:4px;'>▼{d}</span>"
            elif d > 0:
                delta_badge = f"<span style='color:#e11d48;font-size:11px;font-weight:700;margin-right:4px;'>▲+{d}</span>"

        cards_html += f"""
        <div style="padding:10px 12px;border-radius:12px;border:1px solid #e2e8f0;background:#f8fafc;display:flex;flex-direction:column;justify-content:space-between;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
            <span style="font-size:12.5px;font-weight:700;color:#1e293b;">{m['name']}</span>
            <div style="display:flex;align-items:center;">
              {delta_badge}
              <span style="padding:2px 7px;border-radius:6px;font-size:11.5px;font-weight:800;{get_badge_style(sc)}">VAS {sc}점</span>
            </div>
          </div>
          <div style="font-size:11.5px;color:#475569;margin-top:5px;">• {note}</div>
        </div>
        """

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
          background: transparent;
          color: #1e293b;
        }}
        .main-card {{
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 16px;
          padding: 16px;
          margin-bottom: 14px;
        }}
        .body-layout {{
          display: grid;
          grid-template-columns: 210px 1fr;
          gap: 14px;
          align-items: center;
        }}
        @media (max-width: 680px) {{
          .body-layout {{ grid-template-columns: 1fr; }}
        }}
        .parts-grid {{
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 9px;
        }}
        @media (max-width: 520px) {{
          .parts-grid {{ grid-template-columns: 1fr; }}
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
          margin-top: 10px;
        }}
        .matrix-table th, .matrix-table td {{
          border: 1px solid #e2e8f0;
          padding: 6px 5px;
          text-align: center;
        }}
        .matrix-table th {{
          background: #f1f5f9;
          font-weight: 800;
          color: #334155;
        }}
      </style>
    </head>
    <body>
      <div class="main-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
          <div>
            <span style="background:#64748b;color:#fff;font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:999px;">보조 지표 (VAS)</span>
            <span style="font-size:14.5px;font-weight:800;color:#0f172a;margin-left:6px;">📉 날짜별 6대 부위 통증지수(VAS) 추이 & 특이점 그래프</span>
          </div>
        </div>
        <div id="partFilterBar" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;"></div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:10px;">
          <svg id="multiLineSvg" viewBox="0 0 680 230" style="width:100%;height:auto;overflow:visible;"></svg>
        </div>
        <div id="chartPointDetailBox" style="margin-top:8px;padding:10px 12px;border-radius:10px;background:#f8fafc;border:1px solid #cbd5e1;font-size:12px;color:#334155;"></div>
        <div style="overflow-x:auto;margin-top:10px;">
          <table class="matrix-table" id="painMatrixTable"></table>
        </div>
      </div>

      <div class="main-card">
        <div style="font-size:14px;font-weight:800;color:#0f172a;margin-bottom:10px;">🧍 6대 부위 보조지표 밸런스 맵 ({current_log['date']})</div>
        <div class="body-layout">
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:10px;display:flex;flex-direction:column;align-items:center;">
            <svg viewBox="0 0 220 310" width="175" height="240">
              <circle cx="110" cy="32" r="19" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="102" y="51" width="16" height="16" rx="4" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <path d="M75 67 H145 L138 162 H82 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="53" y="69" width="18" height="86" rx="8" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="149" y="69" width="18" height="86" rx="8" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="82" y="162" width="24" height="122" rx="9" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="114" y="162" width="24" height="122" rx="9" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>

              <circle cx="110" cy="60" r="11" fill="{get_node_color(p['cervical']['score'])}" stroke="#ffffff" stroke-width="2"/>
              <text x="110" y="64" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="bold">{p['cervical']['score']}</text>

              <circle cx="146" cy="80" r="11" fill="{get_node_color(p['leftAnteriorShoulder']['score'])}" stroke="#ffffff" stroke-width="2"/>
              <text x="146" y="84" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="bold">{p['leftAnteriorShoulder']['score']}</text>

              <circle cx="110" cy="138" r="13" fill="{get_node_color(p['lumbar']['score'])}" stroke="#ffffff" stroke-width="2"/>
              <text x="110" y="142" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="bold">{p['lumbar']['score']}</text>

              <circle cx="62" cy="152" r="11" fill="{get_node_color(p['rightWrist']['score'])}" stroke="#ffffff" stroke-width="2"/>
              <text x="62" y="156" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="bold">{p['rightWrist']['score']}</text>

              <circle cx="128" cy="170" r="11" fill="{get_node_color(p['leftHip']['score'])}" stroke="#ffffff" stroke-width="2"/>
              <text x="128" y="174" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="bold">{p['leftHip']['score']}</text>

              <circle cx="94" cy="228" r="11" fill="{get_node_color(p['rightKnee']['score'])}" stroke="#ffffff" stroke-width="2"/>
              <text x="94" y="232" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="bold">{p['rightKnee']['score']}</text>
            </svg>
          </div>
          <div class="parts-grid">{cards_html}</div>
        </div>
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

        function setPartFilter(key) {{
          selectedPartFilter = key;
          renderVasChart();
        }}

        function setFocusedDate(idx) {{
          focusedDateIdx = idx;
          renderVasChart();
        }}

        function renderVasChart() {{
          const filterBar = document.getElementById('partFilterBar');
          let btnsHtml = `<button class="filter-btn ${{selectedPartFilter === 'ALL' ? 'active' : ''}}" onclick="setPartFilter('ALL')">전체 부위</button>`;
          PART_META.forEach(m => {{
            const isAct = selectedPartFilter === m.key;
            const style = isAct ? `background:${{m.color}};color:#fff;border-color:${{m.color}};` : `border-left:4px solid ${{m.color}};`;
            btnsHtml += `<button class="filter-btn" style="${{style}}" onclick="setPartFilter('${{m.key}}')">${{m.short}}</button>`;
          }});
          filterBar.innerHTML = btnsHtml;

          const svg = document.getElementById('multiLineSvg');
          const W = 680, H = 230, padL = 38, padR = 24, padT = 24, padB = 36;
          const plotW = W - padL - padR, plotH = H - padT - padB;
          const n = ALL_LOGS.length;
          const xPos = (i) => n === 1 ? padL + plotW / 2 : padL + (i * plotW) / (n - 1);
          const yPos = (val) => padT + plotH - (Math.min(10, Math.max(0, val)) / 10) * plotH;

          let svgContent = '';
          [0, 2, 4, 6, 8, 10].forEach(v => {{
            const y = yPos(v);
            svgContent += `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="#e2e8f0" stroke-width="1"/>`;
            svgContent += `<text x="${{padL - 6}}" y="${{y + 4}}" text-anchor="end" font-size="10" fill="#64748b">${{v}}</text>`;
          }});

          const fx = xPos(focusedDateIdx);
          svgContent += `<line x1="${{fx}}" y1="${{padT - 6}}" x2="${{fx}}" y2="${{H - padB}}" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3 2"/>`;

          ALL_LOGS.forEach((log, i) => {{
            const x = xPos(i);
            const isSel = i === focusedDateIdx;
            svgContent += `<g style="cursor:pointer;" onclick="setFocusedDate(${{i}})">
              <text x="${{x}}" y="${{H - padB + 18}}" text-anchor="middle" font-size="11" font-weight="${{isSel ? '800' : '600'}}" fill="${{isSel ? '#0f766e' : '#475569'}}">${{log.date.slice(5)}}</text>
            </g>`;
          }});

          PART_META.forEach((m, mIdx) => {{
            const isHighlighted = selectedPartFilter === 'ALL' || selectedPartFilter === m.key;
            const opacity = isHighlighted ? '1' : '0.15';
            const offset = selectedPartFilter === 'ALL' ? (mIdx - 2.5) * 1.0 : 0;
            const pts = ALL_LOGS.map((l, i) => `${{xPos(i)}},${{yPos(l.parts[m.key].score) + offset}}`).join(' ');
            svgContent += `<polyline fill="none" stroke="${{m.color}}" stroke-width="2.2" opacity="${{opacity}}" points="${{pts}}"/>`;
            ALL_LOGS.forEach((l, i) => {{
              const sc = l.parts[m.key].score;
              svgContent += `<circle cx="${{xPos(i)}}" cy="${{yPos(sc) + offset}}" r="4.5" fill="${{m.color}}" stroke="#fff" stroke-width="1.2" opacity="${{opacity}}" style="cursor:pointer;" onclick="setFocusedDate(${{i}})"/>`;
            }});
          }});
          svg.innerHTML = svgContent;

          const fLog = ALL_LOGS[focusedDateIdx];
          document.getElementById('chartPointDetailBox').innerHTML =
            `<strong>📌 [${{fLog.date}} 보조지표 메모]</strong> 수면 ★${{fLog.sleep.score}}점 (${{fLog.sleep.posture}}) · 컨디션: ${{fLog.patientWorkoutNote || '-'}}`;

          const tbl = document.getElementById('painMatrixTable');
          let ths = `<tr><th>부위</th>` + ALL_LOGS.map(l => `<th>${{l.date.slice(5)}}</th>`).join('') + `<th>변화</th></tr>`;
          let trs = PART_META.map(m => {{
            const diff = ALL_LOGS[ALL_LOGS.length - 1].parts[m.key].score - ALL_LOGS[0].parts[m.key].score;
            const dTxt = diff < 0 ? `<span style="color:#0d9488;font-weight:800;">▼${{diff}}</span>` : (diff > 0 ? `<span style="color:#e11d48;">▲+${{diff}}</span>` : '-');
            return `<tr><td style="font-weight:700;">${{m.short}}</td>` +
              ALL_LOGS.map(l => `<td style="${{getCellStyle(l.parts[m.key].score)}}">${{l.parts[m.key].score}}</td>`).join('') +
              `<td>${{dTxt}}</td></tr>`;
          }}).join('');
          tbl.innerHTML = ths + trs;
        }}
        renderVasChart();
      </script>
    </body>
    </html>
    """
    components.html(vas_html, height=780, scrolling=True)


db = load_shared_db()

if "is_owner" not in st.session_state:
    st.session_state.is_owner = False
if "editing_workout_id" not in st.session_state:
    st.session_state.editing_workout_id = None

# --- HEADER & PERMISSION BAR ---
st.markdown("### 🏋️ 매일 튼튼 재활·운동 일지 (피지컬그라운드 공유용)")
st.caption("환자 프로필: 만 31세 남성 · 189cm · 93kg · 장시간 좌식 근무 | 운동(RPE·유지시간·느낌) 중심 기록 & VAS 보조지표")

col_role, col_pin = st.columns([3, 2])
with col_role:
    if st.session_state.is_owner:
        st.success("🔓 **현재 권한: 본인 모드** (운동·RPE·주관적 느낌 및 일지 추가·수정·삭제 가능)")
        if st.button("🩺 원장님/공유자 열람 모드로 전환", use_container_width=True):
            st.session_state.is_owner = False
            st.rerun()
    else:
        st.warning("🩺 **현재 권한: 원장님/공유자 모드** (일지 읽기 전용 · **원장님 소견 탭은 즉시 작성 가능**)")

with col_pin:
    if not st.session_state.is_owner:
        pin_input = st.text_input("🔒 본인 잠금 해제 PIN", type="password", key="pin_box")
        if st.button("본인 권한 잠금 해제", use_container_width=True):
            if pin_input == db.get("ownerPin", "0208"):
                st.session_state.is_owner = True
                st.rerun()
            else:
                st.error("PIN 번호가 일치하지 않습니다.")

# --- DATE SELECTOR & NEW DATE ---
dates = [log["date"] for log in db["logs"]]
selected_idx = dates.index(db["selectedDate"]) if db["selectedDate"] in dates else len(dates) - 1

d_col1, d_col2 = st.columns([3, 1])
with d_col1:
    chosen_date = st.selectbox("📅 일지 날짜 선택", dates, index=selected_idx)
    if chosen_date != db["selectedDate"]:
        db["selectedDate"] = chosen_date
        save_shared_db(db)
        st.rerun()

with d_col2:
    st.write("")
    st.write("")
    if st.button("+ 새 일지 추가", disabled=not st.session_state.is_owner, use_container_width=True):
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
prev_log = db["logs"][current_idx - 1] if current_idx > 0 else None
is_owner = st.session_state.is_owner

# --- MAIN TABS (맨 끝 탭 임상처방 삭제 완료 -> 3개 탭 체제) ---
tab1, tab2, tab3 = st.tabs([
    "🏋️ 운동 요약 & 방문 브리핑",
    f"✍️ 운동·일지 기록 {'🔓' if is_owner else '🔒'}",
    "💬 황인준 원장님 소견 (OPEN)",
])

with tab1:
    # 1) 최상단: 오늘 수행한 개인 운동 요약 (각 운동 밑 주관적 느낌 + RPE + 유지시간) & 방문일 브리핑
    render_workout_first_summary(current_log, prev_log, db["logs"])

    # 2) 원장님 코멘트 요약
    st.markdown("#### 💬 황인준 원장님 코멘트 요약")
    st.success(current_log["directorOpinion"].get("assessment") or "아직 작성된 원장님 소견이 없습니다.")

    # 3) 보조지표: VAS 통증 추이 그래프 및 바디맵 (접기/펼치기 가능하도록 배치)
    with st.expander("📊 보조지표 확인하기: 6대 부위별 VAS 통증 추이 그래프 & 밸런스 바디맵", expanded=True):
        render_secondary_vas_section(current_log, prev_log, db["logs"])

with tab2:
    if not is_owner:
        st.info("🔒 운동 기록(RPE·유지시간·주관적 느낌) 및 일지 수정은 **환자 본인 권한**에서만 가능합니다. 상단에서 잠금을 해제해 주세요.")

    # 1) 제1 핵심: 오늘 수행한 개인 운동 및 운동별 주관적 느낌 기록 (최상단 배치)
    st.markdown("#### 🏋️ 오늘 수행한 개인 운동 & 유지시간·RPE·주관적 느낌 기록 (핵심 지표)")
    st.caption("버티는 계열 훈련 시 운동자각도(RPE 1~10), 유지시간, 그리고 각 운동 바로 밑에 주관적인 느낌을 적어주세요.")

    with st.container(border=True):
        st.markdown("**➕ 새 개인 운동 1개 추가**")
        a_col1, a_col2, a_col3 = st.columns([3, 2, 1])
        with a_col1:
            new_w_title = st.text_input(
                "운동명 및 세트",
                placeholder="예: 무릎꿇고 골반 하늘로 올리기 12초씩 3세트",
                disabled=not is_owner,
                key=f"new_w_title_{db['selectedDate']}",
            )
        with a_col2:
            new_w_dur = st.text_input(
                "유지시간 / 수행량",
                placeholder="예: 12초 × 3세트",
                disabled=not is_owner,
                key=f"new_w_dur_{db['selectedDate']}",
            )
        with a_col3:
            new_w_rpe = st.number_input(
                "RPE (1~10)",
                min_value=1,
                max_value=10,
                value=7,
                disabled=not is_owner,
                key=f"new_w_rpe_{db['selectedDate']}",
            )

        new_w_feel = st.text_input(
            "💬 이 운동 유지시간에 따른 주관적인 느낌 (버틸 때 자극 부위, 떨림, 불편감 등)",
            placeholder="예: 2세트까지는 둔근으로 잘 버텼으나 3세트 마지막 3초에 허리가 살짝 개입됨",
            disabled=not is_owner,
            key=f"new_w_feel_{db['selectedDate']}",
        )

        if st.button("+ 개인 운동 추가", type="primary", disabled=not is_owner, use_container_width=True):
            if new_w_title.strip():
                current_log.setdefault("workoutList", []).append({
                    "id": f"w-{int(datetime.now().timestamp()*1000)}",
                    "text": new_w_title.strip(),
                    "duration": new_w_dur.strip() or "목표 시간/세트 완수",
                    "rpe": int(new_w_rpe),
                    "feeling": new_w_feel.strip(),
                    "done": True,
                })
                save_shared_db(db)
                st.rerun()

    # 등록된 운동 목록 (각 운동 아래에 주관적 느낌 표시 + 수정/삭제)
    for idx, w in enumerate(list(current_log.get("workoutList", []))):
        wid = w["id"]
        with st.container(border=True):
            if st.session_state.editing_workout_id == wid and is_owner:
                st.markdown(f"**✏️ 운동 {idx + 1} 수정 중**")
                ec1, ec2, ec3 = st.columns([3, 2, 1])
                with ec1:
                    ed_title = st.text_input("운동명", value=w["text"], key=f"ed_t_{wid}")
                with ec2:
                    ed_dur = st.text_input("유지시간/세트", value=w.get("duration", ""), key=f"ed_d_{wid}")
                with ec3:
                    ed_rpe = st.number_input("RPE (1~10)", 1, 10, int(w.get("rpe", 7)), key=f"ed_r_{wid}")
                ed_feel = st.text_input("주관적인 느낌", value=w.get("feeling", ""), key=f"ed_f_{wid}")

                b1, b2 = st.columns(2)
                with b1:
                    if st.button("💾 수정 저장", key=f"save_w_{wid}", type="primary", use_container_width=True):
                        if ed_title.strip():
                            w["text"] = ed_title.strip()
                            w["duration"] = ed_dur.strip()
                            w["rpe"] = int(ed_rpe)
                            w["feeling"] = ed_feel.strip()
                            st.session_state.editing_workout_id = None
                            save_shared_db(db)
                            st.rerun()
                with b2:
                    if st.button("취소", key=f"cancel_w_{wid}", use_container_width=True):
                        st.session_state.editing_workout_id = None
                        st.rerun()
            else:
                wc1, wc2, wc3 = st.columns([5, 1, 1])
                with wc1:
                    checked = st.checkbox(
                        f"**{w['text']}**  |  ⏱️ `{w.get('duration', '-')}`  |  🔥 **RPE {w.get('rpe', 7)}/10**",
                        value=bool(w.get("done")),
                        disabled=not is_owner,
                        key=f"chk_{wid}_{db['selectedDate']}",
                    )
                    if checked != bool(w.get("done")) and is_owner:
                        w["done"] = checked
                        save_shared_db(db)
                        st.rerun()
                with wc2:
                    if st.button("수정", key=f"edit_btn_{wid}", disabled=not is_owner, use_container_width=True):
                        st.session_state.editing_workout_id = wid
                        st.rerun()
                with wc3:
                    if st.button("삭제", key=f"del_btn_{wid}", disabled=not is_owner, use_container_width=True):
                        current_log["workoutList"] = [item for item in current_log["workoutList"] if item["id"] != wid]
                        save_shared_db(db)
                        st.rerun()

                st.caption(f"💬 **주관적 느낌:** {w.get('feeling') or '기록된 주관적 느낌이 없습니다. [수정]을 눌러 느낌을 적어보세요.'}")

    new_cond_note = st.text_area(
        "📝 오늘의 전체 컨디션 및 특이사항 메모",
        value=current_log.get("patientWorkoutNote", ""),
        disabled=not is_owner,
        key=f"cond_note_{db['selectedDate']}",
    )
    if is_owner and st.button("📝 전체 컨디션 메모 저장", use_container_width=True):
        current_log["patientWorkoutNote"] = new_cond_note
        save_shared_db(db)
        st.toast("컨디션 메모가 저장되었습니다!")
        st.rerun()

    st.markdown("---")
    # 2) 보조 지표: 수면 및 6대 부위 VAS 통증 기록
    st.markdown("#### 📊 [보조 지표] 수면 만족도 및 6대 부위별 VAS 통증 기록")
    st.caption("VAS 통증 점수는 다양한 외부 요인의 영향을 받으므로 운동 강도 설정 시 참고용 보조지표로 활용합니다.")

    s_col1, s_col2, s_col3, s_col4 = st.columns([2, 3, 2, 2])
    with s_col1:
        new_sleep_score = st.selectbox(
            "수면 만족도 (1~5점)",
            [1, 2, 3, 4, 5],
            index=current_log["sleep"]["score"] - 1,
            disabled=not is_owner,
        )
    with s_col2:
        posture_opts = ["뒤척일 때 뻐근함", "똑바로 누울 때 찌릿함", "새벽·기상 직후 강직", "수면 중 불편감 없음"]
        curr_posture = current_log["sleep"]["posture"]
        p_idx = posture_opts.index(curr_posture) if curr_posture in posture_opts else 0
        new_posture = st.selectbox("수면 중 허리(요추) 불편 양상", posture_opts, index=p_idx, disabled=not is_owner)
    with s_col3:
        new_wake = st.number_input("야간 각성(회)", 0, 10, int(current_log["sleep"]["wakeUpCount"]), disabled=not is_owner)
    with s_col4:
        new_sit = st.number_input("일일 좌식(시간)", 0, 24, int(current_log["sleep"]["sittingHours"]), disabled=not is_owner)

    updated_parts = {}
    for m in PART_META:
        key = m["key"]
        item = current_log["parts"][key]
        c1, c2 = st.columns([1, 1])
        with c1:
            sc = st.slider(f"{m['name']} (보조지표 VAS)", 0, 10, int(item["score"]), disabled=not is_owner, key=f"sl_{key}_{db['selectedDate']}")
        with c2:
            nt = st.text_input(f"{m['name']} 특이사항 메모", value=item["note"], disabled=not is_owner, key=f"nt_{key}_{db['selectedDate']}")
        updated_parts[key] = {"score": sc, "note": nt}

    if is_owner:
        if st.button("💾 보조지표(수면 및 VAS 통증) 서버에 저장", use_container_width=True):
            current_log["sleep"] = {
                "score": new_sleep_score,
                "posture": new_posture,
                "wakeUpCount": new_wake,
                "sittingHours": new_sit,
            }
            current_log["parts"] = updated_parts
            save_shared_db(db)
            st.toast("보조지표(수면 및 VAS 기록)가 서버에 저장되었습니다!")
            st.rerun()

with tab3:
    st.success("💬 **황인준 원장님 소견 보드 (전체 권한 개방 OPEN):** 센터 방문일에 근황을 확인하시고 피드백이나 다음 루틴 가이드를 편하게 남겨주세요.")
    d_op = current_log["directorOpinion"]
    dc1, dc2 = st.columns(2)
    with dc1:
        d_name = st.text_input("담당 전문가 성함 / 소속", value=d_op.get("directorName", "황인준 대표 (피지컬그라운드)"))
    with dc2:
        d_target = st.text_input("이번 세션 중점 타겟", value=d_op.get("focusTarget", ""))

    d_inq = st.text_area("1. 방문 시 체크할 질문 / 확인 사항", value=d_op.get("inquiry", ""))
    d_ass = st.text_area("2. 운동 수행도(RPE·유지시간·느낌) 및 체형 평가 소견", value=d_op.get("assessment", ""))
    d_pre = st.text_area("3. 다음 개인 운동 루틴 & 유지시간·RPE 처방 가이드", value=d_op.get("prescription", ""))

    if st.button("💾 원장님 소견 서버에 즉시 저장 (실시간 공유)", type="primary", use_container_width=True):
        current_log["directorOpinion"] = {
            "directorName": d_name,
            "focusTarget": d_target,
            "inquiry": d_inq,
            "assessment": d_ass,
            "prescription": d_pre,
        }
        save_shared_db(db)
        st.toast("원장님 소견이 서버에 저장되어 즉시 공유되었습니다!")
        st.rerun()

    st.markdown("#### 📋 카카오톡/문자 공유용 텍스트 (운동 요약 최우선 배치)")
    p = current_log["parts"]
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    w_lines = "\n".join([
        f"  {'✅' if w.get('done') else '⬜'} {w['text']} (유지/수행: {w.get('duration', '-')} | RPE {w.get('rpe', 7)}/10)\n"
        f"     ↳ 느낌: {w.get('feeling') or '-'}"
        for w in workouts
    ]) or "  - 등록된 개인 운동 없음"

    share_txt = (
        f"[매일 튼튼 개인 운동 & 재활 근황 리포트 - {current_log['date']}]\n"
        f"🏋️ [1. 오늘 수행한 개인 운동 요약 ({done_cnt}/{len(workouts)} 완료)]\n"
        f"{w_lines}\n"
        f"📝 전체 컨디션 메모: {current_log.get('patientWorkoutNote') or '기록 없음'}\n\n"
        f"💬 [2. {d_name} 소견 및 처방]\n"
        f"• 중점 타겟: {d_target or '-'}\n"
        f"• 확인 사항: {d_inq or '-'}\n"
        f"• 평가 소견: {d_ass or '-'}\n"
        f"• 운동 처방: {d_pre or '-'}\n\n"
        f"📊 [3. 보조지표: 수면 및 6대 부위 VAS 통증]\n"
        f"• 수면 만족도: {current_log['sleep']['score']}/5점 ({current_log['sleep']['posture']}) | 좌식 {current_log['sleep']['sittingHours']}h\n"
        f"• 허리({p['lumbar']['score']}) | 좌고관절({p['leftHip']['score']}) | 좌어깨({p['leftAnteriorShoulder']['score']}) | 우손목({p['rightWrist']['score']}) | 우무릎({p['rightKnee']['score']}) | 목({p['cervical']['score']})"
    )
    st.code(share_txt, language="markdown")
