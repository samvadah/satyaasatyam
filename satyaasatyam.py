import streamlit as st
import random
import json
import os
import uuid
from urllib.parse import urlunparse, urlencode

# --- CONFIGURATION & CONSTANTS ---
GAME_DIR = "gamerooms"
POINTS_POOL = 12

# --- HELPER: Devanagari Numerals ---
def to_devanagari(num_str):
    """Converts Roman numerals (as strings) to Devanagari."""
    return "".join("०१२३४५६७८९"[int(d)] for d in str(num_str))

# --- LANGUAGE & CONTENT (TRANSLATIONS) ---
VARNA_DETAILS = {
    "Brahmin": {
        "sa": {"name": "ब्राह्मणः", "rule": "स्वविषये त्रीणि सत्यानि वाक्यानि लिख।"},
        "en": {"name": "Brahmin", "rule": "Write three true sentences about yourself."}
    },
    "Kshatriya": {
        "sa": {"name": "क्षत्रियः", "rule": "स्वविषये एकम् असत्यं द्वे च सत्ये वाक्यानि लिख।"},
        "en": {"name": "Kshatriya", "rule": "Write one false sentence and two true ones."}
    },
    "Vaishya": {
        "sa": {"name": "वैश्यः", "rule": "स्वविषये एकं सत्यं द्वे च असत्ये वाक्यानि लिख।"},
        "en": {"name": "Vaishya", "rule": "Write one true sentence and two false ones."}
    },
    "Shudra": {
        "sa": {"name": "शूद्रः", "rule": "स्वविषये त्रीणि असत्यानि वाक्यानि लिख।"},
        "en": {"name": "Shudra", "rule": "Write three false sentences about yourself."}
    }
}
VARNA_KEYS = list(VARNA_DETAILS.keys())

TRANSLATIONS = {
    "sa": {
        "game_title": "सत्यासत्यम्",
        "welcome_intro": "सुस्वागतम्। इयं चतुर्णां क्रीडकानां सत्यासत्यपरीक्षा क्रीडा॥",
        "welcome_rules": "अत्र एको ब्राह्मणः सर्वसत्यः क्षत्रियः एकानृतः वैश्यः एकसत्यः शूद्रश्च सर्वानृतः भविष्यति। सर्वेषां वर्णानां सम्यगनुमानमेव तव लक्ष्यम्॥",
        "create_game_button": "✨ नवीनं क्रीडासत्रं रचया",
        "require_names": "नामकरणम् अनिवार्यम्",
        "enter_name_label": "तव नामाङ्कनं कुरु",
        "error_name_required": "कृपया स्वनाम प्रविशतु। नामकरणम् अनिवार्यमस्ति।",
        "join_as": "इति प्रविश",
        "player": "क्रीडकः",
        "you_joined_as": "त्वम् अस्मिन् नाम्ना सम्मिलितोऽसि",
        "waiting_for_players": "अन्येषाम् आगमनं प्रतीक्षस्व। {count} चतुर्षु सम्मिलिताः।",
        "players_in_room": "अस्मिन् सत्रे क्रीडकाः",
        "you_are": "त्वमसि",
        "your_rule": "तव नियमः",
        "write_three_sentences": "अधः स्ववाक्यानि लिख।",
        "sentence_1": "प्रथमं वाक्यम्",
        "sentence_2": "द्वितीयं वाक्यम्",
        "sentence_3": "तृतीयं वाक्यम्",
        "submit_sentences": "वाक्यानि समर्पय",
        "error_all_sentences": "कृपया त्रीणि वाक्यानि लिख।",
        "submission_success": "✅ तव वाक्यानि समर्पितानि।",
        "waiting_for_others_submit": "अन्यक्रीडकानां समर्पणं प्रतीक्षस्व।",
        "players_submitted": "{count} चतुर्षु क्रीडकैः समर्पितम्।",
        "guessing_time": "🤔 अनुमानपर्व",
        "guessing_instructions": "प्रत्येकस्य क्रीडकस्य वर्णं योजय।",
        "player_sentences": "{name} इत्यस्य वाक्यानि",
        "your_guesses": "तव अनुमानानि",
        "submit_guess": "अनुमानं निश्चिनु",
        "error_all_guesses": "कृपया सर्वेषां क्रीडकानां कृते वर्णान् योजय।",
        "guess_submitted": "✅ तवानुमानं समर्पितम्। परिणामान् प्रतीक्षस्व।",
        "reveal_results": "सर्वेषां परिणामान् प्रकाशय",
        "results_are_in": "✨ परिणामाः आगताः ✨",
        "true_varnas": "यथार्थवर्णाः",
        "player_was_a": "{name} वस्तुतः आसीत्",
        "scoring": "🏆 अङ्कगणना",
        "no_correct_guesses": "केनचिदपि सम्यक् नानुमितम्। अस्मिन् चक्रे कोऽपि अङ्को न दीयते।",
        "correct_guessers_info": "{count} जनैः सम्यगनुमितम्। तेषु प्रत्येकं **{points} अङ्कान्** प्राप्नोति।",
        "leaderboard": "अङ्कतालिका",
        "points": "अङ्काः",
        "start_new_round": "🔄 नवीनं चक्रमारभस्व",
        "share_the_game": "🔗 क्रीडासूत्रम्",
        "player_link_info": "क्रीडकेभ्यः सूत्रम्",
        "viewer_link_info": "दर्शकेभ्यः सूत्रम्",
        "game_full_warning": "इयं क्रीडा पूर्णा। त्वं दर्शकत्वेन सम्मिलितोऽसि।",
        "game_room_not_found": "क्रीडासत्रं न लब्धम्।",
        "go_to_main_menu": "मुख्यपृष्ठं गच्छ",
        "refresh_status": "🔄 स्थितिं नवीकुरु",
        "viewer": "दर्शकः",
        "guesser_a_viewer": "एको दर्शकः",
        "host_controls": "यजमानस्य नियन्त्रणम्",
        "end_game": "क्रीडां समापय",
        "confirm_end_game": "निश्चितं क्रीडां समापयितुमिच्छसि? एतत् सर्वेषां कृते सत्रं निष्कासयिष्यति।",
        "game_ended_by_host": "यजमानेन क्रीडा समापिता।",
    },
    # (English translations are omitted for brevity, but would be here in a real file)
    "en": { "game_title": "Satyasatyam", "welcome_intro": "Welcome!", "require_names": "Require names", "host_controls": "Host Controls", "end_game": "End Game", "confirm_end_game": "Are you sure you want to end the game? This will delete the session for everyone.", "game_ended_by_host": "The game was ended by the host.", "player_link_info": "Player Link", "viewer_link_info": "Viewer Link", # ... and so on
    }
}

# --- STATE MANAGEMENT ---
def get_game_filepath(game_id):
    return os.path.join(GAME_DIR, f"{game_id}.json")

def get_initial_state(game_id, settings):
    shuffled_varnas = random.sample(VARNA_KEYS, len(VARNA_KEYS))
    return {
        "id": game_id, "phase": "joining", "players": {}, "host_id": None,
        "true_varna_map": {f"player_{i+1}": varna for i, varna in enumerate(shuffled_varnas)},
        "guesses": {}, "scores": {}, "settings": settings
    }

def load_game_state(game_id):
    filepath = get_game_filepath(game_id)
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return None

def save_game_state(game_id, state):
    os.makedirs(GAME_DIR, exist_ok=True)
    filepath = get_game_filepath(game_id)
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(state, f, indent=2, ensure_ascii=False)

def get_user_id():
    if 'user_id' not in st.session_state: st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def t(key, **kwargs):
    """Translation helper function."""
    lang = st.session_state.get('lang', 'sa')
    # Simple fallback to English if a key is missing in Sanskrit
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))
    
    # Format with Devanagari numerals if in Sanskrit mode
    if lang == 'sa':
        for k, v in kwargs.items():
            if isinstance(v, (int, str)) and str(v).isdigit():
                kwargs[k] = to_devanagari(v)
    return text.format(**kwargs)

# --- UI COMPONENTS ---
def display_main_menu():
    st.title(t('game_title'))
    st.write(t('welcome_intro'))
    st.write(t('welcome_rules'))
    
    require_names = st.checkbox(t('require_names'), value=False)
    
    if st.button(t('create_game_button')):
        game_id = str(uuid.uuid4().hex[:6].upper())
        settings = {"require_names": require_names}
        state = get_initial_state(game_id, settings)
        state['host_id'] = get_user_id() # The creator is the host
        save_game_state(game_id, state)
        
        st.session_state.game_id = game_id
        st.session_state.player_id = "player_1"
        st.query_params["id"] = game_id
        st.rerun()

def display_joining_phase(state, player_id):
    game_id = state['id']
    player_num = player_id.split('_')[1]
    
    if player_id not in state['players']:
        default_name = f"{t('player')} {t(key='', count=player_num)}" # Hack to translate number
        player_name = st.text_input(t('enter_name_label'), placeholder=default_name)
        
        if st.button(f"{default_name} {t('join_as')}"):
            name_to_save = player_name.strip()
            if state['settings'].get('require_names', False) and not name_to_save:
                st.error(t('error_name_required'))
            else:
                if not name_to_save: name_to_save = default_name
                state['players'][player_id] = {"name": name_to_save, "sentences": None, "submitted": False}
                if not state['scores'].get(name_to_save): state['scores'][name_to_save] = 0
                save_game_state(game_id, state)
                st.rerun()
    else:
        st.success(f"**{t('you_joined_as')} {state['players'][player_id]['name']}।**")
        if len(state['players']) == 4:
            state['phase'] = "writing"
            save_game_state(game_id, state)
            st.rerun()
        else:
            st.info(t('waiting_for_players', count=len(state['players'])))
            st.write(f"**{t('players_in_room')}**")
            for p_data in state['players'].values(): st.write(f"• {p_data['name']}")

def display_writing_phase(state, player_id):
    game_id = state['id']
    player_data = state['players'][player_id]
    
    if player_data['submitted']:
        st.success(t('submission_success'))
        submitted_count = sum(1 for p in state['players'].values() if p['submitted'])
        st.progress(submitted_count / 4, text=t('players_submitted', count=submitted_count))
        return

    my_varna_key = state['true_varna_map'][player_id]
    varna_details = VARNA_DETAILS[my_varna_key][st.session_state.lang]
    st.header(f"{t('you_are')} **{varna_details['name']}**")
    st.warning(f"**{t('your_rule')}** {varna_details['rule']}")

    with st.form("sentence_form"):
        st.write(t('write_three_sentences'))
        s1 = st.text_area(t('sentence_1'), key="s1", height=80)
        s2 = st.text_area(t('sentence_2'), key="s2", height=80)
        s3 = st.text_area(t('sentence_3'), key="s3", height=80)
        
        if st.form_submit_button(t('submit_sentences')):
            if not all([s1, s2, s3]): st.error(t('error_all_sentences'))
            else:
                player_data['sentences'] = [s1, s2, s3]
                player_data['submitted'] = True
                if all(p['submitted'] for p in state['players'].values()): state['phase'] = "guessing"
                save_game_state(game_id, state)
                st.rerun()

def display_match_the_following_guessing(state):
    if get_user_id() in state['guesses']:
        st.success(t('guess_submitted'))
        return

    st.header(t('guessing_time'))
    st.info(t('guessing_instructions'))

    for p_id, p_data in sorted(state['players'].items()):
        player_num = p_id.split('_')[-1]
        sent_num_1, sent_num_2, sent_num_3 = (t(key='', count=n) for n in ['1', '2', '3'])
        with st.expander(t('player_sentences', name=p_data['name']), expanded=True):
            st.markdown(f"{sent_num_1}. *{p_data['sentences'][0]}*\n\n{sent_num_2}. *{p_data['sentences'][1]}*\n\n{sent_num_3}. *{p_data['sentences'][2]}*")

    with st.form("guessing_form"):
        st.subheader(t('your_guesses'))
        
        player_ids = sorted(state['players'].keys())
        all_varna_names = [VARNA_DETAILS[key][st.session_state.lang]['name'] for key in VARNA_KEYS]
        
        player_guesses = {}
        used_varnas = []
        
        cols = st.columns(len(player_ids))
        for i, p_id in enumerate(player_ids):
            with cols[i]:
                player_name = state['players'][p_id]['name']
                available_varnas = [v for v in all_varna_names if v not in used_varnas]
                
                guess = st.selectbox(f"**{player_name}**", options=available_varnas, index=None, placeholder="---")
                if guess:
                    player_guesses[p_id] = guess
                    used_varnas.append(guess)
        
        if st.form_submit_button(t('submit_guess')):
            if len(player_guesses) < len(player_ids):
                st.error(t('error_all_guesses'))
            else:
                varna_name_to_key_map = {VARNA_DETAILS[key][st.session_state.lang]['name']: key for key in VARNA_KEYS}
                final_guess_map = {p_id: varna_name_to_key_map[v_name] for p_id, v_name in player_guesses.items()}
                
                state['guesses'][get_user_id()] = final_guess_map
                save_game_state(state['id'], state)
                st.rerun()

    if st.button(t('reveal_results')):
        state['phase'] = "results"
        save_game_state(state['id'], state)
        st.rerun()

def display_results_phase(state):
    st.header(t('results_are_in'))
    st.subheader(t('true_varnas'))
    truth = state['true_varna_map']
    cols = st.columns(len(state['players']))
    for i, (p_id, p_data) in enumerate(sorted(state['players'].items())):
        with cols[i]:
            true_varna_name = VARNA_DETAILS[truth[p_id]][st.session_state.lang]['name']
            st.metric(label=t('player_was_a', name=p_data['name']), value=true_varna_name)

    st.subheader(t('scoring'))
    correct_guessers = []
    for user_id, guess in state['guesses'].items():
        if guess == truth:
            guesser_name = None
            for p_id, p_data in state['players'].items():
                if state.get('player_user_ids', {}).get(p_id) == user_id:
                    guesser_name = p_data['name']
                    break
            if not guesser_name: guesser_name = f"{t('guesser_a_viewer')} ({user_id[:6]})"
            correct_guessers.append(guesser_name)

    if not correct_guessers: st.warning(t('no_correct_guesses'))
    else:
        points_per_winner = POINTS_POOL // len(correct_guessers)
        st.success(t('correct_guessers_info', count=len(correct_guessers), points=points_per_winner))
        for name in correct_guessers:
            st.write(f"🎉 **{name}**")
            state['scores'][name] = state['scores'].get(name, 0) + points_per_winner
                
    save_game_state(state['id'], state)

    st.subheader(t('leaderboard'))
    if state.get('scores'):
        sorted_scores = sorted(state['scores'].items(), key=lambda item: item[1], reverse=True)
        for name, score in sorted_scores: st.markdown(f"**{name}** `{t(key='', points=score)} {t('points')}`")

    if st.button(t('start_new_round')):
        new_state = get_initial_state(state['id'], state['settings'])
        new_state['players'] = {p_id: {"name": p_data["name"], "sentences": None, "submitted": False} for p_id, p_data in state['players'].items()}
        new_state['phase'] = 'writing'
        new_state['scores'] = state.get('scores', {})
        new_state['host_id'] = state.get('host_id')
        save_game_state(state['id'], new_state)
        st.rerun()

def display_sidebar(state):
    with st.sidebar:
        st.title("सत्यासत्यम्")
        st.selectbox("भाषा / Language", options=['sa', 'en'], format_func=lambda x: "संस्कृतम्" if x == 'sa' else "English", key='lang')
        st.markdown("---")

        if state:
            # Game Links
            st.subheader(t('share_the_game'))
            base_url = "https://<your-app-name>.streamlit.app" # Placeholder
            player_link = f"{base_url}/?id={state['id']}"
            viewer_link = f"{base_url}/?id={state['id']}&role=viewer"
            st.caption(t('player_link_info'))
            st.code(player_link)
            st.caption(t('viewer_link_info'))
            st.code(viewer_link)
            st.info("Replace `<your-app-name>.streamlit.app` with your actual app's URL.")
            st.markdown("---")

            # Host Controls
            if state.get('host_id') == get_user_id():
                st.subheader(t('host_controls'))
                if st.button(t('end_game'), type="primary"):
                    if st.checkbox(t('confirm_end_game')):
                        filepath = get_game_filepath(state['id'])
                        if os.path.exists(filepath): os.remove(filepath)
                        st.query_params.clear()
                        st.success(t('game_ended_by_host'))
                        st.rerun()

        st.button(t('refresh_status'), key="manual_refresh", use_container_width=True)

# --- MAIN APP LOGIC ---
def main():
    st.set_page_config(page_title="सत्यासत्यम्", layout="centered")

    game_id = st.query_params.get("id")
    state = load_game_state(game_id) if game_id else None

    display_sidebar(state)
    
    if not game_id:
        display_main_menu()
        return

    if not state:
        st.error(t('game_room_not_found'))
        if st.button(t('go_to_main_menu')):
            st.query_params.clear()
            st.rerun()
        return

    is_viewer = st.query_params.get("role") == "viewer"
    if not is_viewer:
        if 'player_id' not in st.session_state:
            num_players = len(state.get('players', {}))
            if num_players < 4: st.session_state.player_id = f"player_{num_players + 1}"
            else: is_viewer = True; st.warning(t('game_full_warning'))
    
    if 'player_id' in st.session_state:
        if 'player_user_ids' not in state: state['player_user_ids'] = {}
        state['player_user_ids'][st.session_state.player_id] = get_user_id()
        save_game_state(game_id, state)

    # UI Routing
    if state['phase'] == 'joining': display_joining_phase(state, st.session_state.get('player_id')) if not is_viewer else st.info("...")
    elif state['phase'] == 'writing': display_writing_phase(state, st.session_state.get('player_id')) if not is_viewer else st.info("...")
    elif state['phase'] == 'guessing': display_match_the_following_guessing(state)
    elif state['phase'] == 'results': display_results_phase(state)

if __name__ == "__main__":
    main()rs'][player_id]['name']}।**")
        if len(state['players']) == 4:
            state['phase'] = "writing"
            save_game_state(game_id, state)
            st.rerun()
        else:
            display_game_links(game_id)
            st.info(t('waiting_for_players', count=len(state['players'])))
            st.write(f"**{t('players_in_room')}**")
            for p_data in state['players'].values():
                st.write(f"• {p_data['name']}")

def display_writing_phase(state, player_id):
    game_id = state['game_id']
    player_data = state['players'][player_id]
    
    if player_data['submitted']:
        st.success(t('submission_success'))
        st.info(t('waiting_for_others_submit'))
        submitted_count = sum(1 for p in state['players'].values() if p['submitted'])
        st.progress(submitted_count / 4, text=t('players_submitted', count=submitted_count))
        return

    my_varna_key = state['true_varna_map'][player_id]
    varna_details = VARNA_DETAILS[my_varna_key][st.session_state.lang]
    st.header(f"{t('you_are')} **{varna_details['name']}**")
    st.warning(f"**{t('your_rule')}** {varna_details['rule']}")

    with st.form("sentence_form"):
        st.write(t('write_three_sentences'))
        s1 = st.text_area(t('sentence_1'), key="s1", height=100)
        s2 = st.text_area(t('sentence_2'), key="s2", height=100)
        s3 = st.text_area(t('sentence_3'), key="s3", height=100)
        submitted = st.form_submit_button(t('submit_sentences'))

        if submitted:
            if not all([s1, s2, s3]):
                st.error(t('error_all_sentences'))
            else:
                player_data['sentences'] = [s1, s2, s3]
                player_data['submitted'] = True
                if all(p['submitted'] for p in state['players'].values()):
                    state['phase'] = "guessing"
                save_game_state(game_id, state)
                st.rerun()

def display_guessing_phase(state):
    user_id = get_user_id()

    if user_id in state['guesses']:
        st.success(t('guess_submitted'))
        return

    st.header(t('guessing_time'))
    st.info(t('guessing_instructions'))

    for p_id, p_data in sorted(state['players'].items()):
        with st.expander(t('player_sentences', name=p_data['name']), expanded=True):
            st.markdown(f"१. *{p_data['sentences'][0]}*\n\n२. *{p_data['sentences'][1]}*\n\n३. *{p_data['sentences'][2]}*")
            
    with st.form("guessing_form"):
        st.subheader(t('your_guesses'))
        player_guesses = {}
        sorted_players = sorted(state['players'].items())
        
        varna_options = [VARNA_DETAILS[key][st.session_state.lang]['name'] for key in VARNA_KEYS]
        varna_name_to_key_map = {VARNA_DETAILS[key][st.session_state.lang]['name']: key for key in VARNA_KEYS}

        cols = st.columns(len(sorted_players))
        for i, (p_id, p_data) in enumerate(sorted_players):
            with cols[i]:
                selected_varna_name = st.selectbox(
                    f"**{p_data['name']}** {t('is')}",
                    options=varna_options,
                    key=f"guess_{p_id}",
                    index=None,
                    placeholder=t('select_varna')
                )
                if selected_varna_name:
                    player_guesses[p_id] = varna_name_to_key_map[selected_varna_name]
        
        submit_guess = st.form_submit_button(t('submit_guess'))
        
        if submit_guess:
            if len(player_guesses) < len(state['players']):
                st.error(t('error_all_guesses'))
            else:
                state['guesses'][user_id] = player_guesses
                save_game_state(state['game_id'], state)
                st.rerun()

    if st.button(t('reveal_results')):
        state['phase'] = "results"
        save_game_state(state['game_id'], state)
        st.rerun()


def display_results_phase(state):
    st.header(t('results_are_in'))
    st.subheader(t('true_varnas'))
    truth = state['true_varna_map']
    cols = st.columns(len(state['players']))
    for i, (p_id, p_data) in enumerate(sorted(state['players'].items())):
        with cols[i]:
            true_varna_name = VARNA_DETAILS[truth[p_id]][st.session_state.lang]['name']
            st.metric(label=t('player_was_a', name=p_data['name']), value=true_varna_name)

    st.subheader(t('scoring'))
    correct_guessers = []
    for user_id, guess in state['guesses'].items():
        if guess == truth:
            guesser_name = None
            for p_id, p_data in state['players'].items():
                if st.session_state.get(f'user_id_for_{p_id}') == user_id:
                    guesser_name = p_data['name']
                    break
            if guesser_name:
                correct_guessers.append(guesser_name)
            else: 
                viewer_name = f"{t('guesser_a_viewer')} ({user_id[:6]})"
                correct_guessers.append(viewer_name)

    if not correct_guessers:
        st.warning(t('no_correct_guesses'))
    else:
        points_per_winner = POINTS_POOL // len(correct_guessers)
        st.success(t('correct_guessers_info', count=len(correct_guessers), points=points_per_winner))
        for name in correct_guessers:
            st.write(f"🎉 **{name}**")
            if t('viewer') not in name:
                state['scores'][name] = state['scores'].get(name, 0) + points_per_winner
            else:
                 state['scores'][name] = state['scores'].get(name, 0) + points_per_winner
                
    save_game_state(state['game_id'], state)

    st.subheader(t('leaderboard'))
    if state.get('scores'):
        sorted_scores = sorted(state['scores'].items(), key=lambda item: item[1], reverse=True)
        for name, score in sorted_scores:
            st.markdown(f"**{name}** `{score} {t('points')}`")

    if st.button(t('start_new_round')):
        new_state = get_initial_state(state['game_id'])
        new_state['players'] = {p_id: {"name": p_data["name"], "sentences": None, "submitted": False} for p_id, p_data in state['players'].items()}
        new_state['phase'] = 'writing'
        new_state['scores'] = state.get('scores', {})
        save_game_state(state['game_id'], new_state)
        st.rerun()

def display_game_links(game_id):
    base_url = st.get_option("server.baseUrlPath").strip('/')
    player_link = f"{base_url}?game_id={game_id}"
    viewer_link = f"{base_url}?game_id={game_id}&role=viewer"
    st.markdown("---")
    st.subheader(t('share_the_game'))
    st.write(f"**{t('player_link_info')}**")
    st.code(player_link, language=None)
    st.write(f"**{t('viewer_link_info')}**")
    st.code(viewer_link, language=None)
    st.markdown("---")

# --- MAIN APP LOGIC (No changes needed here) ---

def main():
    st.set_page_config(page_title="सत्यासत्यम्", layout="centered")

    if 'lang' not in st.session_state:
        st.session_state.lang = 'sa' 

    selected_lang_key = st.radio(
        "भाषा / Language",
        options=['sa', 'en'],
        format_func=lambda x: "संस्कृतम्" if x == 'sa' else "English",
        horizontal=True,
        key='lang_selector'
    )
    if st.session_state.lang != selected_lang_key:
        st.session_state.lang = selected_lang_key
        st.rerun()

    st.markdown("---")

    query_params = st.query_params
    game_id = query_params.get("game_id")

    if not game_id:
        display_main_menu()
        return

    state = load_game_state(game_id)
    if not state:
        st.error(t('game_room_not_found'))
        if st.button(t('go_to_main_menu')):
            st.query_params.clear()
            st.rerun()
        return

    is_viewer = query_params.get("role") == "viewer"
    
    if not is_viewer:
        if 'player_id' not in st.session_state:
            num_players = len(state.get('players', {}))
            if num_players < 4:
                st.session_state.player_id = f"player_{num_players + 1}"
            else:
                is_viewer = True
                st.warning(t('game_full_warning'))
    
    if 'player_id' in st.session_state:
        st.session_state[f'user_id_for_{st.session_state.player_id}'] = get_user_id()
    
    if state['phase'] == 'joining':
        if is_viewer: st.info(t('viewer_info_joining'))
        else: display_joining_phase(state, st.session_state.player_id)
            
    elif state['phase'] == 'writing':
        if is_viewer:
            submitted_count = sum(1 for p in state['players'].values() if p['submitted'])
            st.progress(submitted_count / 4, text=t('viewer_info_writing') + f" ({submitted_count}/4)")
        else: display_writing_phase(state, st.session_state.player_id)

    elif state['phase'] == 'guessing': display_guessing_phase(state)
    elif state['phase'] == 'results': display_results_phase(state)

    st.button(t('refresh_status'), key="manual_refresh")

if __name__ == "__main__":
    main()
