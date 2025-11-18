import json
import os
import time
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
# Set a secret key for session management
app.secret_key = 'super_secret_sct_key_change_me_in_production'

# Filenames
USERS_FILE = 'users.json'
WEATHER_API_KEY = '5aac2166b8c04f2b88905750252507'

# Supported languages (English names for display)
LANGUAGES = {
    'en': 'English', 'hi': 'Hindi', 'bn': 'Bengali', 'ta': 'Tamil',
    'te': 'Telugu', 'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada',
    'ml': 'Malayalam', 'pa': 'Punjabi', 'or': 'Odia'
}

# --- Localization Messages ---
MESSAGES = {
    'en': {
        'app_name': 'SCT - Soil Caretaker',
        'dashboard': 'Dashboard',
        'support': 'Support',
        'settings': 'Settings',
        'sign_out': 'Sign Out',
        'welcome_back': 'Welcome back',
        'soil_vitals': 'Soil Vitals',
        'ph_level': 'Soil pH Level',
        'ph_status_ideal': 'Status: Ideal for most crops',
        'moisture_content': 'Soil Moisture Content',
        'moisture_status_good': 'Status: Good, monitor during heat',
        'weather_forecast': '3-Day Weather Forecast for',
        'weather_region_placeholder': 'your region',
        'farm_profile': 'Your Farm Profile',
        'total_land': 'Total Land',
        'plant_types': 'Plant Types',
        'error_weather': 'Error fetching weather data:',
        
        # Settings
        'general_settings': 'General Settings',
        'language': 'Language',
        'theme': 'Theme',
        'light': 'Light',
        'dark': 'Dark',
        'save_preferences': 'Save Preferences',
        'account_management': 'Account Management',
        'reset_setup': 'Reset Setup Wizard',
        'signout_btn': 'Sign Out',
        
        # Setup
        'setup_title': 'Setup',
        'step_1_title': 'Step 1: Preferences',
        'step_1_desc': 'Select your language and preferred theme.',
        'next': 'Next',
        'back': 'Back',
        'step_2_title': 'Step 2: Account',
        'step_2_desc': 'Login or create a new account.',
        'email_placeholder': 'Email Address',
        'password_placeholder': 'Password',
        'submit_continue': 'Submit & Continue',
        'step_3_title': 'Step 3: Plants',
        'step_3_desc': 'How many types of plants are you managing?',
        'num_plants_placeholder': 'Number of plant types',
        'step_4_title': 'Step 4: Plant Names',
        'step_4_desc': 'Enter the name for each type of plant.',
        'plant_name_placeholder': 'Name of Plant',
        'step_5_title': 'Step 5: Land Size',
        'step_5_desc': 'How much land in acres?',
        'acres_placeholder': 'Acres of Land (e.g., 5.5)',
        'land_info_small': 'This information will be used to calculate resource management needs.',
        'complete_setup': 'Complete Setup',
        
        # Support
        'support_title': 'Customer Support',
        'support_intro': 'We are here to help you care for your soil and plants.',
        'email_support': 'Email Support',
        'phone_support': 'Phone Support (India)',
        'support_response_time': 'We aim to respond to all inquiries within 24 hours.',

        # Confirmation Modal
        'confirm_title': 'Confirmation Required',
        'confirm_reset_text': 'Are you sure you want to reset your setup? You will lose your plant/land data and be redirected to the setup wizard.',
        'cancel': 'Cancel',
        'confirm_reset_btn': 'Confirm Reset',
    },
    'hi': { # Hindi Translations
        'app_name': 'एससीटी - मिट्टी की देखभाल',
        'dashboard': 'डैशबोर्ड',
        'support': 'समर्थन',
        'settings': 'सेटिंग्स',
        'sign_out': 'साइन आउट',
        'welcome_back': 'वापस स्वागत है',
        'soil_vitals': 'मिट्टी की जीवनशक्ति',
        'ph_level': 'मिट्टी का पीएच स्तर',
        'ph_status_ideal': 'स्थिति: अधिकांश फसलों के लिए आदर्श',
        'moisture_content': 'मिट्टी में नमी की मात्रा',
        'moisture_status_good': 'स्थिति: अच्छा है, गर्मी के दौरान निगरानी करें',
        'weather_forecast': 'का 3-दिवसीय मौसम पूर्वानुमान',
        'weather_region_placeholder': 'आपका क्षेत्र',
        'farm_profile': 'आपका फार्म प्रोफाइल',
        'total_land': 'कुल भूमि',
        'plant_types': 'पौधों के प्रकार',
        'error_weather': 'मौसम डेटा प्राप्त करने में त्रुटि:',
        
        # Settings
        'general_settings': 'सामान्य सेटिंग्स',
        'language': 'भाषा',
        'theme': 'थीम',
        'light': 'हल्का',
        'dark': 'गहरा',
        'save_preferences': 'पसंद सहेजें',
        'account_management': 'खाता प्रबंधन',
        'reset_setup': 'सेटअप विज़ार्ड रीसेट करें',
        'signout_btn': 'साइन आउट',

        # Setup
        'setup_title': 'सेटअप',
        'step_1_title': 'चरण 1: प्राथमिकताएं',
        'step_1_desc': 'अपनी भाषा और पसंदीदा थीम चुनें।',
        'next': 'आगे',
        'back': 'पीछे',
        'step_2_title': 'चरण 2: खाता',
        'step_2_desc': 'लॉगिन करें या नया खाता बनाएं।',
        'email_placeholder': 'ईमेल पता',
        'password_placeholder': 'पासवर्ड',
        'submit_continue': 'जमा करें और जारी रखें',
        'step_3_title': 'चरण 3: पौधे',
        'step_3_desc': 'आप कितने प्रकार के पौधे प्रबंधित कर रहे हैं?',
        'num_plants_placeholder': 'पौधों के प्रकारों की संख्या',
        'step_4_title': 'चरण 4: पौधों के नाम',
        'step_4_desc': 'प्रत्येक प्रकार के पौधे का नाम दर्ज करें।',
        'plant_name_placeholder': 'पौधे का नाम',
        'step_5_title': 'चरण 5: भूमि का आकार',
        'step_5_desc': 'एकड़ में कितनी जमीन है?',
        'acres_placeholder': 'भूमि के एकड़ (उदाहरण के लिए, 5.5)',
        'land_info_small': 'इस जानकारी का उपयोग संसाधन प्रबंधन की ज़रूरतों की गणना के लिए किया जाएगा।',
        'complete_setup': 'सेटअप पूरा करें',

        # Support
        'support_title': 'ग्राहक समर्थन',
        'support_intro': 'हम आपकी मिट्टी और पौधों की देखभाल में मदद करने के लिए यहां हैं।',
        'email_support': 'ईमेल समर्थन',
        'phone_support': 'फोन समर्थन (भारत)',
        'support_response_time': 'हम 24 घंटों के भीतर सभी पूछताछ का जवाब देने का लक्ष्य रखते हैं।',

        # Confirmation Modal
        'confirm_title': 'पुष्टि आवश्यक है',
        'confirm_reset_text': 'क्या आप वाकई अपना सेटअप रीसेट करना चाहते हैं? आप अपना पौधा/भूमि डेटा खो देंगे और आपको सेटअप विज़ार्ड पर रीडायरेक्ट कर दिया जाएगा।',
        'cancel': 'रद्द करें',
        'confirm_reset_btn': 'रीसेट की पुष्टि करें',
    },
    'ml': { # Malayalam Translations
        'app_name': 'എസ്.സി.ടി - മണ്ണ് പരിപാലകൻ',
        'dashboard': 'ഡാഷ്ബോർഡ്',
        'support': 'പിന്തുണ',
        'settings': 'ക്രമീകരണങ്ങൾ',
        'sign_out': 'പുറത്തുകടക്കുക',
        'welcome_back': 'തിരികെ സ്വാഗതം',
        'soil_vitals': 'മണ്ണ് സ്ഥിതിവിവരക്കണക്കുകൾ',
        'ph_level': ' മണ്ണിന്റെ pH നില',
        'ph_status_ideal': 'നില: മിക്ക വിളകൾക്കും അനുയോജ്യം',
        'moisture_content': 'മണ്ണിന്റെ ഈർപ്പത്തിന്റെ അളവ്',
        'moisture_status_good': 'നില: നല്ലത്, ചൂടുള്ള സമയത്ത് നിരീക്ഷിക്കുക',
        'weather_forecast': 'നുള്ള 3 ദിവസത്തെ കാലാവസ്ഥാ പ്രവചനം',
        'weather_region_placeholder': 'നിങ്ങളുടെ പ്രദേശം',
        'farm_profile': 'നിങ്ങളുടെ ഫാം പ്രൊഫൈൽ',
        'total_land': 'മൊത്തം ഭൂമി',
        'plant_types': 'ചെടി ഇനങ്ങൾ',
        'error_weather': 'കാലാവസ്ഥാ ഡാറ്റ ലഭ്യമാക്കുന്നതിൽ പിശക്:',

        # Settings
        'general_settings': 'പൊതുവായ ക്രമീകരണങ്ങൾ',
        'language': 'ഭാഷ',
        'theme': 'തീം',
        'light': 'ലൈറ്റ്',
        'dark': 'ഡാർക്ക്',
        'save_preferences': 'മുൻഗണനകൾ സംരക്ഷിക്കുക',
        'account_management': 'അക്കൗണ്ട് മാനേജ്മെന്റ്',
        'reset_setup': 'സജ്ജീകരണ വിസാർഡ് പുനഃസജ്ജമാക്കുക',
        'signout_btn': 'പുറത്തുകടക്കുക',

        # Setup
        'setup_title': 'സജ്ജീകരണം',
        'step_1_title': 'ഘട്ടം 1: മുൻഗണനകൾ',
        'step_1_desc': 'നിങ്ങളുടെ ഭാഷയും ഇഷ്ടപ്പെട്ട തീമും തിരഞ്ഞെടുക്കുക.',
        'next': 'അടുത്ത്',
        'back': 'പുറകോട്ട്',
        'step_2_title': 'ഘട്ടം 2: അക്കൗണ്ട്',
        'step_2_desc': 'ലോഗിൻ ചെയ്യുക അല്ലെങ്കിൽ ഒരു പുതിയ അക്കൗണ്ട് സൃഷ്ടിക്കുക.',
        'email_placeholder': 'ഇമെയിൽ വിലാസം',
        'password_placeholder': 'പാസ്‌വേഡ്',
        'submit_continue': 'സമർപ്പിക്കുക, തുടരുക',
        'step_3_title': 'ഘട്ടം 3: ചെടികൾ',
        'step_3_desc': 'നിങ്ങൾ എത്ര തരം ചെടികളാണ് കൈകാര്യം ചെയ്യുന്നത്?',
        'num_plants_placeholder': 'ചെടി ഇനങ്ങളുടെ എണ്ണം',
        'step_4_title': 'ഘട്ടം 4: ചെടി പേരുകൾ',
        'step_4_desc': 'ഓരോ തരം ചെടിയുടെയും പേര് നൽകുക.',
        'plant_name_placeholder': 'ചെടിയുടെ പേര്',
        'step_5_title': 'ഘട്ടം 5: ഭൂമിയുടെ വലുപ്പം',
        'step_5_desc': 'ഏക്കറിൽ എത്ര ഭൂമിയുണ്ട്?',
        'acres_placeholder': 'ഭൂമിയുടെ ഏക്കർ (ഉദാഹരണത്തിന്, 5.5)',
        'land_info_small': 'വിഭവ മാനേജ്മെന്റ് ആവശ്യകതകൾ കണക്കാക്കാൻ ഈ വിവരങ്ങൾ ഉപയോഗിക്കും.',
        'complete_setup': 'സജ്ജീകരണം പൂർത്തിയാക്കുക',

        # Support
        'support_title': 'ഉപഭോക്തൃ പിന്തുണ',
        'support_intro': 'നിങ്ങളുടെ മണ്ണിന്റെയും ചെടികളുടെയും പരിചരണത്തിനായി ഞങ്ങൾ നിങ്ങളെ സഹായിക്കാൻ ഇവിടെയുണ്ട്.',
        'email_support': 'ഇമെയിൽ പിന്തുണ',
        'phone_support': 'ഫോൺ പിന്തുണ (ഇന്ത്യ)',
        'support_response_time': '24 മണിക്കൂറിനുള്ളിൽ എല്ലാ അന്വേഷണങ്ങൾക്കും മറുപടി നൽകാൻ ഞങ്ങൾ ലക്ഷ്യമിടുന്നു.',

        # Confirmation Modal
        'confirm_title': 'സ്ഥിരീകരണം ആവശ്യമാണ്',
        'confirm_reset_text': 'നിങ്ങളുടെ സജ്ജീകരണം പുനഃസജ്ജമാക്കാൻ നിങ്ങൾ ആഗ്രഹിക്കുന്നുണ്ടോ? നിങ്ങളുടെ ചെടി/ഭൂമി ഡാറ്റ നഷ്ടപ്പെടുകയും സജ്ജീകരണ വിസാർഡിലേക്ക് റീഡയറക്‌ട് ചെയ്യപ്പെടുകയും ചെയ്യും.',
        'cancel': 'റദ്ദാക്കുക',
        'confirm_reset_btn': 'പുനഃസജ്ജീകരണം സ്ഥിരീകരിക്കുക',
    }
}

def get_messages(lang_code):
    """Retrieves the message dictionary for the requested language, falling back to English."""
    return MESSAGES.get(lang_code, MESSAGES['en'])

def load_users():
    """Safely loads user data from users.json."""
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Initialize an empty file if decoding fails
        return {}

def save_users(users_data):
    """Safely saves user data to users.json."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

def get_user_data(email):
    """Retrieves specific user data based on email."""
    return load_users().get(email)

def get_user_settings(email):
    """Retrieves language and theme settings for a user."""
    user = get_user_data(email)
    if user:
        return {'lang': user.get('lang', 'en'), 'theme': user.get('theme', 'light')}
    return {'lang': 'en', 'theme': 'light'}

@app.before_request
def check_setup_and_auth():
    """Checks if the user is authenticated and if setup is complete."""
    # UPDATED: Added '/complete_setup' to allowed paths for logged-in, incomplete setup users.
    allowed_paths = ['/', '/setup', '/login_or_signup', '/static/', '/complete_setup']
    
    # Check if the request is an API call (POST/PUT/DELETE) that expects JSON
    is_api_call = request.method in ['POST', 'PUT', 'DELETE'] and not request.path.startswith('/login_or_signup')

    if 'email' not in session and not any(request.path.startswith(p) for p in allowed_paths):
        # Case 1: Not logged in.
        if is_api_call:
            # If it's an API call, return a JSON error instead of redirecting
            return jsonify({'success': False, 'message': 'Unauthorized (Session Expired). Please log in again.'}), 401
        else:
            # If it's a page request (GET), redirect to the initial page
            return redirect(url_for('index'))

    if 'email' in session:
        user_data = get_user_data(session['email'])
        
        # Case 2: Logged in, but setup is incomplete.
        # This now checks if the path is NOT in the allowed list.
        if user_data and not user_data.get('setup_complete') and request.path not in allowed_paths:
            if is_api_call:
                 # If it's an API call trying to access non-setup data (like /update_settings), deny.
                 return jsonify({'success': False, 'message': 'Setup required.'}), 403
            else:
                 return redirect(url_for('setup'))
        
        # Case 3: Setup is complete and user is trying to access setup page (GET /setup).
        elif user_data and user_data.get('setup_complete') and request.path == '/setup' and request.method == 'GET':
            # Redirect to dashboard if setup is complete and user tries to go back to /setup page
            return redirect(url_for('dashboard'))

# --- Routes ---

@app.route('/')
def index():
    """Initial check for user state, redirects to dashboard or setup."""
    if 'email' in session:
        user_data = get_user_data(session['email'])
        if user_data and user_data.get('setup_complete'):
            return redirect(url_for('dashboard'))
    
    # If not logged in or setup is incomplete, start/continue setup
    return redirect(url_for('setup'))


@app.route('/setup')
def setup():
    """Handles the multi-step setup wizard."""
    user_settings = get_user_settings(session.get('email')) if 'email' in session else {'lang': 'en', 'theme': 'light'}
    messages = get_messages(user_settings['lang'])
    return render_template('setup.html', languages=LANGUAGES, settings=user_settings, text=messages)


@app.route('/login_or_signup', methods=['POST'])
def login_or_signup():
    """Handles login or signup from Step 2 of the setup wizard."""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    lang = data.get('lang')
    theme = data.get('theme')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required.'}), 400

    users = load_users()

    if email in users:
        # Login
        if users[email]['password'] == password:
            session['email'] = email
            # Update current session settings in case the user changes them in step 1
            if lang in LANGUAGES:
                 users[email]['lang'] = lang
            if theme in ['dark', 'light']:
                users[email]['theme'] = theme

            save_users(users)
            # Send back the saved theme/lang for immediate JS application
            return jsonify({'success': True, 'action': 'login', 'setup_complete': users[email].get('setup_complete', False), 'theme': users[email]['theme'], 'lang': users[email]['lang']})
        else:
            return jsonify({'success': False, 'message': 'Invalid password.'}), 401
    else:
        # Signup
        users[email] = {
            'password': password,
            'lang': lang,
            'theme': theme,
            'setup_complete': False,
            'plants': [],
            'acres': 0
        }
        save_users(users)
        session['email'] = email
        # Send back the saved theme/lang for immediate JS application
        return jsonify({'success': True, 'action': 'signup', 'setup_complete': False, 'theme': theme, 'lang': lang})


@app.route('/complete_setup', methods=['POST'])
def complete_setup():
    """Handles the completion of the setup wizard (Steps 3, 4, 5)."""
    # NOTE: The @app.before_request now ensures a logged-in, setup-incomplete user 
    # can reach this route without a 403.
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized (Session Expired)'}), 401

    data = request.json
    try:
        num_plants = int(data.get('num_plants'))
        plant_names = data.get('plant_names')
        acres = float(data.get('acres'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid data submitted.'}), 400

    users = load_users()
    user_email = session['email']

    if user_email in users:
        users[user_email].update({
            'setup_complete': True,
            'plants': plant_names,
            'acres': acres
        })
        save_users(users)
        # Return JSON success
        return jsonify({'success': True, 'message': 'Setup complete.'})
    
    return jsonify({'success': False, 'message': 'User not found.'}), 404


@app.route('/dashboard')
def dashboard():
    """Main application dashboard."""
    if 'email' not in session:
        return redirect(url_for('index'))
    
    user_data = get_user_data(session['email'])
    if not user_data or not user_data.get('setup_complete'):
        return redirect(url_for('setup'))

    settings = get_user_settings(session['email'])
    messages = get_messages(settings['lang']) # Get localized messages

    # City/Location is not stored, so we'll use a placeholder for weather
    city = 'Mumbai, IN'
    weather_data = get_weather_forecast(city)

    return render_template('dashboard.html', 
                           settings=settings, 
                           user=user_data,
                           weather=weather_data,
                           text=messages) # Pass messages to template


@app.route('/support')
def support():
    """Customer support page."""
    if 'email' not in session:
        return redirect(url_for('index'))
    
    settings = get_user_settings(session['email'])
    messages = get_messages(settings['lang']) # Get localized messages
    return render_template('support.html', settings=settings, text=messages) # Pass messages to template


@app.route('/settings')
def settings():
    """User settings page."""
    if 'email' not in session:
        return redirect(url_for('index'))

    settings = get_user_settings(session['email'])
    messages = get_messages(settings['lang']) # Get localized messages
    return render_template('settings.html', settings=settings, languages=LANGUAGES, text=messages) # Pass messages to template


@app.route('/update_settings', methods=['POST'])
def update_settings():
    """API endpoint to update theme and language settings."""
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    new_lang = data.get('lang')
    new_theme = data.get('theme')

    users = load_users()
    user_email = session['email']

    if user_email in users:
        # Check and update language
        if new_lang and new_lang in LANGUAGES:
            users[user_email]['lang'] = new_lang
        # Check and update theme
        if new_theme in ['dark', 'light']:
            users[user_email]['theme'] = new_theme
        
        save_users(users)
        return jsonify({'success': True, 'lang': users[user_email]['lang'], 'theme': users[user_email]['theme']})

    return jsonify({'success': False, 'message': 'User not found.'}), 404


@app.route('/reset_setup', methods=['POST'])
def reset_setup():
    """Resets the user's setup status."""
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    users = load_users()
    user_email = session['email']

    if user_email in users:
        users[user_email]['setup_complete'] = False
        users[user_email]['plants'] = []
        users[user_email]['acres'] = 0
        save_users(users)
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'User not found.'}), 404


@app.route('/signout')
def signout():
    """Clears the session and signs the user out."""
    session.pop('email', None)
    return redirect(url_for('setup'))


# --- Weather API Function ---

def get_weather_forecast(city):
    """Fetches a 3-day weather forecast."""
    try:
        # Request for 3-day forecast
        url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=3'
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        # Extract relevant forecast data
        forecast = []
        for day in data.get('forecast', {}).get('forecastday', []):
            forecast.append({
                'date': day.get('date'),
                'max_temp_c': day.get('day', {}).get('maxtemp_c'),
                'min_temp_c': day.get('day', {}).get('mintemp_c'),
                'condition_text': day.get('day', {}).get('condition', {}).get('text'),
                'condition_icon': day.get('day', {}).get('condition', {}).get('icon')
            })
        
        return {
            'success': True,
            'location': data.get('location', {}).get('name'),
            'forecast': forecast
        }

    except requests.exceptions.RequestException as e:
        print(f"Weather API error: {e}")
        return {'success': False, 'message': 'Could not fetch weather data.'}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {'success': False, 'message': 'An unexpected error occurred.'}

if __name__ == '__main__':
    # Ensure users.json exists or is initialized
    if not os.path.exists(USERS_FILE):
        save_users({})
    
    # MODIFIED: Use '0.0.0.0' to listen on all interfaces.
    app.run(debug=True, host='0.0.0.0')
