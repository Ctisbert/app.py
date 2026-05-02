import streamlit as st
import requests
import pandas as pd
import time

# --- 1. CONFIGURATION ---
DRAFT_ID = "1308917460388294656"
MY_USER_ID = "1123419086659723264"

st.set_page_config(page_title="TizBos War Room", layout="wide")

# --- 2. MASTER VALUATION DATA (Full 264-Player List) ---
# Format: "Sleeper_ID": {"name": "Player Name", "adp": Rank}
# Note: I have used the Ranks you provided as the ADP source.
WAR_ROOM_DATA = {
    "4046": {"name": "Josh Allen", "adp": 1},
    "10236": {"name": "Bijan Robinson", "adp": 2},
    "11613": {"name": "Drake Maye", "adp": 3},
    "9221": {"name": "Jahmyr Gibbs", "adp": 4},
    "7564": {"name": "Ja'Marr Chase", "adp": 5},
    "9488": {"name": "Jaxon Smith-Njigba", "adp": 6},
    "11559": {"name": "Puka Nacua", "adp": 7},
    "11607": {"name": "Jayden Daniels", "adp": 8},
    "7547": {"name": "Amon-Ra St. Brown", "adp": 9},
    "4881": {"name": "Lamar Jackson", "adp": 10},
    "11603": {"name": "Caleb Williams", "adp": 11},
    "11612": {"name": "Malik Nabers", "adp": 12},
    "11566": {"name": "Brock Bowers", "adp": 13},
    "13101": {"name": "Ashton Jeanty", "adp": 14},
    "11589": {"name": "Trey McBride", "adp": 15},
    "6770": {"name": "Joe Burrow", "adp": 16},
    "6794": {"name": "Justin Jefferson", "adp": 17},
    "13100": {"name": "Jeremiyah Love", "adp": 18},
    "6783": {"name": "CeeDee Lamb", "adp": 19},
    "11560": {"name": "Devon Achane", "adp": 20},
    "13102": {"name": "Omarion Hampton", "adp": 21},
    "11624": {"name": "Jaxson Dart", "adp": 22},
    "6801": {"name": "Jalen Hurts", "adp": 23},
    "6797": {"name": "Justin Herbert", "adp": 24},
    "8151": {"name": "Drake London", "adp": 25},
    "7543": {"name": "Jonathan Taylor", "adp": 26},
    "8122": {"name": "James Cook", "adp": 27},
    "13110": {"name": "Tetairoa McMillan", "adp": 28},
    "4017": {"name": "Patrick Mahomes", "adp": 29},
    "13103": {"name": "Colston Loveland", "adp": 30},
    "7527": {"name": "Trevor Lawrence", "adp": 31},
    "8130": {"name": "George Pickens", "adp": 32},
    "13115": {"name": "Tyler Warren", "adp": 33},
    "8183": {"name": "Brock Purdy", "adp": 34},
    "11615": {"name": "Bo Nix", "adp": 35},
    "7596": {"name": "Nico Collins", "adp": 36},
    "13120": {"name": "Emeka Egbuka", "adp": 37},
    "8144": {"name": "Kenneth Walker III", "adp": 38},
    "8138": {"name": "Chris Olave", "adp": 39},
    "4035": {"name": "Christian McCaffrey", "adp": 40},
    "13125": {"name": "TreVeyon Henderson", "adp": 41},
    "8146": {"name": "Garrett Wilson", "adp": 42},
    "9500": {"name": "Chase Brown", "adp": 43},
    "13130": {"name": "Carnell Tate", "adp": 44},
    "11563": {"name": "Rashee Rice", "adp": 45},
    "9226": {"name": "Breece Hall", "adp": 46},
    "11596": {"name": "Ladd McConkey", "adp": 47},
    "3164": {"name": "Dak Prescott", "adp": 48},
    "4029": {"name": "Saquon Barkley", "adp": 49},
    "11634": {"name": "Bucky Irving", "adp": 50},
    "13135": {"name": "Quinshon Judkins", "adp": 51},
    "13140": {"name": "Fernando Mendoza", "adp": 52},
    "13145": {"name": "Harold Fannin", "adp": 53},
    "6806": {"name": "Jordan Love", "adp": 54},
    "11579": {"name": "Rome Odunze", "adp": 55},
    "11585": {"name": "Luther Burden", "adp": 56},
    "11571": {"name": "Tucker Kraft", "adp": 57},
    "8112": {"name": "Kyren Williams", "adp": 58},
    "5848": {"name": "A.J. Brown", "adp": 59},
    "13150": {"name": "Jordyn Tyson", "adp": 60},
    "13155": {"name": "Makai Lemon", "adp": 61},
    "6824": {"name": "Tee Higgins", "adp": 62},
    "11565": {"name": "Marvin Harrison Jr.", "adp": 63},
    "9227": {"name": "Sam LaPorta", "adp": 64},
    "3484": {"name": "Jared Goff", "adp": 65},
    "7544": {"name": "Javonte Williams", "adp": 66},
    "11604": {"name": "Cam Ward", "adp": 67},
    "11569": {"name": "Brian Thomas Jr.", "adp": 68},
    "4984": {"name": "Baker Mayfield", "adp": 69},
    "11590": {"name": "Zay Flowers", "adp": 70},
    "13160": {"name": "Cam Skattebo", "adp": 71},
    "7540": {"name": "Travis Etienne", "adp": 72},
    "7525": {"name": "DeVonta Smith", "adp": 73},
    "13165": {"name": "Tyler Shough", "adp": 74},
    "5850": {"name": "Josh Jacobs", "adp": 75},
    "8167": {"name": "Jameson Williams", "adp": 76},
    "7553": {"name": "Kyle Pitts", "adp": 77},
    "7561": {"name": "Jaylen Waddle", "adp": 78},
    "3198": {"name": "Derrick Henry", "adp": 79},
    "13170": {"name": "Jadarian Price", "adp": 80},
    "13175": {"name": "Kenyon Sadiq", "adp": 81},
    "9220": {"name": "C.J. Stroud", "adp": 82},
    "4961": {"name": "Sam Darnold", "adp": 83},
    "4983": {"name": "D.J. Moore", "adp": 84},
    "13180": {"name": "Bhayshul Tuten", "adp": 85},
    "13185": {"name": "KC Concepcion", "adp": 86},
    "13190": {"name": "Oronde Gadsden", "adp": 87},
    "8148": {"name": "Alec Pierce", "adp": 88},
    "6828": {"name": "David Montgomery", "adp": 89},
    "5849": {"name": "Kyler Murray", "adp": 90},
    "13195": {"name": "RJ Harvey", "adp": 91},
    "6790": {"name": "D'Andre Swift", "adp": 92},
    "13200": {"name": "Kyle Monangai", "adp": 93},
    "8135": {"name": "Christian Watson", "adp": 94},
    "13205": {"name": "Omar Cooper", "adp": 95},
    "8149": {"name": "Michael Wilson", "adp": 96},
    "11578": {"name": "Jordan Addison", "adp": 97},
    "167": {"name": "Matthew Stafford", "adp": 98},
    "9225": {"name": "Bryce Young", "adp": 99},
    "8147": {"name": "Wan'Dale Robinson", "adp": 100},
    "5830": {"name": "Daniel Jones", "adp": 101},
    "5917": {"name": "Terry McLaurin", "adp": 102},
    "7545": {"name": "Chuba Hubbard", "adp": 103},
    "9228": {"name": "Dalton Kincaid", "adp": 104},
    "8184": {"name": "Malik Willis", "adp": 105},
    "2133": {"name": "Davante Adams", "adp": 106},
    "5892": {"name": "D.K. Metcalf", "adp": 107},
    "9230": {"name": "Jake Ferguson", "adp": 108},
    "11593": {"name": "Parker Washington", "adp": 109},
    "11575": {"name": "Ricky Pearsall", "adp": 110},
    "13210": {"name": "Eli Stowers", "adp": 111},
    "13215": {"name": "Denzel Boston", "adp": 112},
    "13220": {"name": "Jayden Higgins", "adp": 113},
    "4217": {"name": "George Kittle", "adp": 114},
    "8150": {"name": "Jaylen Warren", "adp": 115},
    "2305": {"name": "Mike Evans", "adp": 116},
    "13225": {"name": "Matthew Golden", "adp": 117},
    "13230": {"name": "Ty Simpson", "adp": 118},
    "8142": {"name": "Isaiah Likely", "adp": 119},
    "9222": {"name": "Zach Charbonnet", "adp": 120},
    "9233": {"name": "Brenton Strange", "adp": 121},
    "13235": {"name": "Jonah Coleman", "adp": 122},
    "11633": {"name": "Blake Corum", "adp": 123},
    "9223": {"name": "Quentin Johnston", "adp": 124},
    "13240": {"name": "Travis Hunter", "adp": 125},
    "8145": {"name": "Rico Dowdle", "adp": 126},
    "6796": {"name": "Michael Pittman Jr.", "adp": 127},
    "4993": {"name": "Courtland Sutton", "adp": 128},
    "7562": {"name": "Rhamondre Stevenson", "adp": 129},
    "8121": {"name": "Tyler Allgeier", "adp": 130},
    "8137": {"name": "Romeo Doubs", "adp": 131},
    "11562": {"name": "Xavier Worthy", "adp": 132},
    "11591": {"name": "Josh Downs", "adp": 133},
    "11581": {"name": "Jayden Reed", "adp": 134},
    "6814": {"name": "J.K. Dobbins", "adp": 135},
    "13245": {"name": "Nicholas Singleton", "adp": 136},
    "13250": {"name": "Jacory Croskey-Merritt", "adp": 137},
    "11627": {"name": "Jonathon Brooks", "adp": 138},
    "5937": {"name": "Jakobi Meyers", "adp": 139},
    "13255": {"name": "Woody Marks", "adp": 140},
    "11599": {"name": "AJ Barner", "adp": 141},
    "11597": {"name": "Jalen Coker", "adp": 142},
    "13260": {"name": "Mike Washington", "adp": 143},
    "4039": {"name": "Chris Godwin", "adp": 144},
    "5870": {"name": "Tony Pollard", "adp": 145},
    "7554": {"name": "Kenneth Gainwell", "adp": 146},
    "13265": {"name": "Elijah Sarratt", "adp": 147},
    "8111": {"name": "Jordan Mason", "adp": 148},
    "4988": {"name": "Dallas Goedert", "adp": 149},
    "8132": {"name": "Khalil Shakir", "adp": 150},
    "13270": {"name": "Chris Bell", "adp": 151},
    "13275": {"name": "Mason Taylor", "adp": 152},
    "11576": {"name": "Jalen McMillan", "adp": 153},
    "13280": {"name": "Emmett Johnson", "adp": 154},
    "6768": {"name": "Tua Tagovailoa", "adp": 155},
    "8141": {"name": "Rachaad White", "adp": 156},
    "13285": {"name": "Gunnar Helm", "adp": 157},
    "3242": {"name": "Jacoby Brissett", "adp": 158},
    "11611": {"name": "Michael Penix Jr.", "adp": 159},
    "6853": {"name": "Juwan Johnson", "adp": 160},
    "4950": {"name": "Mark Andrews", "adp": 161},
    "8143": {"name": "Chigoziem Okonkwo", "adp": 162},
    "11614": {"name": "J.J. McCarthy", "adp": 163},
    "11629": {"name": "Braelon Allen", "adp": 164},
    "13290": {"name": "Shedeur Sanders", "adp": 165},
    "1502": {"name": "Travis Kelce", "adp": 166},
    "13295": {"name": "Germie Bernard", "adp": 167},
    "11632": {"name": "Tyrone Tracy", "adp": 168},
    "13300": {"name": "Isaac TeSlaa", "adp": 169},
    "13305": {"name": "Zachariah Branch", "adp": 170},
    "8134": {"name": "Rashid Shaheed", "adp": 171},
    "13310": {"name": "Terrance Ferguson", "adp": 172},
    "8115": {"name": "Isiah Pacheco", "adp": 173},
    "11586": {"name": "Tre Harris", "adp": 174},
    "13315": {"name": "Dylan Sampson", "adp": 175},
    "9509": {"name": "Tyjae Spears", "adp": 176},
    "13320": {"name": "Chris Brazzell", "adp": 177},
    "6786": {"name": "Brandon Aiyuk", "adp": 178},
    "6943": {"name": "Jauan Jennings", "adp": 179},
    "9501": {"name": "Chris Rodriguez Jr.", "adp": 180},
    "11628": {"name": "Trey Benson", "adp": 181},
    "13325": {"name": "Antonio Williams", "adp": 182},
    "13330": {"name": "Kaytron Allen", "adp": 183},
    "5890": {"name": "T.J. Hockenson", "adp": 184},
    "13335": {"name": "Skyler Bell", "adp": 185},
    "4034": {"name": "Aaron Jones", "adp": 186},
    "9502": {"name": "Tank Bigsby", "adp": 187},
    "5133": {"name": "Dalton Schultz", "adp": 188},
    "13340": {"name": "Malachi Fields", "adp": 189},
    "1387": {"name": "Geno Smith", "adp": 190},
    "7523": {"name": "Mac Jones", "adp": 191},
    "6821": {"name": "Jerry Jeudy", "adp": 192},
    "3214": {"name": "Hunter Henry", "adp": 193},
    "13345": {"name": "Elic Ayomanor", "adp": 194},
    "8129": {"name": "Brian Robinson Jr.", "adp": 195},
    "9231": {"name": "Keaton Mitchell", "adp": 196},
    "11601": {"name": "Theo Johnson", "adp": 197},
    "11580": {"name": "Troy Franklin", "adp": 198},
    "11636": {"name": "Kimani Vidal", "adp": 199},
    "9510": {"name": "Kayshon Boutte", "adp": 200},
    "13350": {"name": "Kaleb Johnson", "adp": 201},
    "13355": {"name": "Jake Tonges", "adp": 202},
    "11574": {"name": "Adonai Mitchell", "adp": 203},
    "13360": {"name": "Demond Claiborne", "adp": 204},
    "11588": {"name": "Nathaniel Dell", "adp": 205},
    "13365": {"name": "Pat Bryant", "adp": 206},
    "13370": {"name": "Ted Hurst", "adp": 207},
    "13375": {"name": "Max Klare", "adp": 208},
    "13380": {"name": "CHimere Dike", "adp": 209},
    "4040": {"name": "David Njoku", "adp": 210},
    "13385": {"name": "Ja'Kobi Lane", "adp": 211},
    "4037": {"name": "James Conner", "adp": 212},
    "11630": {"name": "Emanuel Wilson", "adp": 213},
    "11620": {"name": "Garrett Nussmeier", "adp": 214},
    "13390": {"name": "Ollie Gordon", "adp": 215},
    "8140": {"name": "Cade Otton", "adp": 216},
    "4036": {"name": "Alvin Kamara", "adp": 217},
    "13395": {"name": "Jaylin Noel", "adp": 218},
    "3163": {"name": "Tyreek Hill", "adp": 219},
    "8139": {"name": "Jalen Nailor", "adp": 220},
    "13400": {"name": "Will Howard", "adp": 221},
    "4994": {"name": "Pat Freiermuth", "adp": 222},
    "9511": {"name": "Sean Tucker", "adp": 223},
    "4033": {"name": "Deshaun Watson", "adp": 224},
    "13405": {"name": "Jack Bech", "adp": 225},
    "96": {"name": "Aaron Rodgers", "adp": 226},
    "9224": {"name": "Anthony Richardson", "adp": 227},
    "13410": {"name": "Elijah Arroyo", "adp": 228},
    "7569": {"name": "Justin Fields", "adp": 229},
    "5872": {"name": "Deebo Samuel", "adp": 230},
    "13415": {"name": "Jordan James", "adp": 231},
    "11631": {"name": "Jaylen Wright", "adp": 232},
    "11638": {"name": "Ray Davis", "adp": 233},
    "11617": {"name": "Carson Beck", "adp": 234},
    "13420": {"name": "Kyle Williams", "adp": 235},
    "11602": {"name": "Malik Washington", "adp": 236},
    "11626": {"name": "Devin Neal", "adp": 237},
    "13425": {"name": "DJ Giddens", "adp": 238},
    "2449": {"name": "Stefon Diggs", "adp": 239},
    "13430": {"name": "Michael Trigg", "adp": 240},
    "11584": {"name": "Keon Coleman", "adp": 241},
    "13435": {"name": "Jaydon Blue", "adp": 242},
    "11618": {"name": "Jalen Milroe", "adp": 243},
    "11582": {"name": "Tre Tucker", "adp": 244},
    "8133": {"name": "Michael Mayer", "adp": 245},
    "7555": {"name": "Colby Parkinson", "adp": 246},
    "1166": {"name": "Kirk Cousins", "adp": 247},
    "6791": {"name": "Darnell Mooney", "adp": 248},
    "9512": {"name": "Dontayvion Wicks", "adp": 249},
    "13440": {"name": "Isaiah Bond", "adp": 250},
    "13445": {"name": "Le'Veon Moss", "adp": 251},
    "13450": {"name": "Kevin Coleman", "adp": 252},
    "11568": {"name": "Xavier Legette", "adp": 253},
    "13455": {"name": "LeQuint Allen", "adp": 254},
    "4199": {"name": "Christian Kirk", "adp": 255},
    "13460": {"name": "Cade Klubnik", "adp": 256},
    "11587": {"name": "Devaughn Vele", "adp": 257},
    "13465": {"name": "Tez Johnson", "adp": 258},
    "13470": {"name": "Jack Endries", "adp": 259},
    "13475": {"name": "Jam Miller", "adp": 260},
    "13480": {"name": "Brashard Smith", "adp": 261},
    "13485": {"name": "J'Mari Taylor", "adp": 262},
    "11621": {"name": "Riley Leonard", "adp": 263},
    "4018": {"name": "Najee Harris", "adp": 264},
}

# --- 3. FETCHING ENGINE ---
def fetch_live_picks():
    try:
        r = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks")
        return r.json() if r.status_code == 200 else []
    except: return []

# --- 4. THE INTERFACE ---
def run_war_room():
    picks = fetch_live_picks()
    current_pick = len(picks) + 1
    drafted_ids = {str(p.get('player_id')) for p in picks}

    with st.sidebar:
        st.header("🔍 Board Inspector")
        inspect = st.selectbox("Check Tracking Status:", ["-- Search --"] + [v['name'] for v in WAR_ROOM_DATA.values()])
        if inspect != "-- Search --":
            # Reverse lookup ID
            pid = next(k for k, v in WAR_ROOM_DATA.items() if v['name'] == inspect)
            status = "❌ DRAFTED" if pid in drafted_ids else "✅ AVAILABLE"
            st.write(f"**ID:** `{pid}`")
            st.write(f"**Rank:** `{WAR_ROOM_DATA[pid]['adp']}`")
            st.write(f"**Status:** {status}")

    st.title(f"🛡️ TizBos War Room | Pick {current_pick}")
    
    col_board, col_smash = st.columns([2, 1])

    with col_board:
        st.subheader("📊 Draft History")
        if picks:
            history = []
            for p in picks:
                history.append({
                    "Pick": p['pick_no'],
                    "Player": f"{p['metadata'].get('first_name')} {p['metadata'].get('last_name')}",
                    "Status": "✅ MINE" if str(p.get('picked_by')) == MY_USER_ID else "❌ GONE"
                })
            st.table(pd.DataFrame(history).iloc[::-1].head(15))
        else:
            st.info("Draft hasn't started yet.")

    with col_smash:
        st.subheader("🔥 Smash Alerts (+2 Target)")
        smashes = []
        
        # We loop through the 264 players
        for pid, data in WAR_ROOM_DATA.items():
            # If they are NOT in the drafted ID set, they are available
            if pid not in drafted_ids:
                # Trigger alert if the draft pick number is 2+ spots past their rank
                if current_pick >= (data['adp'] + 2):
                    smashes.append({
                        "Player": data['name'],
                        "Rank": data['adp'],
                        "Value": f"+{round(current_pick - data['adp'], 1)}"
                    })

        if smashes:
            st.success(f"VALUE DETECTED AT PICK {current_pick}")
            # Sort by biggest fall
            smash_df = pd.DataFrame(smashes).sort_values(by="Rank", ascending=True)
            st.dataframe(smash_df, hide_index=True)
        else:
            st.info("Market is currently efficient.")

# Execute and auto-refresh every 20s
run_war_room()
time.sleep(20)
st.rerun()
