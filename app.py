import json
import os
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(
    page_title="매일 튼튼 재활 일지 & 통합 임상 케어",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_FILE = "rehab_shared_data.json"

PART_META = [
    {"key": "lumbar", "name": "1. 허리 (요추 부위)", "side": "중앙 코어", "desc": "수면 시 불편감 및 좌식 디스크 하중"},
    {"key": "leftHip", "name": "2. 왼쪽 고관절", "side": "좌측 하체", "desc": "장요근 단축 및 골반 전면 집임"},
    {"key": "leftAnteriorShoulder", "name": "3. 왼쪽 전면 어깨", "side": "좌측 상체", "desc": "소흉근 단축 및 라운드 숄더"},
    {"key": "rightWrist", "name": "4. 오른쪽 손목", "side": "우측 상체", "desc": "마우스 과사용 및 신경 포착 주의"},
    {"key": "rightKnee", "name": "5. 오른쪽 무릎", "side": "우측 하체", "desc": "좌측 고관절 제한에 따른 대각선 과부하"},
    {"key": "cervical", "name": "6. 목 (일자목)", "side": "상부 코어", "desc": "모니터 높이에 따른 경추 전만 소실"},
]

DEFAULT_DATA = {
    "ownerPin": "0208",
    "selectedDate": "2026-11-13",
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
                "lumbar": {"score": 4, "note": "중간에 깨지 않고 숙면함, 아침 강직만 약간 있음"},
                "leftHip": {"score": 4, "note": "의자에서 일어날 때 펴지는 속도가 빨라짐"},
                "leftAnteriorShoulder": {"score": 3, "note": "어깨 앞쪽 말림이 줄어든 느낌"},
                "rightWrist": {"score": 3, "note": "손목 보호대 착용 및 겨드랑이·목 신경길 스트레칭 효과 좋음"},
                "rightKnee": {"score": 3, "note": "계단 내려갈 때 통증 거의 없음"},
                "cervical": {"score": 4, "note": "50분마다 알람 맞춰 일어나 기지개 켬"},
            },
            "workoutList": [
                {"id": "w-301", "text": "50분 좌식 후 3분 기립 스트레칭 루틴 실천", "done": True},
                {"id": "w-302", "text": "런지 좌측 장요근 및 문틀 좌측 소흉근 이완 4세트", "done": True},
                {"id": "w-303", "text": "글루트 브릿지 둔근 활성화 15회×3세트", "done": False},
            ],
            "patientWorkoutNote": "낮 동안 50:3 루틴과 장요근·소흉근 이완 완료, 저녁에 브릿지 추가 예정",
            "directorOpinion": {
                "directorName": "황인준 PT 원장",
                "focusTarget": "둔근(엉덩이 근육) 활성화 및 코어 안정화 진입",
                "inquiry": "오늘 PT 수업 전 브릿지 동작 시 허리가 먼저 쓰이는지, 엉덩이에 힘이 잘 들어오는지 체크해 볼게요!",
                "assessment": "수면 만족도가 4점으로 올라오면서 전신 근막 긴장도가 눈에 띄게 떨어졌습니다. 좌고관절-우무릎 대각선 사슬이 안정화 단계에 진입했습니다.",
                "prescription": "통증이 3~4점대로 안정되었으므로, 오늘부터는 이완 후 글루트 브릿지(15회×3세트)와 버드독 코어 안정화 운동을 본 운동에 추가합니다.",
            },
        },
    ],
}


def load_shared_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=2)
    return json.loads(json.dumps(DEFAULT_DATA))


def save_shared_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


db = load_shared_db()

if "is_owner" not in st.session_state:
    st.session_state.is_owner = False
if "editing_workout_id" not in st.session_state:
    st.session_state.editing_workout_id = None

# --- HEADER & PERMISSION BAR ---
st.markdown("### 🩺 매일 튼튼 재활 일지 & 통합 임상 케어 (실시간 공유 서버)")
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
        pin_input = st.text_input("🔒 본인 잠금 해제 PIN (기본 0208)", type="password", key="pin_box")
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

current_log = next((l for l in db["logs"] if l["date"] == db["selectedDate"]), db["logs"][-1])
is_owner = st.session_state.is_owner

# --- MAIN TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 종합 요약",
    f"✍️ 일지 기록 {'🔓' if is_owner else '🔒'}",
    "💬 원장님 소견 (OPEN)",
    "🩺 50년 임상 처방 (참조)",
])

with tab1:
    scores = [current_log["parts"][m["key"]]["score"] for m in PART_META]
    avg_pain = round(sum(scores) / len(scores), 1)
    workouts = current_log.get("workoutList", [])
    done_cnt = sum(1 for w in workouts if w.get("done"))

    m1, m2, m3 = st.columns(3)
    m1.metric("선택일 평균 통증 (VAS)", f"{avg_pain} / 10점")
    m2.metric("수면 만족도", "★" * current_log["sleep"]["score"] + f" ({current_log['sleep']['score']}/5)")
    m3.metric("좌식 시간 / 개인 운동", f"{current_log['sleep']['sittingHours']}시간", f"운동 {done_cnt}/{len(workouts)} 완료")

    st.markdown("#### 6대 집중 관리 부위 현황")
    p_cols = st.columns(2)
    for idx, m in enumerate(PART_META):
        p_data = current_log["parts"][m["key"]]
        note_text = p_data["note"] or m["desc"]
        with p_cols[idx % 2]:
            st.info(f"**{m['name']}**: VAS **{p_data['score']}점**  \n- {note_text}")

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
        st.info("🔒 일지 기록과 개인 운동 관리는 **환자 본인 권한(PIN 0208)**에서만 수정할 수 있습니다. 상단에서 잠금을 해제해 주세요.")

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

    # 운동 1개 추가 바
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

    # 개별 운동 리스트 (체크 / 수정 / 삭제)
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

    # 컨디션 메모
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
    st.markdown("#### 🩺 50년 임상 권위자 황원택 원장의 4단 융합 임상 처방전 (참조용)")
    st.markdown(
        "- **1단계 · 공감 및 맞춤 문진:** 189cm, 93kg의 건장한 체격으로 장시간 좌식 근무를 하시느라 척추와 관절의 지렛대 하중이 매우 큰 상태입니다. 수면 중 다리를 쭉 펴실 때 요추가 들뜨는지, 기립 시 왼쪽 고관절이 뻣뻣해 오른쪽 무릎에 체중을 싣는지 확인해 보세요.\n"
        "- **2단계 · 원인 분석 (전신 나선형 교차 보상 증후군):** 좌식으로 인해 단축된 **왼쪽 장요근**이 수면 시 요추를 잡아당겨 야간 허리 불편감을 만들고, 보행 시 충격이 반대편 **오른쪽 무릎**으로 쏠립니다. 상체에서는 낮은 모니터로 인한 **일자목(사각근 긴장)**이 팔 신경을 압박해 **오른쪽 손목**과 **왼쪽 전면 어깨(소흉근 단축)**의 비대칭 통증을 유발합니다.\n"
        "- **3단계 · 대처 방안:** 취침 시 무릎 오금 아래에 높은 베개를 받쳐 장요근 긴장을 즉시 완화하세요. 오른쪽 손목 통증 시 상류 신경 통로인 오른쪽 목 옆(사각근)·겨드랑이를 먼저 풀어주고, 오른쪽 무릎 통증 시 반대쪽 왼쪽 장요근·중둔근을 이완하는 것이 50년 실전 비법입니다.\n"
        "- **4단계 · 생활 수칙:** 개인 운동 목록에 **런지 좌측 장요근 이완, 문틀 좌측 소흉근 스트레칭, 우측 정중신경 글라이딩**을 등록해 매일 체크하시고, 하루 2L 미온수 섭취와 오메가-3·마그네슘이 풍부한 식단을 병행하세요."
    )
