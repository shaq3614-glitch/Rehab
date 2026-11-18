import json
import os
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="재활·운동 일지",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 트렌디한 멀티 파스텔(Soft Wellness / Notion 스타일) 전역 CSS
st.markdown(
    """
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        color: #2d3748;
        background-color: #fafbfc;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 780px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_FILE = "rehab_shared_data.json"
SCHEMA_VERSION = "2026-11-19-v11-trendy-pastel"

# 6개 부위별 명확히 구분되는 트렌디 파스텔 팔레트 (코랄·피치·버터·민트·스카이·라벤더)
PART_META = [
    {
        "key": "lumbar",
        "name": "1. 허리 (요추)",
        "short": "허리",
        "side": "중앙 코어",
        "color": "#e58a8a",
        "bg": "#fdf2f2",
        "text": "#9b3b3b",
        "desc": "수면 시 불편감 및 좌식 하중",
    },
    {
        "key": "leftHip",
        "name": "2. 왼쪽 고관절",
        "short": "좌고관절",
        "side": "좌측 하체",
        "color": "#eba06a",
        "bg": "#fef6ee",
        "text": "#9a4e1c",
        "desc": "장요근 단축 및 회전 시 집임",
    },
    {
        "key": "leftAnteriorShoulder",
        "name": "3. 왼쪽 전면 어깨",
        "short": "좌어깨",
        "side": "좌측 상체",
        "color": "#d9b44a",
        "bg": "#fdf9eb",
        "text": "#856414",
        "desc": "측면 지지 및 기울 때 불편",
    },
    {
        "key": "rightWrist",
        "name": "4. 오른쪽 손목",
        "short": "우손목",
        "side": "우측 상체",
        "color": "#67b89a",
        "bg": "#effaf5",
        "text": "#246b52",
        "desc": "마우스 사용 및 땅 짚을 때",
    },
    {
        "key": "rightKnee",
        "name": "5. 오른쪽 무릎",
        "short": "우무릎",
        "side": "우측 하체",
        "color": "#6ea8dc",
        "bg": "#f0f7fe",
        "text": "#245b8f",
        "desc": "스쿼트 시 대각선 보상 하중",
    },
    {
        "key": "cervical",
        "name": "6. 목 (일자목)",
        "short": "목",
        "side": "상부 코어",
        "color": "#9b89d9",
        "bg": "#f5f2fd",
        "text": "#513d96",
        "desc": "컴퓨터 작업 시 경추 피로",
    },
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


def get_rpe_pastel_pill(rpe_val):
    if rpe_val <= 5:
        return "background:#eef6ff;color:#356399;border:1px solid #d4e6fb;"
    if rpe_val <= 7:
        return "background:#eef9f4;color:#2c7058;border:1px solid #ccebdc;"
    return "background:#fef5ec;color:#a15826;border:1px solid #f7dec4;"


def render_trendy_pastel_first_page(current_log, all_logs):
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    total_cnt = len(workouts)
    avg_rpe = round(sum(int(w.get("rpe", 7)) for w in workouts) / total_cnt, 1) if total_cnt > 0 else 0.0

    workout_rows = ""
    if not workouts:
        workout_rows = "<div style='padding:14px;text-align:center;color:#718096;font-size:13px;'>등록된 운동이 없습니다.</div>"
    else:
        for idx, w in enumerate(workouts):
            is_done = bool(w.get("done"))
            rpe_v = int(w.get("rpe", 7))
            dur = w.get("duration") or "-"
            feel = w.get("feeling") or "기록된 주관적 느낌 없음"
            check_dot = (
                "<span style='display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:6px;background:#67b89a;color:#fff;font-size:11px;font-weight:800;margin-right:7px;'>✓</span>"
                if is_done
                else "<span style='display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:6px;background:#edf2f7;color:#a0aec0;font-size:11px;margin-right:7px;'>-</span>"
            )
            workout_rows += f"""
            <div style="border:1px solid #e6ebf2;background:#ffffff;border-radius:12px;padding:12px 15px;margin-bottom:9px;box-shadow:0 1px 2px rgba(15,23,42,0.02);">
              <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px;">
                <div style="display:flex;align-items:center;font-size:13.5px;font-weight:700;color:#1e293b;">
                  {check_dot}<span>{idx + 1}. {w['text']}</span>
                </div>
                <div style="display:flex;gap:6px;">
                  <span style="font-size:11.5px;font-weight:600;padding:2px 9px;border-radius:999px;background:#f4f2fc;color:#5a4a9c;border:1px solid #e2dcf8;">⏱️ {dur}</span>
                  <span style="font-size:11.5px;font-weight:700;padding:2px 9px;border-radius:999px;{get_rpe_pastel_pill(rpe_v)}">RPE {rpe_v}/10</span>
                </div>
              </div>
              <div style="margin-top:7px;padding:7px 11px;background:#f8fafc;border-left:3px solid #9b89d9;border-radius:0 8px 8px 0;font-size:12.5px;color:#334155;line-height:1.48;">
                <strong style="color:#5a4a9c;">느낌:</strong> {feel}
              </div>
            </div>
            """

    logs_json = json.dumps(all_logs, ensure_ascii=False)
    meta_json = json.dumps(PART_META, ensure_ascii=False)
    selected_date_str = current_log["date"]

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
          color: #2d3748;
        }}
        .section-card {{
          background: #ffffff;
          border: 1px solid #e6ebf2;
          border-radius: 16px;
          padding: 16px;
          margin-bottom: 14px;
          box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        }}
        .workout-surface {{
          background: linear-gradient(180deg, #faf9ff 0%, #ffffff 100%);
          border: 1px solid #e3def7;
        }}
        .filter-btn {{
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 5px 11px;
          border-radius: 999px;
          font-size: 11.5px;
          font-weight: 600;
          border: 1px solid #e2e8f0;
          background: #ffffff;
          color: #4a5568;
          cursor: pointer;
          transition: all 0.16s ease;
        }}
        .filter-btn:hover {{
          background: #f8fafc;
        }}
        .filter-btn.active-all {{
          background: #3b4963;
          color: #ffffff;
          border-color: #3b4963;
          font-weight: 700;
        }}
        .color-dot {{
          width: 8px;
          height: 8px;
          border-radius: 50%;
          display: inline-block;
        }}
        .matrix-table {{
          width: 100%;
          border-collapse: separate;
          border-spacing: 0;
          font-size: 11.5px;
          margin-top: 12px;
          border: 1px solid #e6ebf2;
          border-radius: 10px;
          overflow: hidden;
        }}
        .matrix-table th, .matrix-table td {{
          border-bottom: 1px solid #edf2f7;
          border-right: 1px solid #edf2f7;
          padding: 6px 5px;
          text-align: center;
          color: #334155;
        }}
        .matrix-table th:last-child, .matrix-table td:last-child {{
          border-right: none;
        }}
        .matrix-table tr:last-child td {{
          border-bottom: none;
        }}
        .matrix-table th {{
          background: #f8fafc;
          font-weight: 700;
          color: #475569;
        }}
      </style>
    </head>
    <body>
      <!-- 1. 오늘 수행한 개인 운동 요약 (최상단 배치 - 황인준 대표님 피드백 유지) -->
      <div class="section-card workout-surface">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:6px;margin-bottom:11px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:15px;font-weight:800;color:#1e293b;">오늘 수행한 개인 운동 요약</span>
            <span style="font-size:11.5px;font-weight:700;color:#5a4a9c;background:#f0ecfe;padding:2px 9px;border-radius:999px;">{current_log['date']}</span>
          </div>
          <span style="font-size:11.5px;font-weight:700;color:#2c7058;background:#eef9f4;border:1px solid #ccebdc;padding:3px 10px;border-radius:999px;">
            완료 {done_cnt}/{total_cnt} · 평균 RPE {avg_rpe}
          </span>
        </div>

        {workout_rows}

        <div style="margin-top:8px;padding:9px 12px;background:#fffbf2;border:1px solid #f3e5c8;border-radius:10px;font-size:12px;color:#745420;">
          <strong>오늘 컨디션 메모:</strong> {current_log.get('patientWorkoutNote') or '-'}
        </div>
      </div>

      <!-- 2. 부위별 멀티 파스텔 VAS 통증 추이 & 특이점 그래프 (보조지표) -->
      <div class="section-card">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:6px;margin-bottom:9px;">
          <div>
            <span style="font-size:14.5px;font-weight:800;color:#1e293b;">날짜별 6대 부위 통증지수(VAS) 추이 & 특이점</span>
            <span style="margin-left:6px;font-size:10.5px;font-weight:700;color:#64748b;background:#f1f5f9;padding:2px 7px;border-radius:999px;">보조지표</span>
            <div style="font-size:11.5px;color:#718096;margin-top:3px;">
              각 부위별 파스텔 컬러로 구분됩니다 · 부위 버튼이나 표의 부위명을 누르면 단독 강조됩니다.
            </div>
          </div>
        </div>

        <!-- 부위별 파스텔 필터 버튼 -->
        <div id="partFilterBar" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px;"></div>

        <!-- 인터랙티브 SVG 멀티 파스텔 라인 차트 -->
        <div style="background:#fafbfd;border:1px solid #edf2f7;border-radius:12px;padding:12px 10px 6px 10px;">
          <svg id="trendyVasSvg" viewBox="0 0 660 230" style="width:100%;height:auto;overflow:visible;"></svg>
        </div>

        <!-- 선택 날짜/부위 특이점 콜아웃 -->
        <div id="pointNoteBox" style="margin-top:10px;padding:10px 13px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0;font-size:12px;color:#334155;line-height:1.55;"></div>

        <!-- 파스텔 히트맵 매트릭스 표 -->
        <div style="overflow-x:auto;">
          <table class="matrix-table" id="trendyMatrixTable"></table>
        </div>
      </div>

      <script>
        const ALL_LOGS = {logs_json};
        const PART_META = {meta_json};
        let selectedPart = 'ALL';
        let focusedIdx = ALL_LOGS.findIndex(l => l.date === '{selected_date_str}');
        if (focusedIdx < 0) focusedIdx = ALL_LOGS.length - 1;

        // 점수대별 부드러운 파스텔 톤 (민트 → 스카이 → 버터 → 코랄)
        function getScorePastelCell(sc) {{
          if (sc <= 1) return 'background:#effaf5;color:#246b52;font-weight:700;';
          if (sc <= 3) return 'background:#f0f7fe;color:#245b8f;font-weight:700;';
          if (sc <= 5) return 'background:#fdf9eb;color:#856414;font-weight:700;';
          return 'background:#fdf2f2;color:#9b3b3b;font-weight:800;';
        }}

        function setPart(key) {{ selectedPart = key; renderChart(); }}
        function setDateIdx(idx) {{ focusedIdx = idx; renderChart(); }}

        function renderChart() {{
          // 1. 필터 버튼 렌더링
          const bar = document.getElementById('partFilterBar');
          let btns = `<button class="filter-btn ${{selectedPart === 'ALL' ? 'active-all' : ''}}" onclick="setPart('ALL')">전체 6부위</button>`;
          PART_META.forEach(m => {{
            const act = selectedPart === m.key;
            const style = act
              ? `background:${{m.color}};color:#ffffff;border-color:${{m.color}};font-weight:700;`
              : `background:${{m.bg}};color:${{m.text}};border-color:${{m.color}}66;`;
            const dot = act
              ? `<span class="color-dot" style="background:#ffffff;"></span>`
              : `<span class="color-dot" style="background:${{m.color}};"></span>`;
            btns += `<button class="filter-btn" style="${{style}}" onclick="setPart('${{m.key}}')">${{dot}}${{m.short}}</button>`;
          }});
          bar.innerHTML = btns;

          // 2. SVG 차트 렌더링
          const svg = document.getElementById('trendyVasSvg');
          const W = 660, H = 230, padL = 36, padR = 24, padT = 26, padB = 34;
          const plotW = W - padL - padR, plotH = H - padT - padB;
          const n = ALL_LOGS.length;
          const xPos = (i) => n === 1 ? padL + plotW / 2 : padL + (i * plotW) / (n - 1);
          const yPos = (v) => padT + plotH - (Math.min(10, Math.max(0, v)) / 10) * plotH;

          let out = '';
          [0, 2, 4, 6, 8, 10].forEach(v => {{
            const y = yPos(v);
            out += `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="#e9eef5" stroke-width="1"/>`;
            out += `<text x="${{padL - 8}}" y="${{y + 4}}" text-anchor="end" font-size="10" fill="#94a3b8">${{v}}</text>`;
          }});

          const fx = xPos(focusedIdx);
          out += `<line x1="${{fx}}" y1="${{padT - 8}}" x2="${{fx}}" y2="${{H - padB}}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="3 3"/>`;

          ALL_LOGS.forEach((l, i) => {{
            const x = xPos(i);
            const sel = i === focusedIdx;
            const avg = (PART_META.reduce((a, m) => a + l.parts[m.key].score, 0) / PART_META.length).toFixed(1);
            out += `
              <g style="cursor:pointer;" onclick="setDateIdx(${{i}})">
                <rect x="${{x - 24}}" y="${{H - padB + 6}}" width="48" height="20" rx="6" fill="${{sel ? '#3b4963' : '#f1f5f9'}}"/>
                <text x="${{x}}" y="${{H - padB + 20}}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${{sel ? '#ffffff' : '#475569'}}">${{l.date.slice(5)}}</text>
                <text x="${{x}}" y="${{padT - 10}}" text-anchor="middle" font-size="9.5" font-weight="700" fill="${{sel ? '#3b4963' : '#94a3b8'}}">평균 ${{avg}}</text>
              </g>
            `;
          }});

          // 6개 부위별 개별 파스텔 라인
          PART_META.forEach((m, idx) => {{
            const isTarget = selectedPart === m.key;
            const isAll = selectedPart === 'ALL';
            const op = (isTarget || isAll) ? '0.95' : '0.13';
            const sw = isTarget ? '3.4' : '2.2';
            const off = isAll ? (idx - 2.5) * 1.15 : 0;
            const pts = ALL_LOGS.map((l, i) => `${{xPos(i)}},${{yPos(l.parts[m.key].score) + off}}`).join(' ');

            out += `<polyline fill="none" stroke="${{m.color}}" stroke-width="${{sw}}" opacity="${{op}}" points="${{pts}}" stroke-linecap="round" stroke-linejoin="round"/>`;

            ALL_LOGS.forEach((l, i) => {{
              const sc = l.parts[m.key].score;
              const cx = xPos(i), cy = yPos(sc) + off;
              const r = isTarget ? 5.2 : (i === focusedIdx ? 4.8 : 3.8);
              out += `
                <g style="cursor:pointer;" opacity="${{op}}" onclick="setDateIdx(${{i}})">
                  <circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="${{m.color}}" stroke="#ffffff" stroke-width="1.5">
                    <title>${{l.date}} ${{m.short}}: ${{sc}}점 (${{l.parts[m.key].note || '-'}})</title>
                  </circle>
                  ${{isTarget ? `<text x="${{cx}}" y="${{cy - 9}}" text-anchor="middle" font-size="10.5" font-weight="800" fill="${{m.text}}">${{sc}}점</text>` : ''}}
                </g>
              `;
            }});
          }});

          svg.innerHTML = out;

          // 3. 특이점 요약 콜아웃 업데이트
          const fLog = ALL_LOGS[focusedIdx];
          const box = document.getElementById('pointNoteBox');
          if (selectedPart === 'ALL') {{
            const pNotes = PART_META.map(m =>
              `<span style="display:inline-flex;align-items:center;gap:4px;margin-right:8px;">
                <span class="color-dot" style="background:${{m.color}};"></span>
                <strong>${{m.short}}(${{fLog.parts[m.key].score}}):</strong> ${{fLog.parts[m.key].note || '-'}}
              </span>`
            ).join('');
            box.style.background = '#f8fafc';
            box.style.borderColor = '#e2e8f0';
            box.innerHTML = `
              <div style="margin-bottom:4px;"><strong>[${{fLog.date}} 특이점]</strong> 수면 ★${{fLog.sleep.score}}점 (${{fLog.sleep.posture}}) · 좌식 ${{fLog.sleep.sittingHours}}h</div>
              <div style="font-size:11.5px;color:#475569;line-height:1.6;">${{pNotes}}</div>
            `;
          }} else {{
            const pm = PART_META.find(m => m.key === selectedPart);
            const diff = fLog.parts[pm.key].score - ALL_LOGS[0].parts[pm.key].score;
            const dStr = diff < 0 ? `첫날 대비 ${{-diff}}점 호전` : (diff > 0 ? `첫날 대비 +${{diff}}점` : '첫날과 동일');
            box.style.background = pm.bg;
            box.style.borderColor = pm.color + '88';
            box.innerHTML = `
              <div style="color:${{pm.text}};"><strong>[${{pm.name}} · ${{fLog.date}}]</strong> VAS ${{fLog.parts[pm.key].score}}점 (${{dStr}})</div>
              <div style="margin-top:3px;color:#334155;"><strong>특이점 메모:</strong> ${{fLog.parts[pm.key].note || '-'}}</div>
              <div style="margin-top:2px;font-size:11.5px;color:#64748b;">당일 컨디션: ${{fLog.patientWorkoutNote || '-'}}</div>
            `;
          }}

          // 4. 히트맵 매트릭스 표 렌더링
          const tbl = document.getElementById('trendyMatrixTable');
          let th = `<tr><th style="text-align:left;padding-left:10px;">부위</th>`
            + ALL_LOGS.map((l, i) => `<th style="cursor:pointer;${{i === focusedIdx ? 'background:#eef2f7;color:#1e293b;' : ''}}" onclick="setDateIdx(${{i}})">${{l.date.slice(5)}}</th>`).join('')
            + `<th>변화</th><th style="text-align:left;padding-left:8px;">선택일 특이점</th></tr>`;

          let tr = PART_META.map(m => {{
            const d = ALL_LOGS[ALL_LOGS.length - 1].parts[m.key].score - ALL_LOGS[0].parts[m.key].score;
            const dTxt = d < 0
              ? `<span style="color:#2c7058;font-weight:800;">▼${{d}}</span>`
              : (d > 0 ? `<span style="color:#9b3b3b;font-weight:700;">▲+${{d}}</span>` : `<span style="color:#94a3b8;">-</span>`);
            const note = fLog.parts[m.key].note || '-';
            return `<tr style="cursor:pointer;" onclick="setPart('${{m.key}}')">
              <td style="text-align:left;padding-left:10px;font-weight:700;white-space:nowrap;">
                <span class="color-dot" style="background:${{m.color}};margin-right:6px;"></span>${{m.short}}
              </td>` +
              ALL_LOGS.map(l => `<td style="${{getScorePastelCell(l.parts[m.key].score)}}">${{l.parts[m.key].score}}</td>`).join('') +
              `<td>${{dTxt}}</td><td style="text-align:left;padding-left:8px;color:#475569;">${{note}}</td></tr>`;
          }}).join('');
          tbl.innerHTML = th + tr;
        }}

        renderChart();
      </script>
    </body>
    </html>
    """
    dynamic_h = min(1020, max(780, 580 + len(workouts) * 76))
    components.html(html_code, height=dynamic_h, scrolling=True)


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
    "운동 요약 & 추이 그래프",
    f"기록·수정 {'(열림)' if is_owner else '(잠김)'}",
    "원장님 소견",
])

# --- TAB 1: 운동 요약 최우선 + 멀티 파스텔 VAS 추이 그래프 + 방문일 근황 ---
with tab1:
    render_trendy_pastel_first_page(current_log, db["logs"])

    d_op = current_log.get("directorOpinion", {})
    if d_op.get("assessment") or d_op.get("prescription"):
        with st.container(border=True):
            st.markdown(f"**{d_op.get('directorName', '담당 원장님')} 코멘트**")
            if d_op.get("assessment"):
                st.write(f"- 평가: {d_op['assessment']}")
            if d_op.get("prescription"):
                st.write(f"- 가이드: {d_op['prescription']}")

    st.markdown("**일자별 운동 근황 모아보기 (방문일 확인용)**")
    for l in reversed(db["logs"]):
        lw = l.get("workoutList", [])
        ldone = sum(1 for w in lw if w.get("done"))
        lrpe = round(sum(int(w.get("rpe", 7)) for w in lw) / len(lw), 1) if lw else 0.0
        with st.expander(f"{l['date']}  |  운동 {ldone}/{len(lw)} 완료 · 평균 RPE {lrpe} · 수면 {l['sleep']['score']}점", expanded=False):
            if l.get("patientWorkoutNote"):
                st.caption(f"메모: {l['patientWorkoutNote']}")
            for w in lw:
                st.markdown(f"- **{w['text']}** (`{w.get('duration', '-')}` | RPE {w.get('rpe', 7)})  \n  ↳ 느낌: {w.get('feeling') or '-'}")

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
