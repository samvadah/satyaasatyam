import streamlit as st
import random
import json
import os
import uuid
import time

# --- 1. CONFIGURATION & CONSTANTS ---
GAME_DIR = "gamerooms"
POINTS_POOL = 12
AUTO_REFRESH_SECONDS = 4

# --- 2. LANGUAGE & CONTENT ---
def to_devanagari(num_str):
    return "".join("०१२३४५६७८९"[int(d)] for d in str(num_str))

VARNA_DETAILS = {
    "Brahmin": {"sa": {"name": "ब्राह्मणः", "rule": "स्वविषये त्रीणि सत्यानि वाक्यानि लिख।"}, "en": {"name": "Brahmin", "rule": "Write three true sentences about yourself."}},
    "Kshatriya": {"sa": {"name": "क्षत्रियः", "rule": "स्वविषये एकम् असत्यं द्वे च सत्ये वाक्यानि लिख।"}, "en": {"name": "Kshatriya", "rule": "Write one false sentence and two true ones."}},
    "Vaishya": {"sa": {"name": "वैश्यः", "rule": "स्वविषये एकं सत्यं द्वे च असत्ये वाक्यानि लिख।"}, "en": {"name": "Vaishya", "rule": "Write one true sentence and two false ones."}},
    "Shudra": {"sa": {"name": "शूद्रः", "rule": "स्वविषये त्रीणि असत्यानि वाक्यानि लिख।"}, "en": {"name": "Shudra", "rule": "Write three false sentences about yourself."}},
}
VARNA_KEYS = list(VARNA_DETAILS.keys())

# All UI text is centralized here.
TRANSLATIONS = {
    "sa": {
        "game_title": "सत्यासत्यम्",
        "how_to_play_title": "क्रीडाविधिः",
        "how_to_play_content": """
        १. **आरम्भः** - एकः क्रीडकः सत्रं रचयति।
        २. **वर्णप्राप्तिः** - चत्वारः क्रीडकाः सम्मिलिताः सन्तः प्रत्येकं गोप्यं वर्णं प्राप्नुवन्ति।
        ३. **वाक्यरचना** - स्ववर्णस्य नियमानुसारं वाक्यानि लिखन्तु।
        ४. **अनुमानम्** - सर्वेषां वाक्यानि पठित्वा कः कस्य वर्णस्य इति अनुमानं कुर्वन्तु।
        ५. **अङ्कप्राप्तिः** - सम्यगनुमानकर्तारः अङ्कान् प्राप्नुवन्ति।
        """,
        "welcome_intro": "सुस्वागतम्। इयं चतुर्णां क्रीडकानां सत्यासत्यपरीक्षा क्रीडा॥",
        "create_game_button": "✨ नवीनं क्रीडासत्रं रचया",
        "require_names": "नामकरणम् अनिवार्यम्",
        "enter_name_label": "तव नामाङ्कनं कुरु",
        "error_name_required": "अनिवार्यत्वात् कृपया स्वनाम प्रविशतु।",
        "error_name_taken": "इदं नाम पूर्वमेव स्वीकृतम्। अन्यत् चिनोतु।",
        "join_as": "इति प्रविश",
        "player": "क्रीडकः",
        "you_joined_as": "त्वम् अस्मिन् नाम्ना सम्मिलितोऽसि",
        "waiting_for_players": "अन्येषाम् आगमनं प्रतीक्षस्व...",
        "players_in_room": "अस्मिन् सत्रे क्रीडकाः",
        "you_are": "त्वमसि",
        "your_rule": "तव नियमः",
        "write_three_sentences": "अधः स्ववाक्यानि लिख।",
        "sentence_1": "प्रथमं वाक्यम्", "sentence_2": "द्वितीयं वाक्यम्", "sentence_3": "तृतीयं वाक्यम्",
        "submit_sentences": "वाक्यानि समर्पय",
        "submission_success": "✅ तव वाक्यानि समर्पितानि। इतरेषां प्रतीक्षा...",
        "guessing_time": "🤔 अनुमानपर्व",
        "guessing_instructions": "प्रत्येकस्य क्रीडकस्य वर्णं योजय।",
        "player_sentences": "{name} इत्यस्य वाक्यानि",
        "your_guesses": "तव अनुमानानि",
        "submit_guess": "अनुमानं निश्चिनु",
        "guess_submitted": "✅ तवानुमानं समर्पितम्। परिणामान् प्रतीक्षस्व।",
        "reveal_results": "सर्वेषां परिणामान् प्रकाशय",
        "results_are_in": "✨ परिणामाः आगताः ✨",
        "true_varnas": "यथार्थवर्णाः",
        "scoring": "🏆 अङ्कगणना",
        "no_correct_guesses": "केनचिदपि सम्यक् नानुमितम्। अस्मिन् चक्रे कोऽपि अङ्को न दीयते।",
        "correct_guessers_info": "{count} जनैः सम्यगनुमितम्। तेषु प्रत्येकं **{points} अङ्कान्** प्राप्नोति।",
        "leaderboard": "अङ्कतालिका",
        "points": "अङ्काः",
        "start_new_round": "🔄 नवीनं चक्रमारभस्व",
        "share_the_game": "🔗 क्रीडासूत्रम्",
        "player_link_info": "क्रीडकेभ्यः सूत्रम्",
        "viewer_link_info": "दर्शकेभ्यः सूत्रम्",
        "game_room_not_found": "क्रीडासत्रं न लब्धम्।",
        "go_to_main_menu": "मुख्यपृष्ठं गच्छ",
        "host_controls": "यजमानस्य नियन्त्रणम्",
        "end_game": "क्रीडां समापय",
        "confirm_end_game": "निश्चितम्? एतत् सर्वेषां कृते सत्रं निष्कासयिष्यति।",
        "game_ended_by_host": "यजमानेन क्रीडा समापिता।",
    },
    "en": { "game_title": "Satyasatyam", "how_to_play_title": "How to Play", "welcome_intro": "Welcome!", "require_names": "Require names", "host_controls": "Host Controls", "end_game": "End Game", "error_name_taken": "This name is already taken. Please choose another.", # etc...
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
        "guesses": {}, "scores": {}
    }

def load_game_state(game_id):
    filepath = get_game_filepath(game_id)
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return None

def save_game_state(game_id, state):
    os.makedirs(GAME_DIR, exist_ok=True)
    with open(get_game_filepath(game_id), 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_session_info():
    """Centralizes session state management for the current user."""
    user_id = st.session_state.setdefault('user_id', str(uuid.uuid4()))
    player_id = st.session_state.get('player_id')
    game_id = st.query_params.get("id")
    is_viewer = st.query_params.get("role") == "viewer"
    return user_id, player_id, game_id, is_viewer

def t(key, **kwargs):
    """Translation helper function with robust fallback and Devanagari numbers."""
    lang = st.session_state.get('lang', 'sa')
    text = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS.get('en', {}).get(key, key)
    if lang == 'sa':
        for k, v in kwargs.items():
            if isinstance(v, (int, str)) and str(v).isdigit(): kwargs[k] = to_devanagari(v)
    return text.format(**kwargs)

# --- 4. UI COMPONENTS ---
def display_main_menu():
    st.title(t('game_title'))
    st.write(t('welcome_intro'))
    require_names = st.checkbox(t('require_names'), value=True)
    if st.button(t('create_game_button')):
        user_id = get_session_info()[0]
        game_id = str(uuid.uuid4().hex[:6].upper())
        state = get_initial_state(game_id, {"require_names": require_names}, user_id)
        save_game_state(game_id, state)
        st.session_state.player_id = "player_1"
        st.query_params["id"] = game_id
        st.rerun()

def display_joining_phase(state, player_id, user_id):
    player_num = player_id.split('_')[1]
    
    if player_id not in state['players']:
        default_name = f"{t('player')} {t(key='', count=player_num)}"
        player_name_input = st.text_input(t('enter_name_label'), placeholder=default_name, key="player_name_input")
        
        if st.button(f"{default_name} {t('join_as')}"):
            name_to_save = player_name_input.strip()
            existing_names = [p['name'] for p in state['players'].values()]
            
            if state['settings'].get('require_names') and not name_to_save:
                st.error(t('error_name_required'))
            elif name_to_save in existing_names:
                st.error(t('error_name_taken'))
            else:
                if not name_to_save: name_to_save = default_name
                state['players'][player_id] = {"name": name_to_save, "user_id": user_id}
                state['player_user_ids'][user_id] = player_id
                state['scores'].setdefault(name_to_save, 0)
                save_game_state(state['id'], state)
                st.rerun()
    else:
        status_placeholder = st.empty()
        while len(state['players']) < 4:
            with status_placeholder.container():
                st.success(f"**{t('you_joined_as')} {state['players'][player_id]['name']}**।")
                st.info(t('waiting_for_players'))
                st.write(f"**{t('players_in_room')}**")
                display_player_list(state)
            
            time.sleep(AUTO_REFRESH_SECONDS)
            new_state = load_game_state(state['id'])
            if not new_state or len(new_state['players']) != len(state['players']):
                st.rerun()
            state = new_state # Update local state if no major change occurred

        state['phase'] = "writing"
        save_game_state(state['id'], state)
        st.rerun()

def display_writing_phase(state, player_id):
    player_data = state['players'][player_id]
    if player_data.get('submitted'):
        status_placeholder = st.empty()
        while not all(p.get('submitted') for p in state['players'].values()):
            submitted_count = sum(1 for p in state['players'].values() if p.get('submitted'))
            with status_placeholder.container():
                st.success(t('submission_success'))
                st.progress(submitted_count / 4, text=t(key='', count=submitted_count)+f"/{t(key='', count=4)}")
            
            time.sleep(AUTO_REFRESH_SECONDS)
            new_state = load_game_state(state['id'])
            if not new_state or sum(1 for p in new_state['players'].values() if p.get('submitted')) != submitted_count:
                st.rerun()
            state = new_state
            
        state['phase'] = "guessing"
        save_game_state(state['id'], state)
        st.rerun()
    else:
        # Display form for writing
        my_varna_key = state['true_varna_map'][player_id]
        varna_details = VARNA_DETAILS[my_varna_key][st.session_state.lang]
        st.header(f"{t('you_are')} **{varna_details['name']}**")
        st.warning(f"**{t('your_rule')}** {varna_details['rule']}")
        with st.form("sentence_form"):
            sentences = [st.text_area(t(f'sentence_{i+1}'), height=80) for i in range(3)]
            if st.form_submit_button(t('submit_sentences')):
                if all(sentences):
                    state['players'][player_id]['sentences'] = sentences
                    state['players'][player_id]['submitted'] = True
                    save_game_state(state['id'], state)
                    st.rerun()
                else: st.error(t('error_all_sentences'))

def display_guessing_phase(state, user_id):
    if user_id in state['guesses']:
        st.success(t('guess_submitted'))
        return # Further logic to auto-refresh while waiting for others could go here

    st.header(t('guessing_time'))
    st.info(t('guessing_instructions'))
    for p_id, p_data in sorted(state['players'].items()):
        player_name = p_data['name'] + (" 👑" if p_data.get('user_id') == state.get('host_user_id') else "")
        with st.expander(t('player_sentences', name=player_name), expanded=True):
            st.markdown("\n\n".join(f"{to_devanagari(i+1) if st.session_state.lang=='sa' else i+1}. *{s}*" for i, s in enumerate(p_data['sentences'])))

    with st.form("guessing_form"):
        st.subheader(t('your_guesses'))
        player_ids = sorted(state['players'].keys())
        all_varna_names = [VARNA_DETAILS[key][st.session_state.lang]['name'] for key in VARNA_KEYS]
        player_guesses, used_varnas = {}, []
        
        cols = st.columns(len(player_ids))
        for i, p_id in enumerate(player_ids):
            with cols[i]:
                player_name = state['players'][p_id]['name']
                available_varnas = [v for v in all_varna_names if v not in used_varnas]
                guess = st.selectbox(f"**{player_name}**", available_varnas, index=None, placeholder="---")
                if guess: player_guesses[p_id], used_varnas.append(guess)
        
        if st.form_submit_button(t('submit_guess')):
            if len(player_guesses) < len(player_ids): st.error(t('error_all_guesses'))
            else:
                varna_map = {VARNA_DETAILS[k][st.session_state.lang]['name']: k for k in VARNA_KEYS}
                state['guesses'][user_id] = {pid: varna_map[vname] for pid, vname in player_guesses.items()}
                save_game_state(state['id'], state)
                st.rerun()

    if st.button(t('reveal_results')):
        state['phase'] = "results"; save_game_state(state['id'], state); st.rerun()

def display_results_phase(state):
    # (Implementation similar to previous versions, with added host 👑)
    st.header(t('results_are_in')); st.subheader(t('true_varnas'))
    truth = state['true_varna_map']
    cols = st.columns(len(state['players']))
    for i, (p_id, p_data) in enumerate(sorted(state['players'].items())):
        with cols[i]:
            player_name = p_data['name'] + (" 👑" if p_data.get('user_id') == state.get('host_user_id') else "")
            true_varna_name = VARNA_DETAILS[truth[p_id]][st.session_state.lang]['name']
            st.metric(label=player_name, value=true_varna_name)

    st.subheader(t('scoring')) # Scoring logic remains similar
    #...
    if st.button(t('start_new_round')): # Reset logic
        #...
        st.rerun()

def display_sidebar(state, user_id):
    with st.sidebar:
        st.title("सत्यासत्यम्")
        st.selectbox("भाषा / Language", options=['sa', 'en'], format_func=lambda x: "संस्कृतम्" if x == 'sa' else "English", key='lang')
        with st.expander(t('how_to_play_title')): st.write(t('how_to_play_content'))
        st.markdown("---")

        if state:
            st.subheader(t('share_the_game'))
            # Note: This requires you to know your app's final URL.
            base_url = "https://your-app-name.streamlit.app" 
            st.code(f"{base_url}/?id={state['id']}")
            
            # Host Controls
            if state.get('host_user_id') == user_id:
                st.subheader(t('host_controls'))
                if st.button(t('end_game'), type="primary", use_container_width=True):
                    filepath = get_game_filepath(state['id'])
                    if os.path.exists(filepath): os.remove(filepath)
                    st.query_params.clear()
                    st.success(t('game_ended_by_host')); time.sleep(2); st.rerun()

def display_player_list(state):
    """Helper to display the list of joined players with host indicator."""
    for p_id in sorted(state['players'].keys()):
        p_data = state['players'][p_id]
        is_host = p_data.get('user_id') == state.get('host_user_id')
        st.write(f"• {p_data['name']}{' 👑' if is_host else ''}")

# --- 5. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="सत्यासत्यम्", layout="centered")
    
    user_id, player_id, game_id, is_viewer = get_session_info()
    state = load_game_state(game_id) if game_id else None

    display_sidebar(state, user_id)
    
    if not game_id:
        display_main_menu()
        return

    if not state:
        st.error(t('game_room_not_found'))
        if st.button(t('go_to_main_menu')): st.query_params.clear(); st.rerun()
        return
    
    # --- Host Transfer Logic ---
    host_id = state.get('host_user_id')
    if host_id and host_id not in state['player_user_ids'].values() and state['phase'] != 'joining':
        # Host has left, find the next player in line to be the new host.
        for p_key in sorted(state['players'].keys()): # player_1, player_2...
            new_host_id = state['players'][p_key].get('user_id')
            if new_host_id:
                state['host_user_id'] = new_host_id
                save_game_state(game_id, state)
                break
    
    # --- Player Assignment Logic ---
    if not player_id and not is_viewer and len(state.get('players', {})) < 4:
        st.session_state.player_id = f"player_{len(state.get('players', {})) + 1}"
        st.rerun()
    elif len(state.get('players', {})) >= 4 and not player_id:
        is_viewer = True

    # --- UI Routing ---
    phase = state['phase']
    if phase == 'joining':
        if is_viewer: st.info(t('waiting_for_players'))
        else: display_joining_phase(state, player_id, user_id)
    elif phase == 'writing':
        if is_viewer: st.info("क्रीडकाः वाक्यानि लिखन्ति...")
        else: display_writing_phase(state, player_id)
    elif phase == 'guessing':
        display_guessing_phase(state, user_id)
    elif phase == 'results':
        display_results_phase(state)

if __name__ == "__main__":
    main()
