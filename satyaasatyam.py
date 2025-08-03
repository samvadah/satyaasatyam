import streamlit as st
import random
import json
import os
import uuid
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# --- CONFIGURATION & CONSTANTS ---
GAME_DIR = "gamerooms"
POINTS_POOL = 12
BASE_URL = "https://satyaasatyam.streamlit.app"
VARNA_KEYS = ["Brahmin", "Kshatriya", "Vaishya", "Shudra"]

# --- LANGUAGE & CONTENT (TRANSLATIONS) ---
def to_devanagari(num_str):
    return "".join("०१२३४५६७८९"[int(d)] for d in str(num_str))

VARNA_DETAILS = {
    "Brahmin": {"sa": {"name": "ब्राह्मणः", "rule": "स्वविषये त्रीणि सत्यानि वाक्यानि लिख।"}, "en": {"name": "Brahmin", "rule": "Write three true sentences about yourself."}},
    "Kshatriya": {"sa": {"name": "क्षत्रियः", "rule": "स्वविषये एकम् असत्यं द्वे च सत्ये वाक्यानि लिख।"}, "en": {"name": "Kshatriya", "rule": "Write one false sentence and two true ones."}},
    "Vaishya": {"sa": {"name": "वैश्यः", "rule": "स्वविषये एकं सत्यं द्वे च असत्ये वाक्यानि लिख।"}, "en": {"name": "Vaishya", "rule": "Write one true sentence and two false ones."}},
    "Shudra": {"sa": {"name": "शूद्रः", "rule": "स्वविषये त्रीणि असत्यानि वाक्यानि लिख।"}, "en": {"name": "Shudra", "rule": "Write three false sentences about yourself."}}
}

TRANSLATIONS = {
    "sa": {
        "game_title": "सत्यासत्यम्", "language_select": "भाषा", "host": "आतिथेयः", "you": "त्वम्",
        "welcome_intro": "सुस्वागतम्। इयं चतुर्णां क्रीडकानां सत्यासत्यपरीक्षा क्रीडा॥",
        "welcome_rules": "अत्र एको ब्राह्मणः सर्वसत्यः क्षत्रियः एकानृतः वैश्यः एकसत्यः शूद्रश्च सर्वानृतः भविष्यति। सर्वेषां वर्णानां सम्यगनुमानमेव तव लक्ष्यम्॥",
        "create_game_button": "✨ नवीनं क्रीडासत्रं रचया", "require_names": "नामकरणम् अनिवार्यम्",
        "share_and_wait_instruction": "इदं सूत्रम् अन्येभ्यः क्रीडकेभ्यः प्रसारय। क्रीडार्थं चतुर्णां क्रीडकानाम् आवश्यकता वर्तते॥",
        "enter_name_label": "तव नामाङ्कनं कुरु", "error_name_required": "कृपया स्वनाम प्रविशतु। नामकरणम् अनिवार्यमस्ति।",
        "join_as": "इति प्रविश", "player": "क्रीडकः", "you_joined_as": "त्वम् अस्मिन् नाम्ना सम्मिलितोऽसि।",
        "waiting_for_players": "अन्येषाम् आगमनं प्रतीक्षस्व। {count} चतुर्षु सम्मिलिताः।",
        "players_in_room": "सत्रस्थाः क्रीडकाः।", "you_are": "त्वमसि", "your_rule": "तव नियमः।",
        "write_three_sentences": "अधः स्ववाक्यानि लिख।", "sentence_1": "प्रथमं वाक्यम्", "sentence_2": "द्वितीयं वाक्यम्", "sentence_3": "तृतीयं वाक्यम्",
        "submit_sentences": "वाक्यानि समर्पय", "error_all_sentences": "कृपया त्रीणि वाक्यानि लिख।",
        "submission_success": "✅ तव वाक्यानि समर्पितानि।", "waiting_for_others_submit": "अन्यक्रीडकानां समर्पणं प्रतीक्षस्व।",
        "players_submitted": "{count} चतुर्षु क्रीडकैः समर्पितम्।", "guessing_time": "🤔 अनुमानपर्व",
        "guessing_instructions": "प्रत्येकस्य क्रीडकस्य वर्णं योजय।", "player_sentences": "{name} इत्यस्य वाक्यानि।",
        "your_guesses": "तव अनुमानानि।", "submit_guess": "अनुमानं निश्चिनु", "error_all_guesses": "कृपया सर्वेषां क्रीडकानां कृते वर्णान् योजय।",
        "guess_submitted": "✅ तवानुमानं समर्पितम्। परिणामान् प्रतीक्षस्व।", "reveal_results": "सर्वेभ्यः परिणामान् प्रकाशयतु",
        "results_are_in": "✨ परिणामाः आगताः ✨", "true_varnas": "यथार्थवर्णाः।", "player_was_a": "{name} वस्तुतः आसीत्",
        "scoring": "🏆 अङ्कगणना।", "no_correct_guesses": "केनचिदपि सम्यक् नानुमितम्। अस्मिन् चक्रे कोऽपि अङ्को न दीयते।",
        "correct_guessers_info": "{count} जनैः सम्यगनुमितम्। तेषु प्रत्येकं **{points} अङ्कान्** प्राप्नोति।",
        "leaderboard": "अङ्कतालिका।", "points": "अङ्काः", "start_new_round": "🔄 नवीनं चक्रमारभस्व",
        "share_the_game": "🔗 क्रीडां प्रसारय", "player_link_info": "क्रीडकसङ्केतः", "viewer_link_info": "दर्शक सङ्केतः",
        "game_full_warning": "इयं क्रीडा पूर्णा। त्वं दर्शकत्वेन सम्मिलितोऽसि।", "game_room_not_found": "क्रीडासत्रं न लब्धम्।",
        "go_to_main_menu": "मुख्यपृष्ठं गच्छ", "viewer": "दर्शकः", "guesser_a_viewer": "एको दर्शकः",
        "you_are_host": "त्वम् आतिथेयः असि।", "host_transfer_notice": "आतिथेयः क्रीडातः निर्गतः। त्वम् इदानीं नूतनः आतिथेयः।",
        "end_game": "क्रीडां समापय", "confirm_end_game": "निश्चितं क्रीडां समापयितुमिच्छसि? एतत् सर्वेषां कृते सत्रं निष्कासयिष्यति।",
        "game_ended_by_host": "आतिथेयेन क्रीडा समापिता।", "quit_game": "क्रीडातः निर्गच्छ", "confirm_quit_game": "निश्चितं निर्गन्तुमिच्छसि?",
        "rules": "क्रीडानियमाः।", "share_button": "प्रसारय", "link_copied": "सङ्केतः प्रतिलिपितः।"
    },
    "en": {
        "game_title": "Satyasatyam", "language_select": "Language", "host": "Host", "you": "You",
        "welcome_intro": "Welcome. This is a four-player game to test truth and untruth.",
        "welcome_rules": "Here, one will be the all-truth Brahmin, one the one-lie Kshatriya, one the one-truth Vaishya, and one the all-lie Shudra. Your goal is to correctly guess everyone's Varna.",
        "create_game_button": "✨ Create a New Game Room", "require_names": "Require names",
        "share_and_wait_instruction": "Share this link with other players. You need four players to start the game.",
        "enter_name_label": "Enter your name", "error_name_required": "Please enter your name. It is required for this game.",
        "join_as": "Join as", "player": "Player", "you_joined_as": "You have joined.",
        "waiting_for_players": "Waiting for other players... {count} of four have joined.",
        "players_in_room": "Players in this Room:", "you_are": "You are the", "your_rule": "Your Rule:",
        "write_three_sentences": "Write your three sentences below.", "sentence_1": "Sentence 1", "sentence_2": "Sentence 2", "sentence_3": "Sentence 3",
        "submit_sentences": "Submit Sentences", "error_all_sentences": "Please write all three sentences.",
        "submission_success": "✅ Your sentences have been submitted.", "waiting_for_others_submit": "Waiting for other players to submit...",
        "players_submitted": "{count}/{total} players have submitted.", "guessing_time": "🤔 Guessing Time!",
        "guessing_instructions": "Match each player to their Varna.", "player_sentences": "{name}'s Sentences:",
        "your_guesses": "Your Guesses:", "submit_guess": "Submit Guess", "error_all_guesses": "Please assign a Varna to every player.",
        "guess_submitted": "✅ Your guess has been submitted! Waiting for results.", "reveal_results": "Reveal Results for Everyone",
        "results_are_in": "✨ Results Are In! ✨", "true_varnas": "The True Varnas:", "player_was_a": "{name} was actually the",
        "scoring": "🏆 Scoring:", "no_correct_guesses": "Nobody guessed everything correctly! No points awarded this round.",
        "correct_guessers_info": "{count} person/people guessed correctly! They each get **{points} points**.",
        "leaderboard": "Leaderboard:", "points": "points", "start_new_round": "🔄 Start a New Round",
        "share_the_game": "🔗 Share the Game", "player_link_info": "Player Link", "viewer_link_info": "Viewer Link",
        "game_full_warning": "This game is full. You have joined as a viewer.", "game_room_not_found": "Game room not found.",
        "go_to_main_menu": "Go to Main Menu", "viewer": "Viewer", "guesser_a_viewer": "A Viewer",
        "you_are_host": "You are the host.", "host_transfer_notice": "The host has quit. You are the new host.",
        "end_game": "End Game", "confirm_end_game": "Are you sure you want to end the game? This will delete the session for everyone.",
        "game_ended_by_host": "The game was ended by the host.", "quit_game": "Quit Game", "confirm_quit_game": "Are you sure you want to quit?",
        "rules": "Game Rules:", "share_button": "Share", "link_copied": "Link copied!"
    }
}

# --- STATE MANAGEMENT & HELPERS ---
def get_game_filepath(game_id): return os.path.join(GAME_DIR, f"{game_id}.json")
def load_game_state(game_id):
    if not game_id: return None
    try:
        with open(get_game_filepath(game_id), 'r', encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return None
def save_game_state(state):
    if not state: return
    os.makedirs(GAME_DIR, exist_ok=True)
    with open(get_game_filepath(state['id']), 'w', encoding='utf-8') as f: json.dump(state, f, indent=2, ensure_ascii=False)
def get_initial_state(game_id, settings):
    shuffled_varnas = random.sample(VARNA_KEYS, len(VARNA_KEYS))
    return {"id": game_id, "phase": "joining", "players": {}, "host_id": get_user_session()['user_id'],
            "player_user_ids": {}, "true_varna_map": {f"player_{i+1}": varna for i, varna in enumerate(shuffled_varnas)},
            "guesses": {}, "scores": {}, "settings": settings}
def get_user_session():
    if "user_id" not in st.session_state: st.session_state.user_id = str(uuid.uuid4())
    return {"user_id": st.session_state.user_id, "player_id": st.session_state.get("player_id")}
def re_establish_session(state, user_id):
    if 'player_id' not in st.session_state:
        for p_id, u_id in state.get("player_user_ids", {}).items():
            if u_id == user_id: st.session_state.player_id = p_id; return
def t(key, **kwargs):
    lang = st.session_state.get('lang', 'sa')
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    if lang == 'sa':
        for k, v in kwargs.items():
            if isinstance(v, (int, str)) and str(v).isdigit(): kwargs[k] = to_devanagari(str(v))
    return text.format(**kwargs)

# --- UI COMPONENTS ---
def display_sidebar(state, session):
    with st.sidebar:
        st.title("सत्यासत्यम्")
        st.selectbox(t('language_select'), options=['sa', 'en'], format_func=lambda x: "संस्कृतम्" if x == 'sa' else "English", key='lang')
        st.markdown("---")
        if state and state['phase'] != 'aborted':
            if session.get('player_id'): display_game_controls(state, session)
            st.subheader(t('players_in_room'))
            display_player_list(state, session)
            st.markdown("---")
            st.subheader(t('rules'))
            for varna_key in VARNA_KEYS:
                details = VARNA_DETAILS[varna_key][st.session_state.lang]
                st.markdown(f"**{details['name']}**। {details['rule']}")
def display_player_list(state, session):
    for p_id in sorted(state['players'].keys()):
        player_name = state['players'][p_id]['name']
        is_you = p_id == session.get('player_id')
        is_host = state.get('player_user_ids', {}).get(p_id) == state.get('host_id')
        you_marker = f" ॥ {t('you')} ॥" if is_you else ""
        host_marker = "👑 " if is_host else ""
        st.markdown(f"• {host_marker}{player_name}{you_marker}")
def display_game_controls(state, session):
    is_host = state.get('host_id') == session['user_id']
    if is_host: st.success(t('you_are_host'))
    if st.button(t('quit_game'), use_container_width=True):
        if st.checkbox(t('confirm_quit_game'), key=f"quit_{session['user_id']}"):
            player_id_to_remove = session['player_id']
            if player_id_to_remove in state['players']:
                del state['players'][player_id_to_remove]
                if player_id_to_remove in state['player_user_ids']: del state['player_user_ids'][player_id_to_remove]
                if is_host: # Host transfer logic
                    if state['player_user_ids']:
                        next_host_pid = sorted(state['player_user_ids'].keys())[0]; state['host_id'] = state['player_user_ids'][next_host_pid]
                    else: state['phase'] = 'aborted'
                if len(state['players']) < 4 and state['phase'] != 'joining': state['phase'] = 'aborted'
                save_game_state(state)
                st.session_state.player_id = None; st.rerun()
    if is_host:
        if st.button(t('end_game'), use_container_width=True, type="primary"):
            if st.checkbox(t('confirm_end_game'), key=f"end_{session['user_id']}"): state['phase'] = 'aborted'; save_game_state(state); st.rerun()
def one_click_copy_button(element_id, button_text, button_key):
    js = f"""
        <script>
        function copyToClipboard(elementId, button) {{
            const input = document.getElementById(elementId);
            navigator.clipboard.writeText(input.value).then(() => {{
                button.innerText = "{t('link_copied')}";
                setTimeout(() => {{ button.innerText = "{button_text}"; }}, 2000);
            }});
        }}
        const button{button_key} = document.getElementById('{button_key}');
        if (button{button_key}) {{
            button{button_key}.onclick = function() {{
                copyToClipboard('{element_id}', button{button_key});
            }}
        }}
        </script>
        <button id="{button_key}" style='width: 100%;'>{button_text}</button>
    """
    return components.html(js, height=38)
def display_game_links(state):
    with st.expander(t('share_the_game'), expanded=True):
        player_link = f"{BASE_URL}?id={state['id']}"; viewer_link = f"{player_link}&role=viewer"
        st.caption(t('player_link_info')); col1, col2 = st.columns([4, 1])
        with col1: st.text_input("Player Link", value=player_link, key="pl_link_input", label_visibility="collapsed")
        with col2: one_click_copy_button("pl_link_input", "📋", "copy_player_btn")
        st.markdown(f'<a href="https://api.whatsapp.com/send?text=Join my Satyasatyam game: {player_link}" target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>', unsafe_allow_html=True)
        st.markdown("---")
        st.caption(t('viewer_link_info')); col3, col4 = st.columns([4, 1])
        with col3: st.text_input("Viewer Link", value=viewer_link, key="v_link_input", label_visibility="collapsed")
        with col4: one_click_copy_button("v_link_input", "📋", "copy_viewer_btn")
        st.markdown(f'<a href="https://api.whatsapp.com/send?text=Watch this Satyasatyam game: {viewer_link}" target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>', unsafe_allow_html=True)
def display_main_menu():
    st.title(t('game_title'))
    st.write(t('welcome_intro')); st.write(t('welcome_rules'))
    require_names = st.checkbox(t('require_names'), value=True)
    if st.button(t('create_game_button')):
        session = get_user_session()
        state = get_initial_state(str(uuid.uuid4().hex[:6].upper()), {"require_names": require_names})
        st.session_state.player_id = "player_1"
        state['player_user_ids']['player_1'] = session['user_id']
        save_game_state(state); st.query_params["id"] = state['id']; st.rerun()

# --- GAME PHASE DISPLAYS ---
def display_joining_phase(state, session):
    # This block now handles players joining and displays the correct info
    st.success(f"{t('you_joined_as')} **{state['players'][session['player_id']]['name']}**")
    if len(state['players']) < 4: st.info(t('share_and_wait_instruction'))
def display_name_entry(state, session):
    # This block handles the initial name entry
    player_id, user_id = session['player_id'], session['user_id']
    if not player_id: # A returning user or new user needs a slot
        if user_id in state['player_user_ids'].values(): re_establish_session(state, user_id)
        else:
            available_slots = [f"player_{i+1}" for i in range(4) if f"player_{i+1}" not in state['player_user_ids']]
            if not available_slots: st.warning(t('game_full_warning')); return
            st.session_state.player_id = available_slots[0]
            state['player_user_ids'][st.session_state.player_id] = user_id; save_game_state(state)
        player_id = st.session_state.player_id
    
    player_num_str = to_devanagari(player_id.split('_')[-1]) if st.session_state.lang == 'sa' else player_id.split('_')[-1]
    default_name = f"{t('player')} {player_num_str}"
    player_name = st.text_input(t('enter_name_label'), placeholder=default_name)
    if st.button(f"{default_name} {t('join_as')}"):
        name_to_save = player_name.strip()
        if state['settings'].get('require_names', False) and not name_to_save: st.error(t('error_name_required'))
        else:
            state['players'][player_id] = {"name": name_to_save or default_name, "sentences": None, "submitted": False}
            if len(state['players']) == 4: state['phase'] = "writing"
            save_game_state(state); st.rerun()
def display_writing_phase(state, session):
    st.success(f"{t('you_joined_as')} **{state['players'][session['player_id']]['name']}**")
    player_data = state['players'][session['player_id']]
    if player_data['submitted']:
        st.success(t('submission_success'))
        submitted_count = sum(1 for p in state['players'].values() if p['submitted'])
        total_players_str = to_devanagari('4') if st.session_state.lang == 'sa' else '4'
        progress_text = t('players_submitted', count=submitted_count, total=total_players_str)
        st.progress(submitted_count / 4, text=progress_text)
        return
    my_varna_key = state['true_varna_map'][session['player_id']]
    varna_details = VARNA_DETAILS[my_varna_key][st.session_state.lang]
    st.header(f"{t('you_are')} **{varna_details['name']}**")
    st.warning(f"**{t('your_rule')}**")
    with st.form("sentence_form"):
        s1 = st.text_area(t('sentence_1'), key="s1", height=80); s2 = st.text_area(t('sentence_2'), key="s2", height=80); s3 = st.text_area(t('sentence_3'), key="s3", height=80)
        if st.form_submit_button(t('submit_sentences')):
            if not all([s1, s2, s3]): st.error(t('error_all_sentences'))
            else:
                player_data['sentences'] = [s1, s2, s3]; player_data['submitted'] = True
                if all(p['submitted'] for p in state['players'].values()): state['phase'] = "guessing"
                save_game_state(state); st.rerun()
def display_match_the_following_guessing(state, session):
    if session['user_id'] in state['guesses']: st.success(t('guess_submitted')); return
    st.header(t('guessing_time')); st.info(t('guessing_instructions'))
    for p_id, p_data in sorted(state['players'].items()):
        sent_nums = [to_devanagari(str(n)) for n in [1, 2, 3]] if st.session_state.lang == 'sa' else ['1', '2', '3']
        with st.expander(t('player_sentences', name=p_data['name']), expanded=True):
            st.markdown(f"{sent_nums[0]}। *{p_data['sentences'][0]}*\n\n{sent_nums[1]}। *{p_data['sentences'][1]}*\n\n{sent_nums[2]}। *{p_data['sentences'][2]}*")
    st.subheader(t('your_guesses'))
    player_ids = sorted(state['players'].keys())
    varna_options = [VARNA_DETAILS[key][st.session_state.lang]['name'] for key in VARNA_KEYS]
    if 'guesses' not in st.session_state: st.session_state.guesses = {p_id: None for p_id in player_ids}
    
    cols = st.columns(len(player_ids))
    current_guesses = {p_id: st.session_state.get(f"guess_{p_id}") for p_id in player_ids}
    for i, p_id in enumerate(player_ids):
        with cols[i]:
            player_name = state['players'][p_id]['name']
            used_varnas = [v for v in current_guesses.values() if v is not None and v != current_guesses[p_id]]
            available_varnas = [v for v in varna_options if v not in used_varnas]
            st.selectbox(f"**{player_name}**", available_varnas, index=None, placeholder="---", key=f"guess_{p_id}")

    if st.button(t('submit_guess'), use_container_width=True):
        final_guesses = {pid: st.session_state.get(f"guess_{pid}") for pid in player_ids}
        if any(v is None for v in final_guesses.values()): st.error(t('error_all_guesses'))
        else:
            varna_name_to_key_map = {VARNA_DETAILS[key][st.session_state.lang]['name']: key for key in VARNA_KEYS}
            state['guesses'][session['user_id']] = {p_id: varna_name_to_key_map[v_name] for p_id, v_name in final_guesses.items()}
            del st.session_state.guesses; save_game_state(state); st.rerun()
def display_results_phase(state):
    st.header(t('results_are_in')); st.subheader(t('true_varnas'))
    truth = state['true_varna_map']; cols = st.columns(len(state['players']))
    for i, (p_id, p_data) in enumerate(sorted(state['players'].items())):
        with cols[i]: st.metric(label=t('player_was_a', name=p_data['name']), value=VARNA_DETAILS[truth[p_id]][st.session_state.lang]['name'])
    st.subheader(t('scoring')); correct_guessers = []
    for user_id, guess in state['guesses'].items():
        if guess == truth:
            guesser_name = next((p['name'] for p_id, p in state['players'].items() if state.get('player_user_ids', {}).get(p_id) == user_id), f"{t('guesser_a_viewer')} ॥ {user_id[:6]} ॥")
            correct_guessers.append(guesser_name)
    if not correct_guessers: st.warning(t('no_correct_guesses'))
    else:
        points_per_winner = POINTS_POOL // len(correct_guessers)
        st.success(t('correct_guessers_info', count=len(correct_guessers), points=points_per_winner))
        for name in correct_guessers: st.write(f"🎉 **{name}**"); state['scores'][name] = state['scores'].get(name, 0) + points_per_winner
    save_game_state(state)
    st.subheader(t('leaderboard'))
    if state.get('scores'):
        for name, score in sorted(state['scores'].items(), key=lambda item: item[1], reverse=True):
            points_str = to_devanagari(str(score)) if st.session_state.lang == 'sa' else str(score)
            st.markdown(f"**{name}**। {points_str} {t('points')}")
    if st.button(t('start_new_round')):
        new_state = get_initial_state(state['id'], state['settings'])
        new_state.update({'players': {p_id: {"name": p_data["name"], "sentences": None, "submitted": False} for p_id, p_data in state['players'].items()},
                          'player_user_ids': state['player_user_ids'], 'phase': 'writing', 'scores': state.get('scores', {}), 'host_id': state.get('host_id')})
        save_game_state(new_state); st.rerun()

# --- MAIN LOGIC ---
def main():
    st.set_page_config(page_title="सत्यासत्यम्", layout="centered", initial_sidebar_state="expanded")
    session = get_user_session()
    game_id = st.query_params.get("id")
    state = load_game_state(game_id)
    if state:
        re_establish_session(state, session['user_id'])
        session = get_user_session() # Re-fetch session state after potential update
        if state['phase'] != 'joining': st_autorefresh(interval=2000, limit=None, key="game_refresher")
    
    display_sidebar(state, session)
    if not state:
        display_main_menu();
        if game_id: st.error(t('game_room_not_found'))
        return
    
    if state['phase'] == 'aborted':
        st.info(t('game_ended_by_host'))
        if st.button(t('go_to_main_menu')): st.query_params.clear(); st.rerun()
    elif state['phase'] == 'joining':
        if session['player_id'] not in state['players']: display_name_entry(state, session)
        else: display_joining_phase(state, session)
    elif session['player_id'] in state['players']: # Player is fully in the game
        if state['phase'] == 'writing': display_writing_phase(state, session)
        elif state['phase'] == 'guessing': display_match_the_following_guessing(state, session)
        elif state['phase'] == 'results': display_results_phase(state)
    
    if state and state['phase'] != 'aborted': display_game_links(state)

if __name__ == "__main__":
    main()
