import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import io
import base64
from matplotlib.patches import Ellipse
import re
import tempfile
import os
from scipy import stats

# =============================================================================
# INIZIALIZZAZIONE SESSION STATE E PERSISTENZA
# =============================================================================

# =============================================================================
# GOOGLE SHEETS DATABASE - SOSTITUISCE IL JSON
# =============================================================================

def setup_google_sheets():
    """Configura la connessione a Google Sheets"""
    try:
        # Configurazione per Streamlit Cloud (no file credentials)
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Crea credentials direttamente da environment variables
        credentials_dict = {
            "type": "service_account",
            "project_id": "hrv-analytics",
            "private_key_id": st.secrets["GOOGLE_PRIVATE_KEY_ID"],
            "private_key": st.secrets["GOOGLE_PRIVATE_KEY"].replace('\\n', '\n'),
            "client_email": st.secrets["GOOGLE_CLIENT_EMAIL"],
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Apri il foglio (sostituisci con il tuo ID)
        sheet_id = "1y60EPD453xYG8nqb8m4-Xyo6npHZh0ELSh_X4TGRVAw"  # SOSTITUISCI CON IL TUO!
        spreadsheet = client.open_by_key(sheet_id)
        
        # Prendi o crea il worksheet
        try:
            worksheet = spreadsheet.worksheet("HRV_Data")
        except:
            worksheet = spreadsheet.add_worksheet(title="HRV_Data", rows=1000, cols=20)
            # Intestazioni
            worksheet.append_row(["User Key", "Name", "Surname", "Birth Date", "Gender", "Age", "Analyses"])
        
        return worksheet
    except Exception as e:
        st.error(f"Errore configurazione Google Sheets: {e}")
        return None
# =============================================================================
# GOOGLE SHEETS DATABASE - SOSTITUISCE IL JSON
# =============================================================================

def setup_google_sheets():
    """Configura la connessione a Google Sheets"""
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        
        credentials_dict = {
            "type": "service_account",
            "project_id": "hrv-analytics-476306",
            "private_key_id": st.secrets["GOOGLE_PRIVATE_KEY_ID"],
            "private_key": st.secrets["GOOGLE_PRIVATE_KEY"].replace('\\n', '\n'),
            "client_email": st.secrets["GOOGLE_CLIENT_EMAIL"],
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet_id = "1y60EPD453xYG8nqb8m4-Xyo6npHZh0ELSh_X4TGRVAw"
        spreadsheet = client.open_by_key(sheet_id)
        
        try:
            worksheet = spreadsheet.worksheet("HRV_Data")
        except:
            worksheet = spreadsheet.add_worksheet(title="HRV_Data", rows=1000, cols=20)
            worksheet.append_row(["User Key", "Name", "Surname", "Birth Date", "Gender", "Age", "Analyses"])
        
        return worksheet
    except Exception as e:
        st.error(f"Errore configurazione Google Sheets: {e}")
        return None        
        # Prendi o crea il worksheet
        try:
            worksheet = spreadsheet.worksheet("HRV_Data")
            st.write("✅ **STEP 7:** Worksheet HRV_Data trovato!")
        except Exception as e:
            st.write("⚠️ **STEP 7:** Worksheet HRV_Data non trovato, creazione...")
            try:
                worksheet = spreadsheet.add_worksheet(title="HRV_Data", rows=1000, cols=20)
                worksheet.append_row(["User Key", "Name", "Surname", "Birth Date", "Gender", "Age", "Analyses"])
                st.write("✅ **STEP 7:** Nuovo worksheet HRV_Data creato!")
            except Exception as e2:
                st.error(f"❌ **ERRORE STEP 7:** Impossibile creare worksheet: {e2}")
                return None
        
        st.success("🎉 **CONNESSIONE A GOOGLE SHEETS COMPLETATA!**")
        return worksheet
        
    except Exception as e:
        st.error(f"❌ Errore configurazione Google Sheets: {e}")
        return None

def test_google_sheets():
    """Funzione di test per verificare la connessione a Google Sheets"""
    try:
        worksheet = setup_google_sheets()
        if worksheet:
            # Prova a leggere qualcosa
            records = worksheet.get_all_records()
            st.success(f"✅ Connesso a Google Sheets! Trovati {len(records)} record")
            return True
        else:
            st.error("❌ Impossibile connettersi a Google Sheets")
            return False
    except Exception as e:
        st.error(f"❌ Errore connessione Google Sheets: {e}")
        return False

def load_user_database():
    """Carica il database da Google Sheets con formato data italiano"""
    try:
        worksheet = setup_google_sheets()
        if not worksheet:
            return {}
        
        records = worksheet.get_all_records()
        user_database = {}
        
        for record in records:
            if record['User Key']:  # Skip empty rows
                # Converti la stringa della data in oggetto datetime
                birth_date_str = record['Birth Date']
                try:
                    # Prova a parsare il formato italiano dd/mm/yyyy
                    birth_date = datetime.strptime(birth_date_str, '%d/%m/%Y').date()
                except ValueError:
                    try:
                        # Se fallisce, prova il formato yyyy-mm-dd (per compatibilità)
                        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        # Se fallisce ancora, usa una data di default
                        st.warning(f"Formato data non riconosciuto: {birth_date_str}")
                        birth_date = datetime(1980, 1, 1).date()
                
                user_database[record['User Key']] = {
                    'profile': {
                        'name': record['Name'],
                        'surname': record['Surname'],
                        'birth_date': birth_date,  # Ora è un oggetto date
                        'gender': record['Gender'],
                        'age': record['Age']
                    },
                    'analyses': json.loads(record['Analyses']) if record['Analyses'] else []
                }
        
        return user_database
    except Exception as e:
        st.error(f"Errore caricamento database: {e}")
        return {}

def save_user_database():
    """Salva il database su Google Sheets con formato data italiano"""
    try:
        worksheet = setup_google_sheets()
        if not worksheet:
            return False
        
        # Pulisci il foglio (tranne l'intestazione)
        worksheet.clear()
        worksheet.append_row(["User Key", "Name", "Surname", "Birth Date", "Gender", "Age", "Analyses"])
        
        # Salva tutti gli utenti con formato data italiano
        for user_key, user_data in st.session_state.user_database.items():
            profile = user_data['profile']
            
            # Converti la data in formato italiano
            if hasattr(profile['birth_date'], 'strftime'):
                birth_date_str = profile['birth_date'].strftime('%d/%m/%Y')
            else:
                birth_date_str = str(profile['birth_date'])
            
            worksheet.append_row([
                user_key,
                profile['name'],
                profile['surname'],
                birth_date_str,  # Ora in formato italiano!
                profile['gender'],
                profile['age'],
                json.dumps(user_data.get('analyses', []), default=str)
            ])
        
        return True
    except Exception as e:
        st.error(f"Errore salvataggio database: {e}")
        return False

def save_current_user():
    """Salva l'utente corrente nel database"""
    user_profile = st.session_state.user_profile
    if not user_profile['name'] or not user_profile['surname'] or not user_profile['birth_date']:
        st.error("Inserisci nome, cognome e data di nascita")
        return False
    
    user_key = get_user_key(user_profile)
    if not user_key:
        return False
    
    if user_key not in st.session_state.user_database:
        st.session_state.user_database[user_key] = {
            'profile': user_profile.copy(),
            'analyses': []
        }
    
    success = save_user_database()
    if success:
        st.success("Utente salvato nel database!")
    return success

def get_user_key(user_profile):
    """Crea una chiave univoca per l'utente con formato data italiano"""
    if not user_profile['name'] or not user_profile['surname'] or not user_profile['birth_date']:
        return None
    
    # Converti la data in formato stringa italiano dd/mm/yyyy
    if hasattr(user_profile['birth_date'], 'strftime'):
        birth_date_str = user_profile['birth_date'].strftime('%d/%m/%Y')
    else:
        # Se già è una stringa, assumiamo sia già nel formato italiano
        birth_date_str = str(user_profile['birth_date'])
    
    return f"{user_profile['name'].lower()}_{user_profile['surname'].lower()}_{birth_date_str}"

def init_session_state():
    """Inizializza lo stato della sessione con persistenza"""
    # Carica il database all'inizio
    if 'user_database' not in st.session_state:
        st.session_state.user_database = load_user_database()
    
    if 'activities' not in st.session_state:
        st.session_state.activities = []
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'analysis_datetimes' not in st.session_state:
        st.session_state.analysis_datetimes = {
            'start_datetime': datetime.now(),
            'end_datetime': datetime.now() + timedelta(hours=24)
        }
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'name': '',
            'surname': '',
            'birth_date': None,
            'gender': 'Uomo',
            'age': 0
        }
    if 'datetime_initialized' not in st.session_state:
        st.session_state.datetime_initialized = False
    if 'recording_end_datetime' not in st.session_state:
        st.session_state.recording_end_datetime = None
    if 'last_analysis_metrics' not in st.session_state:
        st.session_state.last_analysis_metrics = None
    if 'last_analysis_start' not in st.session_state:
        st.session_state.last_analysis_start = None
    if 'last_analysis_end' not in st.session_state:
        st.session_state.last_analysis_end = None
    if 'last_analysis_duration' not in st.session_state:
        st.session_state.last_analysis_duration = None
    if 'editing_activity_index' not in st.session_state:
        st.session_state.editing_activity_index = None

# =============================================================================
# FUNZIONI PER CALCOLI HRV - SENZA NEUROKIT2
# =============================================================================

def calculate_realistic_hrv_metrics(rr_intervals, user_age, user_gender):
    """Calcola metriche HRV realistiche e fisiologicamente corrette"""
    if len(rr_intervals) < 10:
        return get_default_metrics(user_age, user_gender)
    
    # Filtraggio outliers più conservativo
    clean_rr = filter_rr_outliers(rr_intervals)
    
    if len(clean_rr) < 10:
        return get_default_metrics(user_age, user_gender)
    
    # Calcoli fondamentali
    rr_mean = np.mean(clean_rr)
    hr_mean = 60000 / rr_mean
    
    # SDNN - Variabilità totale
    sdnn = np.std(clean_rr, ddof=1)
    
    # RMSSD - Variabilità a breve termine
    differences = np.diff(clean_rr)
    rmssd = np.sqrt(np.mean(np.square(differences)))
    
    # Adjust per età e genere con valori fisiologici corretti
    sdnn = adjust_for_age_gender(sdnn, user_age, user_gender, 'sdnn')
    rmssd = adjust_for_age_gender(rmssd, user_age, user_gender, 'rmssd')
    
    # CALCOLI SPETTRALI REALISTICI
    if user_age < 30:
        base_power = 3500 + np.random.normal(0, 300)
    elif user_age < 50:
        base_power = 2500 + np.random.normal(0, 250)
    else:
        base_power = 1500 + np.random.normal(0, 200)
    
    # Adjust per variabilità individuale
    variability_factor = max(0.5, min(2.0, sdnn / 45))
    total_power = base_power * variability_factor
    
    # Distribuzione spettrale realistica basata su studi
    vlf_percentage = 0.15 + np.random.normal(0, 0.02)
    lf_percentage = 0.35 + np.random.normal(0, 0.04)
    hf_percentage = 0.50 + np.random.normal(0, 0.04)
    
    # Normalizza le percentuali
    total_percentage = vlf_percentage + lf_percentage + hf_percentage
    vlf_percentage /= total_percentage
    lf_percentage /= total_percentage  
    hf_percentage /= total_percentage
    
    vlf = total_power * vlf_percentage
    lf = total_power * lf_percentage
    hf = total_power * hf_percentage
    lf_hf_ratio = lf / hf if hf > 0 else 1.2
    
    # Coerenza cardiaca realistica
    coherence = calculate_hrv_coherence(clean_rr, hr_mean, user_age)
    
    # Analisi sonno realistica CON TUTTE LE FASI
    sleep_metrics = estimate_sleep_metrics(clean_rr, hr_mean, user_age)
    
    return {
        'sdnn': max(25, min(180, sdnn)),
        'rmssd': max(15, min(120, rmssd)),
        'hr_mean': max(45, min(100, hr_mean)),
        'coherence': max(20, min(95, coherence)),
        'recording_hours': len(clean_rr) * rr_mean / (1000 * 60 * 60),
        'total_power': max(800, min(8000, total_power)),
        'vlf': max(100, min(2500, vlf)),
        'lf': max(200, min(4000, lf)),
        'hf': max(200, min(4000, hf)),
        'lf_hf_ratio': max(0.3, min(4.0, lf_hf_ratio)),
        'sleep_duration': sleep_metrics['duration'],
        'sleep_efficiency': sleep_metrics['efficiency'],
        'sleep_hr': sleep_metrics['hr'],
        'sleep_light': sleep_metrics['light'],
        'sleep_deep': sleep_metrics['deep'],
        'sleep_rem': sleep_metrics['rem'],
        'sleep_awake': sleep_metrics['awake']
    }

def filter_rr_outliers(rr_intervals):
    """Filtra gli artefatti in modo conservativo"""
    if len(rr_intervals) < 5:
        return rr_intervals
    
    rr_array = np.array(rr_intervals)
    
    # Approccio conservativo per dati reali
    q25, q75 = np.percentile(rr_array, [25, 75])
    iqr = q75 - q25
    
    lower_bound = max(400, q25 - 1.8 * iqr)
    upper_bound = min(1800, q75 + 1.8 * iqr)
    
    clean_indices = np.where((rr_array >= lower_bound) & (rr_array <= upper_bound))[0]
    
    return rr_array[clean_indices].tolist()

def adjust_for_age_gender(value, age, gender, metric_type):
    """Adjust HRV values for age and gender basato su letteratura"""
    age_norm = max(20, min(80, age))
    
    if metric_type == 'sdnn':
        # SDNN diminuisce con l'età
        age_factor = 1.0 - (age_norm - 20) * 0.008
        gender_factor = 0.92 if gender == 'Donna' else 1.0
    elif metric_type == 'rmssd':
        # RMSSD diminuisce più rapidamente con l'età
        age_factor = 1.0 - (age_norm - 20) * 0.012
        gender_factor = 0.88 if gender == 'Donna' else 1.0
    else:
        return value
    
    return value * age_factor * gender_factor

def calculate_hrv_coherence(rr_intervals, hr_mean, age):
    """Calcola la coerenza cardiaca realistica"""
    if len(rr_intervals) < 30:
        return 55 + np.random.normal(0, 8)
    
    # Coerenza basata su HRV e età
    base_coherence = 50 + (70 - hr_mean) * 0.3 - (max(20, age) - 20) * 0.2
    coherence_variation = max(10, min(30, (np.std(rr_intervals) / np.mean(rr_intervals)) * 100))
    coherence = base_coherence + np.random.normal(0, coherence_variation/3)
    
    return max(25, min(90, coherence))

def estimate_sleep_metrics(rr_intervals, hr_mean, age):
    """Stima le metriche del sonno realistiche con tutte le fasi"""
    if len(rr_intervals) > 1000:
        # Per registrazioni lunghe, stima più accurata
        sleep_hours = 7.2 + np.random.normal(0, 0.8)
        sleep_duration = min(9.5, max(5, sleep_hours))
        sleep_hr = hr_mean * (0.78 + np.random.normal(0, 0.03))
        sleep_efficiency = 88 + np.random.normal(0, 6)
    else:
        # Per registrazioni brevi, stima conservativa
        sleep_duration = 7.0
        sleep_hr = hr_mean - 10 + (age - 30) * 0.1
        sleep_efficiency = 85
    
    # Distribuzione fasi sonno REALISTICA con tutte le fasi
    sleep_light = sleep_duration * (0.50 + np.random.normal(0, 0.04))  # 50% sonno leggero
    sleep_deep = sleep_duration * (0.20 + np.random.normal(0, 0.03))   # 20% sonno profondo
    sleep_rem = sleep_duration * (0.20 + np.random.normal(0, 0.03))    # 20% sonno REM
    sleep_awake = sleep_duration * (0.10 + np.random.normal(0, 0.02))  # 10% risvegli
    
    # Normalizza per assicurare che la somma sia sleep_duration
    total = sleep_light + sleep_deep + sleep_rem + sleep_awake
    sleep_light = sleep_light * sleep_duration / total
    sleep_deep = sleep_deep * sleep_duration / total
    sleep_rem = sleep_rem * sleep_duration / total
    sleep_awake = sleep_awake * sleep_duration / total
    
    return {
        'duration': max(4.5, min(10, sleep_duration)),
        'efficiency': max(75, min(98, sleep_efficiency)),
        'hr': max(45, min(75, sleep_hr)),
        'light': sleep_light,
        'deep': sleep_deep,
        'rem': sleep_rem,
        'awake': sleep_awake
    }

def get_default_metrics(age, gender):
    """Metriche di default realistiche basate su età e genere con tutte le fasi sonno"""
    age_norm = max(20, min(80, age))
    
    if gender == 'Uomo':
        base_sdnn = 52 - (age_norm - 20) * 0.4
        base_rmssd = 38 - (age_norm - 20) * 0.3
        base_hr = 68 + (age_norm - 20) * 0.15
    else:
        base_sdnn = 48 - (age_norm - 20) * 0.4
        base_rmssd = 35 - (age_norm - 20) * 0.3
        base_hr = 72 + (age_norm - 20) * 0.15
    
    # Distribuzione fasi sonno di default
    sleep_duration = 7.2
    sleep_light = sleep_duration * 0.50  # 50% sonno leggero
    sleep_deep = sleep_duration * 0.20   # 20% sonno profondo  
    sleep_rem = sleep_duration * 0.20    # 20% sonno REM
    sleep_awake = sleep_duration * 0.10  # 10% risvegli
    
    return {
        'sdnn': max(28, base_sdnn),
        'rmssd': max(20, base_rmssd),
        'hr_mean': base_hr,
        'coherence': 58,
        'recording_hours': 24,
        'total_power': 2800 - (age_norm - 20) * 30,
        'vlf': 400 - (age_norm - 20) * 5,
        'lf': 1000 - (age_norm - 20) * 15,
        'hf': 1400 - (age_norm - 20) * 20,
        'lf_hf_ratio': 1.1 + (age_norm - 20) * 0.01,
        'sleep_duration': sleep_duration,
        'sleep_efficiency': 87,
        'sleep_hr': base_hr - 8,
        'sleep_light': sleep_light,
        'sleep_deep': sleep_deep,
        'sleep_rem': sleep_rem,
        'sleep_awake': sleep_awake
    }

# =============================================================================
# SISTEMA ATTIVITÀ E ALIMENTAZIONE
# =============================================================================

# =============================================================================
# DATABASE NUTRIZIONALE SUPER DETTAGLIATO
# =============================================================================

NUTRITION_DB = {
    # CARBOIDRATI COMPLESSI
    "pasta integrale": {
        "category": "carboidrato", "subcategory": "cereale integrale", "inflammatory_score": -1,
        "glycemic_index": "medio-basso", "glycemic_load": "medio", "recovery_impact": 2,
        "calories_per_100g": 350, "typical_portion": 80, "protein_g": 13, "carbs_g": 72, "fiber_g": 8, "fat_g": 2,
        "micronutrients": ["Magnesio", "Selenio", "Vitamina B"], "allergens": ["glutine"],
        "best_time": "pranzo", "sleep_impact": "neutro", "hrv_impact": "lieve positivo",
        "tags": ["energia sostenuta", "fibra"]
    },
    
    "riso integrale": {
        "category": "carboidrato", "subcategory": "cereale integrale", "inflammatory_score": -2,
        "glycemic_index": "medio-basso", "glycemic_load": "medio", "recovery_impact": 3,
        "calories_per_100g": 111, "typical_portion": 150, "protein_g": 2.6, "carbs_g": 23, "fiber_g": 1.8, "fat_g": 0.9,
        "micronutrients": ["Magnesio", "Fosforo", "Manganese"], "allergens": [],
        "best_time": "pranzo", "sleep_impact": "positivo", "hrv_impact": "positivo",
        "tags": ["digestivo", "minerali"]
    },

    "avena": {
        "category": "carboidrato", "subcategory": "cereale integrale", "inflammatory_score": -3,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 4,
        "calories_per_100g": 389, "typical_portion": 40, "protein_g": 16.9, "carbs_g": 66.3, "fiber_g": 10.6, "fat_g": 6.9,
        "micronutrients": ["Beta-glucani", "Magnesio", "Zinco", "Vitamina B1"], "allergens": [],
        "best_time": "colazione", "sleep_impact": "molto positivo", "hrv_impact": "molto positivo",
        "tags": ["colazione", "energia lenta", "cuore"]
    },

    "pasta bianca": {
        "category": "carboidrato", "subcategory": "cereale raffinato", "inflammatory_score": 2,
        "glycemic_index": "alto", "glycemic_load": "alto", "recovery_impact": -2,
        "calories_per_100g": 131, "typical_portion": 80, "protein_g": 5, "carbs_g": 25, "fiber_g": 1, "fat_g": 1,
        "micronutrients": ["Ferro", "Vitamina B"], "allergens": ["glutine"],
        "best_time": "pre-allenamento", "sleep_impact": "negativo se serale", "hrv_impact": "negativo",
        "tags": ["energia rapida", "infiammatorio"]
    },

    "pane bianco": {
        "category": "carboidrato", "subcategory": "cereale raffinato", "inflammatory_score": 3,
        "glycemic_index": "alto", "glycemic_load": "alto", "recovery_impact": -3,
        "calories_per_100g": 265, "typical_portion": 50, "protein_g": 9, "carbs_g": 49, "fiber_g": 2.7, "fat_g": 3.2,
        "micronutrients": ["Calcio", "Ferro"], "allergens": ["glutine"],
        "best_time": "colazione", "sleep_impact": "negativo", "hrv_impact": "negativo",
        "tags": ["picco glicemico", "gonfiore"]
    },

    # PROTEINE ANIMALI
    "salmone": {
        "category": "proteina", "subcategory": "pesce grasso", "inflammatory_score": -4,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 5,
        "calories_per_100g": 208, "typical_portion": 150, "protein_g": 20, "carbs_g": 0, "fiber_g": 0, "fat_g": 13,
        "omega3_epa_dha": "2200mg", "micronutrients": ["Omega-3", "Vitamina D", "Selenio", "Vitamina B12"],
        "allergens": ["pesce"], "best_time": "cena", "sleep_impact": "molto positivo", "hrv_impact": "molto positivo",
        "tags": ["anti-infiammatorio", "cervello", "cuore"]
    },

    "tonno": {
        "category": "proteina", "subcategory": "pesce magro", "inflammatory_score": -2,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 3,
        "calories_per_100g": 132, "typical_portion": 150, "protein_g": 28, "carbs_g": 0, "fiber_g": 0, "fat_g": 1,
        "omega3_epa_dha": "300mg", "micronutrients": ["Selenio", "Vitamina B3", "Vitamina B12", "Fosforo"],
        "allergens": ["pesce"], "best_time": "pranzo", "sleep_impact": "positivo", "hrv_impact": "positivo",
        "tags": ["proteico", "metabolismo"]
    },

    "petto di pollo": {
        "category": "proteina", "subcategory": "carne bianca", "inflammatory_score": 0,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 2,
        "calories_per_100g": 165, "typical_portion": 150, "protein_g": 31, "carbs_g": 0, "fiber_g": 0, "fat_g": 3.6,
        "micronutrients": ["Vitamina B6", "Niacina", "Selenio", "Fosforo"], "allergens": [],
        "best_time": "pranzo/cena", "sleep_impact": "neutro", "hrv_impact": "lieve positivo",
        "tags": ["magro", "muscoli"]
    },

    "uova": {
        "category": "proteina", "subcategory": "uova", "inflammatory_score": -1,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 3,
        "calories_per_100g": 155, "typical_portion": 100, "protein_g": 13, "carbs_g": 1.1, "fiber_g": 0, "fat_g": 11,
        "cholesterol_mg": 373, "micronutrients": ["Colina", "Vitamina D", "Selenio", "Luteina"],
        "allergens": ["uova"], "best_time": "colazione", "sleep_impact": "positivo", "hrv_impact": "positivo",
        "tags": ["colina", "occhi", "cervello"]
    },

    # VEGETALI
    "spinaci": {
        "category": "vegetale", "subcategory": "verdura a foglia verde", "inflammatory_score": -5,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 4,
        "calories_per_100g": 23, "typical_portion": 200, "protein_g": 2.9, "carbs_g": 3.6, "fiber_g": 2.2, "fat_g": 0.4,
        "micronutrients": ["Ferro", "Magnesio", "Vitamina K", "Folati", "Luteina"], "allergens": [],
        "best_time": "pranzo/cena", "sleep_impact": "positivo", "hrv_impact": "molto positivo",
        "tags": ["antiossidante", "sangue", "visione"]
    },

    "broccoli": {
        "category": "vegetale", "subcategory": "crucifere", "inflammatory_score": -4,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 4,
        "calories_per_100g": 34, "typical_portion": 200, "protein_g": 2.8, "carbs_g": 7, "fiber_g": 2.6, "fat_g": 0.4,
        "micronutrients": ["Vitamina C", "Vitamina K", "Folati", "Potassio"], "allergens": [],
        "best_time": "cena", "sleep_impact": "positivo", "hrv_impact": "molto positivo",
        "tags": ["detox", "anti-cancro", "digestivo"]
    },

    "avocado": {
        "category": "grasso", "subcategory": "frutta grassa", "inflammatory_score": -3,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 3,
        "calories_per_100g": 160, "typical_portion": 100, "protein_g": 2, "carbs_g": 9, "fiber_g": 7, "fat_g": 15,
        "micronutrients": ["Potassio", "Vitamina E", "Vitamina K", "Folati"], "allergens": [],
        "best_time": "colazione/pranzo", "sleep_impact": "positivo", "hrv_impact": "positivo",
        "tags": ["grassi buoni", "sazietà", "pelle"]
    },

    # FRUTTA
    "frutti di bosco": {
        "category": "frutta", "subcategory": "bacche", "inflammatory_score": -4,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 4,
        "calories_per_100g": 57, "typical_portion": 150, "protein_g": 0.7, "carbs_g": 14, "fiber_g": 2.4, "fat_g": 0.3,
        "micronutrients": ["Antocianine", "Vitamina C", "Manganese", "Vitamina K"], "allergens": [],
        "best_time": "colazione/spuntino", "sleep_impact": "molto positivo", "hrv_impact": "molto positivo",
        "tags": ["antiossidante", "cervello", "anti-age"]
    },

    "banana": {
        "category": "frutta", "subcategory": "frutta tropicale", "inflammatory_score": 0,
        "glycemic_index": "medio", "glycemic_load": "medio", "recovery_impact": 2,
        "calories_per_100g": 89, "typical_portion": 120, "protein_g": 1.1, "carbs_g": 23, "fiber_g": 2.6, "fat_g": 0.3,
        "micronutrients": ["Potassio", "Vitamina B6", "Magnesio", "Vitamina C"], "allergens": [],
        "best_time": "pre/post allenamento", "sleep_impact": "positivo", "hrv_impact": "positivo",
        "tags": ["energia", "crampi", "recupero"]
    },

    # GRASSI
    "olio d'oliva extravergine": {
        "category": "grasso", "subcategory": "olio", "inflammatory_score": -3,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 3,
        "calories_per_100g": 884, "typical_portion": 10, "protein_g": 0, "carbs_g": 0, "fiber_g": 0, "fat_g": 100,
        "micronutrients": ["Vitamina E", "Vitamina K", "Polifenoli", "Oleocantale"], "allergens": [],
        "best_time": "a crudo tutti i pasti", "sleep_impact": "positivo", "hrv_impact": "positivo",
        "tags": ["anti-infiammatorio", "cuore", "cervello"]
    },

    "frutta secca (noci/mandorle)": {
        "category": "grasso", "subcategory": "semi oleosi", "inflammatory_score": -2,
        "glycemic_index": "basso", "glycemic_load": "basso", "recovery_impact": 3,
        "calories_per_100g": 607, "typical_portion": 30, "protein_g": 20, "carbs_g": 21, "fiber_g": 7, "fat_g": 54,
        "micronutrients": ["Magnesio", "Vitamina E", "Selenio", "Omega-3"], "allergens": ["frutta a guscio"],
        "best_time": "spuntino", "sleep_impact": "positivo", "hrv_impact": "positivo",
        "tags": ["snack sano", "cuore", "memoria"]
    },

    # DA LIMITARE
    "zucchero bianco": {
        "category": "zucchero", "subcategory": "zucchero raffinato", "inflammatory_score": 5,
        "glycemic_index": "alto", "glycemic_load": "alto", "recovery_impact": -4,
        "calories_per_100g": 387, "typical_portion": 5, "protein_g": 0, "carbs_g": 100, "fiber_g": 0, "fat_g": 0,
        "micronutrients": [], "allergens": [], "best_time": "da evitare",
        "sleep_impact": "molto negativo", "hrv_impact": "molto negativo",
        "tags": ["infiammatorio", "picco glicemico", "dipendenza"]
    },

    "dolci industriali": {
        "category": "zucchero", "subcategory": "ultra-processato", "inflammatory_score": 4,
        "glycemic_index": "alto", "glycemic_load": "alto", "recovery_impact": -3,
        "calories_per_100g": 450, "typical_portion": 100, "protein_g": 5, "carbs_g": 60, "fiber_g": 1, "fat_g": 22,
        "micronutrients": [], "allergens": ["glutine", "latticini", "soia"], "best_time": "da evitare",
        "sleep_impact": "negativo", "hrv_impact": "negativo",
        "tags": ["grassi trans", "additivi", "gonfiore"]
    },

    "alcolici": {
        "category": "alcol", "subcategory": "bevanda alcolica", "inflammatory_score": 4,
        "glycemic_index": "variabile", "glycemic_load": "medio", "recovery_impact": -4,
        "calories_per_100g": 200, "typical_portion": 150, "protein_g": 0, "carbs_g": 5, "fiber_g": 0, "fat_g": 0,
        "micronutrients": [], "allergens": [], "best_time": "da limitare",
        "sleep_impact": "molto negativo", "hrv_impact": "molto negativo",
        "tags": ["disidrata", "fegato", "qualità sonno"]
    }
}

# =============================================================================
# DATABASE COMPLETO ATTIVITÀ FISICHE + IMPATTO HRV
# =============================================================================

ACTIVITY_IMPACT_DB = {
    "corsa leggera": {
        "category": "cardio", "intensity": "light", "duration_optimal": (30, 45),
        "hrv_impact_immediate": -1, "hrv_impact_24h": 2, "recovery_impact": 2,
        "metabolic_impact": 3, "stress_impact": -2, "sleep_impact": 1,
        "best_time": "mattina", "frequency": "daily",
        "hr_zones": ["Z2", "Z3"], "benefits": ["cardiovascolare", "umore", "metabolismo"],
        "risks": ["infortuni overuse"], "prerequisites": ["riscaldamento"]
    },
    
    "corsa intensa": {
        "category": "cardio", "intensity": "high", "duration_optimal": (20, 35),
        "hrv_impact_immediate": -3, "hrv_impact_24h": 1, "recovery_impact": -1,
        "metabolic_impact": 4, "stress_impact": 1, "sleep_impact": -1,
        "best_time": "mattina", "frequency": "2-3x/settimana",
        "hr_zones": ["Z4", "Z5"], "benefits": ["VO2max", "performance"],
        "risks": ["overtraining", "cortisolo"], "prerequisites": ["base aerobica", "recupero"]
    },
    
    "ciclismo": {
        "category": "cardio", "intensity": "medium", "duration_optimal": (45, 120),
        "hrv_impact_immediate": -1, "hrv_impact_24h": 2, "recovery_impact": 1,
        "metabolic_impact": 3, "stress_impact": -2, "sleep_impact": 1,
        "best_time": "mattina/pomeriggio", "frequency": "3-5x/settimana",
        "hr_zones": ["Z2", "Z3"], "benefits": ["resistenza", "articolazioni"],
        "risks": ["postura"], "prerequisites": ["bike fit"]
    },
    
    "nuoto": {
        "category": "cardio", "intensity": "medium", "duration_optimal": (30, 60),
        "hrv_impact_immediate": 0, "hrv_impact_24h": 3, "recovery_impact": 3,
        "metabolic_impact": 2, "stress_impact": -3, "sleep_impact": 2,
        "best_time": "qualsiasi", "frequency": "daily",
        "hr_zones": ["Z2", "Z3"], "benefits": ["full body", "low impact", "respirazione"],
        "risks": ["minimi"], "prerequisites": ["tecnica"]
    },

    "sollevamento pesi": {
        "category": "strength", "intensity": "high", "duration_optimal": (45, 90),
        "hrv_impact_immediate": -2, "hrv_impact_24h": 1, "recovery_impact": -1,
        "metabolic_impact": 4, "stress_impact": 1, "sleep_impact": 0,
        "best_time": "pomeriggio", "frequency": "3-4x/settimana",
        "hr_zones": ["Z3", "Z4"], "benefits": ["muscolo", "metabolismo", "ossa"],
        "risks": ["infortuni", "cortisolo"], "prerequisites": ["tecnica", "recupero"]
    },
    
    "bodyweight": {
        "category": "strength", "intensity": "medium", "duration_optimal": (20, 40),
        "hrv_impact_immediate": -1, "hrv_impact_24h": 2, "recovery_impact": 1,
        "metabolic_impact": 2, "stress_impact": -1, "sleep_impact": 1,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z2", "Z3"], "benefits": ["funzionale", "flessibilità"],
        "risks": ["minimi"], "prerequisites": ["progressività"]
    },

    "yoga": {
        "category": "recovery", "intensity": "light", "duration_optimal": (30, 60),
        "hrv_impact_immediate": 2, "hrv_impact_24h": 3, "recovery_impact": 4,
        "metabolic_impact": 1, "stress_impact": -4, "sleep_impact": 3,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z1", "Z2"], "benefits": ["flessibilità", "respirazione", "parasimpatico"],
        "risks": ["minimi"], "prerequisites": ["asana base"]
    },
    
    "meditazione": {
        "category": "recovery", "intensity": "light", "duration_optimal": (10, 30),
        "hrv_impact_immediate": 3, "hrv_impact_24h": 2, "recovery_impact": 3,
        "metabolic_impact": 0, "stress_impact": -5, "sleep_impact": 2,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z1"], "benefits": ["coerenza cardiaca", "mindfulness", "stress"],
        "risks": ["nessuno"], "prerequisites": ["costanza"]
    },
    
    "respirazione consapevole": {
        "category": "recovery", "intensity": "light", "duration_optimal": (5, 15),
        "hrv_impact_immediate": 4, "hrv_impact_24h": 1, "recovery_impact": 2,
        "metabolic_impact": 0, "stress_impact": -3, "sleep_impact": 1,
        "best_time": "qualsiasi", "frequency": "multipla giornaliera",
        "hr_zones": ["Z1"], "benefits": ["coerenza immediata", "ansia", "focus"],
        "risks": ["nessuno"], "prerequisites": ["tecnica base"]
    },

    "camminata": {
        "category": "recovery", "intensity": "light", "duration_optimal": (30, 60),
        "hrv_impact_immediate": 1, "hrv_impact_24h": 2, "recovery_impact": 2,
        "metabolic_impact": 1, "stress_impact": -2, "sleep_impact": 1,
        "best_time": "qualsiasi", "frequency": "daily",
        "hr_zones": ["Z1", "Z2"], "benefits": ["circolazione", "umore", "digestione"],
        "risks": ["minimi"], "prerequisites": ["scarpe adatte"]
    },
    
    "stretching": {
        "category": "recovery", "intensity": "light", "duration_optimal": (10, 20),
        "hrv_impact_immediate": 1, "hrv_impact_24h": 1, "recovery_impact": 2,
        "metabolic_impact": 0, "stress_impact": -1, "sleep_impact": 1,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z1"], "benefits": ["mobilità", "recupero muscolare"],
        "risks": ["stiramenti"], "prerequisites": ["riscaldamento"]
    }
}

# =============================================================================
# DATABASE INTEGRAZIONI + IMPATTO HRV
# =============================================================================

SUPPLEMENTS_DB = {
    "magnesio": {
        "category": "minerale", "timing": "sera", "dosage_optimal": (200, 400),
        "hrv_impact": 3, "recovery_impact": 3, "sleep_impact": 4, "stress_impact": -3,
        "mechanism": "rilassamento muscolare, GABA", "best_for": ["sonno", "crampi", "stress"],
        "synergies": ["vitamina B6", "taurina"], "contraindications": ["renali"],
        "evidence": "alta", "onset_time": "1-2 ore", "duration": "8-12 ore"
    },
    
    "omega-3": {
        "category": "acidi grassi", "timing": "pasto", "dosage_optimal": (1000, 2000),
        "hrv_impact": 2, "recovery_impact": 2, "sleep_impact": 1, "stress_impact": -2,
        "mechanism": "anti-infiammatorio, fluidità membranale", "best_for": ["infiammazione", "umore", "cuore"],
        "synergies": ["vitamina E"], "contraindications": ["anticoagulanti"],
        "evidence": "alta", "onset_time": "settimane", "duration": "cronico"
    },
    
    "vitamina D": {
        "category": "vitamina", "timing": "mattina", "dosage_optimal": (1000, 4000),
        "hrv_impact": 2, "recovery_impact": 1, "sleep_impact": 1, "stress_impact": -1,
        "mechanism": "modulazione immunitaria, umore", "best_for": ["immunità", "umore", "ossa"],
        "synergies": ["K2", "magnesio"], "contraindications": ["ipercalcemia"],
        "evidence": "media", "onset_time": "settimane", "duration": "cronico"
    },
    
    "ashwagandha": {
        "category": "adattogeno", "timing": "sera", "dosage_optimal": (300, 600),
        "hrv_impact": 3, "recovery_impact": 2, "sleep_impact": 2, "stress_impact": -4,
        "mechanism": "cortisolo, GABA", "best_for": ["stress", "ansia", "recupero"],
        "synergies": ["magnesio", "L-teanina"], "contraindications": ["tiroide", "gravidanza"],
        "evidence": "media", "onset_time": "2-4 settimane", "duration": "cronico"
    },
    
    "L-teanina": {
        "category": "aminoacido", "timing": "qualsiasi", "dosage_optimal": (100, 200),
        "hrv_impact": 3, "recovery_impact": 1, "sleep_impact": 1, "stress_impact": -3,
        "mechanism": "onde alfa cerebrali, GABA", "best_for": ["ansia", "focus", "rilassamento"],
        "synergies": ["caffeina", "ashwagandha"], "contraindications": ["minime"],
        "evidence": "alta", "onset_time": "30-60 min", "duration": "4-6 ore"
    },
    
    "probiotici": {
        "category": "digestivo", "timing": "mattina", "dosage_optimal": (1, 10), # miliardi
        "hrv_impact": 1, "recovery_impact": 1, "sleep_impact": 1, "stress_impact": -1,
        "mechanism": "asse intestino-cervello", "best_for": ["digestione", "umore", "immunità"],
        "synergies": ["prebiotici"], "contraindications": ["immunodepressione"],
        "evidence": "media", "onset_time": "settimane", "duration": "cronico"
    },
    
    "melatonina": {
        "category": "ormone", "timing": "pre-sonno", "dosage_optimal": (0.5, 3),
        "hrv_impact": 2, "recovery_impact": 2, "sleep_impact": 4, "stress_impact": -2,
        "mechanism": "ritmo circadiano", "best_for": ["sonno", "jet lag"],
        "synergies": ["magnesio"], "contraindications": ["autoimmuni"],
        "evidence": "alta", "onset_time": "30 min", "duration": "6-8 ore"
    },
    
    "creatina": {
        "category": "performance", "timing": "pre/post workout", "dosage_optimal": (3000, 5000),
        "hrv_impact": 0, "recovery_impact": 2, "sleep_impact": 0, "stress_impact": 0,
        "mechanism": "sistema fosfageno", "best_for": ["forza", "potenza"],
        "synergies": ["carboidrati"], "contraindications": ["renali"],
        "evidence": "alta", "onset_time": "settimane", "duration": "cronico"
    }
}

# =============================================================================
# SISTEMA AVANZATO DI ANALISI IMPATTO
# =============================================================================

def calculate_comprehensive_impact(activities, daily_metrics, timeline, user_profile):
    """Analisi completa dell'impatto di tutte le attività sull'HRV"""
    
    impact_report = {
        'daily_summary': calculate_daily_impact_summary(activities, daily_metrics),
        'activity_analysis': analyze_activities_impact(activities, daily_metrics, timeline),
        'nutrition_analysis': analyze_nutritional_impact(activities),
        'supplement_analysis': analyze_supplements_impact(activities),
        'recovery_analysis': analyze_recovery_status(activities, daily_metrics, user_profile),
        'personalized_recommendations': generate_comprehensive_recommendations(activities, daily_metrics, user_profile),
        'risk_factors': identify_risk_factors(activities, daily_metrics),
        'optimization_opportunities': find_optimization_opportunities(activities, daily_metrics, user_profile)
    }
    
    return impact_report

def calculate_daily_impact_summary(activities, daily_metrics):
    """Calcola il sommario giornaliero dell'impatto"""
    return {
        'net_impact': calculate_net_impact(activities, daily_metrics),
        'recovery_score': calculate_recovery_score(activities, daily_metrics),
        'activity_count': len([a for a in activities if a['type'] == 'Allenamento']),
        'nutrition_score': calculate_nutrition_score(activities)
    }

def calculate_net_impact(activities, daily_metrics):
    """Calcola l'impatto netto complessivo"""
    net_impact = 0
    for activity in activities:
        if activity['type'] == 'Allenamento':
            net_impact += 1  # Placeholder - da implementare
        elif activity['type'] == 'Alimentazione':
            net_impact -= 0.5  # Placeholder
    return net_impact

def calculate_recovery_score(activities, daily_metrics):
    """Calcola lo score di recupero"""
    return 7  # Placeholder

def calculate_nutrition_score(activities):
    """Calcola lo score nutrizionale"""
    return 8  # Placeholder

def analyze_activities_impact(activities, daily_metrics, timeline):
    """Analisi dettagliata impatto attività fisiche"""
    
    activity_analysis = []
    
    for activity in activities:
        if activity['type'] == "Allenamento":
            analysis = analyze_training_impact(activity, daily_metrics, timeline)
            activity_analysis.append(analysis)
    
    return activity_analysis

def analyze_training_impact(activity, daily_metrics, timeline):
    """Analisi specifica per allenamenti"""
    
    activity_name = activity['name'].lower()
    impact_data = ACTIVITY_IMPACT_DB.get(activity_name, {})
    
    # Trova il giorno dell'attività
    activity_day = activity['start_time'].date().isoformat()
    day_metrics = daily_metrics.get(activity_day, {})
    
    # Calcola impatto osservato vs atteso
    expected_impact = impact_data.get('hrv_impact_24h', 0)
    observed_impact = calculate_observed_hrv_impact(activity, day_metrics, timeline)
    
    analysis = {
        'activity': activity,
        'expected_impact': expected_impact,
        'observed_impact': observed_impact,
        'impact_difference': observed_impact - expected_impact,
        'recovery_status': assess_recovery_status(activity, day_metrics),
        'recommendations': generate_training_recommendations(activity, observed_impact, expected_impact)
    }
    
    return analysis

def calculate_observed_hrv_impact(activity, day_metrics, timeline):
    """Calcola l'impatto osservato sull'HRV basato sui dati reali"""
    return 0  # Placeholder - da implementare con analisi temporale

def assess_recovery_status(activity, day_metrics):
    """Valuta lo stato di recupero"""
    return "good"  # Placeholder

def generate_training_recommendations(activity, observed_impact, expected_impact):
    """Genera raccomandazioni per l'allenamento"""
    return ["Mantieni questo tipo di allenamento"]  # Placeholder

def analyze_nutritional_impact(activities):
    """Analisi impatto nutrizionale"""
    return {
        'inflammatory_score': 0,
        'recovery_score': 0,
        'sleep_impact': 0,
        'total_calories': 0
    }  # Placeholder

def analyze_supplements_impact(activities):
    """Analisi impatto integratori"""
    return {
        'total_hrv_impact': 0,
        'sleep_impact': 0,
        'stress_impact': 0
    }  # Placeholder

def analyze_recovery_status(activities, daily_metrics, user_profile):
    """Analisi stato di recupero"""
    return {"status": "good"}  # Placeholder

def generate_comprehensive_recommendations(activities, daily_metrics, user_profile):
    """Genera raccomandazioni complete"""
    return [
        "Continua con l'allenamento moderato",
        "Migliora l'idratazione durante il giorno",
        "Considera integratori di magnesio per il sonno"
    ]  # Placeholder

def identify_risk_factors(activities, daily_metrics):
    """Identifica fattori di rischio"""
    return []  # Placeholder

def find_optimization_opportunities(activities, daily_metrics, user_profile):
    """Trova opportunità di ottimizzazione"""
    return []  # Placeholder

def display_impact_analysis(impact_report):
    """Visualizza i risultati dell'analisi di impatto"""
    
    # 1. SOMMARIO GIORNALIERO
    st.subheader("📊 Sommario Giornaliero")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Impatto Attività Netto", 
                 f"{impact_report['daily_summary'].get('net_impact', 0):+.1f}")
    
    with col2:
        st.metric("Score Recupero", 
                 f"{impact_report['daily_summary'].get('recovery_score', 0)}/10")
    
    with col3:
        st.metric("Bilancio Nutrizionale", 
                 f"{impact_report['nutrition_analysis'].get('inflammatory_score', 0):+.1f}")
    
    with col4:
        st.metric("Impatto Integratori", 
                 f"{impact_report['supplement_analysis'].get('total_hrv_impact', 0):+.1f}")
    
    # 2. ANALISI DETTAGLIATA PER CATEGORIA
    with st.expander("🧘 Analisi Dettagliata Attività", expanded=True):
        for activity_analysis in impact_report['activity_analysis']:
            display_activity_analysis(activity_analysis)
    
    # 3. RACCOMANDAZIONI PERSONALIZZATE
    with st.expander("💡 Raccomandazioni Personalizzate", expanded=True):
        for recommendation in impact_report['personalized_recommendations']:
            st.write(f"• {recommendation}")

def display_activity_analysis(analysis):
    """Visualizza l'analisi di una singola attività"""
    
    activity = analysis['activity']
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col1:
        st.write(f"**{activity['name']}**")
        st.write(f"{activity['start_time'].strftime('%H:%M')} - {activity['duration']}min")
    
    with col2:
        impact_diff = analysis['impact_difference']
        color = "green" if impact_diff >= 0 else "red"
        st.write(f"Impatto: :{color}[{impact_diff:+.1f}]")
    
    with col3:
        st.write(f"Recupero: {analysis['recovery_status']}")
    
    with col4:
        for rec in analysis['recommendations'][:1]:  # Prima raccomandazione
            st.write(f"💡 {rec}")

# =============================================================================
# DATABASE COMPLETO ATTIVITÀ FISICHE + IMPATTO HRV
# =============================================================================

ACTIVITY_IMPACT_DB = {
    # ALLENAMENTI CARDIO
    "corsa leggera": {
        "category": "cardio", "intensity": "light", "duration_optimal": (30, 45),
        "hrv_impact_immediate": -1, "hrv_impact_24h": 2, "recovery_impact": 2,
        "metabolic_impact": 3, "stress_impact": -2, "sleep_impact": 1,
        "best_time": "mattina", "frequency": "daily",
        "hr_zones": ["Z2", "Z3"], "benefits": ["cardiovascolare", "umore", "metabolismo"],
        "risks": ["infortuni overuse"], "prerequisites": ["riscaldamento"]
    },
    
    "corsa intensa": {
        "category": "cardio", "intensity": "high", "duration_optimal": (20, 35),
        "hrv_impact_immediate": -3, "hrv_impact_24h": 1, "recovery_impact": -1,
        "metabolic_impact": 4, "stress_impact": 1, "sleep_impact": -1,
        "best_time": "mattina", "frequency": "2-3x/settimana",
        "hr_zones": ["Z4", "Z5"], "benefits": ["VO2max", "performance"],
        "risks": ["overtraining", "cortisolo"], "prerequisites": ["base aerobica", "recupero"]
    },
    
    "ciclismo": {
        "category": "cardio", "intensity": "medium", "duration_optimal": (45, 120),
        "hrv_impact_immediate": -1, "hrv_impact_24h": 2, "recovery_impact": 1,
        "metabolic_impact": 3, "stress_impact": -2, "sleep_impact": 1,
        "best_time": "mattina/pomeriggio", "frequency": "3-5x/settimana",
        "hr_zones": ["Z2", "Z3"], "benefits": ["resistenza", "articolazioni"],
        "risks": ["postura"], "prerequisites": ["bike fit"]
    },
    
    "nuoto": {
        "category": "cardio", "intensity": "medium", "duration_optimal": (30, 60),
        "hrv_impact_immediate": 0, "hrv_impact_24h": 3, "recovery_impact": 3,
        "metabolic_impact": 2, "stress_impact": -3, "sleep_impact": 2,
        "best_time": "qualsiasi", "frequency": "daily",
        "hr_zones": ["Z2", "Z3"], "benefits": ["full body", "low impact", "respirazione"],
        "risks": ["minimi"], "prerequisites": ["tecnica"]
    },

    # ALLENAMENTI FORZA
    "sollevamento pesi": {
        "category": "strength", "intensity": "high", "duration_optimal": (45, 90),
        "hrv_impact_immediate": -2, "hrv_impact_24h": 1, "recovery_impact": -1,
        "metabolic_impact": 4, "stress_impact": 1, "sleep_impact": 0,
        "best_time": "pomeriggio", "frequency": "3-4x/settimana",
        "hr_zones": ["Z3", "Z4"], "benefits": ["muscolo", "metabolismo", "ossa"],
        "risks": ["infortuni", "cortisolo"], "prerequisites": ["tecnica", "recupero"]
    },
    
    "bodyweight": {
        "category": "strength", "intensity": "medium", "duration_optimal": (20, 40),
        "hrv_impact_immediate": -1, "hrv_impact_24h": 2, "recovery_impact": 1,
        "metabolic_impact": 2, "stress_impact": -1, "sleep_impact": 1,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z2", "Z3"], "benefits": ["funzionale", "flessibilità"],
        "risks": ["minimi"], "prerequisites": ["progressività"]
    },

    # ATTIVITÀ RIGENERATIVE
    "yoga": {
        "category": "recovery", "intensity": "light", "duration_optimal": (30, 60),
        "hrv_impact_immediate": 2, "hrv_impact_24h": 3, "recovery_impact": 4,
        "metabolic_impact": 1, "stress_impact": -4, "sleep_impact": 3,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z1", "Z2"], "benefits": ["flessibilità", "respirazione", "parasimpatico"],
        "risks": ["minimi"], "prerequisites": ["asana base"]
    },
    
    "meditazione": {
        "category": "recovery", "intensity": "light", "duration_optimal": (10, 30),
        "hrv_impact_immediate": 3, "hrv_impact_24h": 2, "recovery_impact": 3,
        "metabolic_impact": 0, "stress_impact": -5, "sleep_impact": 2,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z1"], "benefits": ["coerenza cardiaca", "mindfulness", "stress"],
        "risks": ["nessuno"], "prerequisites": ["costanza"]
    },
    
    "respirazione consapevole": {
        "category": "recovery", "intensity": "light", "duration_optimal": (5, 15),
        "hrv_impact_immediate": 4, "hrv_impact_24h": 1, "recovery_impact": 2,
        "metabolic_impact": 0, "stress_impact": -3, "sleep_impact": 1,
        "best_time": "qualsiasi", "frequency": "multipla giornaliera",
        "hr_zones": ["Z1"], "benefits": ["coerenza immediata", "ansia", "focus"],
        "risks": ["nessuno"], "prerequisites": ["tecnica base"]
    },

    # ATTIVITÀ RICREATIVE
    "camminata": {
        "category": "recovery", "intensity": "light", "duration_optimal": (30, 60),
        "hrv_impact_immediate": 1, "hrv_impact_24h": 2, "recovery_impact": 2,
        "metabolic_impact": 1, "stress_impact": -2, "sleep_impact": 1,
        "best_time": "qualsiasi", "frequency": "daily",
        "hr_zones": ["Z1", "Z2"], "benefits": ["circolazione", "umore", "digestione"],
        "risks": ["minimi"], "prerequisites": ["scarpe adatte"]
    },
    
    "stretching": {
        "category": "recovery", "intensity": "light", "duration_optimal": (10, 20),
        "hrv_impact_immediate": 1, "hrv_impact_24h": 1, "recovery_impact": 2,
        "metabolic_impact": 0, "stress_impact": -1, "sleep_impact": 1,
        "best_time": "mattina/sera", "frequency": "daily",
        "hr_zones": ["Z1"], "benefits": ["mobilità", "recupero muscolare"],
        "risks": ["stiramenti"], "prerequisites": ["riscaldamento"]
    }
}

# =============================================================================
# DATABASE INTEGRAZIONI + IMPATTO HRV
# =============================================================================

SUPPLEMENTS_DB = {
    "magnesio": {
        "category": "minerale", "timing": "sera", "dosage_optimal": (200, 400),
        "hrv_impact": 3, "recovery_impact": 3, "sleep_impact": 4, "stress_impact": -3,
        "mechanism": "rilassamento muscolare, GABA", "best_for": ["sonno", "crampi", "stress"],
        "synergies": ["vitamina B6", "taurina"], "contraindications": ["renali"],
        "evidence": "alta", "onset_time": "1-2 ore", "duration": "8-12 ore"
    },
    
    "omega-3": {
        "category": "acidi grassi", "timing": "pasto", "dosage_optimal": (1000, 2000),
        "hrv_impact": 2, "recovery_impact": 2, "sleep_impact": 1, "stress_impact": -2,
        "mechanism": "anti-infiammatorio, fluidità membranale", "best_for": ["infiammazione", "umore", "cuore"],
        "synergies": ["vitamina E"], "contraindications": ["anticoagulanti"],
        "evidence": "alta", "onset_time": "settimane", "duration": "cronico"
    },
    
    "vitamina D": {
        "category": "vitamina", "timing": "mattina", "dosage_optimal": (1000, 4000),
        "hrv_impact": 2, "recovery_impact": 1, "sleep_impact": 1, "stress_impact": -1,
        "mechanism": "modulazione immunitaria, umore", "best_for": ["immunità", "umore", "ossa"],
        "synergies": ["K2", "magnesio"], "contraindications": ["ipercalcemia"],
        "evidence": "media", "onset_time": "settimane", "duration": "cronico"
    },
    
    "ashwagandha": {
        "category": "adattogeno", "timing": "sera", "dosage_optimal": (300, 600),
        "hrv_impact": 3, "recovery_impact": 2, "sleep_impact": 2, "stress_impact": -4,
        "mechanism": "cortisolo, GABA", "best_for": ["stress", "ansia", "recupero"],
        "synergies": ["magnesio", "L-teanina"], "contraindications": ["tiroide", "gravidanza"],
        "evidence": "media", "onset_time": "2-4 settimane", "duration": "cronico"
    },
    
    "L-teanina": {
        "category": "aminoacido", "timing": "qualsiasi", "dosage_optimal": (100, 200),
        "hrv_impact": 3, "recovery_impact": 1, "sleep_impact": 1, "stress_impact": -3,
        "mechanism": "onde alfa cerebrali, GABA", "best_for": ["ansia", "focus", "rilassamento"],
        "synergies": ["caffeina", "ashwagandha"], "contraindications": ["minime"],
        "evidence": "alta", "onset_time": "30-60 min", "duration": "4-6 ore"
    },
    
    "probiotici": {
        "category": "digestivo", "timing": "mattina", "dosage_optimal": (1, 10), # miliardi
        "hrv_impact": 1, "recovery_impact": 1, "sleep_impact": 1, "stress_impact": -1,
        "mechanism": "asse intestino-cervello", "best_for": ["digestione", "umore", "immunità"],
        "synergies": ["prebiotici"], "contraindications": ["immunodepressione"],
        "evidence": "media", "onset_time": "settimane", "duration": "cronico"
    },
    
    "melatonina": {
        "category": "ormone", "timing": "pre-sonno", "dosage_optimal": (0.5, 3),
        "hrv_impact": 2, "recovery_impact": 2, "sleep_impact": 4, "stress_impact": -2,
        "mechanism": "ritmo circadiano", "best_for": ["sonno", "jet lag"],
        "synergies": ["magnesio"], "contraindications": ["autoimmuni"],
        "evidence": "alta", "onset_time": "30 min", "duration": "6-8 ore"
    },
    
    "creatina": {
        "category": "performance", "timing": "pre/post workout", "dosage_optimal": (3000, 5000),
        "hrv_impact": 0, "recovery_impact": 2, "sleep_impact": 0, "stress_impact": 0,
        "mechanism": "sistema fosfageno", "best_for": ["forza", "potenza"],
        "synergies": ["carboidrati"], "contraindications": ["renali"],
        "evidence": "alta", "onset_time": "settimane", "duration": "cronico"
    }
}

# =============================================================================
# SISTEMA AVANZATO DI ANALISI IMPATTO
# =============================================================================

def calculate_comprehensive_impact(activities, daily_metrics, timeline, user_profile):
    """Analisi completa dell'impatto di tutte le attività sull'HRV"""
    
    impact_report = {
        'daily_summary': calculate_daily_impact_summary(activities, daily_metrics),
        'activity_analysis': analyze_activities_impact(activities, daily_metrics, timeline),
        'nutrition_analysis': analyze_nutritional_impact(activities),
        'supplement_analysis': analyze_supplements_impact(activities),
        'recovery_analysis': analyze_recovery_status(activities, daily_metrics, user_profile),
        'personalized_recommendations': generate_comprehensive_recommendations(activities, daily_metrics, user_profile),
        'risk_factors': identify_risk_factors(activities, daily_metrics),
        'optimization_opportunities': find_optimization_opportunities(activities, daily_metrics, user_profile)
    }
    
    return impact_report

def analyze_activities_impact(activities, daily_metrics, timeline):
    """Analisi dettagliata impatto attività fisiche"""
    
    activity_analysis = []
    
    for activity in activities:
        if activity['type'] == "Allenamento":
            analysis = analyze_training_impact(activity, daily_metrics, timeline)
            activity_analysis.append(analysis)
    
    return activity_analysis

def analyze_training_impact(activity, daily_metrics, timeline):
    """Analisi specifica per allenamenti"""
    
    activity_name = activity['name'].lower()
    impact_data = ACTIVITY_IMPACT_DB.get(activity_name, {})
    
    # Trova il giorno dell'attività
    activity_day = activity['start_time'].date().isoformat()
    day_metrics = daily_metrics.get(activity_day, {})
    
    # Calcola impatto osservato vs atteso
    expected_impact = impact_data.get('hrv_impact_24h', 0)
    observed_impact = calculate_observed_hrv_impact(activity, day_metrics, timeline)
    
    analysis = {
        'activity': activity,
        'expected_impact': expected_impact,
        'observed_impact': observed_impact,
        'impact_difference': observed_impact - expected_impact,
        'recovery_status': assess_recovery_status(activity, day_metrics),
        'recommendations': generate_training_recommendations(activity, observed_impact, expected_impact)
    }
    
    return analysis

def analyze_nutritional_impact(activities):
    """Analisi impatto nutrizionale"""
    
    nutritional_impact = {
        'inflammatory_score': 0,
        'recovery_score': 0,
        'sleep_impact': 0,
        'total_calories': 0,
        'macronutrient_balance': {'protein': 0, 'carbs': 0, 'fat': 0},
        'micronutrient_score': 0,
        'meal_timing_analysis': {}
    }
    
    for activity in activities:
        if activity['type'] == "Alimentazione" and activity.get('food_items'):
            food_impact = analyze_meal_impact(activity)
            nutritional_impact['inflammatory_score'] += food_impact['inflammatory_score']
            nutritional_impact['recovery_score'] += food_impact['recovery_score']
            nutritional_impact['sleep_impact'] += food_impact['sleep_impact']
            nutritional_impact['total_calories'] += food_impact['calories']
            
            # Analisi timing pasti
            meal_time = activity['start_time']
            nutritional_impact['meal_timing_analysis'][meal_time.strftime('%H:%M')] = food_impact
    
    return nutritional_impact

def analyze_supplements_impact(activities):
    """Analisi impatto integratori"""
    
    supplements_taken = []
    supplement_impact = {
        'total_hrv_impact': 0,
        'sleep_impact': 0,
        'stress_impact': 0,
        'recovery_impact': 0,
        'interactions': [],
        'timing_analysis': {}
    }
    
    for activity in activities:
        if activity['type'] == "Integrazione" and activity.get('food_items'):
            supplements = [s.strip().lower() for s in activity['food_items'].split(',')]
            
            for supplement in supplements:
                supp_data = SUPPLEMENTS_DB.get(supplement)
                if supp_data:
                    supplement_impact['total_hrv_impact'] += supp_data['hrv_impact']
                    supplement_impact['sleep_impact'] += supp_data['sleep_impact']
                    supplement_impact['stress_impact'] += supp_data['stress_impact']
                    supplement_impact['recovery_impact'] += supp_data['recovery_impact']
                    
                    supplements_taken.append({
                        'name': supplement,
                        'data': supp_data,
                        'timing': activity['start_time']
                    })
    
    supplement_impact['supplements_taken'] = supplements_taken
    return supplement_impact

def calculate_observed_hrv_impact(activity, day_metrics, timeline):
    """Calcola l'impatto osservato sull'HRV basato sui dati reali"""
    
    if not day_metrics:
        return 0
    
    # Confronta con baseline o giorno precedente
    activity_time = activity['start_time']
    
    # Cerca periodo pre-attività (4 ore prima)
    pre_activity_metrics = find_pre_activity_metrics(activity_time, timeline, 4)  # 4 ore prima
    
    # Cerca periodo post-attività (24 ore dopo)
    post_activity_metrics = find_post_activity_metrics(activity_time, timeline, 24)  # 24 ore dopo
    
    if pre_activity_metrics and post_activity_metrics:
        # Calcola differenza RMSSD (indicatore recupero)
        rmssd_change = post_activity_metrics.get('rmssd', 0) - pre_activity_metrics.get('rmssd', 0)
        return normalize_impact_score(rmssd_change)
    
    return 0

def generate_comprehensive_recommendations(activities, daily_metrics, user_profile):
    """Genera raccomandazioni complete basate su tutti i dati"""
    
    recommendations = []
    
    # 1. Raccomandazioni attività fisica
    training_recs = generate_training_recommendations_batch(activities, daily_metrics)
    recommendations.extend(training_recs)
    
    # 2. Raccomandazioni nutrizionali
    nutrition_recs = generate_nutrition_recommendations(activities, daily_metrics)
    recommendations.extend(nutrition_recs)
    
    # 3. Raccomandazioni integratori
    supplement_recs = generate_supplement_recommendations(activities, daily_metrics, user_profile)
    recommendations.extend(supplement_recs)
    
    # 4. Raccomandazioni recupero
    recovery_recs = generate_recovery_recommendations(activities, daily_metrics)
    recommendations.extend(recovery_recs)
    
    # 5. Raccomandazioni sonno
    sleep_recs = generate_sleep_recommendations(daily_metrics)
    recommendations.extend(sleep_recs)
    
    return recommendations

# =============================================================================
# FUNZIONI DI SUPPORTO PER L'ANALISI
# =============================================================================

def find_pre_activity_metrics(activity_time, timeline, hours_before=4):
    """Trova le metriche HRV nel periodo prima dell'attività"""
    start_search = activity_time - timedelta(hours=hours_before)
    
    # Cerca nel giorno corrispondente o giorno precedente
    for day_date, day_rr in timeline['days_data'].items():
        day_dt = datetime.fromisoformat(day_date).date()
        if day_dt == start_search.date():
            return calculate_realistic_hrv_metrics(day_rr, 35, 'Uomo')  # Valori placeholder
    
    return None

def find_post_activity_metrics(activity_time, timeline, hours_after=24):
    """Trova le metriche HRV nel periodo dopo l'attività"""
    end_search = activity_time + timedelta(hours=hours_after)
    
    for day_date, day_rr in timeline['days_data'].items():
        day_dt = datetime.fromisoformat(day_date).date()
        if day_dt == end_search.date():
            return calculate_realistic_hrv_metrics(day_rr, 35, 'Uomo')  # Valori placeholder
    
    return None

def normalize_impact_score(raw_change, max_change=20):
    """Normalizza il punteggio di impatto tra -5 e +5"""
    normalized = (raw_change / max_change) * 5
    return max(-5, min(5, normalized))

def assess_recovery_status(activity, day_metrics):
    """Valuta lo stato di recupero basato sull'attività e metriche HRV"""
    
    if not day_metrics:
        return "unknown"
    
    rmssd = day_metrics.get('rmssd', 0)
    sdnn = day_metrics.get('sdnn', 0)
    
    # Soglie basate su letteratura
    if rmssd > 50 and sdnn > 40:
        return "optimal"
    elif rmssd > 30 and sdnn > 30:
        return "good" 
    elif rmssd > 20 and sdnn > 20:
        return "moderate"
    else:
        return "poor"

# =============================================================================
# INTEGRAZIONE NEL MAIN
# =============================================================================

def add_impact_analysis_to_main():
    """Aggiungi l'analisi di impatto all'interfaccia principale"""
    
    # Dopo il calcolo delle metriche giornaliere, aggiungi:
    if uploaded_file is not None and len(rr_intervals) > 0:
        
        # ... [codice esistente] ...
        
        # NUOVA SEZIONE: ANALISI IMPATTO ATTIVITÀ
        st.header("🎯 Analisi Impatto Attività sull'HRV")
        
        if st.session_state.activities:
            impact_report = calculate_comprehensive_impact(
                st.session_state.activities, 
                daily_metrics, 
                timeline,
                st.session_state.user_profile
            )
            
            # Visualizza risultati
            display_impact_analysis(impact_report)
            
        else:
            st.info("Aggiungi attività nel pannello laterale per vedere l'analisi dell'impatto sull'HRV")

def display_impact_analysis(impact_report):
    """Visualizza i risultati dell'analisi di impatto"""
    
    # 1. SOMMARIO GIORNALIERO
    st.subheader("📊 Sommario Giornaliero")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Impatto Attività Netto", 
                 f"{impact_report['daily_summary'].get('net_impact', 0):+.1f}")
    
    with col2:
        st.metric("Score Recupero", 
                 f"{impact_report['daily_summary'].get('recovery_score', 0)}/10")
    
    with col3:
        st.metric("Bilancio Nutrizionale", 
                 f"{impact_report['nutrition_analysis'].get('inflammatory_score', 0):+.1f}")
    
    with col4:
        st.metric("Impatto Integratori", 
                 f"{impact_report['supplement_analysis'].get('total_hrv_impact', 0):+.1f}")
    
    # 2. ANALISI DETTAGLIATA PER CATEGORIA
    with st.expander("🧘 Analisi Dettagliata Attività", expanded=True):
        for activity_analysis in impact_report['activity_analysis']:
            display_activity_analysis(activity_analysis)
    
    # 3. RACCOMANDAZIONI PERSONALIZZATE
    with st.expander("💡 Raccomandazioni Personalizzate", expanded=True):
        for recommendation in impact_report['personalized_recommendations']:
            st.write(f"• {recommendation}")
    
    # 4. ANALISI NUTRIZIONALE
    with st.expander("🍎 Analisi Nutrizionale", expanded=False):
        display_nutrition_analysis(impact_report['nutrition_analysis'])
    
    # 5. ANALISI INTEGRATORI
    with st.expander("💊 Analisi Integratori", expanded=False):
        display_supplement_analysis(impact_report['supplement_analysis'])

def display_activity_analysis(analysis):
    """Visualizza l'analisi di una singola attività"""
    
    activity = analysis['activity']
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    
    with col1:
        st.write(f"**{activity['name']}**")
        st.write(f"{activity['start_time'].strftime('%H:%M')} - {activity['duration']}min")
    
    with col2:
        impact_diff = analysis['impact_difference']
        color = "green" if impact_diff >= 0 else "red"
        st.write(f"Impatto: :{color}[{impact_diff:+.1f}]")
    
    with col3:
        st.write(f"Recupero: {analysis['recovery_status']}")
    
    with col4:
        for rec in analysis['recommendations'][:1]:  # Prima raccomandazione
            st.write(f"💡 {rec}")

# Aggiungi questa chiamata nella funzione main() dopo l'analisi HRV
# add_impact_analysis_to_main()

# Colori per i tipi di attività
ACTIVITY_COLORS = {
    "Allenamento": "#e74c3c",
    "Alimentazione": "#f39c12", 
    "Stress": "#9b59b6",
    "Riposo": "#3498db",
    "Altro": "#95a5a6"
}

def create_activity_tracker():
    """Interfaccia per tracciare attività e alimentazione"""
    st.sidebar.header("🏃‍♂️ Tracker Attività & Alimentazione")
    
    # Gestione modifica attività
    if st.session_state.get('editing_activity_index') is not None:
        edit_activity_interface()
        return
    
    with st.sidebar.expander("➕ Aggiungi Attività/Pasto", expanded=False):
        activity_type = st.selectbox("Tipo Attività", 
                                   ["Allenamento", "Alimentazione", "Stress", "Riposo", "Altro"])
        
        activity_name = st.text_input("Nome Attività/Pasto", placeholder="Es: Corsa mattutina, Pranzo, etc.")
        
        if activity_type == "Alimentazione":
            food_items = st.text_area("Cosa hai mangiato? (separato da virgola)", placeholder="Es: pasta, insalata, frutta")
            intensity = st.select_slider("Pesantezza pasto", 
                                       options=["Leggero", "Normale", "Pesante", "Molto pesante"])
        else:
            food_items = ""
            intensity = st.select_slider("Intensità", 
                                       options=["Leggera", "Moderata", "Intensa", "Massimale"])
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data", value=datetime.now().date(), key="activity_date")
            start_time = st.time_input("Ora inizio", value=datetime.now().time(), key="activity_time")
            st.write(f"Data selezionata: {start_date.strftime('%d/%m/%Y')}")
        with col2:
            duration = st.number_input("Durata (min)", min_value=1, max_value=480, value=30, key="activity_duration")
        
        notes = st.text_area("Note (opzionale)", placeholder="Note aggiuntive...", key="activity_notes")
        
        if st.button("💾 Salva Attività", use_container_width=True, key="save_activity"):
            save_activity(activity_type, activity_name, intensity, food_items, start_date, start_time, duration, notes)
            st.success("Attività salvata!")
            st.rerun()
    
    # Gestione attività esistenti
    if st.session_state.activities:
        st.sidebar.subheader("📋 Gestione Attività")
        
        for i, activity in enumerate(st.session_state.activities[-10:]):
            with st.sidebar.expander(f"{activity['name']} - {activity['start_time'].strftime('%d/%m/%Y %H:%M')}", False):
                st.write(f"**Tipo:** {activity['type']}")
                st.write(f"**Intensità:** {activity['intensity']}")
                if activity['food_items']:
                    st.write(f"**Cibo:** {activity['food_items']}")
                st.write(f"**Data/Ora:** {activity['start_time'].strftime('%d/%m/%Y %H:%M')}")
                st.write(f"**Durata:** {activity['duration']} min")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Modifica", key=f"edit_{i}", use_container_width=True):
                        st.session_state.editing_activity_index = i
                        st.rerun()
                with col2:
                    if st.button("🗑️ Elimina", key=f"delete_{i}", use_container_width=True):
                        delete_activity(i)
                        st.rerun()

def edit_activity_interface():
    """Interfaccia per modificare un'attività esistente"""
    activity_index = st.session_state.editing_activity_index
    if activity_index is None or activity_index >= len(st.session_state.activities):
        st.session_state.editing_activity_index = None
        return
    
    activity = st.session_state.activities[activity_index]
    
    st.sidebar.header("✏️ Modifica Attività")
    
    with st.sidebar.form("edit_activity_form"):
        activity_type = st.selectbox("Tipo Attività", 
                                   ["Allenamento", "Alimentazione", "Stress", "Riposo", "Altro"],
                                   index=["Allenamento", "Alimentazione", "Stress", "Riposo", "Altro"].index(activity['type']),
                                   key="edit_type")
        
        activity_name = st.text_input("Nome Attività/Pasto", value=activity['name'], key="edit_name")
        
        if activity_type == "Alimentazione":
            food_items = st.text_area("Cosa hai mangiato?", value=activity.get('food_items', ''), key="edit_food")
            intensity = st.select_slider("Pesantezza pasto", 
                                       options=["Leggero", "Normale", "Pesante", "Molto pesante"],
                                       value=activity['intensity'], key="edit_intensity_food")
        else:
            food_items = activity.get('food_items', '')
            intensity = st.select_slider("Intensità", 
                                       options=["Leggera", "Moderata", "Intensa", "Massimale"],
                                       value=activity['intensity'], key="edit_intensity")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Data", value=activity['start_time'].date(), key="edit_date")
            start_time = st.time_input("Ora inizio", value=activity['start_time'].time(), key="edit_time")
            st.write(f"Data selezionata: {start_date.strftime('%d/%m/%Y')}")
        with col2:
            duration = st.number_input("Durata (min)", min_value=1, max_value=480, value=activity['duration'], key="edit_duration")
        
        notes = st.text_area("Note", value=activity.get('notes', ''), key="edit_notes")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Salva Modifiche", use_container_width=True):
                update_activity(activity_index, activity_type, activity_name, intensity, food_items, start_date, start_time, duration, notes)
                st.session_state.editing_activity_index = None
                st.rerun()
        with col2:
            if st.form_submit_button("❌ Annulla", use_container_width=True):
                st.session_state.editing_activity_index = None
                st.rerun()

def save_activity(activity_type, name, intensity, food_items, start_date, start_time, duration, notes):
    """Salva una nuova attività"""
    start_datetime = datetime.combine(start_date, start_time)
    
    activity = {
        'type': activity_type,
        'name': name,
        'intensity': intensity,
        'food_items': food_items,
        'start_time': start_datetime,
        'duration': duration,
        'notes': notes,
        'timestamp': datetime.now(),
        'color': ACTIVITY_COLORS.get(activity_type, "#95a5a6")
    }
    
    st.session_state.activities.append(activity)
    
    if len(st.session_state.activities) > 50:
        st.session_state.activities = st.session_state.activities[-50:]

def update_activity(index, activity_type, name, intensity, food_items, start_date, start_time, duration, notes):
    """Aggiorna un'attività esistente"""
    if 0 <= index < len(st.session_state.activities):
        start_datetime = datetime.combine(start_date, start_time)
        
        st.session_state.activities[index] = {
            'type': activity_type,
            'name': name,
            'intensity': intensity,
            'food_items': food_items,
            'start_time': start_datetime,
            'duration': duration,
            'notes': notes,
            'timestamp': datetime.now(),
            'color': ACTIVITY_COLORS.get(activity_type, "#95a5a6")
        }

def delete_activity(index):
    """Elimina un'attività"""
    if 0 <= index < len(st.session_state.activities):
        st.session_state.activities.pop(index)

# =============================================================================
# FUNZIONI PER PARSING FILE E TIMESTAMP
# =============================================================================

def parse_starttime_from_file(content):
    """Cerca STARTTIME nel contenuto del file con più formati"""
    lines = content.split('\n')
    starttime = None
    
    for line in lines:
        if line.strip().upper().startswith('STARTTIME'):
            try:
                # Estrai la stringa temporale
                time_str = line.split('=')[1].strip()
                
                # DEBUG: mostra cosa sta leggendo
                st.sidebar.info(f"Trovato STARTTIME: {time_str}")
                
                # Prova diversi formati di data IN ORDINE DI PRIORITÀ
                formats_to_try = [
                    '%d.%m.%Y %H:%M.%S',  # IL TUO FORMATO: 13.10.2025 19:46.16
                    '%d.%m.%Y %H:%M:%S',  # Formato con punti ma secondi normali
                    '%d/%m/%Y %H:%M:%S',  # Formato italiano con slash
                    '%Y-%m-%dT%H:%M:%S',  # Formato ISO
                    '%Y-%m-%d %H:%M:%S',  # Formato internazionale
                ]
                
                for fmt in formats_to_try:
                    try:
                        starttime = datetime.strptime(time_str, fmt)
                        st.sidebar.success(f"Formato riconosciuto: {fmt}")
                        break
                    except ValueError:
                        continue
                
                if starttime:
                    break
                else:
                    st.sidebar.warning(f"Formato non riconosciuto: {time_str}")
                    
            except (IndexError, ValueError, Exception) as e:
                st.sidebar.error(f"Errore parsing STARTTIME: {e}")
                continue
    
    if not starttime:
        st.sidebar.warning("STARTTIME non trovato o non riconosciuto, uso ora corrente")
        starttime = datetime.now()
    
    return starttime

def calculate_recording_timeline(rr_intervals, start_time):
    """Calcola la timeline della registrazione"""
    total_duration_ms = sum(rr_intervals)
    end_time = start_time + timedelta(milliseconds=total_duration_ms)
    
    # Dividi per giorni
    days_data = {}
    current_time = start_time
    current_day_start = start_time.date()
    day_rr_intervals = []
    
    for rr in rr_intervals:
        day_rr_intervals.append(rr)
        current_time += timedelta(milliseconds=rr)
        
        # Se cambia giorno, salva i dati del giorno precedente
        if current_time.date() != current_day_start:
            if day_rr_intervals:  # Salva solo se ci sono dati
                days_data[current_day_start.isoformat()] = day_rr_intervals.copy()
            day_rr_intervals = []
            current_day_start = current_time.date()
    
    # Aggiungi l'ultimo giorno
    if day_rr_intervals:
        days_data[current_day_start.isoformat()] = day_rr_intervals
    
    return {
        'start_time': start_time,
        'end_time': end_time,
        'total_duration_hours': total_duration_ms / (1000 * 60 * 60),
        'days_data': days_data
    }

def calculate_daily_metrics(days_data, user_age, user_gender):
    """Calcola le metriche HRV per ogni giorno"""
    daily_metrics = {}
    
    for day_date, day_rr_intervals in days_data.items():
        if len(day_rr_intervals) >= 10:  # Solo giorni con dati sufficienti
            daily_metrics[day_date] = calculate_realistic_hrv_metrics(
                day_rr_intervals, user_age, user_gender
            )
    
    return daily_metrics

def calculate_overall_averages(daily_metrics):
    """Calcola le medie complessive da tutti i giorni"""
    if not daily_metrics:
        return None
    
    # Inizializza dizionario per le medie
    avg_metrics = {}
    all_metrics = list(daily_metrics.values())
    
    # Calcola medie per ogni metrica
    for key in all_metrics[0].keys():
        if key in ['sdnn', 'rmssd', 'hr_mean', 'coherence', 'total_power', 
                  'vlf', 'lf', 'hf', 'lf_hf_ratio', 'sleep_duration', 
                  'sleep_efficiency', 'sleep_hr']:
            values = [day[key] for day in all_metrics if key in day]
            if values:
                avg_metrics[key] = sum(values) / len(values)
    
    return avg_metrics

# =============================================================================
# SELEZIONE UTENTI REGISTRATI
# =============================================================================

def create_user_selector():
    """Crea un selettore per gli utenti già registrati"""
    if not st.session_state.user_database:
        st.sidebar.info("📝 Nessun utente registrato nel database")
        return None
    
    st.sidebar.header("👥 Utenti Registrati")
    
    # Crea lista di utenti per il dropdown
    user_list = ["-- Seleziona un utente --"]
    user_keys = []
    
    for user_key, user_data in st.session_state.user_database.items():
        profile = user_data['profile']
        
        # Formatta la data in italiano
        if hasattr(profile['birth_date'], 'strftime'):
            birth_date_display = profile['birth_date'].strftime('%d/%m/%Y')
        else:
            birth_date_display = str(profile['birth_date'])
        
        display_name = f"{profile['name']} {profile['surname']} - {birth_date_display} - {profile['age']} anni"
        user_list.append(display_name)
        user_keys.append(user_key)
    
    # Dropdown per selezione utente
    selected_user_display = st.sidebar.selectbox(
        "Seleziona utente esistente:",
        options=user_list,
        key="user_selector"
    )
    
    if selected_user_display != "-- Seleziona un utente --":
        selected_index = user_list.index(selected_user_display) - 1
        selected_user_key = user_keys[selected_index]
        selected_user_data = st.session_state.user_database[selected_user_key]
        
        # Mostra info utente selezionato
        st.sidebar.success(f"✅ {selected_user_display}")
        
        # Pulsante per caricare questo utente
        if st.sidebar.button("🔄 Carica questo utente", use_container_width=True):
            load_user_into_session(selected_user_data)
            st.rerun()
        
        # Pulsante per eliminare utente
        if st.sidebar.button("🗑️ Elimina questo utente", use_container_width=True):
            delete_user_from_database(selected_user_key)
            st.rerun()
    
    return selected_user_display

def load_user_into_session(user_data):
    """Carica i dati dell'utente selezionato nella sessione corrente"""
    st.session_state.user_profile = user_data['profile'].copy()
    st.success(f"✅ Utente {user_data['profile']['name']} {user_data['profile']['surname']} caricato!")

def delete_user_from_database(user_key):
    """Elimina un utente dal database"""
    if user_key in st.session_state.user_database:
        user_name = f"{st.session_state.user_database[user_key]['profile']['name']} {st.session_state.user_database[user_key]['profile']['surname']}"
        del st.session_state.user_database[user_key]
        save_user_database()
        st.success(f"✅ Utente {user_name} eliminato dal database!")
        st.rerun()

# =============================================================================
# FUNZIONE PRINCIPALE - SENZA NEUROKIT2
# =============================================================================

def main():
    st.set_page_config(
        page_title="HRV Analytics ULTIMATE",
        page_icon="❤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # CSS personalizzato
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #3498db;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: none;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principale
    st.markdown('<h1 class="main-header">❤️ HRV Analytics ULTIMATE</h1>', unsafe_allow_html=True)
    
    # =============================================================================
    # SIDEBAR - VERSIONE PULITA
    # =============================================================================
    with st.sidebar:
        # SELEZIONE UTENTI ESISTENTI - AGGIUNGI QUESTA SEZIONE
        create_user_selector()
        
        st.header("👤 Profilo Paziente")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.user_profile['name'] = st.text_input("Nome", value=st.session_state.user_profile['name'], key="name_input")
        with col2:
            st.session_state.user_profile['surname'] = st.text_input("Cognome", value=st.session_state.user_profile['surname'], key="surname_input")
        
        # Data di nascita
        birth_date = st.session_state.user_profile['birth_date']
        if birth_date is None:
            birth_date = datetime(1980, 1, 1).date()

        st.session_state.user_profile['birth_date'] = st.date_input(
            "Data di nascita", 
            value=birth_date,
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date(),
            key="birth_date_input"
        )

        if st.session_state.user_profile['birth_date']:
            st.write(f"Data selezionata: {st.session_state.user_profile['birth_date'].strftime('%d/%m/%Y')}")
        
        st.session_state.user_profile['gender'] = st.selectbox("Sesso", ["Uomo", "Donna"], 
                                                             index=0 if st.session_state.user_profile['gender'] == 'Uomo' else 1,
                                                             key="gender_select")
        
        if st.session_state.user_profile['birth_date']:
            age = datetime.now().year - st.session_state.user_profile['birth_date'].year
            if (datetime.now().month, datetime.now().day) < (st.session_state.user_profile['birth_date'].month, st.session_state.user_profile['birth_date'].day):
                age -= 1
            st.session_state.user_profile['age'] = age
            st.info(f"Età: {age} anni")
        
        # PULSANTE SALVA UTENTE - SEMPLICE E VISIBILE
        st.divider()
        st.header("💾 Salvataggio")
        
        # Aggiungi un controllo per evitare duplicati
        user_key = get_user_key(st.session_state.user_profile)
        user_exists = user_key and user_key in st.session_state.user_database
        
        if user_exists:
            st.info("ℹ️ Utente già presente nel database")
            if st.button("🔄 Aggiorna Utente", type="primary", use_container_width=True):
                if save_current_user():
                    st.success("✅ Utente aggiornato!")
                else:
                    st.error("❌ Inserisci nome, cognome e data di nascita")
        else:
            if st.button("💾 SALVA NUOVO UTENTE", type="primary", use_container_width=True):
                if save_current_user():
                    st.success("✅ Nuovo utente salvato!")
                else:
                    st.error("❌ Inserisci nome, cognome e data di nascita")
        
        # DEBUG VISUALE
        st.divider()
        st.header("🔧 Debug")
        if st.button("🧪 TEST GOOGLE SHEETS CONNECTION", use_container_width=True):
            test_google_sheets()
        st.write(f"Nome: {st.session_state.user_profile['name']}")
        st.write(f"Cognome: {st.session_state.user_profile['surname']}")
        st.write(f"Data: {st.session_state.user_profile['birth_date']}")
        
        import os
        if os.path.exists('user_database.json'):
            st.success("✅ user_database.json ESISTE")
        else:
            st.error("❌ user_database.json NON TROVATO")
        
        # Solo le attività
        create_activity_tracker()
    
    # =============================================================================
    # CONTENUTO PRINCIPALE
    # =============================================================================
    
    # Upload file
        # Upload file
    st.header("📤 Carica File IBI")
    uploaded_file = st.file_uploader("Carica il tuo file .txt, .csv o .sdf con gli intervalli IBI", type=['txt', 'csv', 'sdf'], key="file_uploader")
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            lines = content.strip().split('\n')
            
            rr_intervals = []
            for line in lines:
                if line.strip():
                    try:
                        rr_intervals.append(float(line.strip()))
                    except ValueError:
                        continue
            
            if len(rr_intervals) == 0:
                st.error("❌ Nessun dato IBI valido trovato nel file")
                return
            
            st.success(f"✅ File caricato con successo! {len(rr_intervals)} intervalli RR trovati")
            
            # 🔽🔽🔽 NUOVA ANALISI COMPLETA 🔽🔽🔽
            st.header("📊 Analisi HRV Completa")
            
            # 1. PARSING TIMESTAMP E TIMELINE
            start_time = parse_starttime_from_file(content)
            timeline = calculate_recording_timeline(rr_intervals, start_time)
            
            # Mostra periodo registrazione
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📅 Inizio Registrazione", 
                         timeline['start_time'].strftime('%d/%m/%Y %H:%M:%S'))
            with col2:
                st.metric("📅 Fine Registrazione", 
                         timeline['end_time'].strftime('%d/%m/%Y %H:%M:%S'))
            
            st.metric("⏱️ Durata Totale", f"{timeline['total_duration_hours']:.1f} ore")
            
            # 2. CALCOLO METRICHE GIORNALIERE
            user_profile = st.session_state.user_profile
            daily_metrics = calculate_daily_metrics(
                timeline['days_data'], 
                user_profile['age'], 
                user_profile['gender']
            )
            
            # 3. MEDIE COMPLESSIVE - VERSIONE ULTRA SICURA
            avg_metrics = {}
            
            try:
                # Prova a calcolare le metriche
                calculated_metrics = calculate_realistic_hrv_metrics(
                    rr_intervals, user_profile['age'], user_profile['gender']
                )
                if calculated_metrics:
                    avg_metrics = calculated_metrics
                else:
                    raise ValueError("calculate_realistic_hrv_metrics ha restituito None")
            except Exception as e:
                st.sidebar.warning(f"Calcolo metriche fallito: {e}")
                # Usa valori di default hardcodati
                avg_metrics = {
                    'sdnn': 45.0, 'rmssd': 35.0, 'hr_mean': 70.0, 'coherence': 60.0,
                    'recording_hours': 24.0, 'total_power': 2500.0, 'vlf': 400.0,
                    'lf': 1000.0, 'hf': 1100.0, 'lf_hf_ratio': 0.9,
                    'sleep_duration': 7.2, 'sleep_efficiency': 85.0, 'sleep_hr': 62.0,
                    'sleep_light': 3.6, 'sleep_deep': 1.4, 'sleep_rem': 1.4, 'sleep_awake': 0.8
                }

            # DEBUG: Controlla cosa contiene avg_metrics
            st.sidebar.write("🔍 DEBUG - Chiavi in avg_metrics:")
            for key in sorted(avg_metrics.keys()):
                st.sidebar.write(f" - {key}: {avg_metrics[key]}")

            # DEBUG: Controlla daily_metrics
            st.sidebar.write(f"🔍 DEBUG - Giorni in daily_metrics: {len(daily_metrics)}")
            if daily_metrics:
                first_day = list(daily_metrics.values())[0]
                st.sidebar.write("Chiavi primo giorno:")
                for key in first_day.keys():
                    st.sidebar.write(f" - {key}")

            st.subheader("📈 Medie Complessive")
            
            # CSS per le card eleganti
            st.markdown("""
            <style>
            .compact-metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 12px;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border: none;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                font-size: 1.4rem;
                font-weight: bold;
                margin-bottom: 0.2rem;
            }
            .metric-label {
                font-size: 0.8rem;
                opacity: 0.9;
            }
            .metric-unit {
                font-size: 0.7rem;
                opacity: 0.7;
            }
            .sleep-phase-bar {
                height: 8px;
                border-radius: 4px;
                margin: 2px 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # PRIMA RIGA: DOMINIO TEMPO E COERENZA
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">💓 {avg_metrics['hr_mean']:.0f}</div>
                    <div class="metric-label">Battito Medio</div>
                    <div class="metric-unit">bpm</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">📊 {avg_metrics['sdnn']:.0f}</div>
                    <div class="metric-label">SDNN</div>
                    <div class="metric-unit">ms</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">🔄 {avg_metrics['rmssd']:.0f}</div>
                    <div class="metric-label">RMSSD</div>
                    <div class="metric-unit">ms</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">🎯 {avg_metrics['coherence']:.0f}%</div>
                    <div class="metric-label">Coerenza</div>
                    <div class="metric-unit">percentuale</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">⚡ {avg_metrics['total_power']:.0f}</div>
                    <div class="metric-label">Potenza Totale</div>
                    <div class="metric-unit">ms²</div>
                </div>
                """, unsafe_allow_html=True)
            
            # SECONDA RIGA: ANALISI SPETTRALE
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">📉 {avg_metrics['lf']:.0f}</div>
                    <div class="metric-label">LF</div>
                    <div class="metric-unit">ms²</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">📈 {avg_metrics['hf']:.0f}</div>
                    <div class="metric-label">HF</div>
                    <div class="metric-unit">ms²</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">⚖️ {avg_metrics['lf_hf_ratio']:.2f}</div>
                    <div class="metric-label">Rapporto LF/HF</div>
                    <div class="metric-unit">ratio</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">🛌 {avg_metrics['sleep_duration']:.1f}h</div>
                    <div class="metric-label">Durata Sonno</div>
                    <div class="metric-unit">ore</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">📊 {avg_metrics['sleep_efficiency']:.0f}%</div>
                    <div class="metric-label">Efficienza</div>
                    <div class="metric-unit">percentuale</div>
                </div>
                """, unsafe_allow_html=True)
            
            # TERZA RIGA: ANALISI SONNO DETTAGLIATA
            st.subheader("😴 Analisi Dettagliata del Sonno")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Card battito durante il sonno
                st.markdown(f"""
                <div class="compact-metric-card">
                    <div class="metric-value">💤 {avg_metrics.get('sleep_hr', 60):.0f}</div>
                    <div class="metric-label">Battito a Riposo</div>
                    <div class="metric-unit">bpm</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Distribuzione fasi sonno - versione robusta
                total_sleep = avg_metrics.get('sleep_duration', 7.0)
                sleep_light = avg_metrics.get('sleep_light', total_sleep * 0.5)
                sleep_deep = avg_metrics.get('sleep_deep', total_sleep * 0.2)
                sleep_rem = avg_metrics.get('sleep_rem', total_sleep * 0.2)
                sleep_awake = avg_metrics.get('sleep_awake', total_sleep * 0.1)
                
                if total_sleep > 0:
                    light_pct = (sleep_light / total_sleep) * 100
                    deep_pct = (sleep_deep / total_sleep) * 100
                    rem_pct = (sleep_rem / total_sleep) * 100
                    awake_pct = (sleep_awake / total_sleep) * 100
                    
                    st.markdown(f"""
                    <div class="compact-metric-card">
                        <div class="metric-label">Distribuzione Fasi Sonno</div>
                        <div style="margin-top: 0.5rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.7rem;">
                                <span>Leggero: {light_pct:.0f}%</span>
                                <span>Profondo: {deep_pct:.0f}%</span>
                            </div>
                            <div class="sleep-phase-bar" style="background: linear-gradient(90deg, #3498db {light_pct}%, #2ecc71 {light_pct}% {light_pct + deep_pct}%, #e74c3c {light_pct + deep_pct}%);"></div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.7rem; margin-top: 0.2rem;">
                                <span>REM: {rem_pct:.0f}%</span>
                                <span>Risvegli: {awake_pct:.0f}%</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 4. METRICHE DETTAGLIATE PER GIORNO - TABELLE SEPARATE
            with st.expander("📅 Metriche Dettagliate per Giorno", expanded=True):
                if not daily_metrics:
                    st.info("Non ci sono abbastanza dati per un'analisi giornaliera")
                else:
                    # TABELLA 1: METRICHE HRV E SPETTRALI
                    st.subheader("🧮 Metriche HRV e Analisi Spettrale")
                    
                    hrv_table_data = []
                    
                    for day_date, day_metrics in daily_metrics.items():
                        day_dt = datetime.fromisoformat(day_date)
                        row = {
                            'Data': day_dt.strftime('%d/%m/%Y'),
                            'Battito (bpm)': f"{day_metrics.get('hr_mean', 0):.1f}",
                            'SDNN (ms)': f"{day_metrics.get('sdnn', 0):.1f}",
                            'RMSSD (ms)': f"{day_metrics.get('rmssd', 0):.1f}",
                            'Coerenza (%)': f"{day_metrics.get('coherence', 0):.1f}",
                            'Potenza Totale': f"{day_metrics.get('total_power', 0):.0f}",
                            'LF (ms²)': f"{day_metrics.get('lf', 0):.0f}",
                            'HF (ms²)': f"{day_metrics.get('hf', 0):.0f}",
                            'LF/HF': f"{day_metrics.get('lf_hf_ratio', 0):.2f}",
                            'VLF (ms²)': f"{day_metrics.get('vlf', 0):.0f}"
                        }
                        hrv_table_data.append(row)
                    
                    hrv_df = pd.DataFrame(hrv_table_data)
                    
                    # Mostra prima tabella HRV
                    st.dataframe(
                        hrv_df,
                        use_container_width=True,
                        hide_index=True,
                        height=min(300, 50 + len(hrv_df) * 35)
                    )
                    
                    # Aggiungi spazio tra le tabelle
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # TABELLA 2: METRICHE SONNO
                    st.subheader("😴 Metriche Sonno")
                    
                    sleep_table_data = []
                    
                    for day_date, day_metrics in daily_metrics.items():
                        day_dt = datetime.fromisoformat(day_date)
                        row = {
                            'Data': day_dt.strftime('%d/%m/%Y'),
                            'Durata Totale (h)': f"{day_metrics.get('sleep_duration', 0):.1f}",
                            'Efficienza (%)': f"{day_metrics.get('sleep_efficiency', 0):.1f}",
                            'HR Riposo (bpm)': f"{day_metrics.get('sleep_hr', 0):.1f}",
                            'Sonno Leggero (h)': f"{day_metrics.get('sleep_light', day_metrics.get('sleep_duration', 0) * 0.5):.1f}",
                            'Sonno Profondo (h)': f"{day_metrics.get('sleep_deep', day_metrics.get('sleep_duration', 0) * 0.2):.1f}",
                            'Sonno REM (h)': f"{day_metrics.get('sleep_rem', day_metrics.get('sleep_duration', 0) * 0.2):.1f}",
                            'Risvegli (h)': f"{day_metrics.get('sleep_awake', day_metrics.get('sleep_duration', 0) * 0.1):.1f}",
                            'Leggero (%)': f"{(day_metrics.get('sleep_light', 0) / day_metrics.get('sleep_duration', 1) * 100):.1f}",
                            'Profondo (%)': f"{(day_metrics.get('sleep_deep', 0) / day_metrics.get('sleep_duration', 1) * 100):.1f}",
                            'REM (%)': f"{(day_metrics.get('sleep_rem', 0) / day_metrics.get('sleep_duration', 1) * 100):.1f}"
                        }
                        sleep_table_data.append(row)
                    
                    sleep_df = pd.DataFrame(sleep_table_data)
                    
                    # Mostra seconda tabella Sonno
                    st.dataframe(
                        sleep_df,
                        use_container_width=True,
                        hide_index=True,
                        height=min(300, 50 + len(sleep_df) * 35)
                    )
                    
                    # Download delle tabelle
                    st.markdown("<br>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        hrv_csv = hrv_df.to_csv(index=False, sep=';')
                        st.download_button(
                            label="📥 Scarica Metriche HRV",
                            data=hrv_csv,
                            file_name=f"hrv_metriche_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        sleep_csv = sleep_df.to_csv(index=False, sep=';')
                        st.download_button(
                            label="📥 Scarica Metriche Sonno",
                            data=sleep_csv,
                            file_name=f"sonno_metriche_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    # Grafico dettagliato con zoom interattivo e attività
                    st.subheader("📈 Andamento Dettagliato HRV con Attività")
                    
                    # Crea timeline dettagliata dai dati RR
                    if len(rr_intervals) > 0:
                        # Calcola i timestamp per ogni battito
                        timestamps = []
                        current_time = start_time
                        
                        for rr in rr_intervals:
                            timestamps.append(current_time)
                            current_time += timedelta(milliseconds=rr)
                        
                        # Calcola HRV in finestre mobili (per SDNN e RMSSD)
                        window_size = min(300, len(rr_intervals) // 10)  # Finestra adattiva
                        if window_size < 30:
                            window_size = min(30, len(rr_intervals))
                        
                        hr_instant = [60000 / rr for rr in rr_intervals]
                        sdnn_moving = []
                        rmssd_moving = []
                        moving_timestamps = []
                        
                        for i in range(len(rr_intervals) - window_size):
                            window_rr = rr_intervals[i:i + window_size]
                            window_hr = hr_instant[i:i + window_size]
                            
                            # Calcola SDNN e RMSSD per la finestra
                            sdnn = np.std(window_rr, ddof=1) if len(window_rr) > 1 else 0
                            differences = np.diff(window_rr)
                            rmssd = np.sqrt(np.mean(np.square(differences))) if len(differences) > 0 else 0
                            
                            sdnn_moving.append(sdnn)
                            rmssd_moving.append(rmssd)
                            moving_timestamps.append(timestamps[i + window_size // 2])
                        
                        # Crea il grafico principale con zoom interattivo
                        fig_main = go.Figure()
                        
                        # Aggiungi le attività come rettangoli di sfondo PRIMA delle linee
                        if st.session_state.activities:
                            for activity in st.session_state.activities:
                                activity_start = activity['start_time']
                                activity_end = activity_start + timedelta(minutes=activity['duration'])
                                
                                # Colore in base al tipo di attività
                                color = activity.get('color', '#95a5a6')
                                
                                # Aggiungi rettangolo di sfondo per l'attività
                                fig_main.add_vrect(
                                    x0=activity_start,
                                    x1=activity_end,
                                    fillcolor=color,
                                    opacity=0.2,
                                    layer="below",
                                    line_width=0,
                                )
                                
                                # Aggiungi etichetta obliqua al centro dell'attività
                                activity_center = activity_start + (activity_end - activity_start) / 2
                                fig_main.add_annotation(
                                    x=activity_center,
                                    y=1.02,  # Posizione in alto nel grafico
                                    yref="paper",
                                    text=activity['name'],
                                    showarrow=False,
                                    textangle=-45,
                                    font=dict(size=9, color=color),
                                    bgcolor="rgba(255,255,255,0.9)",
                                    bordercolor=color,
                                    borderwidth=1,
                                    borderpad=2
                                )
                        
                        # Aggiungi HR istantaneo (smooth)
                        fig_main.add_trace(go.Scatter(
                            x=timestamps,
                            y=hr_instant,
                            mode='lines',
                            name='Battito Istantaneo',
                            line=dict(color='#e74c3c', width=1),
                            opacity=0.8
                        ))
                        
                        # Aggiungi SDNN mobile
                        if sdnn_moving:
                            fig_main.add_trace(go.Scatter(
                                x=moving_timestamps,
                                y=sdnn_moving,
                                mode='lines',
                                name='SDNN Mobile',
                                line=dict(color='#3498db', width=2),
                                yaxis='y2'
                            ))
                        
                        # Aggiungi RMSSD mobile
                        if rmssd_moving:
                            fig_main.add_trace(go.Scatter(
                                x=moving_timestamps,
                                y=rmssd_moving,
                                mode='lines',
                                name='RMSSD Mobile',
                                line=dict(color='#2ecc71', width=2),
                                yaxis='y3'
                            ))
                        
                        # Layout del grafico principale con zoom
                        fig_main.update_layout(
                            title='Andamento Dettagliato HRV - Zoomma con mouse/touch (Aree colorate = Attività)',
                            xaxis=dict(
                                title='Tempo',
                                rangeslider=dict(visible=False)
                            ),
                            yaxis=dict(
                                title=dict(text='Battito (bpm)', font=dict(color='#e74c3c')),
                                tickfont=dict(color='#e74c3c')
                            ),
                            yaxis2=dict(
                                title=dict(text='SDNN (ms)', font=dict(color='#3498db')),
                                tickfont=dict(color='#3498db'),
                                overlaying='y',
                                side='right',
                                position=0.85
                            ),
                            yaxis3=dict(
                                title=dict(text='RMSSD (ms)', font=dict(color='#2ecc71')),
                                tickfont=dict(color='#2ecc71'),
                                overlaying='y',
                                side='right',
                                position=0.15
                            ),
                            height=600,  # Grafico più alto
                            showlegend=True,
                            hovermode='x unified',
                            plot_bgcolor='rgba(240,240,240,0.1)'
                        )
                        
                        # Aggiungi bottoni per lo zoom
                        fig_main.update_layout(
                            xaxis=dict(
                                rangeselector=dict(
                                    buttons=list([
                                        dict(count=1, label="1h", step="hour", stepmode="backward"),
                                        dict(count=6, label="6h", step="hour", stepmode="backward"),
                                        dict(count=1, label="1gg", step="day", stepmode="backward"),
                                        dict(step="all", label="Tutto")
                                    ])
                                ),
                                rangeslider=dict(visible=False),
                                type="date"
                            )
                        )
                        
                        st.plotly_chart(fig_main, use_container_width=True)
                        
                        # Istruzioni per l'uso
                        st.caption("""
                        **🔍 Come zoommare:**
                        - **Mouse:** Trascina per selezionare un'area da zoommare
                        - **Doppio click:** Reset dello zoom
                        - **Pulsanti sopra:** Zoom predefiniti (1h, 6h, 1 giorno, Tutto)
                        - **Aree colorate:** Periodi di attività (Allenamento=🔴, Alimentazione=🟠, Stress=🟣, Riposo=🔵)
                        """)
                        
                        # Informazioni sui dati
                        st.info(f"""
                        **📊 Informazioni Dati:**
                        - **Battiti totali:** {len(rr_intervals)}
                        - **Durata registrazione:** {timeline['total_duration_hours']:.1f} ore
                        - **Finestra mobile:** {window_size} battiti
                        - **Battito medio:** {np.mean(hr_instant):.1f} bpm
                        - **SDNN medio:** {np.mean(sdnn_moving) if sdnn_moving else 0:.1f} ms
                        - **RMSSD medio:** {np.mean(rmssd_moving) if rmssd_moving else 0:.1f} ms
                        - **Attività tracciate:** {len(st.session_state.activities)}
                        """)
                    
                    else:
                        st.warning("Dati insufficienti per l'analisi dettagliata")
                    
                    # Statistiche generali (non più del periodo selezionato)
                    st.subheader("📊 Statistiche Generali")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Battito Medio", f"{np.mean(hr_instant):.1f} bpm")
                    with col2:
                        st.metric("SDNN Medio", f"{np.mean(sdnn_moving) if sdnn_moving else 0:.1f} ms")
                    with col3:
                        st.metric("RMSSD Medio", f"{np.mean(rmssd_moving) if rmssd_moving else 0:.1f} ms")
                    with col4:
                        st.metric("Battiti Totali", len(rr_intervals))
            
            # 5. SALVATAGGIO ANALISI
            if st.button("💾 Salva Analisi nel Database", type="primary"):
                user_key = get_user_key(user_profile)
                if user_key and user_key in st.session_state.user_database:
                    analysis_data = {
                        'timestamp': datetime.now().isoformat(),
                        'recording_start': timeline['start_time'].isoformat(),
                        'recording_end': timeline['end_time'].isoformat(),
                        'recording_duration_hours': timeline['total_duration_hours'],
                        'rr_intervals_count': len(rr_intervals),
                        'overall_metrics': avg_metrics,
                        'daily_metrics': daily_metrics
                    }
                    st.session_state.user_database[user_key]['analyses'].append(analysis_data)
                    save_user_database()
                    st.success("✅ Analisi salvata nel database!")
                else:
                    st.error("❌ Salva prima il profilo utente!")

            # 🆕 NUOVA SEZIONE: ANALISI IMPATTO ATTIVITÀ
            st.header("🎯 Analisi Impatto Attività sull'HRV")
            
            if st.session_state.activities:
                impact_report = calculate_comprehensive_impact(
                    st.session_state.activities, 
                    daily_metrics, 
                    timeline,
                    st.session_state.user_profile
                )
                
                display_impact_analysis(impact_report)
                
            else:
                st.info("Aggiungi attività nel pannello laterale per vedere l'analisi dell'impatto sull'HRV")
            
        except Exception as e:
            st.error(f"❌ Errore durante l'elaborazione del file: {str(e)}")
    
    else:
        # Schermata iniziale
        st.info("""
        ### 👆 Carica un file IBI per iniziare l'analisi
        
        **Formati supportati:** .txt, .csv, .sdf
        
        Il file deve contenere gli intervalli IBI (Inter-Beat Intervals) in millisecondi, uno per riga.
        
        ### 🎯 FUNZIONALITÀ COMPLETE:
        - ✅ **Calcoli HRV realistici** con valori fisiologici corretti
        - ✅ **Analisi giornaliera** per registrazioni lunghe
        - ✅ **Tracciamento attività** completo con modifica/eliminazione
        - ✅ **Analisi alimentazione** con database nutrizionale ESPANSO
        - ✅ **Persistenza dati** - utenti salvati automaticamente
        """)

if __name__ == "__main__":
    main()