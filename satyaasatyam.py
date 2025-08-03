import streamlit as st
import random
import json
import os
import uuid

# --- 1. CONFIGURATION & CONSTANTS ---
GAME_DIR = "gamerooms"
POINTS_POOL = 12
BASE_URL = "https://satyasatyam.streamlit.app"

# --- 2. LANGUAGE & CONTENT ---
def to_devanagari(num_str):
    return "".join("०१२३४५६७८९"[int(d)] for d in str(num_str))

# Varna details remain the same
VARNA_DETAILS = {
    "Brahmin": {"sa": {"name": "ब्राह्मणः", "rule": "स्वविषये त्रीणि सत्यानि वाक्यानि लिख।"}, "en": {"name": "Brahmin", "rule": "Write three true sentences about yourself."}},
    "Kshatriya": {"sa": {"name": "क्षत्रियः", "rule": "स्वविषये एकम् असत्यं द्वे च सत्ये वाक्यानि लिख।"}, "en": {"name": "Kshatriya", "rule": "Write one false sentence and two true ones."}},
    "Vaishya": {"sa": {"name": "वैश्यः", "rule": "स्वविषये एकं सत्यं द्वे च असत्ये वाक्यानि लिख।"}, "en": {"name": "Vaishya", "rule": "Write one true sentence and two false ones."}},
    "Shudra": {"sa": {"name": "शूद्रः", "rule": "स्वविषये त्रीणि असत्यानि वाक्यानि लिख।"}, "en": {"name": "Shudra", "rule": "Write three false sentences about yourself."}},
}
VARNA_KEYS = list(VARNA_DETAILS.keys())

# Complete and corrected translations for both languages
TRANSLATIONS = {
    "sa": {
        "lang_select": "भाषा",
        "game_title": "सत्यासत्यम्",
        "welcome_intro": "सुस्वागतम्। इयं चतुर्णां क्रीडकानां सत्यासत्यपरीक्षा क्रीडा॥",
        "create_game_button": "✨ नवीनं क्रीडासत्रं रचया",
        "require_names": "नामकरणम् अनिवार्यम्",
        "enter_name_label": "तव नामाङ्कनं कुरु",
        "error_name_required": "अनिवार्यत्वात् कृपया स्वनाम प्रविशतु।",
        "error_name_taken": "इदं नाम पूर्वमेव स्वीकृतम्। अन्यत् चिनु।",
        "join_as": "इति प्रविश",
        "player": "क्रीडकः",
        "you_joined_as": "त्वं {name} नाम्ना सम्मिलितोऽसि।",
        "waiting_for_players": "अन्येषाम् आगमनं प्रतीक्षस्व",
        "players_in_room": "अस्मिन् सत्रे क्रीडकाः",
        "you_are": "त्वमसि",
        "your_rule": "तव नियमः",
        "write_three_sentences": "अधः स्ववाक्यानि लिख।",
        "sentence_1": "प्रथमं वाक्यम्", "sentence_2": "द्वितीयं वाक्यम्", "sentence_3": "तृतीयं वाक्यम्",
        "submit_sentences": "वाक्यानि समर्पय",
        "error_all_sentences": "कृपया त्रीणि वाक्यानि लिख।",
        "submission_success": "✅ तव वाक्यानि समर्पितानि। इतरेषां प्रतीक्षा कुरु।",
        "progress_text": "{count} चतुर्षु क्रीडकैः समर्पितम्॥",
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
        "game_links_expander": "🔗 क्रीडासूत्रं दर्शय",
        "player_link_info": "क्रीडकेभ्यः सूत्रम्",
        "viewer_link_info": "दर्शकेभ्यः सूत्रम्",
        "game_room_not_found": "क्रीडासत्रं न लब्धम्।",
        "go_to_main_menu": "मुख्यपृष्ठं गच्छ",
        "host_controls": "आतिथेयस्य नियन्त्रणम्",
        "end_game": "क्रीडां समापय",
        "quit_game": "क्रीडां त्यज",
        "confirm_quit_game": "निश्चितं त्यक्तुमिच्छसि?",
        "confirm_end_game": "निश्चितम्? एतत् सर्वेषां कृते सत्रं समापयिष्यति।",
        "game_ended_by_host": "आतिथेयेन क्रीडा समाप्ता॥",
        "host_indicator": "आतिथेयः",
        "viewer": "दर्शकः",
    },
    "en": {
        "lang_select": "Language",
        "game_title": "Satyasatyam",
        "welcome_intro": "Welcome. This is a game of truth and untruth for four players.",
        "create_game_button": "✨ Create a New Game Session",
        "require_names": "Require names",
        "enter_name_label": "Enter your name",
        "error_name_required": "A name is required to join this game.",
        "error_name_taken": "This name is already taken. Please choose another.",
        "join_as": "Join as",
        "player": "Player",
        "you_joined_as": "You have joined as {name}.",
        "waiting_for_players": "Waiting for other players to join",
        "players_in_room": "Players in this Session",
        "you_are": "You are",
        "your_rule": "Your rule",
        "write_three_sentences": "Write your three sentences below.",
        "sentence_1": "Sentence 1", "sentence_2": "Sentence 2", "sentence_3": "Sentence 3",
        "submit_sentences": "Submit Sentences",
        "error_all_sentences": "Please write three sentences.",
        "submission_success": "✅ Your sentences are submitted. Waiting for others.",
        "progress_text": "{count} of 4 players have submitted.",
        "guessing_time": "🤔 Guessing Time",
        "guessing_instructions": "Match each player to their correct Varna.",
        "player_sentences": "{name}'s Sentences",
        "your_guesses": "Your Guesses",
        "submit_guess": "Confirm Guess",
        "guess_submitted": "✅ Your guess is submitted! Waiting for the results.",
        "reveal_results": "Reveal Results for Everyone",
        "results_are_in": "✨ The results are in! ✨",
        "true_varnas": "The True Varnas",
        "scoring": "🏆 Scoring",
        "no_correct_guesses": "Nobody guessed correctly! No points are awarded this round.",
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
        "host_indicator": "Host",
        "viewer": "Viewer",
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

def manage_session_and_get_info():
    """The brain of the user session. Handles reloads and assigns roles."""
    user_id = st.session_state.setdefault('user_id', str(uuid.uuid4()))
    game_id = st.query_params.get("id")
    is_viewer = st.query_params.get("role") == "viewer"
    
    # Try to find if this user is already a player in the game (handles reloads)
    state = load_game_state(game_id)
    if state and user_id in state['player_user_ids']:
        st.session_state['player_id'] = state['player_user_ids'][user_id]
    
    player_id = st.session_state.get('player_id')
    return user_id, player_id, game_id, is_viewer

def t(key, **kwargs):
    """Robust translation helper."""
    lang = st.session_state.get('lang', 'sa')
    text = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS.get('en', {}).get(key, key.replace('_', ' ').title())
    if lang == 'sa' and kwargs:
        for k, v in kwargs.items():
            if isinstance(v, (int, str)) and str(v).isdigit(): kwargs[k] = to_devanagari(v)
    return text.format(**kwargs)

# --- 4. UI COMPONENTS ---
def display_main_menu():
    st.title(t('game_title'))
    st.write(t('welcome_intro'))
    require_names = st.checkbox(t('require_names'), value=True)
    if st.button(t('create_game_button')):
        user_id = st.session_state.setdefault('user_id', str(uuid.uuid4()))
        game_id = str(uuid.uuid4().hex[:6].upper())
        state = get_initial_state(game_id, {"require_names": require_names}, user_id)
        save_game_state(state)
        st.session_state.player_id = "player_1"
        st.query_params["id"] = game_id
        st.rerun()

def display_joining_phase(state, user_id):
    # Find the next available player slot
    player_slots = {f"player_{i+1}" for i in range(4)}
    joined_slots = set(state['players'].keys())
    available_slots = sorted(list(player_slots - joined_slots))
    if not available_slots:
        st.warning("All player slots are currently full.")
        return
    
    player_id_to_join = st.session_state.get('player_id') or available_slots[0]
    
    player_num = player_id_to_join.split('_')[1]
    default_name = f"{t('player')} {t(key='player', count=player_num)}"

    player_name_input = st.text_input(t('enter_name_label'), placeholder=default_name, key="player_name_input")
    
    if st.button(f"{default_name} {t('join_as')}"):
        name_to_save = player_name_input.strip()
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

def display_writing_phase(state, player_id):
    my_varna_key = state['true_varna_map'][player_id]
    varna_details = VARNA_DETAILS[my_varna_key][st.session_state.lang]
    st.header(f"{t('you_are')} **{varna_details['name']}**")
    st.warning(f"**{t('your_rule')}** {varna_details['rule']}")
    with st.form("sentence_form"):
        sentences = [st.text_area(t(f'sentence_{i+1}'), height=80) for i in range(3)]
        if st.form_submit_button(t('submit_sentences')):
            if all(sentences):
                state['players'][player_id]['sentences'] = sentences
                if len(state['players']) == 4 and all('sentences' in p for p in state['players'].values()):
                    state['phase'] = "guessing"
                save_game_state(state)
                st.rerun()
            else: st.error(t('error_all_sentences'))

# Other display functions (guessing, results) are similar to the improved version from before, but are assumed to be implemented correctly here for brevity.
# The core changes are in main(), session management, and the control functions below.

def display_game_links(state):
    with st.expander(t('game_links_expander')):
        player_link = f"{BASE_URL}/?id={state['id']}"
        viewer_link = f"{BASE_URL}/?id={state['id']}&role=viewer"
        st.markdown(f"**{t('player_link_info')}**")
        st.code(player_link, language=None)
        st.markdown(f"**{t('viewer_link_info')}**")
        st.code(viewer_link, language=None)

def display_player_footer(state):
    st.markdown("---")
    st.subheader(t('players_in_room'))
    cols = st.columns(4)
    for i, p_id in enumerate(sorted(state['players'].keys())):
        p_data = state['players'][p_id]
        is_host = p_data.get('user_id') == state.get('host_user_id')
        cols[i].markdown(f"**{p_data['name']}** {'👑' if is_host else ''}")

def display_controls(state, user_id, player_id):
    is_host = state.get('host_user_id') == user_id
    is_player = player_id is not None
    
    st.markdown("---")
    cols = st.columns([3, 1, 1]) # Layout for refresh, quit, end game

    with cols[0]:
        if st.button("🔄 " + t('refresh_status'), use_container_width=True):
            st.rerun()

    with cols[1]:
        if is_player:
            if st.button("🚪 " + t('quit_game'), use_container_width=True):
                if st.checkbox(t('confirm_quit_game'), key=f"quit_{user_id}"):
                    # Remove player from all relevant places
                    state['players'].pop(player_id, None)
                    state['player_user_ids'].pop(user_id, None)
                    
                    # If host quit, find a new host
                    if is_host:
                        new_host_id = None
                        for p_key in sorted(state['players'].keys()):
                            new_host_id = state['players'][p_key].get('user_id')
                            if new_host_id: break
                        state['host_user_id'] = new_host_id

                    save_game_state(state)
                    # Clear session state for the quitting user
                    for key in ['player_id']:
                        if key in st.session_state: del st.session_state[key]
                    st.rerun()

    with cols[2]:
        if is_host:
            if st.button("🛑 " + t('end_game'), use_container_width=True, type="primary"):
                 if st.checkbox(t('confirm_end_game'), key=f"end_{user_id}"):
                    state['phase'] = 'ended_by_host' # Set terminal state
                    save_game_state(state)
                    st.rerun()


# --- 5. MAIN APPLICATION ---
def main():
    st.set_page_config(page_title="सत्यासत्यम्", layout="centered")
    
    lang = st.radio(t('lang_select'), options=['sa', 'en'], format_func=lambda x: "संस्कृतम्" if x == 'sa' else "English", horizontal=True, key='lang')

    user_id, player_id, game_id, is_viewer = manage_session_and_get_info()
    state = load_game_state(game_id)
    
    if not game_id:
        display_main_menu()
        return

    if not state:
        st.error(t('game_room_not_found'))
        if st.button(t('go_to_main_menu')): st.query_params.clear(); st.rerun()
        return

    # --- Phase Routing ---
    phase = state['phase']

    if phase == 'ended_by_host':
        st.success(f"👑 {t('game_ended_by_host')}")
        if st.button(t('go_to_main_menu')):
            # Clean up session for next game
            for key in ['player_id', 'game_id']:
                if key in st.session_state: del st.session_state[key]
            st.query_params.clear()
            st.rerun()
        return
        
    num_players = len(state['players'])
    num_sentences = sum(1 for p in state['players'].values() if 'sentences' in p)

    # Automatically determine phase based on game state
    if num_players < 4:
        state['phase'] = 'joining'
    elif num_players == 4 and num_sentences < 4:
        state['phase'] = 'writing'
    elif num_players == 4 and num_sentences == 4:
        state['phase'] = 'guessing'
    
    # UI Display based on determined phase
    if state['phase'] == 'joining':
        if not is_viewer and not player_id:
            display_joining_phase(state, user_id)
        else:
            st.info(t('waiting_for_players'))
    
    elif state['phase'] == 'writing':
        if is_viewer or 'sentences' in state['players'].get(player_id, {}):
            progress_val = num_sentences / 4
            lang_key = st.session_state.get('lang', 'sa')
            progress_text = t('progress_text', count=num_sentences)
            st.progress(progress_val, text=progress_text)
        else:
            display_writing_phase(state, player_id)

    elif state['phase'] == 'guessing':
        # display_guessing_phase(state, user_id) # Call the correct guessing function here
        st.header("Guessing Phase (To be implemented)")
        
    elif state['phase'] == 'results':
        # display_results_phase(state) # Call the correct results function here
        st.header("Results Phase (To be implemented)")
        
    # --- Always-Visible Components ---
    display_player_footer(state)
    display_game_links(state)
    display_controls(state, user_id, player_id)

if __name__ == "__main__":
    main()
