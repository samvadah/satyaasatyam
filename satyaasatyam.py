import streamlit as st
import random
import json
import os
import uuid
import time

# --- 1. CONFIGURATION & CONSTANTS ---
GAME_DIR = "gamerooms"
POINTS_POOL = 12
BASE_URL = "https://satyaasatyam.streamlit.app"
AUTO_REFRESH_SECONDS = 15
WRITING_TIME_LIMIT = 180  # 3 minutes
GUESSING_TIME_LIMIT = 120 # 2 minutes

# --- 2. LANGUAGE & CONTENT ---
def to_devanagari(num_str):
    return "".join("०१२३४५६७८९"[int(d)] for d in str(num_str))

VARNA_DETAILS = {
    "Brahmin": {"sa": {"name": "ब्राह्मणः"}, "en": {"name": "Brahmin"}},
    "Kshatriya": {"sa": {"name": "क्षत्रियः"}, "en": {"name": "Kshatriya"}},
    "Vaishya": {"sa": {"name": "वैश्यः"}, "en": {"name": "Vaishya"}},
    "Shudra": {"sa": {"name": "शूद्रः"}, "en": {"name": "Shudra"}},
}
VARNA_KEYS = list(VARNA_DETAILS.keys())

SENTENCE_PROMPTS = {
    "Brahmin": ["truth_1", "truth_2", "truth_3"],
    "Kshatriya": ["truth_1", "truth_2", "false_3"],
    "Vaishya": ["truth_1", "false_2", "false_3"],
    "Shudra": ["false_1", "false_2", "false_3"]
}

TRANSLATIONS = {
    "sa": {
        "lang_select": "भाषा",
        "game_title": "सत्यासत्यम्",
        "welcome_intro": "सुस्वागतम्। इयं चतुर्णां क्रीडकानां सत्यासत्यपरीक्षा क्रीडा॥ अत्र एको ब्राह्मणः सर्वसत्यवादी क्षत्रिय एकानृतवादी वैश्य एकसत्यवादी शूद्रश्च सर्वानृतवादी भविष्यति। सर्वेषां वर्णानां सम्यगनुमानमेव तव लक्ष्यम्॥",
        "create_game_button": "✨ नवीनं क्रीडासत्रं रचया",
        "require_names": "नामकरणम् अनिवार्यम्",
        "enter_name_label": "तव नामाङ्कनं कुरु",
        "error_name_required": "अनिवार्यत्वात् कृपया स्वनाम प्रविशतु।",
        "error_name_taken": "इदं नाम पूर्वमेव स्वीकृतम्। अन्यत् चिनु।",
        "join_as": "इति प्रविश",
        "player": "क्रीडकः",
        "waiting_for_players": "अन्येषाम् आगमनं प्रतीक्षस्व",
        "truth_1": "प्रथमं सत्यं वाक्यम्", "truth_2": "द्वितीयं सत्यं वाक्यम्", "truth_3": "तृतीयं सत्यं वाक्यम्",
        "false_1": "प्रथमम् असत्यं वाक्यम्", "false_2": "द्वितीयम् असत्यं वाक्यम्", "false_3": "तृतीयम् असत्यं वाक्यम्",
        "submit_sentences": "वाक्यानि समर्पय",
        "error_all_sentences": "कृपया त्रीणि वाक्यानि लिख।",
        "submission_success": "✅ तव वाक्यानि समर्पितानि। इतरेषां प्रतीक्षा कुरु।",
        "time_left": "⏳ अवशिष्टः समयः",
        "time_up": "समयः समाप्तः",
        "guessing_time": "🤔 अनुमानपर्व",
        "guessing_instructions": "प्रत्येकस्य क्रीडकस्य यथार्थं वर्णं योजय।",
        "player_sentences": "{name} इत्यस्य वाक्यानि",
        "your_guesses": "तव अनुमानानि",
        "submit_guess": "अनुमानं निश्चिनु",
        "error_all_guesses": "कृपया सर्वेभ्यः वर्णं चिनु।",
        "guess_submitted": "✅ तवानुमानं समर्पितम्। परिणामान् प्रतीक्षस्व।",
        "status_submitted": "✅ समर्पितम्",
        "status_writing": "⏳ लिखति",
        "status_guessing": "⏳ चिन्तयति",
        "reveal_results": "सर्वेषां परिणामान् प्रकाशय",
        "results_are_in": "✨ परिणामाः आगताः ✨",
        "true_varnas": "यथार्थवर्णाः",
        "scoring": "🏆 अङ्कगणना",
        "no_correct_guesses": "केनचिदपि सम्यक् नानुमितम्। अस्मिन् चक्रे कोऽपि अङ्को न दीयते।",
        "correct_guessers_info": "{count} जनैः सम्यगनुमितम्। तेषु प्रत्येकं **{points} अङ्कान्** प्राप्नोति।",
        "leaderboard": "अङ्कतालिका",
        "points": "अङ्काः",
        "start_new_round": "🔄 नवीनं चक्रमारभस्व",
        "game_links_expander": "🔗 क्रीडासूत्रं दर्शय",
        "player_link_info": "क्रीडकेभ्यः सूत्रम्",
        "viewer_link_info": "दर्शकेभ्यः सूत्रम्",
        "game_room_not_found": "क्रीडासत्रं न लब्धम्।",
        "go_to_main_menu": "मुख्यपृष्ठं गच्छ",
        "host_controls": "आतिथेयस्य नियन्त्रणम्",
        "end_game": "क्रीडां समापय",
        "quit_game": "क्रीडां त्यज",
        "confirm_quit_game": "निश्चितं त्यक्तुमिच्छसि",
        "confirm_end_game": "निश्चितम्। एतत् सर्वेषां कृते सत्रं समापयिष्यति।",
        "game_ended_by_host": "आतिथेयेन क्रीडा समाप्ता॥",
        "viewer": "दर्शकः",
        "live_chat": "सजीवसम्भाषणम्",
        "type_message": "सन्देशं लिख"
    },
    "en": {
        "lang_select": "Language",
        "game_title": "Satyasatyam",
        "welcome_intro": "Welcome. This is a 4-player game of truth and untruth. One player will be the all-truthful Brahmin, one the 1-lie Kshatriya, one the 1-truth Vaishya, and one the all-lie Shudra. Guessing everyone's identity is your goal.",
        "create_game_button": "✨ Create a New Game Session",
        "require_names": "Require names",
        "enter_name_label": "Enter your name",
        "error_name_required": "A name is required to join this game.",
        "error_name_taken": "This name is already taken. Please choose another.",
        "join_as": "Join as",
        "player": "Player",
        "waiting_for_players": "Waiting for other players to join",
        "truth_1": "First True Sentence", "truth_2": "Second True Sentence", "truth_3": "Third True Sentence",
        "false_1": "First False Sentence", "false_2": "Second False Sentence", "false_3": "Third False Sentence",
        "submit_sentences": "Submit Sentences",
        "error_all_sentences": "Please write three sentences.",
        "submission_success": "✅ Your sentences are submitted. Waiting for others.",
        "time_left": "⏳ Time left",
        "time_up": "Time Up",
        "guessing_time": "🤔 Guessing Time",
        "guessing_instructions": "Match each player to their correct Varna.",
        "player_sentences": "{name}'s Sentences",
        "your_guesses": "Your Guesses",
        "submit_guess": "Confirm Guess",
        "error_all_guesses": "Please assign a Varna to everyone.",
        "guess_submitted": "✅ Your guess is submitted! Waiting for the results.",
        "status_submitted": "✅ Submitted",
        "status_writing": "⏳ Writing",
        "status_guessing": "⏳ Thinking",
        "reveal_results": "Reveal Results for Everyone",
        "results_are_in": "✨ The results are in! ✨",
        "true_varnas": "The True Varnas",
        "scoring": "🏆 Scoring",
        "no_correct_guesses": "Nobody guessed correctly! No points awarded.",
        "correct_guessers_info": "{count} people guessed correctly! They each receive **{points} points**.",
        "leaderboard": "Leaderboard",
        "points": "points",
        "start_new_round": "🔄 Start a New Round",
        "game_links_expander": "🔗 Show Game Links",
        "player_link_info": "Player Link",
        "viewer_link_info": "Viewer Link",
        "game_room_not_found": "Game session not found.",
        "go_to_main_menu": "Go to Main Menu",
        "host_controls": "Host Controls",
        "end_game": "End Game",
        "quit_game": "Quit Game",
        "confirm_quit_game": "Are you sure you want to quit?",
        "confirm_end_game": "Are you sure? This will end the session for everyone.",
        "game_ended_by_host": "The game was ended by the host.",
        "viewer": "Viewer",
        "live_chat": "Live Chat",
        "type_message": "Type a message"
    }
}

# --- 3. GAME LOGIC & STATE MANAGEMENT ---
def get_game_filepath(game_id):
    return os.path.join(GAME_DIR, f"{game_id}.json")

def get_initial_state(game_id, settings, host_user_id):
    shuffled_varnas = random.sample(VARNA_KEYS, len(VARNA_KEYS))
    return {
        "id": game_id, "phase": "joining", "settings": settings,
        "players": {}, "player_user_ids": {}, "host_user_id": host_user_id,
        "true_varna_map": {f"player_{i+1}": varna for i, varna in enumerate(shuffled_varnas)},
        "guesses": {}, "scores": {}, "chat": [], "disqualified": []
    }

def load_game_state(game_id):
    if not game_id: return None
    filepath = get_game_filepath(game_id)
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return None

def save_game_state(state):
    if not state: return
    os.makedirs(GAME_DIR, exist_ok=True)
    with open(get_game_filepath(state['id']), 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def manage_session():
    url_uid = st.query_params.get("uid")
    if url_uid:
        user_id = url_uid
        st.session_state['user_id'] = user_id
    else:
        user_id = st.session_state.setdefault('user_id', str(uuid.uuid4()))
        st.query_params["uid"] = user_id 
        
    game_id = st.query_params.get("id")
    is_viewer = st.query_params.get("role") == "viewer"
    
    state = load_game_state(game_id)
    if state and user_id in state['player_user_ids']:
        st.session_state['player_id'] = state['player_user_ids'][user_id]
        
    player_id = st.session_state.get('player_id')
    return user_id, player_id, game_id, is_viewer

def t(key, **kwargs):
    lang = st.session_state.get('lang', 'sa')
    text = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS.get('en', {}).get(key, key)
    return text.format(**kwargs)

# --- 4. UI COMPONENTS ---
def display_player_header(state, player_id):
    if player_id and player_id in state.get('players', {}):
        name = state['players'][player_id]['name']
        varna = state['true_varna_map'].get(player_id)
        if state['phase'] in ['writing', 'guessing'] and varna:
            varna_name = VARNA_DETAILS[varna][st.session_state.lang]['name']
            st.info(f"👤 **{name}** | 🎭 **{varna_name}**")
        else:
            st.info(f"👤 **{name}**")

def display_joining_phase(state, user_id):
    player_slots = {f"player_{i+1}" for i in range(4)}
    available_slots = sorted(list(player_slots - set(state['players'].keys())))
    if not available_slots: return
    
    player_id_to_join = st.session_state.get('player_id') or available_slots[0]
    player_num = player_id_to_join.split('_')[1]
    player_num_str = to_devanagari(player_num) if st.session_state.lang == 'sa' else player_num
    default_name = f"{t('player')} {player_num_str}"

    player_name = st.text_input(t('enter_name_label'), placeholder=default_name)
    
    if st.button(f"{default_name} {t('join_as')}"):
        name_to_save = player_name.strip()
        existing_names = [p['name'] for p in state['players'].values()]
        
        if state['settings'].get('require_names') and not name_to_save: st.error(t('error_name_required'))
        elif name_to_save in existing_names: st.error(t('error_name_taken'))
        else:
            if not name_to_save: name_to_save = default_name
            state['players'][player_id_to_join] = {"name": name_to_save, "user_id": user_id}
            state['player_user_ids'][user_id] = player_id_to_join
            state['scores'].setdefault(name_to_save, 0)
            st.session_state['player_id'] = player_id_to_join
            save_game_state(state)
            st.rerun()

def display_status_list(state, phase):
    st.markdown("---")
    for pid, pdata in sorted(state['players'].items()):
        if phase == 'writing':
            status = t('status_submitted') if pdata.get('submitted') else t('status_writing')
        else:
            status = t('status_submitted') if pdata['user_id'] in state.get('guesses', {}) else t('status_guessing')
        st.write(f"**{pdata['name']}**: {status}")

def display_writing_phase(state, player_id):
    elapsed = time.time() - state.get('writing_start_time', time.time())
    remaining = max(0, WRITING_TIME_LIMIT - int(elapsed))
    
    st.warning(f"**{t('time_left')}: {remaining // 60}:{remaining % 60:02d}**")

    my_varna = state['true_varna_map'][player_id]
    
    with st.form("sentence_form"):
        prompts = SENTENCE_PROMPTS[my_varna]
        sentences = [st.text_area(t(p), height=80) for p in prompts]
        
        if st.form_submit_button(t('submit_sentences')):
            if all(sentences):
                state['players'][player_id]['sentences'] = sentences
                state['players'][player_id]['submitted'] = True
                save_game_state(state)
                st.rerun()
            else: st.error(t('error_all_sentences'))

def display_guessing_phase(state, user_id, player_id):
    elapsed = time.time() - state.get('guessing_start_time', time.time())
    remaining = max(0, GUESSING_TIME_LIMIT - int(elapsed))
    
    st.warning(f"**{t('time_left')}: {remaining // 60}:{remaining % 60:02d}**")

    is_viewer = not player_id
    my_varna = state['true_varna_map'].get(player_id) if not is_viewer else None
    
    players_to_guess = [pid for pid in state['players'] if pid != player_id]
    varna_keys_to_guess = [v for v in VARNA_KEYS if v != my_varna]

    if f"guesses_{state['id']}" not in st.session_state:
        st.session_state[f"guesses_{state['id']}"] = {pid: None for pid in players_to_guess}
    temp_guesses = st.session_state[f"guesses_{state['id']}"]

    st.header(t('guessing_time'))
    st.info(t('guessing_instructions'))

    for p_id, p_data in sorted(state['players'].items()):
        with st.expander(t('player_sentences', name=p_data['name']), expanded=True):
            s1, s2, s3 = (to_devanagari(i) if st.session_state.lang == 'sa' else i for i in [1, 2, 3])
            st.markdown(f"{s1}. *{p_data['sentences'][0]}*\n\n{s2}. *{p_data['sentences'][1]}*\n\n{s3}. *{p_data['sentences'][2]}*")

    st.subheader(t('your_guesses'))
    cols = st.columns(len(players_to_guess))
    
    for i, pid in enumerate(players_to_guess):
        with cols[i]:
            pname = state['players'][pid]['name']
            current_selection = temp_guesses.get(pid)
            
            used_by_others = [val for p, val in temp_guesses.items() if p != pid and val is not None]
            available_keys = [k for k in varna_keys_to_guess if k not in used_by_others]
            
            options_names = [VARNA_DETAILS[k][st.session_state.lang]['name'] for k in available_keys]
            curr_val_name = VARNA_DETAILS[current_selection][st.session_state.lang]['name'] if current_selection else None
            idx = options_names.index(curr_val_name) if curr_val_name in options_names else None
            
            selected_name = st.selectbox(f"**{pname}**", options_names, index=idx, key=f"guess_box_{pid}", placeholder="---")
            
            if selected_name:
                selected_key = [k for k in VARNA_KEYS if VARNA_DETAILS[k][st.session_state.lang]['name'] == selected_name][0]
                temp_guesses[pid] = selected_key
            else:
                temp_guesses[pid] = None

    if st.button(t('submit_guess'), type="primary"):
        if None in temp_guesses.values():
            st.error(t('error_all_guesses'))
        else:
            final_guesses = temp_guesses.copy()
            if not is_viewer: final_guesses[player_id] = my_varna
            state['guesses'][user_id] = final_guesses
            save_game_state(state)
            st.rerun()

def display_results_phase(state, user_id):
    st.header(t('results_are_in'))
    st.subheader(t('true_varnas'))
    truth = state['true_varna_map']
    cols = st.columns(4)
    for i, (p_id, p_data) in enumerate(sorted(state['players'].items())):
        with cols[i]:
            true_varna_name = VARNA_DETAILS[truth[p_id]][st.session_state.lang]['name']
            st.metric(label=p_data['name'], value=true_varna_name)

    st.subheader(t('scoring'))
    correct_guessers = []
    disqualified = state.get('disqualified', [])
    
    for uid, guess in state['guesses'].items():
        # Disqualified users get 0 points even if they guessed correctly
        if guess == truth and uid not in disqualified:
            g_name = state['players'].get(state['player_user_ids'].get(uid, ""), {}).get('name')
            if not g_name: g_name = f"{t('viewer')} ({uid[:4]})"
            correct_guessers.append(g_name)

    if not correct_guessers: st.warning(t('no_correct_guesses'))
    else:
        pts = POINTS_POOL // len(correct_guessers)
        pts_str = to_devanagari(pts) if st.session_state.lang == 'sa' else pts
        count_str = to_devanagari(len(correct_guessers)) if st.session_state.lang == 'sa' else len(correct_guessers)
        
        st.success(t('correct_guessers_info', count=count_str, points=pts_str))
        for name in correct_guessers:
            st.write(f"🎉 **{name}**")
            if t('viewer') not in name: state['scores'][name] = state['scores'].get(name, 0) + pts
                
    save_game_state(state)

    st.subheader(t('leaderboard'))
    if state.get('scores'):
        for name, score in sorted(state['scores'].items(), key=lambda x: x[1], reverse=True):
            score_str = to_devanagari(score) if st.session_state.lang == 'sa' else score
            st.markdown(f"**{name}** : `{score_str} {t('points')}`")

    if state.get('host_user_id') == user_id:
        if st.button(t('start_new_round'), type="primary"):
            new_state = get_initial_state(state['id'], state['settings'], user_id)
            new_state['players'] = {pid: {"name": p["name"], "user_id": p["user_id"]} for pid, p in state['players'].items()}
            new_state['player_user_ids'] = state['player_user_ids']
            new_state['scores'] = state.get('scores', {})
            save_game_state(new_state)
            st.rerun()

def display_chat(state, user_id, player_id):
    st.markdown("---")
    st.subheader(t('live_chat'))
    
    chat_box = st.container(height=300)
    for msg in state.get('chat', []):
        with chat_box.chat_message("user" if msg['user_id'] == user_id else "assistant"):
            st.write(f"**{msg['sender']}**: {msg['text']}")
            
    if prompt := st.chat_input(t('type_message')):
        p_data = state.get('players', {}).get(player_id)
        sender_name = p_data['name'] if p_data else t('viewer')
        
        state.setdefault('chat', []).append({
            "user_id": user_id, "sender": sender_name, "text": prompt
        })
        save_game_state(state)
        st.rerun()

def display_footer(state, user_id, player_id):
    with st.expander(t('game_links_expander')):
        st.write(f"**{t('player_link_info')}**")
        st.code(f"{BASE_URL}/?id={state['id']}")
        st.write(f"**{t('viewer_link_info')}**")
        st.code(f"{BASE_URL}/?id={state['id']}&role=viewer")

    cols = st.columns([1, 1])
    if player_id and player_id in state.get('players', {}):
        with cols[0]:
            if st.button("🚪 " + t('quit_game'), use_container_width=True):
                if st.checkbox(t('confirm_quit_game'), key="quit"):
                    state['players'].pop(player_id, None)
                    state['player_user_ids'].pop(user_id, None)
                    if state.get('host_user_id') == user_id:
                        new_host = next((p['user_id'] for p in state['players'].values() if p.get('user_id')), None)
                        state['host_user_id'] = new_host
                    save_game_state(state)
                    st.session_state.pop('player_id', None)
                    st.rerun()
    
    if state.get('host_user_id') == user_id:
        with cols[1]:
            if st.button("🛑 " + t('end_game'), use_container_width=True, type="primary"):
                 if st.checkbox(t('confirm_end_game'), key="end"):
                    state['phase'] = 'ended_by_host'
                    save_game_state(state)
                    st.rerun()

# --- 5. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="सत्यासत्यम्", layout="centered")
    st.radio(" ", options=['sa', 'en'], format_func=lambda x: "संस्कृतम्" if x == 'sa' else "English", horizontal=True, key='lang', label_visibility="collapsed")

    user_id, player_id, game_id, is_viewer = manage_session()
    state = load_game_state(game_id)
    
    if not game_id:
        st.title(t('game_title'))
        st.write(t('welcome_intro'))
        require_names = st.checkbox(t('require_names'), value=True)
        if st.button(t('create_game_button')):
            new_id = str(uuid.uuid4().hex[:6].upper())
            new_state = get_initial_state(new_id, {"require_names": require_names}, user_id)
            save_game_state(new_state)
            st.session_state.player_id = "player_1"
            st.query_params["id"] = new_id
            st.rerun()
        return

    if not state:
        st.error(t('game_room_not_found'))
        if st.button(t('go_to_main_menu')): st.query_params.clear(); st.rerun()
        return

    if state['phase'] == 'ended_by_host':
        st.success(f"👑 {t('game_ended_by_host')}")
        if st.button(t('go_to_main_menu')):
            st.session_state.pop('player_id', None)
            st.query_params.clear()
            st.rerun()
        return

    # Banner displayed globally for playing users
    display_player_header(state, player_id)
        
    num_players = len(state['players'])
    num_submitted = sum(1 for p in state['players'].values() if p.get('submitted'))
    num_guessed = sum(1 for uid in state['player_user_ids'] if uid in state.get('guesses', {}))

    # --- AUTO-ADVANCE & GLOBAL TIMEOUT LOGIC ---
    current_time = time.time()
    
    if state['phase'] == 'joining' and num_players == 4:
        state['phase'] = 'writing'
        state['writing_start_time'] = current_time
        save_game_state(state)
        st.rerun()
        
    elif state['phase'] == 'writing':
        elapsed = current_time - state.get('writing_start_time', current_time)
        if num_submitted == 4 or elapsed >= WRITING_TIME_LIMIT:
            for pid, pdata in state['players'].items():
                if not pdata.get('submitted'):
                    pdata['sentences'] = [t('time_up')] * 3
                    pdata['submitted'] = True
                    state.setdefault('disqualified', []).append(pdata['user_id'])
            state['phase'] = 'guessing'
            state['guessing_start_time'] = current_time
            save_game_state(state)
            st.rerun()
            
    elif state['phase'] == 'guessing':
        elapsed = current_time - state.get('guessing_start_time', current_time)
        if num_guessed == 4 or elapsed >= GUESSING_TIME_LIMIT:
            for uid in state['player_user_ids']:
                if uid not in state.setdefault('guesses', {}):
                    state['guesses'][uid] = "TIMEOUT"
                    state.setdefault('disqualified', []).append(uid)
            state['phase'] = 'results'
            save_game_state(state)
            st.rerun()
    
    needs_refresh = False
    
    # --- DISPLAY PHASES ---
    if state['phase'] == 'joining':
        if not is_viewer and (not player_id or player_id not in state['players']): 
            display_joining_phase(state, user_id)
        else: 
            st.info(t('waiting_for_players'))
            needs_refresh = True
            
    elif state['phase'] == 'writing':
        if is_viewer or state['players'].get(player_id, {}).get('submitted'):
            st.success(t('submission_success'))
            display_status_list(state, 'writing')
            needs_refresh = True
        else:
            display_writing_phase(state, player_id)
            display_status_list(state, 'writing')
            needs_refresh = True 

    elif state['phase'] == 'guessing':
        if user_id in state.get('guesses', {}) or is_viewer:
            st.success(t('guess_submitted'))
            display_status_list(state, 'guessing')
            needs_refresh = True
        else: 
            display_guessing_phase(state, user_id, player_id)
            display_status_list(state, 'guessing')
            needs_refresh = True
        
    elif state['phase'] == 'results':
        display_results_phase(state, user_id)
        
    # Constant UI Elements
    display_chat(state, user_id, player_id)
    display_footer(state, user_id, player_id)

    # 15s Auto-Refresh
    if needs_refresh:
        time.sleep(AUTO_REFRESH_SECONDS)
        st.rerun()

if __name__ == "__main__":
    main()
