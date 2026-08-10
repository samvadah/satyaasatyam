import streamlit as st
import random
import json
import os
import uuid
import time

# --- 1. CONFIGURATION & CONSTANTS ---
GAME_DIR = "gamerooms"
BASE_URL = "https://satyaasatyam.streamlit.app"
AUTO_REFRESH_SECONDS = 15
WRITING_TIME_LIMIT = 360  # 6 minutes
GUESSING_TIME_LIMIT = 120 # 2 minutes
POINTS_PER_GUESS = 4
MAX_POINTS = 12

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

# Used to grade the sentences in the results phase
SENTENCE_MARKS = {
    "Brahmin": ["✅", "✅", "✅"],
    "Kshatriya": ["✅", "✅", "❌"],
    "Vaishya": ["✅", "❌", "❌"],
    "Shudra": ["❌", "❌", "❌"]
}

TRANSLATIONS = {
    "sa": {
        "lang_select": "भाषा",
        "game_title": "सत्यासत्यम्",
        "welcome_intro": "सुस्वागतम्। इयं चतुर्णां क्रीडकानां सत्यासत्यपरीक्षा क्रीडा॥ अत्र एको ब्राह्मणः सर्वसत्यवादी क्षत्रिय एकानृतवादी वैश्य एकसत्यवादी शूद्रश्च सर्वानृतवादी भविष्यति। सर्वेषां वर्णानां सम्यगनुमानमेव तव लक्ष्यम्॥",
        "how_to_play": "क्रीडाविधिः",
        "how_to_play_text": "१ चत्वारः क्रीडकाः स्वनाम दत्त्वा प्रविशन्ति।\n\n२ प्रत्येकं क्रीडकः एकं वर्णं प्राप्नोति।\n\n३ स्ववर्णस्य नियमानुसारं स्वविषये त्रीणि वाक्यानि लिख। ब्राह्मणः त्रयः सत्यानि। क्षत्रियः द्वे सत्ये एकम् असत्यम्। वैश्यः एकं सत्यं द्वे असत्ये। शूद्रः त्रयः असत्यानि।\n\n४ अन्येषां वाक्यानि पठित्वा तेषां यथार्थवर्णं चिनु।\n\n५ सम्यगनुमानात् प्रतिवर्णं ४ अङ्काः प्राप्यन्ते। पूर्णाङ्काः प्राप्ते 🏆 प्राप्यते।",
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
        "player_sentences": "वाक्यानि",
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
        "sentences_review": "वाक्यानां समीक्षा",
        "scoring": "🏆 अङ्कगणना",
        "round_scores": "अस्मिन् चक्रे प्राप्ताङ्काः",
        "leaderboard": "अङ्कतालिका",
        "points": "अङ्काः",
        "start_new_round": "🔄 नवीनं चक्रमारभस्व",
        "game_links_expander": "🔗 क्रीडासूत्रं दर्शय",
        "player_link_info": "क्रीडकेभ्यः सूत्रम्",
        "viewer_link_info": "दर्शकेभ्यः सूत्रम्",
        "game_room_not_found": "क्रीडासत्रं न लब्धम्।",
        "go_to_main_menu": "मुख्यपृष्ठं गच्छ",
        "end_game": "क्रीडां समापय",
        "quit_game": "क्रीडां त्यज",
        "confirm_quit_game": "निश्चितं त्यक्तुमिच्छसि",
        "confirm_end_game": "निश्चितम्। एतत् सर्वेषां कृते सत्रं समापयिष्यति।",
        "yes": "आम्",
        "game_ended_by_host": "आतिथेयेन क्रीडा समाप्ता॥",
        "viewer": "दर्शकः",
        "live_chat": "💬 सजीवसम्भाषणम्",
        "type_message": "सन्देशं लिख",
        "send": "प्रेषय"
    },
    "en": {
        "lang_select": "Language",
        "game_title": "Satyasatyam",
        "welcome_intro": "Welcome. This is a 4-player game of truth and untruth. One player will be the all-truthful Brahmin, one the 1-lie Kshatriya, one the 1-truth Vaishya, and one the all-lie Shudra. Guessing everyone's identity is your goal.",
        "how_to_play": "How to Play",
        "how_to_play_text": "1. Four players join the game by entering their names.\n\n2. Each player is secretly assigned a Varna.\n\n3. Write 3 sentences about yourself based on your rule. (Brahmin = 3 Truths. Kshatriya = 2 Truths, 1 Lie. Vaishya = 1 Truth, 2 Lies. Shudra = 3 Lies.)\n\n4. Read others' sentences and guess their true Varna.\n\n5. Get 4 points for each correct guess. Score a perfect 12 to earn a 🏆!",
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
        "player_sentences": "Sentences",
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
        "sentences_review": "Sentences Review",
        "scoring": "🏆 Scoring",
        "round_scores": "Scores This Round",
        "leaderboard": "Leaderboard",
        "points": "points",
        "start_new_round": "🔄 Start a New Round",
        "game_links_expander": "🔗 Show Game Links",
        "player_link_info": "Player Link",
        "viewer_link_info": "Viewer Link",
        "game_room_not_found": "Game session not found.",
        "go_to_main_menu": "Go to Main Menu",
        "end_game": "End Game",
        "quit_game": "Quit Game",
        "confirm_quit_game": "Are you sure you want to quit?",
        "confirm_end_game": "Are you sure? This will end the session for everyone.",
        "yes": "Yes",
        "game_ended_by_host": "The game was ended by the host.",
        "viewer": "Viewer",
        "live_chat": "💬 Live Chat",
        "type_message": "Type a message",
        "send": "Send"
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
        "guesses": {}, "scores": {}, "last_round_scores": {}, "chat": [], "disqualified": []
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

def format_player_name(p_id, p_data, state):
    """Formats player name with number and host crown: [1] Name 👑"""
    num = p_id.split('_')[1]
    num_str = to_devanagari(num) if st.session_state.get('lang') == 'sa' else num
    host_str = " 👑" if p_data.get('user_id') == state.get('host_user_id') else ""
    return f"[{num_str}] {p_data['name']}{host_str}"

def get_player_number_str(p_id):
    """Gets just the localized number string for avatars (e.g. '१' or '1')"""
    if not p_id: return "V"
    num = p_id.split('_')[1]
    return to_devanagari(num) if st.session_state.get('lang') == 'sa' else num

# --- 4. UI COMPONENTS ---
def display_player_header(state, player_id):
    if player_id and player_id in state.get('players', {}):
        p_data = state['players'][player_id]
        formatted_name = format_player_name(player_id, p_data, state)
        varna = state['true_varna_map'].get(player_id)
        if state['phase'] in ['writing', 'guessing'] and varna:
            varna_name = VARNA_DETAILS[varna][st.session_state.lang]['name']
            st.info(f"👤 **{formatted_name}** | 🎭 **{varna_name}**")
        else:
            st.info(f"👤 **{formatted_name}**")

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
        formatted_name = format_player_name(pid, pdata, state)
        if phase == 'writing':
            status = t('status_submitted') if pdata.get('submitted') else t('status_writing')
        else:
            status = t('status_submitted') if pdata['user_id'] in state.get('guesses', {}) else t('status_guessing')
        st.write(f"**{formatted_name}**: {status}")

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

    # Display other players' sentences
    for p_id in players_to_guess:
        p_data = state['players'][p_id]
        formatted_name = format_player_name(p_id, p_data, state)
        with st.expander(f"{formatted_name} - {t('player_sentences')}", expanded=True):
            s1, s2, s3 = (to_devanagari(i) if st.session_state.lang == 'sa' else i for i in [1, 2, 3])
            st.markdown(f"{s1}. *{p_data['sentences'][0]}*\n\n{s2}. *{p_data['sentences'][1]}*\n\n{s3}. *{p_data['sentences'][2]}*")

    st.subheader(t('your_guesses'))
    cols = st.columns(len(players_to_guess))
    
    for i, pid in enumerate(players_to_guess):
        with cols[i]:
            p_data = state['players'][pid]
            formatted_name = format_player_name(pid, p_data, state)
            current_selection = temp_guesses.get(pid)
            
            used_by_others = [val for p, val in temp_guesses.items() if p != pid and val is not None]
            available_keys = [k for k in varna_keys_to_guess if k not in used_by_others]
            
            options_names = [VARNA_DETAILS[k][st.session_state.lang]['name'] for k in available_keys]
            curr_val_name = VARNA_DETAILS[current_selection][st.session_state.lang]['name'] if current_selection else None
            idx = options_names.index(curr_val_name) if curr_val_name in options_names else None
            
            selected_name = st.selectbox(f"**{formatted_name}**", options_names, index=idx, key=f"guess_box_{pid}", placeholder="---")
            
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
    
    # Sentences Review (True/False Reveal)
    st.subheader(t('sentences_review'))
    for p_id, p_data in sorted(state['players'].items()):
        formatted_name = format_player_name(p_id, p_data, state)
        varna_key = state['true_varna_map'][p_id]
        varna_name = VARNA_DETAILS[varna_key][st.session_state.lang]['name']
        marks = SENTENCE_MARKS[varna_key]
        
        st.markdown(f"**{formatted_name} | {varna_name}**")
        for i, sent in enumerate(p_data['sentences']):
            num = to_devanagari(i+1) if st.session_state.lang == 'sa' else i+1
            st.markdown(f"{num}. {marks[i]} *{sent}*")
        st.markdown("---")

    # Round Scores
    st.subheader(t('round_scores'))
    if not state.get('last_round_scores'):
        st.warning(t('no_correct_guesses'))
    else:
        for name, pts in state['last_round_scores'].items():
            pts_str = to_devanagari(pts) if st.session_state.lang == 'sa' else pts
            trophy = " 🏆" if pts == MAX_POINTS else ""
            st.success(f"**{name}**: {pts_str} {t('points')}{trophy}")

    # Total Leaderboard
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
    with st.expander(t('live_chat'), expanded=False):
        chat_box = st.container(height=250)
        for msg in state.get('chat', []):
            avatar_txt = get_player_number_str(msg.get('player_id'))
            with chat_box.chat_message("user" if msg['user_id'] == user_id else "assistant", avatar=avatar_txt):
                st.write(f"**{msg['sender']}**: {msg['text']}")
                
        with st.form("chat_form", clear_on_submit=True):
            cols = st.columns([4, 1])
            prompt = cols[0].text_input(t('type_message'), label_visibility="collapsed")
            if cols[1].form_submit_button(t('send')):
                if prompt:
                    p_data = state.get('players', {}).get(player_id)
                    sender_name = format_player_name(player_id, p_data, state) if p_data else t('viewer')
                    state.setdefault('chat', []).append({
                        "user_id": user_id, 
                        "player_id": player_id,
                        "sender": sender_name, 
                        "text": prompt
                    })
                    save_game_state(state)
                    st.rerun()

def display_footer(state, user_id, player_id):
    st.markdown("---")
    with st.expander(t('game_links_expander')):
        st.write(f"**{t('player_link_info')}**")
        st.code(f"{BASE_URL}/?id={state['id']}")
        st.write(f"**{t('viewer_link_info')}**")
        st.code(f"{BASE_URL}/?id={state['id']}&role=viewer")

    cols = st.columns([1, 1])
    if player_id and player_id in state.get('players', {}):
        with cols[0]:
            with st.popover("🚪 " + t('quit_game'), use_container_width=True):
                st.write(t('confirm_quit_game'))
                if st.button(t('yes'), key="quit_yes", use_container_width=True):
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
            with st.popover("🛑 " + t('end_game'), use_container_width=True):
                st.write(t('confirm_end_game'))
                if st.button(t('yes'), key="end_yes", type="primary", use_container_width=True):
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
        with st.expander(t('how_to_play')):
            st.markdown(t('how_to_play_text'))
            
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

    display_player_header(state, player_id)
        
    num_players = len(state['players'])
    num_submitted = sum(1 for p in state['players'].values() if p.get('submitted'))
    num_guessed = sum(1 for uid in state['player_user_ids'] if uid in state.get('guesses', {}))
    current_time = time.time()
    
    # --- AUTO-ADVANCE & SCORING LOGIC (Calculates strictly ONCE per round) ---
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
            
            # SCORE CALCULATION - HAPPENS ONCE
            truth = state['true_varna_map']
            round_scores = {}
            for uid, guess_dict in state['guesses'].items():
                pts = 0
                if uid not in state.get('disqualified', []) and isinstance(guess_dict, dict):
                    for pid, guessed_varna in guess_dict.items():
                        if truth.get(pid) == guessed_varna and pid != state['player_user_ids'].get(uid):
                            pts += POINTS_PER_GUESS
                            
                g_name = state['players'].get(state['player_user_ids'].get(uid, ""), {}).get('name')
                if not g_name: g_name = f"{t('viewer')} ({uid[:4]})"
                
                if pts > 0:
                    round_scores[g_name] = pts
                    state['scores'][g_name] = state['scores'].get(g_name, 0) + pts

            state['last_round_scores'] = round_scores
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
        
    display_chat(state, user_id, player_id)
    display_footer(state, user_id, player_id)

    if needs_refresh:
        time.sleep(AUTO_REFRESH_SECONDS)
        st.rerun()

if __name__ == "__main__":
    main()
