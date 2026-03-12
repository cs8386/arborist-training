"""Pre-built arborist trainings - ISA, ANSI Z133, OSHA Crane, categorized."""
import sqlite3

SEED_TRAININGS = [
    # ========== ANSI Z133 - SAFETY EQUIPMENT ==========
    {"title": "PPE Requirements for Arborists", "description": "Personal protective equipment per ANSI Z133.", "standard": "ANSI_Z133", "category": "Safety Equipment", "topics": "hard hats, eye protection, hearing, chainsaw pants, boots, gloves"},
    {"title": "Chain Saw PPE and Clothing", "description": "Cut-resistant legwear and upper body protection.", "standard": "ANSI_Z133", "category": "Safety Equipment", "topics": "chainsaw pants, chaps, jackets, ASTM standards"},
    {"title": "Head, Eye, and Hearing Protection", "description": "ANSI Z133 requirements for head, eye, and ear protection.", "standard": "ANSI_Z133", "category": "Safety Equipment", "topics": "hard hats, face shields, safety glasses, hearing protection"},
    {"title": "Fall Protection and Harnesses", "description": "Climbing harness fit, inspection, and fall protection.", "standard": "ANSI_Z133", "category": "Safety Equipment", "topics": "harness fit, D-rings, lanyards, inspection"},
    # ========== ANSI Z133 - ELECTRICAL ==========
    {"title": "Electrical Hazard Awareness", "description": "Minimum approach distances and electrical safety.", "standard": "ANSI_Z133", "category": "Electrical Hazards", "topics": "MAD, power line proximity, electrical hazards, spotting"},
    {"title": "Line Clearance and MAD", "description": "Minimum approach distances for energized lines.", "standard": "ANSI_Z133", "category": "Electrical Hazards", "topics": "voltage levels, MAD tables, qualified line-clearance arborist"},
    {"title": "Electrical Spotter Duties", "description": "Role and responsibilities of the electrical spotter.", "standard": "ANSI_Z133", "category": "Electrical Hazards", "topics": "spotter training, communication, when to stop work"},
    {"title": "Working Near Power Lines", "description": "Procedures when operating equipment near energized conductors.", "standard": "ANSI_Z133", "category": "Electrical Hazards", "topics": "equipment positioning, conductive materials, emergency procedures"},
    # ========== ANSI Z133 - CHAIN SAWS & TOOLS ==========
    {"title": "Chain Saw Safety and Maintenance", "description": "Safe operation and maintenance of chain saws.", "standard": "ANSI_Z133", "category": "Equipment Operations", "topics": "PPE, kickback prevention, maintenance, sharpening, fuel handling"},
    {"title": "Chain Saw Kickback Prevention", "description": "Understanding and preventing kickback incidents.", "standard": "ANSI_Z133", "category": "Equipment Operations", "topics": "kickback zones, reactive forces, safe handling"},
    {"title": "Pole Saw and Pole Pruner Safety", "description": "Safe use of pole saws and pole pruners.", "standard": "ANSI_Z133", "category": "Equipment Operations", "topics": "electrical clearance, positioning, maintenance"},
    {"title": "Hand Tool Safety", "description": "Safe use of hand saws, loppers, and pruning tools.", "standard": "ANSI_Z133", "category": "Equipment Operations", "topics": "cutting techniques, sharp tools, handling"},
    # ========== ANSI Z133 - CHIPPERS & STUMP CUTTERS ==========
    {"title": "Chipper Safety", "description": "Safe operation of wood chippers per ANSI Z133.", "standard": "ANSI_Z133", "category": "Equipment Operations", "topics": "chipper operation, feeding, kickback, emergency stop"},
    {"title": "Stump Cutter Safety", "description": "Safe operation of stump cutters.", "standard": "ANSI_Z133", "category": "Equipment Operations", "topics": "stump cutter hazards, PPE, positioning, guards"},
    {"title": "Chipper Feeding Techniques", "description": "Proper feeding procedures and hazard avoidance.", "standard": "ANSI_Z133", "category": "Equipment Operations", "topics": "feeding from side, branch size, jam clearance"},
    # ========== ANSI Z133 - CLIMBING & AERIAL ==========
    {"title": "Climbing and Aerial Operations", "description": "Safe climbing techniques and rope work.", "standard": "ANSI_Z133", "category": "Climbing & Aerial", "topics": "climbing systems, work positioning, TIP selection, aerial rescue"},
    {"title": "Work Positioning and Suspension", "description": "Safe work positioning in the canopy.", "standard": "ANSI_Z133", "category": "Climbing & Aerial", "topics": "straddle position, lanyard use, suspension trauma"},
    {"title": "Aerial Rescue Procedures", "description": "Emergency procedures for injured climbers.", "standard": "ANSI_Z133", "category": "Climbing & Aerial", "topics": "rescue plan, lowering systems, first responder coordination"},
    {"title": "TIP Selection and Anchor Points", "description": "Choosing safe tie-in points in the tree.", "standard": "ANSI_Z133", "category": "Climbing & Aerial", "topics": "structural integrity, redundancy, load testing"},
    # ========== ANSI Z133 - RIGGING ==========
    {"title": "Rigging and Lowering Operations", "description": "Rigging hardware and safe lowering procedures.", "standard": "ANSI_Z133", "category": "Rigging", "topics": "rigging hardware, slings, friction devices, load control"},
    {"title": "Rigging Hardware and Slings", "description": "Selection, inspection, and use of rigging equipment.", "standard": "ANSI_Z133", "category": "Rigging", "topics": "blocks, slings, carabiners, working load limits"},
    {"title": "Negative Rigging and Shock Load", "description": "Controlled lowering and shock load prevention.", "standard": "ANSI_Z133", "category": "Rigging", "topics": "negative rigging, shock load, friction devices"},
    {"title": "Load Calculations for Rigging", "description": "Estimating branch weight and rigging loads.", "standard": "ANSI_Z133", "category": "Rigging", "topics": "weight estimation, leverage, force multipliers"},
    # ========== ANSI Z133 - TREE REMOVAL ==========
    {"title": "Tree Removal Procedures", "description": "Planning and executing safe tree removal.", "standard": "ANSI_Z133", "category": "Tree Removal", "topics": "escape routes, drop zones, felling, sectioning"},
    {"title": "Felling and Limbing", "description": "Safe felling cuts and limbing procedures.", "standard": "ANSI_Z133", "category": "Tree Removal", "topics": "notch, back cut, hinge, limbing sequence"},
    {"title": "Sectional Removal and Dismantling", "description": "Removing trees in sections when felling is not possible.", "standard": "ANSI_Z133", "category": "Tree Removal", "topics": "climb and section, rigging, crane-assisted"},
    {"title": "Escape Routes and Drop Zones", "description": "Establishing safe zones during removal.", "standard": "ANSI_Z133", "category": "Tree Removal", "topics": "escape routes, drop zone clearing, communication"},
    # ========== ANSI Z133 - WORKSITE ==========
    {"title": "Traffic Control and Worksite Safety", "description": "Work zones and traffic management.", "standard": "ANSI_Z133", "category": "Worksite Safety", "topics": "work zone setup, signage, flaggers, pedestrian safety"},
    {"title": "First Aid and Emergency Procedures", "description": "First aid and emergency response for arboriculture.", "standard": "ANSI_Z133", "category": "Worksite Safety", "topics": "first aid kit, bloodborne pathogens, emergency contacts"},
    {"title": "Job Site Hazard Assessment", "description": "Pre-job site assessment and hazard identification.", "standard": "ANSI_Z133", "category": "Worksite Safety", "topics": "JSA, hazard identification, mitigation"},
    # ========== ISA - RISK ASSESSMENT ==========
    {"title": "Tree Risk Assessment", "description": "Evaluating tree defects and failure risk.", "standard": "ISA", "category": "Risk Assessment", "topics": "defect identification, target assessment, risk rating, reporting"},
    {"title": "Tree Defect Identification", "description": "Recognizing structural defects and decay.", "standard": "ISA", "category": "Risk Assessment", "topics": "cavities, cracks, included bark, root decay"},
    {"title": "Target Assessment", "description": "Identifying and rating targets in the impact zone.", "standard": "ISA", "category": "Risk Assessment", "topics": "target types, occupancy, consequence rating"},
    {"title": "Tree Risk Assessment Report Writing", "description": "Documenting and communicating risk assessment findings.", "standard": "ISA", "category": "Risk Assessment", "topics": "report format, mitigation options, liability"},
    # ========== ISA - PRUNING ==========
    {"title": "Pruning Best Practices", "description": "ANSI A300 pruning standards and techniques.", "standard": "ISA", "category": "Pruning", "topics": "crown cleaning, thinning, reduction, structural pruning"},
    {"title": "Structural Pruning", "description": "Developing strong tree structure in young trees.", "standard": "ISA", "category": "Pruning", "topics": "central leader, scaffold selection, subordinate pruning"},
    {"title": "Crown Cleaning and Deadwood Removal", "description": "Removing dead, diseased, and broken branches.", "standard": "ISA", "category": "Pruning", "topics": "crown cleaning, branch collar, proper cuts"},
    {"title": "Crown Thinning and Reduction", "description": "Thinning and reduction pruning per ANSI A300.", "standard": "ISA", "category": "Pruning", "topics": "percent removal, storm resistance, aesthetic pruning"},
    {"title": "Topping and Lion-Tailing", "description": "Why these practices are harmful and alternatives.", "standard": "ISA", "category": "Pruning", "topics": "topping effects, lion-tailing, proper alternatives"},
    # ========== ISA - TREE BIOLOGY ==========
    {"title": "Tree Biology and Identification", "description": "Tree structure, function, and species ID.", "standard": "ISA", "category": "Tree Biology", "topics": "tree anatomy, growth, species identification, site assessment"},
    {"title": "Tree Structure and Compartmentalization", "description": "How trees respond to injury and decay.", "standard": "ISA", "category": "Tree Biology", "topics": "CODIT, compartmentalization, wound response"},
    {"title": "Root Systems and Root Function", "description": "Root biology and implications for tree care.", "standard": "ISA", "category": "Tree Biology", "topics": "root architecture, absorption, structural roots"},
    {"title": "Tree Species Selection", "description": "Selecting the right tree for the right place.", "standard": "ISA", "category": "Tree Biology", "topics": "site conditions, mature size, pest resistance"},
    # ========== ISA - PLANTING ==========
    {"title": "Planting and Establishment", "description": "Proper tree planting and early care.", "standard": "ISA", "category": "Planting", "topics": "site selection, planting depth, mulching, staking, irrigation"},
    {"title": "Bare-Root and B&B Planting", "description": "Planting techniques for different stock types.", "standard": "ISA", "category": "Planting", "topics": "bare-root, B&B, container, root ball handling"},
    {"title": "Tree Staking and Guying", "description": "When and how to stake newly planted trees.", "standard": "ISA", "category": "Planting", "topics": "staking criteria, guying, removal timing"},
    {"title": "Mulching and Weed Management", "description": "Mulch application and weed control for establishment.", "standard": "ISA", "category": "Planting", "topics": "mulch depth, volcano mulching, weed barriers"},
    # ========== ISA - SOIL & ROOTS ==========
    {"title": "Soil Management and Root Care", "description": "Soil assessment and root zone management.", "standard": "ISA", "category": "Soil & Roots", "topics": "compaction, aeration, root pruning, fertilization"},
    {"title": "Soil Compaction and Remediation", "description": "Identifying and addressing soil compaction.", "standard": "ISA", "category": "Soil & Roots", "topics": "compaction effects, aeration, radial trenching"},
    {"title": "Root Pruning and Root Zone Management", "description": "When and how to prune roots.", "standard": "ISA", "category": "Soil & Roots", "topics": "root pruning guidelines, construction impacts"},
    {"title": "Tree Fertilization", "description": "Fertilization strategies for urban trees.", "standard": "ISA", "category": "Soil & Roots", "topics": "soil testing, nutrient deficiencies, application methods"},
    # ========== ISA - PEST MANAGEMENT ==========
    {"title": "Integrated Pest Management", "description": "IPM principles for tree care.", "standard": "ISA", "category": "Pest Management", "topics": "monitoring, thresholds, cultural controls, pesticides"},
    {"title": "Insect Pests of Trees", "description": "Common insect pests and management.", "standard": "ISA", "category": "Pest Management", "topics": "borers, defoliators, scale, identification"},
    {"title": "Tree Diseases", "description": "Fungal, bacterial, and viral diseases of trees.", "standard": "ISA", "category": "Pest Management", "topics": "disease identification, prevention, treatment"},
    {"title": "Invasive Species Management", "description": "Identifying and managing invasive plants and pests.", "standard": "ISA", "category": "Pest Management", "topics": "invasive species, EAB, oak wilt"},
    # ========== ISA - URBAN FORESTRY ==========
    {"title": "Urban Forestry Fundamentals", "description": "Managing trees in the urban environment.", "standard": "ISA", "category": "Urban Forestry", "topics": "urban stress, soil volume, conflicts"},
    {"title": "Construction and Tree Protection", "description": "Protecting trees during construction.", "standard": "ISA", "category": "Urban Forestry", "topics": "tree protection zones, fencing, root protection"},
    # ========== OSHA CRANE - POWER LINE SAFETY ==========
    {"title": "Crane and Derrick Power Line Safety", "description": "Power line safety for cranes in construction.", "standard": "OSHA_CRANE", "category": "Power Line Safety", "topics": "10-foot rule, 20-foot rule, encroachment, qualified person"},
    {"title": "Power Line Proximity and Encroachment", "description": "Procedures when working near energized lines.", "standard": "OSHA_CRANE", "category": "Power Line Safety", "topics": "encroachment prevention, de-energizing, barricades"},
    {"title": "Electrocution Hazard Awareness", "description": "Understanding electrocution risks with cranes.", "standard": "OSHA_CRANE", "category": "Power Line Safety", "topics": "contact, step potential, arc flash"},
    # ========== OSHA CRANE - INSPECTIONS ==========
    {"title": "Crane Pre-Use Inspection", "description": "Daily and periodic inspection requirements.", "standard": "OSHA_CRANE", "category": "Inspections", "topics": "daily inspection, periodic inspection, documentation, out-of-service"},
    {"title": "Wire Rope and Rigging Inspection", "description": "Inspecting wire rope and rigging components.", "standard": "OSHA_CRANE", "category": "Inspections", "topics": "broken wires, wear, replacement criteria"},
    {"title": "Crane Maintenance and Records", "description": "Maintenance requirements and recordkeeping.", "standard": "OSHA_CRANE", "category": "Inspections", "topics": "maintenance schedule, repair documentation"},
    # ========== OSHA CRANE - LOAD OPERATIONS ==========
    {"title": "Load Charts and Capacity", "description": "Understanding and applying load charts.", "standard": "OSHA_CRANE", "category": "Load Operations", "topics": "load charts, capacity, radius, boom angle, load calculation"},
    {"title": "Load Handling and Rigging", "description": "Rigging loads for crane operations.", "standard": "OSHA_CRANE", "category": "Load Operations", "topics": "slings, hardware, load control, tag lines"},
    {"title": "Lifting Personnel with Cranes", "description": "Requirements for personnel platforms.", "standard": "OSHA_CRANE", "category": "Load Operations", "topics": "personnel platform, fall protection, communication"},
    # ========== OSHA CRANE - QUALIFICATIONS ==========
    {"title": "Qualified Signal Person Requirements", "description": "Hand signals and signal person qualification.", "standard": "OSHA_CRANE", "category": "Qualifications", "topics": "hand signals, qualification, direct vs. indirect contact, radio"},
    {"title": "Rigger and Operator Qualifications", "description": "Training for riggers and crane operators.", "standard": "OSHA_CRANE", "category": "Qualifications", "topics": "rigger certification, operator qualification, documentation"},
    {"title": "Competent Person and Qualified Person", "description": "Roles of competent and qualified persons.", "standard": "OSHA_CRANE", "category": "Qualifications", "topics": "definitions, responsibilities, training"},
    # ========== OSHA CRANE - ASSEMBLY & GROUND ==========
    {"title": "Crane Assembly and Disassembly", "description": "Safe assembly and disassembly procedures.", "standard": "OSHA_CRANE", "category": "Assembly & Ground", "topics": "assembly plan, pinning, stability during assembly"},
    {"title": "Ground Conditions and Stability", "description": "Supporting surface and crane stability.", "standard": "OSHA_CRANE", "category": "Assembly & Ground", "topics": "ground bearing pressure, mats, outriggers"},
    {"title": "Swing Radius and Crush Hazards", "description": "Hazards in the crane swing radius.", "standard": "OSHA_CRANE", "category": "Assembly & Ground", "topics": "swing radius, barricades, crush prevention"},
    # ========== OSHA CRANE - SIGNALS ==========
    {"title": "Hand Signals for Cranes", "description": "Standard hand signals per OSHA/ASME.", "standard": "OSHA_CRANE", "category": "Signals & Communication", "topics": "hoist, lower, swing, stop, standard signals"},
    {"title": "Radio and Communication Procedures", "description": "Radio communication for crane operations.", "standard": "OSHA_CRANE", "category": "Signals & Communication", "topics": "radio protocols, clarity, backup signals"},
]

# Deep Dive trainings (2-4 hours, ~30 slides)
DEEP_DIVE_TRAININGS = [
    {"title": "ANSI Z133 Complete Safety Deep Dive", "description": "Full 2-4 hour training covering all ANSI Z133 requirements.", "standard": "ANSI_Z133", "category": "Deep Dive", "format": "deep_dive", "topics": "PPE, electrical, climbing, rigging, chippers, tree removal, worksite safety"},
    {"title": "Tree Anatomy Deep Dive", "description": "Comprehensive 2-4 hour training on tree structure, function, and biology.", "standard": "ISA", "category": "Deep Dive", "format": "deep_dive", "topics": "wood structure, bark, cambium, roots, compartmentalization, growth patterns"},
    {"title": "Knuckle Boom Crane Operations Deep Dive", "description": "Full training on knuckle boom/articulating crane safety and operations for arboriculture.", "standard": "OSHA_CRANE", "category": "Deep Dive", "format": "deep_dive", "topics": "articulating boom, grapple saws, load-moment systems, power lines, load charts, operator certification, hand signals"},
]

# Category order for display
CATEGORY_ORDER = [
    "Safety Equipment", "Electrical Hazards", "Equipment Operations", "Climbing & Aerial", "Rigging",
    "Tree Removal", "Worksite Safety",
    "Risk Assessment", "Pruning", "Tree Biology", "Planting", "Soil & Roots", "Pest Management", "Urban Forestry",
    "Power Line Safety", "Inspections", "Load Operations", "Qualifications", "Assembly & Ground", "Signals & Communication",
]


def seed_trainings(conn: sqlite3.Connection) -> int:
    """Insert seed trainings if table is empty."""
    cur = conn.execute("SELECT COUNT(*) FROM trainings")
    if cur.fetchone()[0] > 0:
        return 0
    for t in SEED_TRAININGS:
        _insert_one(conn, t)
    for t in DEEP_DIVE_TRAININGS:
        _insert_one(conn, t)
    conn.commit()
    return len(SEED_TRAININGS) + len(DEEP_DIVE_TRAININGS)


def add_sample_trainings(conn: sqlite3.Connection) -> int:
    """Add sample trainings (skip if title already exists)."""
    added = 0
    for t in SEED_TRAININGS + DEEP_DIVE_TRAININGS:
        cur = conn.execute("SELECT id FROM trainings WHERE title = ?", (t["title"],))
        if cur.fetchone() is None:
            _insert_one(conn, t)
            added += 1
    conn.commit()
    return added


def _insert_one(conn: sqlite3.Connection, t: dict):
    fmt = t.get("format", "standard")
    cols = ["title", "description", "standard", "category", "format", "topics"]
    conn.execute(
        f"""INSERT INTO trainings ({", ".join(cols)}) VALUES (?, ?, ?, ?, ?, ?)""",
        (t["title"], t["description"], t["standard"], t.get("category", ""), fmt, t["topics"]),
    )
