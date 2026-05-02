# --- REVISED SMASH ALERT LOGIC ---
st.subheader("🔥 Startup Smash Alert")
smashes = []

# 1. Clean the list of drafted names (lowercase and strip spaces)
drafted_names = [
    f"{p['metadata'].get('first_name', '')} {p['metadata'].get('last_name', '')}".strip().lower() 
    for p in picks
]

# 2. Also check player IDs if possible (Sleeper uses IDs as the 'glue')
drafted_ids = {str(p.get('player_id')) for p in picks}

for name, adp in startup_adp.items():
    clean_name = name.strip().lower()
    
    # 3. Use 'in' to check if the cleaned name exists in our drafted list
    if clean_name not in drafted_names:
        if current_pick_no > (adp + 4):
            smashes.append({
                "Player": name, 
                "ADP": adp, 
                "Value": f"+{round(current_pick_no - adp, 1)} spots"
            })

if smashes:
    st.success(f"⚠️ VALUE DETECTED!")
    st.table(pd.DataFrame(smashes))
else:
    st.info("No major values falling past ADP yet.")
