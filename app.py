import json
import os
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="매일 튼튼 재활 일지 & 황원택 원장 통합 임상 케어",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_FILE = "rehab_shared_data.json"
SCHEMA_VERSION = "2026-11-16-v6"

PART_META = [
    {"key": "lumbar", "name": "1. 허리 (요추 부위)", "short": "허리(요추)", "side": "중앙 코어", "color": "#ef4444", "desc": "수면 시 불편감 및 좌식 디스크 하중"},
    {"key": "leftHip", "name": "2. 왼쪽 고관절", "short": "왼쪽 고관절", "side": "좌측 하체", "color": "#f97316", "desc": "장요근 단축 및 골반 전면 집임"},
    {"key": "leftAnteriorShoulder", "name": "3. 왼쪽 전면 어깨", "short": "왼쪽 전면 어깨", "side": "좌측 상체", "color": "#eab308", "desc": "소흉근 단축 및 라운드 숄더"},
    {"key": "rightWrist", "name": "4. 오른쪽 손목", "short": "오른쪽 손목", "side": "우측 상체", "color": "#10b981", "desc": "마우스 과사용 및 신경 포착 주의"},
    {"key": "rightKnee", "name": "5. 오른쪽 무릎", "short": "오른쪽 무릎", "side": "우측 하체", "color": "#06b6d4", "desc": "좌측 고관절 제한에 따른 대각선 과부하"},
    {"key": "cervical", "name": "6. 목 (일자목)", "short": "목(일자목)", "side": "상부 코어", "color": "#6366f1", "desc": "모니터 높이에 따른 경추 전만 소실"},
]

CAPTURED_WORKOUTS = [
    {"id": "w-cap-1", "text": "무릎꿇고 골반 하늘로 올리기 12초씩 3세트", "done": True},
    {"id": "w-cap-2", "text": "플랭크 1분씩( 다리 하나씩 10초씩 들기) 2세트", "done": True},
    {"id": "w-cap-3", "text": "사이드로 누워서 팔로 바닥 버티면서 의자 다리올려서 버티기 2세트", "done": True},
    {"id": "w-cap-4", "text": "어깨 슈러그 30회 3세트 (16kg)", "done": True},
    {"id": "w-cap-5", "text": "다리한쪽 올려서 옆으로 돌리기 10회씩 3세트", "done": True},
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
                {"id": "w-101", "text": "폼롤러 흉추(등뼈) 마사지 10분", "done": True},
                {"id": "w-102", "text": "런지 자세 좌측 장요근 스트레칭 30초×3세트", "done": True},
            ],
            "patientWorkoutNote": "무릎 아래 베개 받치고 취침 시도, 등 마사지 후 호흡이 한결 편해짐",
            "directorOpinion": {
                "directorName": "황인준 PT 원장",
                "focusTarget": "좌측 장요근 이완 및 흉추 신전 가동성 확보",
                "inquiry": "무릎 아래에 베개를 받치고 주무실 때 허리 들뜸이 몇 분 내로 가라앉는지 확인해 주세요.",
                "assessment": "189cm 큰 키에 맞지 않는 낮은 책상 환경으로 일자목-요추 굴곡이 고착화되었고, 좌측 고관절 굴곡근 단축이 반대편 우측 무릎으로 체중을 밀어내는 전형적인 교차 보상 패턴입니다.",
                "prescription": "이번 주 하체 고중량 스쿼트는 중지하고, 런지 자세에서 왼쪽 장요근 늘리기(30초×4세트)와 오픈북 흉추 회전 운동을 우선 진행합니다.",
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
                {"id": "w-201", "text": "런지 장요근 스트레칭 30초×4세트", "done": True},
                {"id": "w-202", "text": "흉추 가동성 오픈북 좌우 15회×3세트", "done": True},
                {"id": "w-203", "text": "우측 목(사각근) 마사지볼 이완 및 손목 신경 글라이딩 10회", "done": False},
            ],
            "patientWorkoutNote": "장요근과 오픈북 완료! 저녁 늦게 손목 스트레칭은 깜빡함",
            "directorOpinion": {
                "directorName": "황인준 PT 원장",
                "focusTarget": "우측 손목 신경 활주 및 좌측 소흉근 이완",
                "inquiry": "모니터 높이를 올린 뒤 오후 시간대 눈 피로도와 목 앞쪽 긴장도가 어떤지 알려주세요.",
                "assessment": "요추 야간 통증이 7점에서 5점으로 유의미하게 감소했습니다. 좌측 고관절 가동범위가 열리면서 우측 무릎의 보상 하중도 함께 줄어들고 있습니다.",
                "prescription": "오른쪽 손목만 주무르지 마시고, 오른쪽 목 옆(사각근)과 왼쪽 가슴 앞쪽(소흉근)을 마사지볼로 먼저 풀어준 뒤 정중신경 글라이딩 운동을 10회씩 반복하세요.",
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
            "workoutList": json.loads(json.dumps(CAPTURED_WORKOUTS)),
            "patientWorkoutNote": "낮 동안 50:3 루틴과 장요근·소흉근 이완 완료, 저녁에 브릿지 추가 예정",
            "directorOpinion": {
                "directorName": "황인준 PT 원장",
                "focusTarget": "둔근(엉덩이 근육) 활성화 및 코어 안정화 진입",
                "inquiry": "오늘 PT 수업 전 브릿지 동작 시 허리가 먼저 쓰이는지, 엉덩이에 힘이 잘 들어오는지 체크해 볼게요!",
                "assessment": "수면 만족도가 4점으로 올라오면서 전신 근막 긴장도가 눈에 띄게 떨어졌습니다. 좌고관절-우무릎 대각선 사슬이 안정화 단계에 진입했습니다.",
                "prescription": "통증이 1~3점대로 안정되었으므로, 무릎 꿇고 골반 올리기와 플랭크·코펜하겐 사이드 버티기 등 코어·둔근 강화 루틴을 유지합니다.",
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
            "workoutList": json.loads(json.dumps(CAPTURED_WORKOUTS)),
            "patientWorkoutNote": "5대 개인 재활 운동 루틴 전체 완료! 오른쪽 손목 통증은 0점으로 소실됨",
            "directorOpinion": {
                "directorName": "황인준 PT 원장",
                "focusTarget": "좌측 어깨 지지 안정성 및 고관절 회전 가동범위 정밀 제어",
                "inquiry": "사이드로 누워 팔로 버틸 때 왼쪽 어깨 앞쪽이 밀리지 않도록 팔꿈치를 갈비뼈 쪽으로 살짝 당겨 지지해 보세요.",
                "assessment": "6대 부위 평균 통증이 1.3점으로 최저치를 기록했습니다. 우측 손목(0점)과 좌측 전면 어깨(1점), 우측 무릎(1점) 모두 뚜렷한 호전세입니다.",
                "prescription": "다리 한쪽 올려 옆으로 돌리기 수행 시 고관절에서 소리가 나거나 집히지 않는 작은 각도(60~70%)에서만 부드럽게 회전해 주세요.",
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
            "workoutList": json.loads(json.dumps(CAPTURED_WORKOUTS)),
            "patientWorkoutNote": "일요일이여서 오래자고 싶었는데 7시반에 깨서 잠 만족도가 별로임.",
            "directorOpinion": {
                "directorName": "황인준 PT 원장",
                "focusTarget": "일요일 조기 각성에 따른 요추·고관절 조조강직 이완",
                "inquiry": "휴일에 7시 반에 일찍 깨셨을 때 허리 뻐근함 때문에 잠이 깬 것인지, 습관적 생체리듬으로 깬 것인지 확인해 볼게요.",
                "assessment": "좌식 시간은 0시간으로 휴식을 취했으나, 수면 만족도가 3점으로 낮아지면서 요추(3점)와 좌측 고관절(3점)의 아침 강직도가 전일 대비 1점씩 소폭 반응했습니다.",
                "prescription": "아침에 일찍 깨셨을 때는 바로 일어나지 마시고 침대 위에서 무릎을 세워 좌우로 살살 흔들어주는 요추·고관절 웜업을 2분간 먼저 시행해 주세요.",
            },
        },
    ],
}


def load_shared_db():
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


def save_shared_db(data):
    data["schemaVersion"] = SCHEMA_VERSION
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_node_color(score):
    if score <= 3:
        return "#10b981"  # Green (0~3 양호)
    if score <= 6:
        return "#f59e0b"  # Amber (4~6 주의)
    return "#ef4444"      # Red (7~10 경고)


def get_badge_style(score):
    if score <= 3:
        return "background:#dcfce7;color:#166534;border:1px solid #86efac;"
    if score <= 6:
        return "background:#fef3c7;color:#92400e;border:1px solid #fde68a;"
    return "background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;"


def render_visual_body_dashboard(current_log, prev_log, all_logs):
    p = current_log["parts"]
    s = current_log["sleep"]
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    total_cnt = len(workouts)
    pct = int(round((done_cnt / total_cnt) * 100)) if total_cnt > 0 else 0

    scores = [p[m["key"]]["score"] for m in PART_META]
    avg_pain = round(sum(scores) / len(scores), 1)

    diff_html = "<span style='color:#64748b;font-size:12px;'>첫 기준 기록일</span>"
    if prev_log:
        prev_scores = [prev_log["parts"][m["key"]]["score"] for m in PART_META]
        prev_avg = round(sum(prev_scores) / len(prev_scores), 1)
        diff = round(avg_pain - prev_avg, 1)
        if diff < 0:
            diff_html = f"<span style='color:#0d9488;font-weight:700;font-size:12px;'>전일 대비 ▼ {abs(diff)}점 호전</span>"
        elif diff > 0:
            diff_html = f"<span style='color:#e11d48;font-weight:700;font-size:12px;'>전일 대비 ▲ +{diff}점 상승</span>"
        else:
            diff_html = "<span style='color:#64748b;font-weight:600;font-size:12px;'>전일과 동일</span>"

    stars = "★" * s["score"] + "☆" * (5 - s["score"])

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
        <div style="padding:11px 13px;border-radius:12px;border:1px solid #e2e8f0;background:#f8fafc;display:flex;flex-direction:column;justify-content:space-between;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
            <span style="font-size:13px;font-weight:700;color:#1e293b;">{m['name']}</span>
            <div style="display:flex;align-items:center;">
              {delta_badge}
              <span style="padding:2px 8px;border-radius:6px;font-size:12px;font-weight:800;{get_badge_style(sc)}">VAS {sc}점</span>
            </div>
          </div>
          <div style="font-size:12px;color:#475569;margin-top:6px;line-height:1.4;">• {note}</div>
        </div>
        """

    # Serialize logs & part meta for Interactive Multi-Line Chart & Milestone Timeline in JS
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
        .body-layout {{
          display: grid;
          grid-template-columns: 220px 1fr;
          gap: 16px;
          align-items: center;
        }}
        @media (max-width: 680px) {{
          .body-layout {{ grid-template-columns: 1fr; }}
        }}
        .parts-grid {{
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
        }}
        @media (max-width: 520px) {{
          .parts-grid {{ grid-template-columns: 1fr; }}
        }}
        .filter-btn {{
          padding: 5px 10px;
          border-radius: 999px;
          font-size: 11.5px;
          font-weight: 700;
          border: 1px solid #cbd5e1;
          background: #f8fafc;
          color: #475569;
          cursor: pointer;
          transition: all 0.15s;
        }}
        .filter-btn.active {{
          background: #0f172a;
          color: #ffffff;
          border-color: #0f172a;
        }}
        .matrix-table {{
          width: 100%;
          border-collapse: collapse;
          font-size: 12px;
          margin-top: 10px;
        }}
        .matrix-table th, .matrix-table td {{
          border: 1px solid #e2e8f0;
          padding: 7px 6px;
          text-align: center;
        }}
        .matrix-table th {{
          background: #f1f5f9;
          font-weight: 800;
          color: #334155;
        }}
        .milestone-box {{
          border-left: 3px solid #0d9488;
          background: #f8fafc;
          padding: 9px 12px;
          border-radius: 0 10px 10px 0;
          margin-bottom: 8px;
          cursor: pointer;
          transition: background 0.15s;
        }}
        .milestone-box:hover {{
          background: #f0fdfa;
        }}
      </style>
    </head>
    <body>
      <!-- 1. Top 4 Summary Cards -->
      <div class="top-grid">
        <div class="metric-card">
          <div style="font-size:12px;color:#64748b;font-weight:600;">선택일 평균 통증 (VAS)</div>
          <div style="display:flex;align-items:baseline;gap:4px;margin-top:4px;">
            <span style="font-size:24px;font-weight:800;color:#0f172a;">{avg_pain}</span>
            <span style="font-size:12px;color:#94a3b8;">/ 10점</span>
          </div>
          <div style="margin-top:4px;">{diff_html}</div>
        </div>

        <div class="metric-card">
          <div style="font-size:12px;color:#64748b;font-weight:600;">수면 만족도 & 요추</div>
          <div style="font-size:17px;font-weight:800;color:#f59e0b;margin-top:5px;">{stars} ({s['score']}점)</div>
          <div style="font-size:11px;color:#e11d48;font-weight:600;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">요추: {s['posture']}</div>
        </div>

        <div class="metric-card">
          <div style="font-size:12px;color:#64748b;font-weight:600;">좌식 시간 / 야간 각성</div>
          <div style="font-size:21px;font-weight:800;color:#0f172a;margin-top:4px;">{s['sittingHours']}시간 좌식</div>
          <div style="font-size:12px;color:#64748b;margin-top:4px;">야간 각성 {s['wakeUpCount']}회</div>
        </div>

        <div class="metric-card" style="border-color:#99f6e4;background:#f0fdfa;">
          <div style="font-size:12px;color:#0f766e;font-weight:700;">오늘의 개인 운동 달성</div>
          <div style="display:flex;align-items:baseline;gap:6px;margin-top:4px;">
            <span style="font-size:21px;font-weight:800;color:#115e59;">{done_cnt}/{total_cnt}</span>
            <span style="font-size:12px;font-weight:700;color:#0d9488;">({pct}%)</span>
          </div>
          <div style="width:100%;height:6px;background:#ccfbf1;border-radius:999px;margin-top:7px;overflow:hidden;">
            <div style="width:{pct}%;height:100%;background:#0d9488;"></div>
          </div>
        </div>
      </div>

      <!-- 2. NEW: 날짜별 6대 부위 통증지수 추이 & 특이점(Milestone) 통합 분석 그래프 -->
      <div class="main-card" style="border:1.5px solid #0d9488;">
        <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;">
          <div>
            <div style="display:flex;align-items:center;gap:6px;">
              <span style="background:#0d9488;color:#fff;font-size:11px;font-weight:800;padding:2px 8px;border-radius:999px;">핵심 개선 추이</span>
              <span style="font-size:15px;font-weight:800;color:#0f172a;">📉 날짜별 6대 부위 통증지수(VAS) 추이 & 특이점 그래프</span>
            </div>
            <div style="font-size:12px;color:#64748b;margin-top:3px;">
              아래 부위 버튼을 클릭하면 해당 부위의 날짜별 통증 궤적과 동작 특이점을 단독 하이라이트합니다 · 그래프의 날짜 점을 클릭해 상세 특이점을 확인하세요.
            </div>
          </div>
        </div>

        <!-- Part Filter Buttons -->
        <div id="partFilterBar" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;"></div>

        <!-- Interactive SVG Line Chart Container -->
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:12px 10px 8px 10px;">
          <svg id="multiLineSvg" viewBox="0 0 680 250" style="width:100%;height:auto;overflow:visible;"></svg>
        </div>

        <!-- Interactive Selected Date / Part Special Note (특이점) Callout Banner -->
        <div id="chartPointDetailBox" style="margin-top:10px;padding:11px 14px;border-radius:12px;background:#f0fdfa;border:1px solid #99f6e4;font-size:12.5px;color:#134e4a;line-height:1.55;"></div>

        <!-- Date x 6 Parts Heatmap Table + Net Improvement Summary -->
        <div style="overflow-x:auto;margin-top:12px;">
          <table class="matrix-table" id="painMatrixTable"></table>
        </div>

        <!-- Date-by-Date Key Milestones & Special Notes Timeline -->
        <div style="margin-top:14px;">
          <div style="font-size:13px;font-weight:800;color:#0f172a;margin-bottom:8px;">📌 날짜별 핵심 특이점 (수면 · 좌식 · 부위별 유발 동작 · 컨디션 타임라인)</div>
          <div id="milestoneTimelineContainer"></div>
        </div>
      </div>

      <!-- 3. 6대 집중 관리 부위 밸런스 맵 (SVG Body Heatmap) -->
      <div class="main-card">
        <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;margin-bottom:12px;">
          <div>
            <div style="font-size:15px;font-weight:800;color:#0f172a;">🧍 6대 집중 관리 부위 밸런스 맵 (전면 기준 · {current_log['date']})</div>
            <div style="font-size:12px;color:#64748b;margin-top:2px;">점선은 좌고관절 ↔ 우무릎 / 우손목 ↔ 좌어깨 대각선 교차 보상 사슬을 나타냅니다</div>
          </div>
          <div style="display:flex;gap:6px;font-size:11px;font-weight:700;">
            <span style="padding:2px 8px;border-radius:6px;background:#dcfce7;color:#166534;border:1px solid #86efac;">0~3 양호</span>
            <span style="padding:2px 8px;border-radius:6px;background:#fef3c7;color:#92400e;border:1px solid #fde68a;">4~6 주의</span>
            <span style="padding:2px 8px;border-radius:6px;background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;">7~10 경고</span>
          </div>
        </div>

        <div class="body-layout">
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:10px;display:flex;flex-direction:column;align-items:center;">
            <div style="width:100%;display:flex;justify-content:space-between;font-size:11px;font-weight:700;color:#94a3b8;margin-bottom:2px;">
              <span>환자 우측 (R)</span>
              <span>환자 좌측 (L)</span>
            </div>
            <svg viewBox="0 0 220 310" width="185" height="255">
              <circle cx="110" cy="32" r="19" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="102" y="51" width="16" height="16" rx="4" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <path d="M75 67 H145 L138 162 H82 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="53" y="69" width="18" height="86" rx="8" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="149" y="69" width="18" height="86" rx="8" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="82" y="162" width="24" height="122" rx="9" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
              <rect x="114" y="162" width="24" height="122" rx="9" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>

              <line x1="128" y1="170" x2="94" y2="228" stroke="#e11d48" stroke-width="2" stroke-dasharray="4 3" />
              <line x1="62" y1="152" x2="146" y2="80" stroke="#d97706" stroke-width="1.8" stroke-dasharray="3 3" />

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
            <div style="font-size:11px;color:#64748b;text-align:center;margin-top:2px;">
              좌고관절({p['leftHip']['score']}) ↔ 우무릎({p['rightKnee']['score']})<br/>우손목({p['rightWrist']['score']}) ↔ 좌어깨({p['leftAnteriorShoulder']['score']})
            </div>
          </div>

          <div class="parts-grid">
            {cards_html}
          </div>
        </div>
      </div>

      <script>
        const ALL_LOGS = {logs_json};
        const PART_META = {meta_json};
        let selectedPartFilter = 'ALL'; // 'ALL' or part.key
        let focusedDateIdx = ALL_LOGS.findIndex(l => l.date === '{selected_date_str}');
        if (focusedDateIdx < 0) focusedDateIdx = ALL_LOGS.length - 1;

        function getCellStyle(sc) {{
          if (sc <= 3) return 'background:#dcfce7;color:#166534;font-weight:800;';
          if (sc <= 6) return 'background:#fef3c7;color:#92400e;font-weight:800;';
          return 'background:#fee2e2;color:#991b1b;font-weight:800;';
        }}

        function summarizeSpecialMilestone(log, idx) {{
          const p = log.parts;
          const s = log.sleep;
          const avg = (PART_META.reduce((acc, m) => acc + p[m.key].score, 0) / PART_META.length).toFixed(1);
          const zeroParts = PART_META.filter(m => p[m.key].score === 0).map(m => m.short);
          const highParts = PART_META.filter(m => p[m.key].score >= 5).map(m => `${{m.short}}(${{p[m.key].score}})`);

          let tag = '';
          if (idx === 0) tag = '🚨 초기 급성기 기준점';
          else if (zeroParts.length > 0 && s.score >= 4) tag = `✨ ${{zeroParts.join('·')}} 통증 0점 소실 & 최저치 달성`;
          else if (s.sittingHours === 0 && s.score <= 3) tag = '⚠️ 휴일 조기 각성(수면 부족)에 따른 아침 강직 반응';
          else if (avg <= 2.5) tag = '🌿 5대 재활 루틴 정착 및 안정화 진입';
          else tag = '📉 베개·모니터 교정 후 통증 하향세';

          return {{
            avg,
            tag,
            condNote: log.patientWorkoutNote || '-',
            sleepInfo: `수면 ★${{s.score}}점 (${{s.posture}}) · 좌식 ${{s.sittingHours}}h`,
            partNotes: PART_META.map(m => `<strong>${{m.short}}(${{p[m.key].score}}점):</strong> ${{p[m.key].note || '-'}}`).join(' | ')
          }};
        }}

        function setPartFilter(key) {{
          selectedPartFilter = key;
          renderTrendSection();
        }}

        function setFocusedDate(idx) {{
          focusedDateIdx = idx;
          renderTrendSection();
        }}

        function renderTrendSection() {{
          // 1. Render Filter Bar
          const filterBar = document.getElementById('partFilterBar');
          let btnsHtml = `<button class="filter-btn ${{selectedPartFilter === 'ALL' ? 'active' : ''}}" onclick="setPartFilter('ALL')">📊 6대 부위 전체 추이</button>`;
          PART_META.forEach(m => {{
            const isAct = selectedPartFilter === m.key;
            const style = isAct
              ? `background:${{m.color}};color:#fff;border-color:${{m.color}};`
              : `border-left:4px solid ${{m.color}};`;
            btnsHtml += `<button class="filter-btn" style="${{style}}" onclick="setPartFilter('${{m.key}}')">${{m.short}}</button>`;
          }});
          filterBar.innerHTML = btnsHtml;

          // 2. Render SVG Multi-Line Chart + Special Event Markers
          const svg = document.getElementById('multiLineSvg');
          const W = 680, H = 250;
          const padL = 42, padR = 28, padT = 26, padB = 42;
          const plotW = W - padL - padR;
          const plotH = H - padT - padB;
          const n = ALL_LOGS.length;

          const xPos = (i) => n === 1 ? padL + plotW / 2 : padL + (i * plotW) / (n - 1);
          const yPos = (val) => padT + plotH - (Math.min(10, Math.max(0, val)) / 10) * plotH;

          let svgContent = '';

          // Y-axis grid lines & labels (0, 2, 4, 6, 8, 10)
          [0, 2, 4, 6, 8, 10].forEach(v => {{
            const y = yPos(v);
            const isSafeZone = v === 3;
            svgContent += `<line x1="${{padL}}" y1="${{y}}" x2="${{W - padR}}" y2="${{y}}" stroke="${{v === 0 ? '#94a3b8' : '#e2e8f0'}}" stroke-width="1" stroke-dasharray="${{v === 0 ? '' : '3 3'}}"/>`;
            svgContent += `<text x="${{padL - 8}}" y="${{y + 4}}" text-anchor="end" font-size="10" fill="#64748b" font-weight="600">${{v}}</text>`;
          }});

          // Highlight Focused Date Vertical Column
          const fx = xPos(focusedDateIdx);
          svgContent += `<line x1="${{fx}}" y1="${{padT - 8}}" x2="${{fx}}" y2="${{H - padB}}" stroke="#0d9488" stroke-width="1.5" stroke-dasharray="4 2"/>`;

          // X-axis date labels + Milestone Pin Icons
          ALL_LOGS.forEach((log, i) => {{
            const x = xPos(i);
            const isSel = i === focusedDateIdx;
            const ms = summarizeSpecialMilestone(log, i);
            svgContent += `
              <g style="cursor:pointer;" onclick="setFocusedDate(${{i}})">
                <rect x="${{x - 28}}" y="${{H - padB + 6}}" width="56" height="22" rx="6" fill="${{isSel ? '#0f766e' : '#f1f5f9'}}" />
                <text x="${{x}}" y="${{H - padB + 21}}" text-anchor="middle" font-size="11" font-weight="800" fill="${{isSel ? '#ffffff' : '#334155'}}">${{log.date.slice(5)}}</text>
                <text x="${{x}}" y="${{padT - 10}}" text-anchor="middle" font-size="10" font-weight="800" fill="${{isSel ? '#0f766e' : '#64748b'}}">📌평균 ${{ms.avg}}</text>
              </g>
            `;
          }});

          // Plot lines for each part
          PART_META.forEach((m, mIdx) => {{
            const isHighlighted = selectedPartFilter === 'ALL' || selectedPartFilter === m.key;
            const opacity = isHighlighted ? '1' : '0.14';
            const strokeW = selectedPartFilter === m.key ? '3.5' : '2.2';

            // Slight vertical offset only when ALL is selected and points overlap
            const offset = selectedPartFilter === 'ALL' ? (mIdx - 2.5) * 1.1 : 0;

            const pts = ALL_LOGS.map((l, i) => `${{xPos(i)}},${{yPos(l.parts[m.key].score) + offset}}`).join(' ');
            svgContent += `<polyline fill="none" stroke="${{m.color}}" stroke-width="${{strokeW}}" opacity="${{opacity}}" points="${{pts}}" stroke-linecap="round" stroke-linejoin="round"/>`;

            ALL_LOGS.forEach((l, i) => {{
              const sc = l.parts[m.key].score;
              const cx = xPos(i);
              const cy = yPos(sc) + offset;
              const r = (selectedPartFilter === m.key || i === focusedDateIdx) ? 5.5 : 4;
              svgContent += `
                <g style="cursor:pointer;" opacity="${{opacity}}" onclick="setFocusedDate(${{i}})">
                  <circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="${{m.color}}" stroke="#ffffff" stroke-width="1.5">
                    <title>${{l.date}} ${{m.short}}: ${{sc}}점 (${{l.parts[m.key].note || '-'}})</title>
                  </circle>
                  ${{selectedPartFilter === m.key ? `<text x="${{cx}}" y="${{cy - 9}}" text-anchor="middle" font-size="11" font-weight="800" fill="${{m.color}}">${{sc}}점</text>` : ''}}
                </g>
              `;
            }});
          }});

          svg.innerHTML = svgContent;

          // 3. Render Selected Date / Part Special Note Banner
          const fLog = ALL_LOGS[focusedDateIdx];
          const fMs = summarizeSpecialMilestone(fLog, focusedDateIdx);
          const detailBox = document.getElementById('chartPointDetailBox');

          if (selectedPartFilter === 'ALL') {{
            detailBox.innerHTML = `
              <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px;margin-bottom:4px;">
                <span style="font-weight:800;font-size:13px;color:#0f766e;">📌 [${{fLog.date}} 특이점 요약] ${{fMs.tag}} (평균 VAS ${{fMs.avg}}점)</span>
                <span style="font-size:11.5px;font-weight:700;color:#475569;">${{fMs.sleepInfo}}</span>
              </div>
              <div style="margin-bottom:4px;"><strong>• 컨디션 특이점:</strong> ${{fMs.condNote}}</div>
              <div style="font-size:11.5px;color:#334155;">• ${{fMs.partNotes}}</div>
            `;
          }} else {{
            const pm = PART_META.find(m => m.key === selectedPartFilter);
            const firstSc = ALL_LOGS[0].parts[pm.key].score;
            const currSc = fLog.parts[pm.key].score;
            const netDiff = currSc - firstSc;
            const netTxt = netDiff < 0 ? `첫날 대비 ▼ ${{Math.abs(netDiff)}}점 개선` : (netDiff > 0 ? `첫날 대비 ▲ +${{netDiff}}점` : '첫날과 동일');
            detailBox.innerHTML = `
              <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px;margin-bottom:4px;">
                <span style="font-weight:800;font-size:13.5px;color:${{pm.color}};">🎯 [${{pm.name}} 집중 추이] ${{fLog.date}} 기준 VAS ${{currSc}}점 (${{netTxt}})</span>
                <span style="font-size:11.5px;font-weight:700;color:#475569;">${{fMs.sleepInfo}}</span>
              </div>
              <div><strong>• ${{fLog.date}} 부위 특이점 메모:</strong> ${{fLog.parts[pm.key].note || pm.desc}}</div>
              <div style="margin-top:2px;"><strong>• 당일 컨디션 메모:</strong> ${{fMs.condNote}}</div>
            `;
          }}

          // 4. Render Matrix Table (Date x Parts + Total Improvement)
          const tbl = document.getElementById('painMatrixTable');
          let ths = `<tr><th style="text-align:left;padding-left:10px;">부위명</th>`;
          ALL_LOGS.forEach((l, i) => {{
            const isSel = i === focusedDateIdx;
            ths += `<th style="cursor:pointer;${{isSel ? 'background:#ccfbf1;color:#0f766e;' : ''}}" onclick="setFocusedDate(${{i}})">${{l.date.slice(5)}}</th>`;
          }});
          ths += `<th>첫날 대비 변화</th><th>주요 유발 동작 / 특이점</th></tr>`;

          let trs = '';
          PART_META.forEach(m => {{
            const firstSc = ALL_LOGS[0].parts[m.key].score;
            const latestSc = ALL_LOGS[ALL_LOGS.length - 1].parts[m.key].score;
            const diff = latestSc - firstSc;
            const diffBadge = diff < 0
              ? `<span style="color:#0d9488;font-weight:800;">▼ ${{diff}}점 호전</span>`
              : (diff > 0 ? `<span style="color:#e11d48;font-weight:800;">▲ +${{diff}}점</span>` : `<span style="color:#64748b;">유지</span>`);
            const latestNote = ALL_LOGS[focusedDateIdx].parts[m.key].note || m.desc;

            trs += `<tr onclick="setPartFilter('${{m.key}}')" style="cursor:pointer;">
              <td style="text-align:left;padding-left:10px;font-weight:700;white-space:nowrap;">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${{m.color}};margin-right:5px;"></span>${{m.short}}
              </td>`;
            ALL_LOGS.forEach((l, i) => {{
              const sc = l.parts[m.key].score;
              trs += `<td style="${{getCellStyle(sc)}}">${{sc}}점</td>`;
            }});
            trs += `<td>${{diffBadge}}</td><td style="text-align:left;padding-left:8px;color:#475569;">${{latestNote}}</td></tr>`;
          }});
          tbl.innerHTML = ths + trs;

          // 5. Render Milestone Timeline Cards
          const tlContainer = document.getElementById('milestoneTimelineContainer');
          tlContainer.innerHTML = ALL_LOGS.slice().reverse().map((l, revIdx) => {{
            const origIdx = ALL_LOGS.length - 1 - revIdx;
            const ms = summarizeSpecialMilestone(l, origIdx);
            const isSel = origIdx === focusedDateIdx;
            return `
              <div class="milestone-box" style="${{isSel ? 'border-left-width:5px;background:#f0fdfa;' : ''}}" onclick="setFocusedDate(${{origIdx}})">
                <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:4px;">
                  <span style="font-size:12.5px;font-weight:800;color:#0f172a;">📅 ${{l.date}} — ${{ms.tag}}</span>
                  <span style="font-size:11px;font-weight:700;color:#0f766e;">평균 통증 ${{ms.avg}}점 · ${{ms.sleepInfo}}</span>
                </div>
                <div style="font-size:12px;color:#334155;margin-top:3px;">
                  <strong>특이점 메모:</strong> ${{ms.condNote}}
                </div>
              </div>
            `;
          }}).join('');
        }}

        renderTrendSection();
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=1220, scrolling=True)


def render_specialist_clinical_tab(current_log):
    p = current_log["parts"]
    s = current_log["sleep"]
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    total_cnt = len(workouts)

    sorted_parts = sorted(
        [{"name": m["name"], "score": p[m["key"]]["score"], "note": p[m["key"]]["note"]} for m in PART_META],
        key=lambda x: x["score"],
        reverse=True,
    )
    worst = sorted_parts[0]

    clinical_html = f"""
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
          background: transparent;
        }}
        .hero-banner {{
          background: linear-gradient(135deg, #134e4a 0%, #0f172a 100%);
          color: #ffffff;
          padding: 20px;
          border-radius: 16px;
          margin-bottom: 14px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}
        .step-card {{
          background: #ffffff;
          border: 1px solid #e2e8f0;
          border-radius: 14px;
          padding: 16px 18px;
          margin-bottom: 12px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .step-header {{
          display: flex;
          align-items: center;
          justify-content: space-between;
          border-bottom: 1px solid #f1f5f9;
          padding-bottom: 10px;
          margin-bottom: 10px;
        }}
        .step-title {{
          font-size: 15px;
          font-weight: 800;
          color: #0f766e;
        }}
        .step-badge {{
          font-size: 11px;
          font-weight: 700;
          padding: 3px 10px;
          border-radius: 999px;
          background: #f0fdfa;
          color: #0f766e;
          border: 1px solid #99f6e4;
        }}
        .step-body {{
          font-size: 13.5px;
          line-height: 1.68;
          color: #334155;
        }}
        .step-body ul {{
          margin: 8px 0 0 0;
          padding-left: 18px;
        }}
        .step-body li {{
          margin-bottom: 7px;
        }}
      </style>
    </head>
    <body>
      <div class="hero-banner">
        <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px;">
          <span style="background:#fbbf24;color:#0f172a;font-size:11px;font-weight:800;padding:3px 10px;border-radius:999px;">50년 임상 · 세계 1위 권위자</span>
          <span style="font-size:12px;color:#99f6e4;font-weight:600;">가정의학과 · 정형외과 · 신경외과 전문의 / 물리·도수치료학 박사 황원택</span>
        </div>
        <div style="font-size:17px;font-weight:800;margin-bottom:6px;">🩺 황원택 원장의 4단 융합 임상 진료실 ({current_log['date']} 맞춤 처방)</div>
        <div style="font-size:13px;color:#e2e8f0;line-height:1.6;">
          "안녕하세요. 50년 동안 수많은 환자분들의 아픔을 다정하게 살피고 완치의 길을 열어온 황원택 원장이에요. 우리 환자분, <strong>만 31세에 189cm, 93kg</strong>이라는 듬직한 체격으로 장시간 좌식 근무를 견디시느라 몸이 많이 고단하셨지요? 단순히 교과서적인 이론에만 가두지 않고, 초음파·신경치료·도수치료를 융합해 수많은 난치성 통증을 완치시켰던 실전 노하우를 오늘 기록하신 수치에 맞춰 차분히 풀어드릴게요."
        </div>
      </div>

      <!-- 1. 공감 및 문진 -->
      <div class="step-card">
        <div class="step-header">
          <span class="step-title">1. 공감 및 문진 (Empathy & Clinical Inquiry)</span>
          <span class="step-badge">다정한 맞춤 문진</span>
        </div>
        <div class="step-body">
          189cm의 큰 키와 93kg의 체격은 일반적인 사무실 책상·의자 규격보다 지렛대 길이가 길어, 앉아 계실 때 요추와 골반이 감당해야 하는 물리적 압박이 남들보다 1.5배 이상 크답니다. 오늘 기록을 보니 <strong>{worst['name']}({worst['score']}점 · {worst['note']})</strong> 증상이 가장 신경 쓰이셨을 텐데, 개인 운동을 <strong>{total_cnt}개 중 {done_cnt}개</strong>나 성실히 해내신 점이 정말 대견해요. 보다 정밀한 치료 방향 설정을 위해 몇 가지만 먼저 여쭤볼게요.
          <ul>
            <li><strong>수면 중 허리(요추) 및 기상 컨디션 ({s['posture']} / 수면 {s['score']}점):</strong> 아침에 눈을 뜨셨을 때({current_log.get('patientWorkoutNote') or '기상 직후'}) 허리 뻐근함 때문에 잠에서 깨어나신 건가요, 아니면 뒤척이는 순간 골반 위쪽이 찌릿하셨나요?</li>
            <li><strong>고관절 회전과 무릎의 연계 반응:</strong> <strong>왼쪽 고관절({p['leftHip']['score']}점 · {p['leftHip']['note']})</strong>이 크게 돌아갈 때 사타구니 안쪽에서 걸리는 느낌이나 '뚝' 소리가 나면서, 스쿼트 시 <strong>오른쪽 무릎({p['rightKnee']['score']}점)</strong>으로 체중이 쏠리진 않으시나요?</li>
            <li><strong>측면 지지 및 상체 기울기:</strong> <strong>왼쪽 전면 어깨({p['leftAnteriorShoulder']['score']}점 · {p['leftAnteriorShoulder']['note']})</strong>의 불편감이 사이드 버티기 운동을 할 때나 책상에서 왼쪽 팔걸이에 기대어 앉을 때 더 뚜렷해지나요?</li>
          </ul>
        </div>
      </div>

      <!-- 2. 원인 분석 -->
      <div class="step-card">
        <div class="step-header">
          <span class="step-title">2. 원인 분석 (교과서적 관점 + 50년 실전 임상 통합 분석)</span>
          <span class="step-badge">전신 근막·신경 사슬</span>
        </div>
        <div class="step-body">
          여섯 부위의 통증이 따로따로 나타나는 것처럼 보이지만, 제 50년 임상 눈으로 보면 이는 <strong>'장시간 좌식으로 인한 전신 나선형(Spiral) 교차 보상 증후군'</strong>이라는 하나의 밧줄로 엮여 있어요.
          <ul>
            <li><strong>① 좌측 고관절({p['leftHip']['score']}점) ↔ 허리 요추({p['lumbar']['score']}점) ↔ 우측 무릎({p['rightKnee']['score']}점)의 삼각 사슬:</strong> 우리 몸을 텐트에 비유해 볼게요. 오래 앉아 있으면 요추 뼈에서 골반 앞쪽을 지나 허벅지 안쪽으로 붙는 굵은 밧줄인 <strong>'장요근(Iliopsoas)'</strong>이 짧게 줄어듭니다. 밤에 누워 다리를 펴거나 뒤척일 때 이 짧아진 왼쪽 장요근이 요추를 앞·아래로 강하게 잡아당기니 수면 중 허리가 불편하고 아침 강직이 남는 거예요. 게다가 왼쪽 고관절 앞쪽 관절낭이 팽팽해져 회전 공간이 좁아지니 <strong>고관절이 심하게 회전될 때 집힘(FAI 유사 자극)</strong>이 생기고, 스쿼트를 할 때는 잠긴 왼쪽 고관절 대신 반대편 기둥인 <strong>오른쪽 무릎</strong>이 93kg의 하중을 대신 받으며 통증이 나타나는 거랍니다.</li>
            <li><strong>② 일자목({p['cervical']['score']}점) ↔ 좌측 전면 어깨({p['leftAnteriorShoulder']['score']}점) ↔ 우측 손목({p['rightWrist']['score']}점)의 신경·근막 사슬:</strong> 큰 키에 비해 모니터를 내려다보면 고개가 앞으로 빠지며(일자목) 목 옆 근육인 <strong>사각근</strong>이 팔로 내려가는 신경 다발(완신경총)을 누릅니다. 동시에 몸이 왼쪽으로 기울거나 사이드 플랭크로 버틸 때 날개뼈를 갈비뼈에 밀착시키는 <strong>전거근(Serratus Anterior)</strong>이 피로해지면, 위팔뼈 머리가 앞쪽으로 밀려나며 <strong>왼쪽 전면 어깨 힘줄</strong>을 찌르게 됩니다.</li>
          </ul>
        </div>
      </div>

      <!-- 3. 대처 방안 -->
      <div class="step-card">
        <div class="step-header">
          <span class="step-title">3. 대처 방안 (안전한 홈케어 · 권장 진료과 · 50년 완치 비법)</span>
          <span class="step-badge">초음파·신경·도수 융합</span>
        </div>
        <div class="step-body">
          단순히 아픈 곳에만 파스를 붙이는 것은 하류에서 흙탕물만 퍼내는 것과 같아요. 실제 완치 사례에서 가장 효과가 뛰어났던 <strong>3단계 융합 해법</strong>을 알려드릴게요.
          <ul>
            <li><strong>집에서 바로 하는 아침·야간 응급조치:</strong> 주무실 때 <strong>무릎 오금 아래에 조금 높은 베개</strong>를 받쳐 장요근의 팽팽한 장력을 풀어주세요. 특히 일요일처럼 아침 일찍 잠이 깨어 허리가 뻐근한 날에는 바로 일어나지 마시고, 누운 채로 양 무릎을 세워 좌우로 살살 흔들어주는 <strong>침대 위 윈드실드 와이퍼(2분)</strong>로 요추 후관절에 윤활액을 먼저 공급해 주세요.</li>
            <li><strong>권장 진료과 및 정밀 융합 치료 안내:</strong> 특정 동작 통증이 지속될 때는 <strong>정형외과·신경외과·재활의학과</strong>를 방문하셔서 고해상도 <strong>초음파 진단(Ultrasound)</strong>을 받아보시는 것이 좋아요. 고관절 회전 시 집히는 장요근 건 주변과 왼쪽 앞어깨(상완이두근 장두건)의 미세 염증을 초음파로 직접 보면서, 유착된 신경과 근막을 생리식염수로 안전하게 분리하는 <strong>초음파 유도하 신경·근막 수액박리술(Hydrodissection)</strong>과 <strong>도수치료</strong>를 병행하면 회복이 놀라울 만큼 빨라집니다.</li>
            <li><strong>황원택 원장의 '틀을 깨는' 50년 실전 비법:</strong>
              <br/>• <strong>사이드로 누워 팔로 바닥 버티기(의자 다리 올리기) 하실 때:</strong> 왼쪽 어깨에 체중을 매달지 마시고, 바닥을 짚은 <strong>왼쪽 팔꿈치로 매트를 강하게 밀어내어 겨드랑이 아래 근육(전거근)을 천장 쪽으로 채워주세요.</strong> 날개뼈가 단단히 고정되면 왼쪽으로 몸이 기울 때 생기던 앞어깨 통증이 즉시 사라집니다.
              <br/>• <strong>다리 한쪽 올려 옆으로 돌리기 하실 때:</strong> 고관절에서 소리가 나거나 집히지 않도록 <strong>기존 원 크기의 60% 정도만 작은 원</strong>으로 부드럽게 돌리시고, 운동 전 <strong>왼쪽 배꼽 옆 깊은 곳(장요근)과 왼쪽 엉덩이 바깥쪽(중둔근)</strong>을 마사지볼로 먼저 풀어주시면 스쿼트 시 오른쪽 무릎 부담까지 한 번에 해결됩니다.</li>
          </ul>
        </div>
      </div>

      <!-- 4. 생활 수칙 -->
      <div class="step-card">
        <div class="step-header">
          <span class="step-title">4. 생활 수칙 (재발 방지를 위한 맞춤형 운동법 및 식습관)</span>
          <span class="step-badge">맞춤 운동 & 영양</span>
        </div>
        <div class="step-body">
          93kg의 탄탄한 근육과 체격을 평생 통증 없는 든든한 갑옷으로 만들려면 일상의 운동 순서와 식습관을 함께 챙기셔야 해요.
          <ul>
            <li><strong>개인 운동 5종 루틴의 황금 배치와 좌식 리셋:</strong> 지금 훌륭하게 수행 중이신 5가지 운동 중 <strong>① 무릎 꿇고 골반 하늘로 올리기(장요근 신전·둔근 수축)</strong>를 가장 먼저 실시해 골반 앞쪽을 열어주시고, <strong>② 16kg 어깨 슈러그</strong>를 하실 때는 고개가 앞으로 빠지지 않게 <strong>턱을 살짝 당긴(Chin-in) 상태</strong>에서 수행해 일자목 긴장을 예방하세요. 주중 근무 시에는 <strong>50분 좌식 후 3분 기립 스트레칭</strong> 원칙을 꼭 지켜주세요.</li>
            <li><strong>깊은 수면과 디스크·근막 회복을 돕는 맞춤 식습관:</strong> 척추 디스크(추간판) 수핵과 근막은 수분이 부족하면 스펀지가 마르듯 탄력을 잃어 아침 강직이 심해집니다. 기상 직후 <strong>미온수 한 잔(300ml)</strong>을 포함해 하루 <strong>2L 이상의 수분</strong>을 섭취해 주세요. 또한 일요일 조기 각성을 줄이고 야간 근육 경직과 신경 미세 염증을 가라앉히기 위해, 저녁 식사에 <strong>오메가-3가 풍부한 등푸른생선(고등어·연어)</strong>과 천연 근육·신경 이완제 역할을 하는 <strong>마그네슘·트립토판이 풍부한 식단(구운 아몬드, 호박씨, 시금치, 바나나, 두부)</strong>을 곁들이시면 수면 만족도가 5점으로 올라가며 아침 허리가 한결 가벼워질 거예요.</li>
          </ul>
        </div>
      </div>
    </body>
    </html>
    """
    components.html(clinical_html, height=1120, scrolling=True)


db = load_shared_db()

if "is_owner" not in st.session_state:
    st.session_state.is_owner = False
if "editing_workout_id" not in st.session_state:
    st.session_state.editing_workout_id = None

# --- HEADER & PERMISSION BAR ---
st.markdown("### 🩺 매일 튼튼 재활 일지 & 황원택 원장 통합 임상 케어")
st.caption("환자 프로필: 만 31세 남성 · 189cm · 93kg · 장시간 좌식 근무 | 실시간 동기화 지원")

col_role, col_pin = st.columns([3, 2])
with col_role:
    if st.session_state.is_owner:
        st.success("🔓 **현재 권한: 본인 모드** (일지 기록 및 개인 운동 추가·수정·삭제 가능)")
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
                {"id": f"w-{int(datetime.now().timestamp())}-{i}", "text": w["text"], "done": False}
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

# --- MAIN TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 종합 요약 (추이 그래프 & 바디맵)",
    f"✍️ 일지 기록 {'🔓' if is_owner else '🔒'}",
    "💬 원장님 소견 (OPEN)",
    "🩺 50년 임상 처방 (황원택 원장)",
])

with tab1:
    render_visual_body_dashboard(current_log, prev_log, db["logs"])

    workouts = current_log.get("workoutList", [])
    st.markdown("#### 🏋️ 오늘 수행한 개인 운동 요약")
    if not workouts:
        st.caption("등록된 개인 운동이 없습니다.")
    else:
        for w in workouts:
            status_icon = "✅" if w.get("done") else "⬜"
            st.write(f"{status_icon} {w['text']}")
    if current_log.get("patientWorkoutNote"):
        st.caption(f"📝 컨디션 메모: {current_log['patientWorkoutNote']}")

    st.markdown("#### 💬 담당 원장님 코멘트 요약")
    st.success(current_log["directorOpinion"].get("assessment") or "아직 작성된 원장님 소견이 없습니다.")

with tab2:
    if not is_owner:
        st.info("🔒 일지 기록과 개인 운동 관리는 **환자 본인 권한**에서만 수정할 수 있습니다. 상단에서 잠금을 해제해 주세요.")

    st.markdown("#### 🌙 수면 만족도 및 좌식 생활 기록")
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

    st.markdown("---")
    st.markdown("#### 📊 6대 부위별 통증 점수 (VAS 0~10) 및 메모")
    updated_parts = {}
    for m in PART_META:
        key = m["key"]
        item = current_log["parts"][key]
        c1, c2 = st.columns([1, 1])
        with c1:
            sc = st.slider(f"{m['name']} ({m['side']})", 0, 10, int(item["score"]), disabled=not is_owner, key=f"sl_{key}_{db['selectedDate']}")
        with c2:
            nt = st.text_input(f"{m['name']} 메모", value=item["note"], disabled=not is_owner, key=f"nt_{key}_{db['selectedDate']}")
        updated_parts[key] = {"score": sc, "note": nt}

    if is_owner:
        if st.button("💾 수면 및 6대 통증 기록 서버에 저장", type="primary", use_container_width=True):
            current_log["sleep"] = {
                "score": new_sleep_score,
                "posture": new_posture,
                "wakeUpCount": new_wake,
                "sittingHours": new_sit,
            }
            current_log["parts"] = updated_parts
            save_shared_db(db)
            st.toast("수면 및 통증 일지가 서버에 저장되어 즉시 공유되었습니다!")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🏋️ 오늘 수행한 개인 운동 및 컨디션 메모 (본인 작성)")
    st.caption("운동을 한 개씩 추가·수정·삭제하고 완료 체크(✓)로 관리하세요. 수정 즉시 서버에 반영됩니다.")

    add_c1, add_c2 = st.columns([4, 1])
    with add_c1:
        new_workout_txt = st.text_input(
            "새 개인 운동 1개 입력",
            placeholder="예: 런지 좌측 장요근 스트레칭 30초×4세트",
            disabled=not is_owner,
            label_visibility="collapsed",
            key=f"add_w_input_{db['selectedDate']}",
        )
    with add_c2:
        if st.button("+ 운동 추가", disabled=not is_owner, use_container_width=True):
            if new_workout_txt.strip():
                current_log.setdefault("workoutList", []).append({
                    "id": f"w-{int(datetime.now().timestamp()*1000)}",
                    "text": new_workout_txt.strip(),
                    "done": False,
                })
                save_shared_db(db)
                st.rerun()

    for idx, w in enumerate(list(current_log.get("workoutList", []))):
        wid = w["id"]
        if st.session_state.editing_workout_id == wid and is_owner:
            ec1, ec2, ec3 = st.columns([4, 1, 1])
            with ec1:
                edited_txt = st.text_input("운동 수정", value=w["text"], key=f"edit_in_{wid}", label_visibility="collapsed")
            with ec2:
                if st.button("저장", key=f"save_w_{wid}", use_container_width=True):
                    if edited_txt.strip():
                        w["text"] = edited_txt.strip()
                        st.session_state.editing_workout_id = None
                        save_shared_db(db)
                        st.rerun()
            with ec3:
                if st.button("취소", key=f"cancel_w_{wid}", use_container_width=True):
                    st.session_state.editing_workout_id = None
                    st.rerun()
        else:
            wc1, wc2, wc3 = st.columns([5, 1, 1])
            with wc1:
                checked = st.checkbox(
                    w["text"],
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

    new_cond_note = st.text_area(
        "📝 오늘의 컨디션 및 특이사항 메모",
        value=current_log.get("patientWorkoutNote", ""),
        disabled=not is_owner,
        key=f"cond_note_{db['selectedDate']}",
    )
    if is_owner and st.button("📝 컨디션 메모 저장", use_container_width=True):
        current_log["patientWorkoutNote"] = new_cond_note
        save_shared_db(db)
        st.toast("컨디션 메모가 저장되었습니다!")
        st.rerun()

with tab3:
    st.success("💬 **원장님 소견 보드 (전체 권한 개방 OPEN):** 별도 비밀번호 없이 언제든 작성·저장하실 수 있으며, 저장 즉시 환자분 화면에도 실시간 반영됩니다.")
    d_op = current_log["directorOpinion"]
    dc1, dc2 = st.columns(2)
    with dc1:
        d_name = st.text_input("담당 전문가 성함 / 직함", value=d_op.get("directorName", "황인준 PT 원장"))
    with dc2:
        d_target = st.text_input("오늘의 중점 교정 타겟", value=d_op.get("focusTarget", ""))

    d_inq = st.text_area("1. 추가 문진 및 체크 사항 (원장님 → 환자 질문)", value=d_op.get("inquiry", ""))
    d_ass = st.text_area("2. 체형·근막 평가 및 통증 원인 소견", value=d_op.get("assessment", ""))
    d_pre = st.text_area("3. 맞춤 재활 운동 처방 및 루틴 가이드", value=d_op.get("prescription", ""))

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

    st.markdown("#### 📋 카카오톡/문자 공유용 텍스트 복사용")
    p = current_log["parts"]
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))
    w_lines = "\n".join([f"  {'✅' if w.get('done') else '⬜'} {w['text']}" for w in workouts]) or "  - 등록된 개인 운동 없음"
    share_txt = (
        f"[매일 튼튼 재활 일지 & 원장님 소견 - {current_log['date']}]\n"
        f"👤 환자: 만 31세 남성 (189cm, 93kg, 좌식 {current_log['sleep']['sittingHours']}시간)\n"
        f"🌙 수면 만족도: {current_log['sleep']['score']}/5점 | 야간 각성: {current_log['sleep']['wakeUpCount']}회\n"
        f"🛏️ 수면 중 요추 상태: {current_log['sleep']['posture']}\n\n"
        f"📊 [6대 부위 통증 수치 (VAS 0~10)]\n"
        f"1. 허리(요추): {p['lumbar']['score']}점 ({p['lumbar']['note'] or '-'})\n"
        f"2. 왼쪽 고관절: {p['leftHip']['score']}점 ({p['leftHip']['note'] or '-'})\n"
        f"3. 왼쪽 전면 어깨: {p['leftAnteriorShoulder']['score']}점 ({p['leftAnteriorShoulder']['note'] or '-'})\n"
        f"4. 오른쪽 손목: {p['rightWrist']['score']}점 ({p['rightWrist']['note'] or '-'})\n"
        f"5. 오른쪽 무릎: {p['rightKnee']['score']}점 ({p['rightKnee']['note'] or '-'})\n"
        f"6. 목(일자목): {p['cervical']['score']}점 ({p['cervical']['note'] or '-'})\n\n"
        f"🏋️ [오늘 수행한 개인 운동 ({done_cnt}/{len(workouts)} 완료) 및 컨디션 메모]\n"
        f"{w_lines}\n"
        f"📝 메모: {current_log.get('patientWorkoutNote') or '기록 없음'}\n\n"
        f"💬 [{d_name} 소견 및 처방]\n"
        f"• 중점 타겟: {d_target or '-'}\n"
        f"• 문진 체크: {d_inq or '-'}\n"
        f"• 평가 소견: {d_ass or '-'}\n"
        f"• 운동 처방: {d_pre or '-'}"
    )
    st.code(share_txt, language="markdown")

with tab4:
    render_specialist_clinical_tab(current_log)
