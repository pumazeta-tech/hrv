def analyze_recovery_impact(activity, daily_metrics):
    """Analisi impatto attività rigenerative"""
    
    activity_name = activity['name'].lower()
    impact_data = ACTIVITY_IMPACT_DB.get(activity_name, {})
    
    return {
        'activity': activity,
        'expected_impact': impact_data.get('hrv_impact_24h', 2),
        'observed_impact': 2,
        'type': 'recovery',
        'recommendations': ["Ottima scelta per il recupero!"]
    }

def analyze_stress_impact(activity, daily_metrics):
    """Analisi impatto attività stressanti"""
    return {
        'activity': activity,
        'expected_impact': -2,
        'observed_impact': -1,
        'type': 'stress',
        'recovery_status': 'poor',
        'recommendations': ["🧘 Considera tecniche di respirazione per gestire lo stress"]
    }

def analyze_other_impact(activity, daily_metrics):
    """Analisi impatto altre attività"""
    return {
        'activity': activity,
        'expected_impact': 0,
        'observed_impact': 0,
        'type': 'other',
        'recovery_status': 'unknown',
        'recommendations': ["📝 Attività registrata"]
    }

def calculate_observed_hrv_impact(activity, day_metrics, timeline):
    """Calcola l'impatto osservato sull'HRV basato sui dati reali"""
    if not day_metrics:
        return 0
    
    rmssd = day_metrics.get('rmssd', 0)
    sdnn = day_metrics.get('sdnn', 0)
    
    if rmssd > 40 and sdnn > 50:
        return 2
    elif rmssd > 25 and sdnn > 35:
        return 1
    else:
        return 0

def assess_recovery_status(activity, day_metrics):
    """Valuta lo stato di recupero"""
    if not day_metrics:
        return "unknown"
    
    rmssd = day_metrics.get('rmssd', 0)
    
    if rmssd > 50:
        return "optimal"
    elif rmssd > 30:
        return "good" 
    elif rmssd > 20:
        return "moderate"
    else:
        return "poor"

def generate_training_recommendations(activity, observed_impact, expected_impact):
    """Genera raccomandazioni per l'allenamento"""
    recommendations = []
    
    activity_name = activity['name'].lower()
    intensity = activity['intensity']
    
    if observed_impact < expected_impact - 1:
        recommendations.append("💡 Considera ridurre l'intensità o aumentare il recupero")
    elif observed_impact > expected_impact + 1:
        recommendations.append("💡 Ottimo! Il tuo corpo risponde bene a questo allenamento")
    
    if "intensa" in intensity.lower() and observed_impact < 0:
        recommendations.append("💡 Allenamenti intensi richiedono almeno 48h di recupero")
    
    if not recommendations:
        recommendations.append("💡 Continua così! Mantieni questo tipo di allenamento")
    
    return recommendations

def generate_nutrition_recommendations(activity, inflammatory_score):
    """Genera raccomandazioni nutrizionali"""
    recommendations = []
    
    if inflammatory_score > 3:
        recommendations.append("🍎 Prova a bilanciare con cibi anti-infiammatori (verdure, pesce)")
    elif inflammatory_score < -2:
        recommendations.append("🍎 Ottima scelta di cibi anti-infiammatori!")
    
    meal_time = activity['start_time'].hour
    if meal_time > 21:
        recommendations.append("⏰ Cena un po' tardiva, prova a mangiare prima delle 21")
    
    return recommendations

def analyze_nutritional_impact(activities):
    """Analisi impatto nutrizionale complessivo"""
    inflammatory_score = 0
    recovery_score = 0
    meal_count = 0
    
    for activity in activities:
        if activity['type'] == "Alimentazione":
            meal_count += 1
            food_items = activity.get('food_items', '')
            for food in food_items.split(','):
                food = food.strip().lower()
                food_data = NUTRITION_DB.get(food, {})
                inflammatory_score += food_data.get('inflammatory_score', 0)
                recovery_score += food_data.get('recovery_impact', 0)
    
    return {
        'inflammatory_score': inflammatory_score,
        'recovery_score': recovery_score,
        'meal_count': meal_count,
        'total_calories': meal_count * 500
    }

def analyze_supplements_impact(activities):
    """Analisi impatto integratori"""
    supplements_taken = []
    total_hrv_impact = 0
    
    for activity in activities:
        if activity['type'] == "Integrazione" and activity.get('food_items'):
            supplements = [s.strip().lower() for s in activity['food_items'].split(',')]
            for supplement in supplements:
                supp_data = SUPPLEMENTS_DB.get(supplement)
                if supp_data:
                    total_hrv_impact += supp_data['hrv_impact']
                    supplements_taken.append({
                        'name': supplement,
                        'data': supp_data,
                        'timing': activity['start_time']
                    })
    
    return {
        'total_hrv_impact': total_hrv_impact,
        'sleep_impact': total_hrv_impact * 0.5,
        'stress_impact': -total_hrv_impact * 0.7,
        'supplements_taken': supplements_taken
    }

def generate_comprehensive_recommendations(activities, daily_metrics, user_profile):
    """Genera raccomandazioni complete basate su tutti i dati"""

    recommendations = []
    
    all_food_items = ""
    for activity in activities:
        if activity['type'] == "Alimentazione" and activity.get('food_items'):
            all_food_items += activity['food_items'] + ","
    
    if all_food_items:
        food_analysis = analyze_food_impact(all_food_items)
        recommendations.extend(food_analysis['recommendations'])
    
    training_count = len([a for a in activities if a['type'] == 'Allenamento'])
    recovery_count = len([a for a in activities if a['type'] == 'Riposo'])
    
    if training_count > 3 and recovery_count < 2:
        recommendations.append("⚖️ Bilanciare più attività di recupero con gli allenamenti")
    
    if daily_metrics:
        avg_rmssd = sum(day.get('rmssd', 0) for day in daily_metrics.values()) / len(daily_metrics)
        if avg_rmssd < 25:
            recommendations.append("😴 Prioritizza il sonno e riduci lo stress per migliorare l'HRV")
    
    if not recommendations:
        recommendations.append("🎉 Ottimo stile di vita! Continua così mantenendo l'equilibrio")
    
    return recommendations

def analyze_food_impact(food_items):
    """Analizza l'impatto di specifici cibi sull'HRV"""
    analysis = {
        'inflammatory_foods': [],
        'recovery_foods': [],
        'inflammatory_score': 0,
        'sleep_impact': 0,
        'recommendations': []
    }
    
    foods = [food.strip().lower() for food in food_items.split(',')]
    
    for food in foods:
        food_data = NUTRITION_DB.get(food, {})
        inflammatory_score = food_data.get('inflammatory_score', 0)
        
        if inflammatory_score > 2:
            analysis['inflammatory_foods'].append(food)
            analysis['inflammatory_score'] += inflammatory_score
        elif inflammatory_score < -2:
            analysis['recovery_foods'].append(food)
        
        sleep_impact = food_data.get('sleep_impact', 'neutro')
        if sleep_impact == "molto negativo":
            analysis['sleep_impact'] -= 2
        elif sleep_impact == "negativo":
            analysis['sleep_impact'] -= 1
        elif sleep_impact == "positivo":
            analysis['sleep_impact'] += 1
        elif sleep_impact == "molto positivo":
            analysis['sleep_impact'] += 2
    
    if analysis['inflammatory_score'] > 5:
        analysis['recommendations'].append("🚨 Alto carico infiammatorio: riduci carboidrati raffinati e alcol")
    
    if "pasta" in foods and "pane" in foods and "patate" in foods:
        analysis['recommendations'].append("🥗 Troppi carboidrati: bilancia con proteine e verdure")
    
    if "vino" in foods or "alcolici" in foods:
        analysis['recommendations'].append("🍷 L'alcol riduce la qualità del sonno e l'HRV")
    
    if not analysis['recommendations']:
        analysis['recommendations'].append("🥦 Buona scelta alimentare!")
    
    return analysis

def display_impact_analysis(impact_report):
    """Visualizza i risultati dell'analisi di impatto"""
    
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
    
    if impact_report['activity_analysis']:
        with st.expander("🧘 Analisi Dettagliata Attività", expanded=True):
            for activity_analysis in impact_report['activity_analysis']:
                display_activity_analysis(activity_analysis)
    else:
        st.info("Nessuna attività da analizzare")
    
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
        st.write(f"*{activity['type']}*")
    
    with col2:
        impact_diff = analysis.get('impact_difference', 0)
        color = "green" if impact_diff >= 0 else "red"
        st.write(f"Impatto: :{color}[{impact_diff:+.1f}]")
    
    with col3:
        recovery_status = analysis.get('recovery_status', 'unknown')
        status_colors = {
            'optimal': 'green', 'good': 'blue', 
            'moderate': 'orange', 'poor': 'red', 'unknown': 'gray'
        }
        st.write(f"Recupero: :{status_colors.get(recovery_status, 'gray')}[{recovery_status}]")
    
    with col4:
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            for rec in recommendations[:1]:
                st.write(f"💡 {rec}")
        else:
            st.write("📝 Nessuna raccomandazione")

# Colori per i tipi di attività
ACTIVITY_COLORS = {
    "Allenamento": "#e74c3c",
    "Alimentazione": "#f39c12", 
    "Stress": "#9b59b6",
    "Riposo": "#3498db",
    "Sonno": "#2c3e50",
    "Altro": "#95a5a6"
}

def create_activity_tracker():
    """Interfaccia per tracciare attività e alimentazione"""
    st.sidebar.header("🏃‍♂️ Tracker Attività & Alimentazione")
    
    if st.session_state.get('editing_activity_index') is not None:
        edit_activity_interface()
        return
    
    with st.sidebar.expander("➕ Aggiungi Attività/Pasto", expanded=False):
        activity_type = st.selectbox("Tipo Attività", 
                                   ["Allenamento", "Alimentazione", "Stress", "Riposo", "Sonno", "Altro"])
        
        activity_name = st.text_input("Nome Attività/Pasto", placeholder="Es: Corsa mattutina, Pranzo, etc.")
        
        if activity_type == "Alimentazione":
            food_items = st.text_area("Cosa hai mangiato? (separato da virgola)", placeholder="Es: pasta, insalata, frutta")
            intensity = st.select_slider("Pesantezza pasto", 
                                       options=["Leggero", "Normale", "Pesante", "Molto pesante"])
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Data", value=datetime.now().date(), key="activity_date")
                start_time = st.time_input("Ora inizio", value=datetime.now().time(), key="activity_time")
                st.write(f"Data selezionata: {start_date.strftime('%d/%m/%Y')}")
            with col2:
                duration = st.number_input("Durata (min)", min_value=1, max_value=480, value=30, key="activity_duration")
                
        elif activity_type == "Sonno":
            st.info("💤 Registra il tuo periodo di sonno")
            
            col1, col2 = st.columns(2)
            with col1:
                sleep_start_date = st.date_input("Data inizio sonno", value=datetime.now().date(), key="sleep_start_date")
            with col2:
                sleep_start_time = st.time_input("Ora inizio sonno", value=datetime(2020,1,1,23,0).time(), key="sleep_start_time")
            
            col1, col2 = st.columns(2)
            with col1:
                sleep_end_date = st.date_input("Data fine sonno", value=datetime.now().date(), key="sleep_end_date")
            with col2:
                sleep_end_time = st.time_input("Ora fine sonno", value=datetime(2020,1,1,7,0).time(), key="sleep_end_time")
            
            sleep_start_datetime = datetime.combine(sleep_start_date, sleep_start_time)
            sleep_end_datetime = datetime.combine(sleep_end_date, sleep_end_time)
            
            if sleep_end_datetime < sleep_start_datetime:
                sleep_end_datetime += timedelta(days=1)
            
            duration_minutes = int((sleep_end_datetime - sleep_start_datetime).total_seconds() / 60)
            
            st.write(f"**Durata sonno:** {duration_minutes // 60}h {duration_minutes % 60}min")
            duration = duration_minutes
            food_items = ""
            intensity = "Normale"
            activity_name = f"Sonno {sleep_start_datetime.strftime('%d/%m/%Y %H:%M')}-{sleep_end_datetime.strftime('%d/%m/%Y %H:%M')}"
            
            st.write(f"**Inizio:** {sleep_start_datetime.strftime('%d/%m/%Y %H:%M')}")
            st.write(f"**Fine:** {sleep_end_datetime.strftime('%d/%m/%Y %H:%M')}")
            
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
            if activity_type == "Sonno":
                # Per Sonno, usa sleep_start_datetime e estrai date/time
                start_date = sleep_start_date
                start_time = sleep_start_time
            else:
                # Per altri tipi, usa i valori normali
                start_date = start_date
                start_time = start_time
                
            save_activity(activity_type, activity_name, intensity, food_items, start_date, start_time, duration, notes)
            st.success("Attività salvata!")
            st.rerun()
    
    if st.session_state.activities:
        st.sidebar.subheader("📋 Gestione Attività")
        
        for i, activity in enumerate(st.session_state.activities[-10:]):
            if activity['type'] == 'Sonno':
                # Per il sonno, mostra solo il nome (che già contiene le dates)
                display_text = f"{activity['name']}"
            else:
                # Per altre attività, mostra nome + data/ora
                display_text = f"{activity['name']} - {activity['start_time'].strftime('%d/%m/%Y %H:%M')}"
            
            with st.sidebar.expander(display_text, False):
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
                                   ["Allenamento", "Alimentazione", "Stress", "Riposo", "Sonno", "Altro"],
                                   index=["Allenamento", "Alimentazione", "Stress", "Riposo", "Sonno", "Altro"].index(activity['type']),
                                   key="edit_type")
        
        activity_name = st.text_input("Nome Attività/Pasto", value=activity['name'], key="edit_name")
        
        if activity_type == "Alimentazione":
            food_items = st.text_area("Cosa hai mangiato?", value=activity.get('food_items', ''), key="edit_food")
            intensity = st.select_slider("Pesantezza pasto", 
                                       options=["Leggero", "Normale", "Pesante", "Molto pesante"],
                                       value=activity['intensity'], key="edit_intensity_food")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Data", value=activity['start_time'].date(), key="edit_date")
                start_time = st.time_input("Ora inizio", value=activity['start_time'].time(), key="edit_time")
                st.write(f"Data selezionata: {start_date.strftime('%d/%m/%Y')}")
            with col2:
                duration = st.number_input("Durata (min)", min_value=1, max_value=480, value=activity['duration'], key="edit_duration")
                
        elif activity_type == "Sonno":
            st.info("💤 Modifica periodo di sonno")
            
            existing_start = activity['start_time']
            
            col1, col2 = st.columns(2)
            with col1:
                sleep_start_date = st.date_input("Data inizio sonno", value=existing_start.date(), key="edit_sleep_start_date")
            with col2:
                sleep_start_time = st.time_input("Ora inizio sonno", value=existing_start.time(), key="edit_sleep_start_time")
            
            existing_end = existing_start + timedelta(minutes=activity['duration'])
            
            col1, col2 = st.columns(2)
            with col1:
                sleep_end_date = st.date_input("Data fine sonno", value=existing_end.date(), key="edit_sleep_end_date")
            with col2:
                sleep_end_time = st.time_input("Ora fine sonno", value=existing_end.time(), key="edit_sleep_end_time")
            
            sleep_start_datetime = datetime.combine(sleep_start_date, sleep_start_time)
            sleep_end_datetime = datetime.combine(sleep_end_date, sleep_end_time)
            
            if sleep_end_datetime < sleep_start_datetime:
                sleep_end_datetime += timedelta(days=1)
            
            duration_minutes = int((sleep_end_datetime - sleep_start_datetime).total_seconds() / 60)
            
            st.write(f"**Durata sonno:** {duration_minutes // 60}h {duration_minutes % 60}min")
            duration = duration_minutes
            food_items = ""
            intensity = "Normale"
            activity_name = f"Sonno {sleep_start_datetime.strftime('%d/%m/%Y %H:%M')}-{sleep_end_datetime.strftime('%d/%m/%Y %H:%M')}"
            
            st.write(f"**Inizio:** {sleep_start_datetime.strftime('%d/%m/%Y %H:%M')}")
            st.write(f"**Fine:** {sleep_end_datetime.strftime('%d/%m/%Y %H:%M')}")
            
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
                if activity_type == "Sonno":
                    # Per Sonno, usa sleep_start_datetime e estrai date/time
                    start_date = sleep_start_date
                    start_time = sleep_start_time
                else:
                    # Per altri tipi, usa i valori normali
                    start_date = start_date
                    start_time = start_time
                    
                update_activity(activity_index, activity_type, activity_name, intensity, food_items, start_date, start_time, duration, notes)
                st.session_state.editing_activity_index = None
                st.rerun()

def save_activity(activity_type, name, intensity, food_items, start_date, start_time, duration, notes):
    """Salva una nuova attività"""
    # Combina data e ora
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
                time_str = line.split('=')[1].strip()
                
                formats_to_try = [
                    '%d.%m.%Y %H:%M.%S',
                    '%d.%m.%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
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
    """Calcola la timeline della registrazione - VERSIONE CORRETTA"""
    total_duration_ms = sum(rr_intervals)
    end_time = start_time + timedelta(milliseconds=total_duration_ms)
    
    days_data = {}
    current_time = start_time
    current_day_start = start_time.date()
    day_rr_intervals = []
    
    for rr in rr_intervals:
        day_rr_intervals.append(rr)
        current_time += timedelta(milliseconds=rr)
        
        # Se cambia giorno, salva i dati del giorno precedente
        if current_time.date() != current_day_start:
            if day_rr_intervals:
                days_data[current_day_start.isoformat()] = day_rr_intervals.copy()
            day_rr_intervals = []
            current_day_start = current_time.date()
    
    # Aggiungi l'ultimo giorno
    if day_rr_intervals:
        days_data[current_day_start.isoformat()] = day_rr_intervals
    
    print(f"📅 Timeline creata:")
    print(f"   Start: {start_time}")
    print(f"   End: {end_time}") 
    print(f"   Durata: {total_duration_ms / (1000 * 60 * 60):.1f} ore")
    print(f"   Giorni: {list(days_data.keys())}")
    print(f"   IBI per giorno: { {k: len(v) for k, v in days_data.items()} }")
    
    return {
        'start_time': start_time,
        'end_time': end_time,
        'total_duration_hours': total_duration_ms / (1000 * 60 * 60),
        'days_data': days_data  # QUESTA È LA CHIAVE CHE MANCAVA!
    }

def calculate_daily_metrics(days_data, user_age, user_gender):
    """Calcola le metriche HRV per ogni giorno - CON SUPPORO PER METRICHE SONNO"""
    daily_metrics = {}
    
    for day_date, day_rr_intervals in days_data.items():
        if len(day_rr_intervals) >= 10:
            # Crea datetime di inizio e fine per ogni giorno
            day_start = datetime.fromisoformat(day_date)
            day_end = day_start + timedelta(hours=24)
            
            # Calcola metriche HRV base
            day_metrics = calculate_realistic_hrv_metrics(
                day_rr_intervals, user_age, user_gender, day_start, day_end
            )
            
            # AGGIUNGI METRICHE SONNO SE CI SONO ATTIVITÀ SONNO PER QUEL GIORNO
            sleep_metrics_for_day = get_sleep_metrics_for_day(day_date, st.session_state.activities, day_metrics)
            if sleep_metrics_for_day:
                day_metrics.update(sleep_metrics_for_day)
            
            daily_metrics[day_date] = day_metrics
    
    return daily_metrics

def get_sleep_metrics_for_day(day_date, activities, day_metrics):
    """Restituisce le metriche sonno REALI per un giorno specifico basate sugli IBI"""
    
    print(f"🔍 DEBUG get_sleep_metrics_for_day:")
    print(f"   Giorno: {day_date}")
    print(f"   Attività totali: {len(activities)}")
    
    sleep_activities_for_day = []
    
    for activity in activities:
        if activity['type'] == 'Sonno':
            activity_date = activity['start_time'].date().isoformat()
            print(f"   Attività sonno: {activity['name']} - {activity_date}")
            # Se l'attività sonno è per questo giorno
            if activity_date == day_date:
                sleep_activities_for_day.append(activity)
                print(f"   ✅ Sonno corrisponde al giorno!")
    
    print(f"   Attività sonno per questo giorno: {len(sleep_activities_for_day)}")
    
    if not sleep_activities_for_day:
        print(f"   ❌ Nessuna attività sonno per questo giorno")
        return {}  # Nessuna attività sonno per questo giorno
    
    # Prendi l'ultima attività sonno del giorno
    latest_sleep = sleep_activities_for_day[-1]
    
    # Per l'analisi giornaliera, usa un fallback poiché non abbiamo il timeline completo
    sleep_analysis = analyze_sleep_impact_advanced(latest_sleep, {}, {})  
    
    print(f"   Risultato analisi: {sleep_analysis.get('sleep_metrics', 'NONE')}")
    
    return sleep_analysis.get('sleep_metrics', {})

def get_sleep_metrics_from_activities(activities, daily_metrics, timeline):
    """Raccoglie le metriche del sonno REALI dalle attività di sonno registrate"""
    
    print(f"🎯 DEBUG get_sleep_metrics_from_activities:")
    print(f"   Numero totale attività: {len(activities)}")
    
    sleep_activities = [a for a in activities if a['type'] == 'Sonno']
    print(f"   Attività sonno trovate: {len(sleep_activities)}")
    
    # DEBUG: mostra TUTTE le attività per vedere cosa c'è
    for i, activity in enumerate(activities):
        print(f"   Attività {i}: {activity['type']} - {activity['name']} - {activity['start_time']}")
    
    if not sleep_activities:
        print(f"   ❌ Nessuna attività 'Sonno' trovata!")
        return {}
    
    # Prendi l'ultima attività sonno
    latest_sleep = sleep_activities[-1]
    print(f"   🔍 Analizzando sonno: {latest_sleep['name']}")
    print(f"      Orario: {latest_sleep['start_time']} -> {latest_sleep['start_time'] + timedelta(minutes=latest_sleep['duration'])}")
    
    # USA LA NUOVA ANALISI AVANZATA
    sleep_analysis = analyze_sleep_impact_advanced(latest_sleep, daily_metrics, timeline)
    
    print(f"   📊 Risultato analisi sonno:")
    print(f"      Ha sleep_metrics: {'sleep_metrics' in sleep_analysis}")
    if 'sleep_metrics' in sleep_analysis and sleep_analysis['sleep_metrics']:
        print(f"      Metriche: {sleep_analysis['sleep_metrics']}")
    else:
        print(f"      ❌ sleep_metrics è None o vuoto!")
    
    return sleep_analysis.get('sleep_metrics', {})

def calculate_overall_averages(daily_metrics):
    """Calcola le medie complessive da tutti i giorni"""
    if not daily_metrics:
        return None
    
    avg_metrics = {}
    all_metrics = list(daily_metrics.values())
    
    for key in all_metrics[0].keys():
        if key in ['sdnn', 'rmssd', 'hr_mean', 'coherence', 'total_power', 
                  'vlf', 'lf', 'hf', 'lf_hf_ratio', 'sleep_duration', 
                  'sleep_efficiency', 'sleep_hr']:
            values = [day[key] for day in all_metrics if key in day]
            if values:
                avg_metrics[key] = sum(values) / len(values)
    
    return avg_metrics

# =============================================================================
# SELEZIONE UTENTI REGISTRATI - FUNZIONE CORRETTA
# =============================================================================

def create_user_selector():
    """Crea un selettore per gli utenti già registrati"""
    if not st.session_state.user_database:
        st.sidebar.info("📝 Nessun utente registrato nel database")
        return None
    
    st.sidebar.header("👥 Utenti Registrati")
    
    user_list = ["-- Seleziona un utente --"]
    user_keys = []
    
    for user_key, user_data in st.session_state.user_database.items():
        profile = user_data['profile']
        
        if hasattr(profile['birth_date'], 'strftime'):
            birth_date_display = profile['birth_date'].strftime('%d/%m/%Y')
        else:
            birth_date_display = str(profile['birth_date'])
        
        display_name = f"{profile['name']} {profile['surname']} - {birth_date_display} - {profile['age']} anni"
        user_list.append(display_name)
        user_keys.append(user_key)
    
    selected_user_display = st.sidebar.selectbox(
        "Seleziona utente esistente:",
        options=user_list,
        key="user_selector"
    )
    
    if selected_user_display != "-- Seleziona un utente --":
        selected_index = user_list.index(selected_user_display) - 1
        selected_user_key = user_keys[selected_index]
        selected_user_data = st.session_state.user_database[selected_user_key]
        
        st.sidebar.success(f"✅ {selected_user_display}")
        
        # CORREZIONE: Salva la user_key nella sessione quando carichi l'utente
        if st.sidebar.button("🔄 Carica questo utente", use_container_width=True):
            load_user_into_session(selected_user_data, selected_user_key)  # Passa anche la key
            st.rerun()
        
        if st.sidebar.button("🗑️ Elimina questo utente", use_container_width=True):
            delete_user_from_database(selected_user_key)
            st.rerun()
    
    return selected_user_display

def load_user_into_session(user_data, user_key=None):
    """Carica i dati dell'utente selezionato nella sessione corrente"""
    st.session_state.user_profile = user_data['profile'].copy()
    
    # CORREZIONE: Salva la user_key nella sessione per usi futuri
    if user_key:
        st.session_state.current_user_key = user_key
    
    st.success(f"✅ Utente {user_data['profile']['name']} {user_data['profile']['surname']} caricato!")

def delete_user_from_database(user_key):
    """Elimina un utente dal database"""
    if user_key in st.session_state.user_database:
        del st.session_state.user_database[user_key]
        save_user_database()
        st.success("Utente eliminato dal database!")

# =============================================================================
# FUNZIONI PER GESTIONE STORICO ANALISI
# =============================================================================

def save_analysis_to_history(analysis_data):
    """Salva l'analisi corrente nello storico - VERSIONE CORRETTA"""
    # CORREZIONE: Usa multiple strategie per trovare la user_key
    user_key = None
    
    # Strategia 1: Usa la key salvata quando si carica un utente
    if hasattr(st.session_state, 'current_user_key') and st.session_state.current_user_key:
        user_key = st.session_state.current_user_key
    
    # Strategia 2: Genera la key dal profilo corrente
    if not user_key:
        user_key = get_user_key(st.session_state.user_profile)
    
    # Strategia 3: Cerca nel database per match
    if not user_key and st.session_state.user_database:
        for key, user_data in st.session_state.user_database.items():
            if (user_data['profile']['name'] == st.session_state.user_profile['name'] and 
                user_data['profile']['surname'] == st.session_state.user_profile['surname'] and
                user_data['profile']['birth_date'] == st.session_state.user_profile['birth_date']):
                user_key = key
                st.session_state.current_user_key = key  # Salva per usi futuri
                break
    
    if user_key and user_key in st.session_state.user_database:
        analysis_data['analysis_id'] = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        analysis_data['saved_at'] = datetime.now().isoformat()
        
        # CORREZIONE: Assicurati che 'analyses' esista
        if 'analyses' not in st.session_state.user_database[user_key]:
            st.session_state.user_database[user_key]['analyses'] = []
        
        st.session_state.user_database[user_key]['analyses'].append(analysis_data)
        success = save_user_database()
        
        if success:
            st.sidebar.success(f"✅ Analisi salvata per {st.session_state.user_profile['name']} {st.session_state.user_profile['surname']}")
            return True
        else:
            st.error("❌ Errore nel salvataggio sul database")
            return False
    else:
        st.error("❌ Utente non trovato nel database. Salva prima il profilo utente!")
        return False

def get_analysis_history():
    """Recupera lo storico delle analisi per l'utente corrente"""
    user_key = get_user_key(st.session_state.user_profile)
    if user_key and user_key in st.session_state.user_database:
        return st.session_state.user_database[user_key].get('analyses', [])
    return []

def display_analysis_history():
    """Mostra lo storico delle analisi nell'interfaccia principale"""
    analyses = get_analysis_history()
    
    if not analyses:
        st.info("📝 Nessuna analisi precedente trovata. Carica un file IBI per creare la prima analisi.")
        return
    
    st.header("📊 Storico Analisi HRV")
    
    table_data = []
    
    for analysis in analyses:
        overall_metrics = analysis.get('overall_metrics', {})
        daily_metrics = analysis.get('daily_metrics', {})
        data_inserimento = datetime.fromisoformat(analysis.get('saved_at', datetime.now().isoformat())).strftime('%d/%m/%Y %H:%M')
        
        # DEBUG: Verifica i dati
        print(f"DEBUG display_analysis_history - Analysis: {analysis.get('recording_start')}")
        print(f"  Has daily_metrics: {bool(daily_metrics)}")
        print(f"  Has overall_metrics: {bool(overall_metrics)}")
        
        # PRIMA processa i daily_metrics (se esistono)
        if daily_metrics:
            for day_date, day_metrics in daily_metrics.items():
                day_dt = datetime.fromisoformat(day_date)
                
                # CORREZIONE: PULIZIA ESPLICITA - rimuovi metriche sonno se non valide
                cleaned_metrics = day_metrics.copy()
                if not has_valid_sleep_metrics(cleaned_metrics):
                    # Rimuovi esplicitamente tutte le metriche del sonno
                    sleep_keys = ['sleep_duration', 'sleep_efficiency', 'sleep_hr', 
                                'sleep_light', 'sleep_deep', 'sleep_rem', 'sleep_awake']
                    for key in sleep_keys:
                        cleaned_metrics.pop(key, None)
                
                # CORREZIONE: Controlla se ci sono metriche del sonno VALIDE (non zero)
                has_sleep_metrics = has_valid_sleep_metrics(cleaned_metrics)
                
                print(f"  Day {day_date}: has_sleep_metrics = {has_sleep_metrics}")
                if has_sleep_metrics:
                    print(f"    Sleep data: { {k: v for k, v in cleaned_metrics.items() if 'sleep' in k} }")
                
                row = {
                    'Data Inserimento': data_inserimento,
                    'Data Registrazione': day_dt.strftime('%d/%m/%Y'),
                    'Battito (bpm)': f"{cleaned_metrics.get('hr_mean', 0):.1f}",
                    'SDNN (ms)': f"{cleaned_metrics.get('sdnn', 0):.1f}",
                    'RMSSD (ms)': f"{cleaned_metrics.get('rmssd', 0):.1f}",
                    'Coerenza (%)': f"{cleaned_metrics.get('coherence', 0):.1f}",
                    'Potenza Totale': f"{cleaned_metrics.get('total_power', 0):.0f}",
                    'LF (ms²)': f"{cleaned_metrics.get('lf', 0):.0f}",
                    'HF (ms²)': f"{cleaned_metrics.get('hf', 0):.0f}",
                    'LF/HF': f"{cleaned_metrics.get('lf_hf_ratio', 0):.2f}",
                    'VLF (ms²)': f"{cleaned_metrics.get('vlf', 0):.0f}"
                }
                
                # CORREZIONE: Aggiungi metriche sonno solo se presenti E VALIDE
                if has_sleep_metrics:
                    row.update({
                        'Sonno Totale (h)': f"{cleaned_metrics.get('sleep_duration', 0):.1f}",
                        'Efficienza Sonno (%)': f"{cleaned_metrics.get('sleep_efficiency', 0):.1f}",
                        'Battito Sonno (bpm)': f"{cleaned_metrics.get('sleep_hr', 0):.1f}",
                        'Sonno Leggero (h)': f"{cleaned_metrics.get('sleep_light', 0):.1f}",
                        'Sonno Profondo (h)': f"{cleaned_metrics.get('sleep_deep', 0):.1f}",
                        'Sonno REM (h)': f"{cleaned_metrics.get('sleep_rem', 0):.1f}",
                        'Risvegli (h)': f"{cleaned_metrics.get('sleep_awake', 0):.1f}"
                    })
                else:
                    row.update({
                        'Sonno Totale (h)': '-',
                        'Efficienza Sonno (%)': '-',
                        'Battito Sonno (bpm)': '-',
                        'Sonno Leggero (h)': '-',
                        'Sonno Profondo (h)': '-',
                        'Sonno REM (h)': '-',
                        'Risvegli (h)': '-'
                    })
                
                table_data.append(row)
        
        # POI processa overall_metrics SOLO se non ci sono daily_metrics
        elif overall_metrics:
            recording_start = datetime.fromisoformat(analysis['recording_start'])
            
            # CORREZIONE: PULIZIA ESPLICITA - rimuovi metriche sonno se non valide
            cleaned_metrics = overall_metrics.copy()
            if not has_valid_sleep_metrics(cleaned_metrics):
                # Rimuovi esplicitamente tutte le metriche del sonno
                sleep_keys = ['sleep_duration', 'sleep_efficiency', 'sleep_hr', 
                            'sleep_light', 'sleep_deep', 'sleep_rem', 'sleep_awake']
                for key in sleep_keys:
                    cleaned_metrics.pop(key, None)
            
            # CORREZIONE: Controlla se ci sono metriche del sonno VALIDE (non zero)
            has_sleep_metrics = has_valid_sleep_metrics(cleaned_metrics)
            
            print(f"  Overall metrics: has_sleep_metrics = {has_sleep_metrics}")
            if has_sleep_metrics:
                print(f"    Sleep data: { {k: v for k, v in cleaned_metrics.items() if 'sleep' in k} }")
            
            row = {
                'Data Inserimento': data_inserimento,
                'Data Registrazione': recording_start.strftime('%d/%m/%Y'),
                'Battito (bpm)': f"{cleaned_metrics.get('hr_mean', 0):.1f}",
                'SDNN (ms)': f"{cleaned_metrics.get('sdnn', 0):.1f}",
                'RMSSD (ms)': f"{cleaned_metrics.get('rmssd', 0):.1f}",
                'Coerenza (%)': f"{cleaned_metrics.get('coherence', 0):.1f}",
                'Potenza Totale': f"{cleaned_metrics.get('total_power', 0):.0f}",
                'LF (ms²)': f"{cleaned_metrics.get('lf', 0):.0f}",
                'HF (ms²)': f"{cleaned_metrics.get('hf', 0):.0f}",
                'LF/HF': f"{cleaned_metrics.get('lf_hf_ratio', 0):.2f}",
                'VLF (ms²)': f"{cleaned_metrics.get('vlf', 0):.0f}"
            }
            
            # CORREZIONE: Aggiungi metriche sonno solo se presenti E VALIDE
            if has_sleep_metrics:
                row.update({
                    'Sonno Totale (h)': f"{cleaned_metrics.get('sleep_duration', 0):.1f}",
                    'Efficienza Sonno (%)': f"{cleaned_metrics.get('sleep_efficiency', 0):.1f}",
                    'Battito Sonno (bpm)': f"{cleaned_metrics.get('sleep_hr', 0):.1f}",
                    'Sonno Leggero (h)': f"{cleaned_metrics.get('sleep_light', 0):.1f}",
                    'Sonno Profondo (h)': f"{cleaned_metrics.get('sleep_deep', 0):.1f}",
                    'Sonno REM (h)': f"{cleaned_metrics.get('sleep_rem', 0):.1f}",
                    'Risvegli (h)': f"{cleaned_metrics.get('sleep_awake', 0):.1f}"
                })
            else:
                row.update({
                    'Sonno Totale (h)': '-',
                    'Efficienza Sonno (%)': '-',
                    'Battito Sonno (bpm)': '-',
                    'Sonno Leggero (h)': '-',
                    'Sonno Profondo (h)': '-',
                    'Sonno REM (h)': '-',
                    'Risvegli (h)': '-'
                })
            
            table_data.append(row)
        
        else:
            print(f"  ❌ Nessuna metrica trovata per questa analisi")
    
    table_data_sorted = sorted(table_data, key=lambda x: datetime.strptime(x['Data Registrazione'], '%d/%m/%Y'), reverse=True)
    
    if table_data_sorted:
        df = pd.DataFrame(table_data_sorted)
        
        st.dataframe(
            df,
            use_container_width=True,
            height=min(600, 150 + len(df) * 35)
        )
        
        csv_data = df.to_csv(index=False, sep=';')
        st.download_button(
            label="📥 Scarica Storico Completo",
            data=csv_data,
            file_name=f"storico_analisi_hrv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"download_storico_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        st.info(f"**📈 Totale:** {len(table_data_sorted)} giorni di registrazione nel database")
    else:
        st.info("Nessun dato da visualizzare")

def load_analysis_to_session(analysis):
    """Carica un'analisi specifica nella sessione corrente"""
    st.session_state.last_analysis_metrics = analysis.get('overall_metrics')
    st.session_state.analysis_datetimes = {
        'start_datetime': datetime.fromisoformat(analysis['recording_start']),
        'end_datetime': datetime.fromisoformat(analysis['recording_end'])
    }
    st.success("✅ Analisi caricata!")

def delete_analysis(analysis_index):
    """Elimina un'analisi dallo storico"""
    user_key = get_user_key(st.session_state.user_profile)
    if user_key and user_key in st.session_state.user_database:
        analyses = st.session_state.user_database[user_key].get('analyses', [])
        if 0 <= analysis_index < len(analyses):
            deleted_analysis = analyses.pop(analysis_index)
            st.session_state.user_database[user_key]['analyses'] = analyses
            save_user_database()
            st.success(f"✅ Analisi del {deleted_analysis.get('saved_at', '')} eliminata!")

# =============================================================================
# FUNZIONE PRINCIPALE
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
    
    # Header principale
    st.markdown('<h1 class="main-header">❤️ HRV Analytics ULTIMATE</h1>', unsafe_allow_html=True)
    
    # =============================================================================
    # SIDEBAR
    # =============================================================================
    with st.sidebar:
        create_user_selector()
        
        st.header("👤 Profilo Paziente")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.user_profile['name'] = st.text_input(
                "Nome", 
                value=st.session_state.user_profile['name'], 
                key=f"name_input_{st.session_state.user_profile.get('name', '')}"  # CHIAVE UNICA
            )
        with col2:
            st.session_state.user_profile['surname'] = st.text_input(
                "Cognome", 
                value=st.session_state.user_profile['surname'], 
                key=f"surname_input_{st.session_state.user_profile.get('surname', '')}"  # CHIAVE UNICA
            )
        
        birth_date = st.session_state.user_profile['birth_date']
        if birth_date is None:
            birth_date = datetime(1980, 1, 1).date()

        # CHIAVE UNICA PER DATA DI NASCITA
        birth_date_key = f"birth_date_{birth_date.strftime('%Y%m%d') if hasattr(birth_date, 'strftime') else 'none'}"
        
        st.session_state.user_profile['birth_date'] = st.date_input(
            "Data di nascita", 
            value=birth_date,
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date(),
            key=birth_date_key  # CHIAVE UNICA
        )

        if st.session_state.user_profile['birth_date']:
            st.write(f"Data selezionata: {st.session_state.user_profile['birth_date'].strftime('%d/%m/%Y')}")
        
        # CHIAVE UNICA PER SESSO
        gender_key = f"gender_{st.session_state.user_profile.get('gender', 'Uomo')}"
        st.session_state.user_profile['gender'] = st.selectbox(
            "Sesso", 
            ["Uomo", "Donna"], 
            index=0 if st.session_state.user_profile['gender'] == 'Uomo' else 1,
            key=gender_key  # CHIAVE UNICA
        )
        
        if st.session_state.user_profile['birth_date']:
            age = datetime.now().year - st.session_state.user_profile['birth_date'].year
            if (datetime.now().month, datetime.now().day) < (st.session_state.user_profile['birth_date'].month, st.session_state.user_profile['birth_date'].day):
                age -= 1
            st.session_state.user_profile['age'] = age
            st.info(f"Età: {age} anni")
        
        st.divider()
        st.header("💾 Salvataggio")
        
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
        
        create_activity_tracker()
    
    # =============================================================================
    # CONTENUTO PRINCIPALE
    # =============================================================================
    
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
            
            st.header("📊 Analisi HRV Completa")
            
            start_time = parse_starttime_from_file(content)
            timeline = calculate_recording_timeline(rr_intervals, start_time)
            
            # 2. DEBUG ESPLOSIVO - controlla ALLINEAMENTO DATE
            print(f"🎯 DEBUG ALLINEAMENTO DATE:")
            print(f"   File start: {start_time}")
            print(f"   Timeline start: {timeline['start_time']}")
            print(f"   Timeline end: {timeline['end_time']}")
            print(f"   Timeline giorni: {list(timeline['days_data'].keys())}")

            # 3. CONTROLLA SE CI SONO ATTIVITÀ SONNO
            if st.session_state.activities:
                sleep_activities = [a for a in st.session_state.activities if a['type'] == 'Sonno']
                print(f"   Attività sonno trovate: {len(sleep_activities)}")
                
                for i, sleep_act in enumerate(sleep_activities):
                    sleep_start = sleep_act['start_time']
                    sleep_end = sleep_start + timedelta(minutes=sleep_act['duration'])
                    print(f"   Sonno {i+1}: {sleep_start} -> {sleep_end}")
                    print(f"     Date: {sleep_start.date().isoformat()} -> {sleep_end.date().isoformat()}")
                    
                    # Verifica se le date coincidono
                    timeline_dates = list(timeline['days_data'].keys())
                    sleep_dates = [sleep_start.date().isoformat(), sleep_end.date().isoformat()]
                    
                    date_match = any(date in timeline_dates for date in sleep_dates)
                    print(f"     Date corrispondono con timeline: {date_match}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📅 Inizio Registrazione", 
                         timeline['start_time'].strftime('%d/%m/%Y %H:%M:%S'))
            with col2:
                st.metric("📅 Fine Registrazione", 
                         timeline['end_time'].strftime('%d/%m/%Y %H:%M:%S'))
            
            st.metric("⏱️ Durata Totale", f"{timeline['total_duration_hours']:.1f} ore")
            
            user_profile = st.session_state.user_profile
            daily_metrics = calculate_daily_metrics(
                timeline['days_data'], 
                user_profile['age'], 
                user_profile['gender']
            )
            
            avg_metrics = {}
            
            try:
                calculated_metrics = calculate_professional_hrv_metrics(
                    rr_intervals, user_profile['age'], user_profile['gender'], start_time, timeline['end_time']
                )
                if calculated_metrics:
                    avg_metrics = calculated_metrics
                else:
                    raise ValueError("calculate_realistic_hrv_metrics ha restituito None")
            except Exception as e:
                st.sidebar.warning(f"Calcolo metriche fallito: {e}")
                avg_metrics = {
                    'sdnn': 45.0, 'rmssd': 35.0, 'hr_mean': 70.0, 'coherence': 60.0,
                    'recording_hours': 24.0, 'total_power': 2500.0, 'vlf': 400.0,
                    'lf': 1000.0, 'hf': 1100.0, 'lf_hf_ratio': 0.9
                    # CORREZIONE: NESSUNA METRICA SONNO nei default
                }

            # DEBUG ULTIMATIVO: verifica ESATTAMENTE cosa c'è nelle attività
            print(f"🎯 DEBUG ULTIMATIVO ACTIVITIES:")
            for i, activity in enumerate(st.session_state.activities):
                print(f"   {i}: type='{activity['type']}', name='{activity['name']}'")
                print(f"      start_time={activity['start_time']}, duration={activity['duration']}min")
            
            sleep_count = sum(1 for a in st.session_state.activities if a['type'] == 'Sonno')
            print(f"   Totale attività 'Sonno': {sleep_count}")
            
            # AGGIUNGI METRICHE SONNO SOLO SE CI SONO ATTIVITÀ SONNO ESPLICITE
            sleep_metrics = get_sleep_metrics_from_activities(
                st.session_state.activities, daily_metrics, timeline
            )

            if sleep_metrics:
                avg_metrics.update(sleep_metrics)
                st.success(f"😴 SONNO RILEVATO: {sleep_metrics.get('sleep_duration', 0):.1f} ore")
                print(f"✅ SONNO AGGIUNTO ALLE METRICHE")
            else:
                st.info("💡 Per vedere l'analisi del sonno, registra un'attività 'Sonno'")
                print(f"❌ NESSUNA METRICA SONNO TROVATA")
            
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
            
            # SECONDA RIGA: ANALISI SPETTRALE E SONNO
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

            # 🔬 REPORT QUALITÀ REGISTRAZIONE
            st.subheader("🔬 Qualità della Registrazione")
            
            col1, col2 = st.columns(2)
            with col1:
                qualita = calculated_metrics.get('qualita_segnale', 'Sconosciuta')
                colore = "🟢" if qualita == "Ottima" else "🔵" if qualita == "Buona" else "🟠" if qualita == "Accettabile" else "🔴"
                st.metric("Livello Qualità", f"{colore} {qualita}")
            
            with col2:
                battiti_corretti = calculated_metrics.get('battiti_corretti', 0)
                st.metric("Battiti Corretti", f"{battiti_corretti}")
            
            if qualita == "Scadente":
                st.error("""
                **🎯 Consigli per migliorare:**
                - Controlla che il sensore sia ben posizionato
                - Stai fermo durante la misurazione  
                - Prova in un ambiente tranquillo
                - Ripeti la registrazione
                """)
            elif qualita == "Accettabile":
                st.warning("""
                **💡 Suggerimenti:**
                - La registrazione è utilizzabile ma puoi fare di meglio
                - Cerca di muoverti meno durante la misurazione
                """)
            else:
                st.success("✅ Ottima registrazione! Dati molto affidabili.")
            
            # CORREZIONE: Mostra metriche sonno solo se presenti
            has_sleep_metrics = has_valid_sleep_metrics(avg_metrics)
            
            with col4:
                if has_sleep_metrics:
                    st.markdown(f"""
                    <div class="compact-metric-card">
                        <div class="metric-value">🛌 {avg_metrics['sleep_duration']:.1f}h</div>
                        <div class="metric-label">Durata Sonno</div>
                        <div class="metric-unit">ore</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="compact-metric-card">
                        <div class="metric-value">☀️ Diurno</div>
                        <div class="metric-label">Registrazione</div>
                        <div class="metric-unit">nessun sonno</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col5:
                if has_sleep_metrics:
                    st.markdown(f"""
                    <div class="compact-metric-card">
                        <div class="metric-value">📊 {avg_metrics['sleep_efficiency']:.0f}%</div>
                        <div class="metric-label">Efficienza Sonno</div>
                        <div class="metric-unit">percentuale</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="compact-metric-card">
                        <div class="metric-value">📈 {avg_metrics['vlf']:.0f}</div>
                        <div class="metric-label">VLF</div>
                        <div class="metric-unit">ms²</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ANALISI SONNO DETTAGLIATA - SOLO SE PRESENTE
            if has_sleep_metrics:
                st.subheader("😴 Analisi Dettagliata del Sonno")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="compact-metric-card">
                        <div class="metric-value">💤 {avg_metrics.get('sleep_hr', 60):.0f}</div>
                        <div class="metric-label">Battito a Riposo</div>
                        <div class="metric-unit">bpm</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
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
            else:
                st.subheader("☀️ Registrazione Diurna")
                st.info("Questa registrazione non include ore notturne. Nessuna analisi del sonno disponibile.")
            
            # METRICHE DETTAGLIATE PER GIORNO
            with st.expander("📅 Metriche Dettagliate per Giorno", expanded=True):
                if not daily_metrics:
                    st.info("Non ci sono abbastanza dati per un'analisi giornaliera")
                else:
                    try:
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
                        
                        st.dataframe(
                            hrv_df,
                            use_container_width=True,
                            hide_index=True,
                            height=min(300, 50 + len(hrv_df) * 35)
                        )

                        # CORREZIONE: Mostra metriche sonno solo se presenti in almeno un giorno
                        has_any_sleep_data = any(
                            any(key.startswith('sleep_') for key in day_metrics.keys())
                            for day_metrics in daily_metrics.values()
                        )

                        if has_any_sleep_data:
                            st.subheader("😴 Metriche Sonno")

                            sleep_table_data = []

                            for day_date, day_metrics in daily_metrics.items():
                                day_dt = datetime.fromisoformat(day_date)
                                
                                # Controlla se ci sono metriche del sonno per questo giorno
                                has_sleep_data = any(key.startswith('sleep_') for key in day_metrics.keys())
                                
                                if has_sleep_data:
                                    row = {
                                        'Data': day_dt.strftime('%d/%m/%Y'),
                                        'Durata Totale (h)': f"{day_metrics.get('sleep_duration', 0):.1f}",
                                        'Efficienza (%)': f"{day_metrics.get('sleep_efficiency', 0):.1f}",
                                        'HR Riposo (bpm)': f"{day_metrics.get('sleep_hr', 0):.1f}",
                                        'Sonno Leggero (h)': f"{day_metrics.get('sleep_light', 0):.1f}",
                                        'Sonno Profondo (h)': f"{day_metrics.get('sleep_deep', 0):.1f}",
                                        'Sonno REM (h)': f"{day_metrics.get('sleep_rem', 0):.1f}",
                                        'Risvegli (h)': f"{day_metrics.get('sleep_awake', 0):.1f}"
                                    }
                                    sleep_table_data.append(row)

                            if sleep_table_data:
                                sleep_df = pd.DataFrame(sleep_table_data)
                                
                                st.dataframe(
                                    sleep_df,
                                    use_container_width=True,
                                    hide_index=True,
                                    height=min(300, 50 + len(sleep_df) * 35)
                                )
                            else:
                                st.info("😴 Nessuna analisi del sonno disponibile per questa registrazione")
                        else:
                            st.info("😴 Nessuna analisi del sonno disponibile - registrazione diurna")                       
                        st.markdown("<br>", unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            hrv_csv = hrv_df.to_csv(index=False, sep=';')
                            st.download_button(
                                label="📥 Scarica Metriche HRV",
                                data=hrv_csv,
                                file_name=f"hrv_metriche_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True,
                                key=f"download_hrv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            )
                        
                        with col2:
                            if has_any_sleep_data and sleep_table_data:
                                sleep_csv = sleep_df.to_csv(index=False, sep=';')
                                st.download_button(
                                    label="📥 Scarica Metriche Sonno",
                                    data=sleep_csv,
                                    file_name=f"sonno_metriche_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    use_container_width=True,
                                    key=f"download_sonno_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                )
                            else:
                                st.empty()
                                
                    except Exception as e:
                        st.error(f"Errore nella visualizzazione delle metriche dettagliate: {e}")
                    
            # GRAFICO DETTAGLIATO CON ZOOM INTERATTIVO
            st.subheader("📈 Andamento Dettagliato HRV con Attività")
            
            if len(rr_intervals) > 0:
                timestamps = []
                current_time = start_time
                
                # FILTRO DI INTERPOLAZIONE PER ARTEFATTI ISOLATI
                def interpolate_artifacts(rr_data):
                    """Corregge artefatti isolati usando la media dei vicini"""
                    cleaned_data = rr_data.copy()
                    artifact_count = 0
                    
                    for i in range(1, len(rr_data) - 1):  # Salta primo e ultimo
                        current_rr = rr_data[i]
                        prev_rr = rr_data[i-1]
                        next_rr = rr_data[i+1]
                        
                        # Definisci range normale basato sui vicini
                        normal_min = min(prev_rr, next_rr) * 0.7   # -30%
                        normal_max = max(prev_rr, next_rr) * 1.3   # +30%
                        
                        # Se il battito corrente è anormale ma i vicini sono normali
                        if not (normal_min <= current_rr <= normal_max) and (400 <= prev_rr <= 1200) and (400 <= next_rr <= 1200):
                            # Interpola con la media dei vicini
                            cleaned_data[i] = (prev_rr + next_rr) / 2
                            artifact_count += 1
                    
                    if artifact_count > 0:
                        st.success(f"🔧 Corretti {artifact_count} artefatti isolati")
                    
                    return cleaned_data
                
                # APPLICA IL FILTRO
                filtered_rr_intervals = interpolate_artifacts(rr_intervals)
                
                # FILTRO SECONDARIO PER ARTEFATTI PERSISTENTI
                final_rr_intervals = []
                for rr in filtered_rr_intervals:
                    if 350 <= rr <= 1300:  # Range fisiologico ampio ma realistico
                        final_rr_intervals.append(rr)
                    else:
                        # Per artefatti estremi, usa un valore conservativo
                        final_rr_intervals.append(800)  # 75 bpm default
                
                # CREA TIMESTAMPS
                for rr in final_rr_intervals:
                    timestamps.append(current_time)
                    current_time += timedelta(milliseconds=rr)
                
                # CALCOLO FREQUENZA CARDIACA CON CONTROLLO FINALE
                hr_instant = []
                for i in range(len(final_rr_intervals)):
                    hr = 60000 / final_rr_intervals[i]
                    
                    # Controllo di coerenza con i vicini
                    if i > 0 and i < len(final_rr_intervals) - 1:
                        prev_hr = 60000 / final_rr_intervals[i-1]
                        next_hr = 60000 / final_rr_intervals[i+1]
                        avg_surrounding = (prev_hr + next_hr) / 2
                        
                        # Se il battito è troppo diverso dai vicini, usa la media
                        if abs(hr - avg_surrounding) > 40:  # Differenza > 40 bpm
                            hr = avg_surrounding
                    
                    # Limiti assoluti
                    hr = max(30, min(hr, 180))  # 30-180 bpm range assoluto
                    hr_instant.append(hr)
                
                # APPLICA SMOOTHING LEGGERO
                if len(hr_instant) > 3:
                    hr_smoothed = []
                    for i in range(len(hr_instant)):
                        if i == 0:
                            hr_smoothed.append(hr_instant[i])
                        elif i == len(hr_instant) - 1:
                            hr_smoothed.append(hr_instant[i])
                        else:
                            # Media pesata: 25% precedente, 50% corrente, 25% successivo
                            smoothed = (hr_instant[i-1] * 0.25 + hr_instant[i] * 0.5 + hr_instant[i+1] * 0.25)
                            hr_smoothed.append(smoothed)
                    hr_instant = hr_smoothed
                
                window_size = min(100, len(final_rr_intervals) // 15)
                if window_size < 30:
                    window_size = min(30, len(final_rr_intervals))
                
                sdnn_moving = []
                rmssd_moving = []
                moving_timestamps = []
                
                # FUNZIONE SMOOTHING
                def smooth_data(data, window_size=3):
                    if len(data) < window_size:
                        return data
                    smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
                    return smoothed.tolist()
                
                for i in range(len(final_rr_intervals) - window_size):
                    window_rr = final_rr_intervals[i:i + window_size]
                    
                    sdnn = np.std(window_rr, ddof=1) if len(window_rr) > 1 else 0
                    differences = np.diff(window_rr)
                    rmssd = np.sqrt(np.mean(np.square(differences))) if len(differences) > 0 else 0
                    
                    sdnn_moving.append(sdnn)
                    rmssd_moving.append(rmssd)
                    if i + window_size // 2 < len(timestamps):
                        moving_timestamps.append(timestamps[i + window_size // 2])
                
                # APPLICA SMOOTHING
                if len(sdnn_moving) > 5:
                    sdnn_moving = smooth_data(sdnn_moving, 5)
                    rmssd_moving = smooth_data(rmssd_moving, 5)
                    if len(moving_timestamps) > 4:
                        moving_timestamps = moving_timestamps[2:-2]
                
                # STATISTICHE
                hr_stats = {
                    'medio': np.mean(hr_instant),
                    'massimo': np.max(hr_instant),
                    'minimo': np.min(hr_instant),
                    'battiti_totali': len(final_rr_intervals)
                }
                
                st.info(f"""
                **📊 Dati Filtrati:**
                - **Battiti:** {hr_stats['battiti_totali']}
                - **Battito medio:** {hr_stats['medio']:.1f} bpm
                - **Range:** {hr_stats['minimo']:.1f} - {hr_stats['massimo']:.1f} bpm
                - **Finestra mobile:** {window_size} battiti
                """)
                
                fig_main = go.Figure()
                
                if st.session_state.activities:
                    for activity in st.session_state.activities:
                        activity_start = activity['start_time']
                        activity_end = activity_start + timedelta(minutes=activity['duration'])
                        
                        color = activity.get('color', '#95a5a6')
                        
                        fig_main.add_vrect(
                            x0=activity_start,
                            x1=activity_end,
                            fillcolor=color,
                            opacity=0.2,
                            layer="below",
                            line_width=0,
                        )
                
                fig_main.add_trace(go.Scatter(
                    x=timestamps,
                    y=hr_instant,
                    mode='lines',
                    name='Battito Istantaneo',
                    line=dict(color='#e74c3c', width=1),
                    opacity=0.8
                ))
                
                if sdnn_moving and len(sdnn_moving) > 0:  # CONTROLLO CORRETTO
                    fig_main.add_trace(go.Scatter(
                        x=moving_timestamps,
                        y=sdnn_moving,
                        mode='lines',
                        name='SDNN Mobile',
                        line=dict(color='#3498db', width=2),
                        yaxis='y2'
                    ))
                
                if rmssd_moving and len(rmssd_moving) > 0:  # CONTROLLO CORRETTO
                    fig_main.add_trace(go.Scatter(
                        x=moving_timestamps,
                        y=rmssd_moving,
                        mode='lines',
                        name='RMSSD Mobile',
                        line=dict(color='#2ecc71', width=2),
                        yaxis='y3'
                    ))
                
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
                    height=600,
                    showlegend=True,
                    hovermode='x unified',
                    plot_bgcolor='rgba(240,240,240,0.1)'
                )
                
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
                
                st.caption("""
                **🔍 Come zoommare:**
                - **Mouse:** Trascina per selezionare un'area da zoommare
                - **Doppio click:** Reset dello zoom
                - **Pulsanti sopra:** Zoom predefiniti (1h, 6h, 1 giorno, Tutto)
                - **Aree colorate:** Periodi di attività (Allenamento=🔴, Alimentazione=🟠, Stress=🟣, Riposo=🔵)
                """)
                
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
            
            # SALVATAGGIO ANALISI - VERSIONE CORRETTA
            if st.button("💾 Salva Analisi nel Database", type="primary"):
                # Verifica che il profilo utente sia completo
                if not st.session_state.user_profile['name'] or not st.session_state.user_profile['surname'] or not st.session_state.user_profile['birth_date']:
                    st.error("❌ Completa il profilo utente (nome, cognome e data di nascita) prima di salvare l'analisi")
                else:
                    analysis_data = {
                        'timestamp': datetime.now().isoformat(),
                        'recording_start': timeline['start_time'].isoformat(),
                        'recording_end': timeline['end_time'].isoformat(),
                        'recording_duration_hours': timeline['total_duration_hours'],
                        'rr_intervals_count': len(rr_intervals),
                        'overall_metrics': avg_metrics,
                        'daily_metrics': daily_metrics
                    }
                    
                    if save_analysis_to_history(analysis_data):
                        st.success("✅ Analisi salvata nello storico!")
                    else:
                        st.error("❌ Errore nel salvataggio dell'analisi")

            # ANALISI IMPATTO ATTIVITÀ
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
        display_analysis_history()
        
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
        - ✅ **Storico analisi** - confronta tutte le tue registrazioni precedenti
        - ✅ **Analisi sonno avanzata** dagli IBI reali invece di stime fisse
        """)

def main_with_auth():
    """Versione principale con sistema di autenticazione"""
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if not st.session_state.authenticated:
        show_auth_interface()
    else:
        add_logout_button()
        main()

def show_auth_interface():
    """Interfaccia di login/registrazione"""
    st.title("🔐 HRV Analytics - Accesso")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Registrazione", "Recupera Password"])
    
    with tab1:
        st.subheader("Accedi al tuo account")
        login_email = st.text_input("Email", key="login_email_auth")
        login_password = st.text_input("Password", type="password", key="login_password_auth")
        
        if st.button("Accedi", key="login_btn_auth"):
            if login_email and login_password:
                success, message = authenticate_user(login_email, login_password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.current_user = login_email
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Inserisci email e password")
    
    with tab2:
        st.subheader("Crea nuovo account")
        reg_name = st.text_input("Nome completo", key="reg_name_auth")
        reg_email = st.text_input("Email", key="reg_email_auth")
        reg_password = st.text_input("Password", type="password", key="reg_password_auth")
        reg_confirm = st.text_input("Conferma Password", type="password", key="reg_confirm_auth")
        
        if st.button("Registrati", key="reg_btn_auth"):
            if reg_password != reg_confirm:
                st.error("Le password non coincidono")
            elif len(reg_password) < 6:
                st.error("La password deve essere di almeno 6 caratteri")
            elif reg_name and reg_email and reg_password:
                success, message = register_user(reg_email, reg_password, reg_name)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Compila tutti i campi")
    
    with tab3:
        st.subheader("Recupera Password")
        reset_email = st.text_input("Inserisci la tua email", key="reset_email_auth")
        
        if st.button("Invia link di reset", key="reset_btn_auth"):
            if reset_email:
                success, message = send_password_reset_email(reset_email)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Inserisci la tua email")

def add_logout_button():
    """Aggiunge il pulsante di logout nella sidebar"""
    if st.session_state.authenticated:
        st.sidebar.divider()
        if st.sidebar.button("🚪 Logout", key="logout_btn_auth", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()

if __name__ == "__main__":
    main_with_auth()