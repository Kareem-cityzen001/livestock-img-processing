"""
Livestock Disease Detection - Disease Information Guide
Includes symptoms, detection tips, and treatment recommendations
"""

DISEASE_DATABASE = {
    "Healthy": {
        "description": "No disease detected. Animal appears healthy.",
        "symptoms": ["Normal movement", "Clear eyes", "Good appetite", "Smooth coat"],
        "severity": "None",
        "actions": ["Continue regular monitoring", "Maintain good hygiene", "Provide balanced nutrition"],
        "prevention": ["Regular health checks", "Vaccination programs", "Proper sanitation"]
    },
    
    "Lumpy Skin Disease": {
        "description": "Viral disease causing painful nodules on skin and mucous membranes",
        "symptoms": [
            "Firm nodules on skin (1-5cm diameter)",
            "Raised lesions on nose, lips, gums",
            "Fever (40-41°C)",
            "Enlarged lymph nodes",
            "Nasal and ocular discharge",
            "Swollen legs",
            "Reduced milk production"
        ],
        "severity": "HIGH",
        "actions": [
            "ISOLATE IMMEDIATELY",
            "Report to veterinary authorities",
            "Contact veterinarian urgently",
            "Implement strict quarantine",
            "Disinfect facilities"
        ],
        "treatment": [
            "Supportive care (fluids, nutrition)",
            "Antibiotics for secondary infections",
            "Pain relief",
            "Wound care with antiseptics",
            "Vaccination if not infected"
        ],
        "transmission": "Insect vectors (flies, mosquitoes, ticks)",
        "duration": "2-4 weeks",
        "mortality": "Low (1-5%) but high morbidity"
    },
    
    "Foot Rot": {
        "description": "Bacterial infection of the foot causing lameness and hoof deterioration",
        "symptoms": [
            "Severe lameness",
            "Swelling between hooves",
            "Foul-smelling discharge",
            "Reluctance to move",
            "Affected animals isolate from group",
            "Weight loss",
            "Elevated temperature (localized)"
        ],
        "severity": "MEDIUM",
        "actions": [
            "Separate affected animals",
            "Trim and clean affected hooves",
            "Use therapeutic foot baths",
            "Dry the hoof area",
            "Monitor other animals"
        ],
        "treatment": [
            "Footbath with copper sulfate or iodine (7-10 days)",
            "Systemic antibiotics (tetracycline, penicillin)",
            "Hoof trimming and cleaning",
            "Pain management",
            "Topical antiseptic dressings",
            "Rest and clean housing"
        ],
        "transmission": "Direct contact with infected hooves, contaminated bedding",
        "duration": "1-3 weeks with treatment",
        "prevention": [
            "Regular foot care",
            "Maintain dry conditions",
            "Periodic footbaths",
            "Good sanitation"
        ]
    },
    
    "Mastitis": {
        "description": "Inflammation of the udder/mammary gland, common in dairy cattle",
        "symptoms": [
            "Swollen, hot, painful udder",
            "Soft or firm lumps in udder",
            "Abnormal milk (watery, clotted, bloody)",
            "Elevated body temperature",
            "Reduced milk production",
            "Loss of appetite",
            "Behavioral changes"
        ],
        "severity": "MEDIUM",
        "actions": [
            "Consult veterinarian",
            "Test milk composition",
            "Implement immediate treatment",
            "Monitor milk production",
            "Maintain hygiene"
        ],
        "treatment": [
            "Antibiotics (intramammary or systemic)",
            "Anti-inflammatory drugs",
            "Frequent milking/draining",
            "Cold compress application",
            "Supportive care (fluids, nutrition)",
            "Culture and sensitivity testing"
        ],
        "types": [
            "Acute Mastitis - sudden onset",
            "Chronic Mastitis - recurring",
            "Subclinical Mastitis - no visible signs"
        ],
        "transmission": "Bacteria, poor milking hygiene, contaminated equipment",
        "prevention": [
            "Proper milking hygiene",
            "Clean equipment",
            "Post-milking teat dipping",
            "Dry cow therapy",
            "Regular udder health monitoring"
        ]
    },
    
    "Blackleg": {
        "description": "Acute, rapidly fatal bacterial disease (Clostridium chauvoei)",
        "symptoms": [
            "Sudden onset of high fever (41-42°C)",
            "Dark, swollen muscles (blackening)",
            "Severe lameness or reluctance to move",
            "Emphysema (crepitus) - gas in tissues",
            "Rapid weakness",
            "Death often occurs within 48 hours"
        ],
        "severity": "CRITICAL",
        "actions": [
            "IMMEDIATE VETERINARY ATTENTION",
            "Isolate animal immediately",
            "Do not move infected animal",
            "Disinfect equipment and facilities",
            "Vaccinate remaining herd urgently"
        ],
        "treatment": [
            "High-dose antibiotics (if caught VERY early)",
            "IV fluids",
            "Pain management",
            "Supportive care",
            "Often fatal despite treatment"
        ],
        "mortality": "90%+ without vaccination",
        "transmission": "Soil-borne spores via minor cuts or wounds",
        "prevention": [
            "VACCINATION (most effective prevention)",
            "Regular revaccination",
            "Booster shots for young animals",
            "Avoid wounds/injections with contaminated equipment"
        ]
    },
    
    "Anthrax Disease": {
        "description": "Acute, highly dangerous zoonotic disease (Bacillus anthracis)",
        "symptoms": [
            "Sudden high fever (40-42°C)",
            "Rapid collapse",
            "Blood from natural orifices",
            "Gaseous swelling of carcass",
            "Pulmonary edema",
            "Rapid death (12-48 hours)"
        ],
        "severity": "CRITICAL",
        "actions": [
            "REPORT TO AUTHORITIES IMMEDIATELY",
            "Do not open carcass",
            "Complete animal quarantine",
            "Restrict all movement",
            "Call public health authorities",
            "Do not handle carcass directly"
        ],
        "treatment": [
            "No practical treatment possible",
            "May respond to antibiotics IF caught very early",
            "Supportive care only"
        ],
        "transmission": "Spores in soil, very dangerous to humans (zoonotic)",
        "public_health": "EXTREMELY SERIOUS - NOTIFIABLE DISEASE",
        "prevention": [
            "Animal vaccination",
            "Proper carcass disposal (incinerate, deep bury)",
            "Decontamination of facilities",
            "Personnel protection (gloves, masks)"
        ],
        "mortality": "Near 100% without treatment"
    },
    
    "Tick-Borne Fever": {
        "description": "Rickettsial disease transmitted by ticks (Anaplasma phagocytophilum)",
        "symptoms": [
            "High fever (40-41°C)",
            "Lack of appetite",
            "Depression and lethargy",
            "Reduced milk production",
            "Weight loss",
            "Dehydration",
            "Diarrhea (sometimes)",
            "Abortion in pregnant animals"
        ],
        "severity": "MEDIUM",
        "actions": [
            "Consult veterinarian",
            "Implement tick control",
            "Monitor for complications",
            "Provide supportive care",
            "Blood testing for confirmation"
        ],
        "treatment": [
            "Tetracycline or doxycycline (most effective)",
            "Chloramphenicol (alternative)",
            "Supportive care (fluids, nutrition)",
            "Recovery typically 1-3 weeks"
        ],
        "transmission": "Tick vectors (Ixodes species), no direct animal-to-animal transmission",
        "season": "Higher in spring/summer (tick season)",
        "prevention": [
            "Regular tick control programs",
            "Environmental management (reduce tick habitat)",
            "Pasture rotation",
            "Chemical tick treatments",
            "Early removal of ticks"
        ]
    }
}

def print_disease_info(disease_name):
    """Print detailed information about a specific disease."""
    if disease_name not in DISEASE_DATABASE:
        print(f"Disease '{disease_name}' not found in database")
        return
    
    disease = DISEASE_DATABASE[disease_name]
    
    print(f"\n{'='*70}")
    print(f"DISEASE: {disease_name.upper()}")
    print(f"{'='*70}")
    
    print(f"\nDescription: {disease.get('description', 'N/A')}")
    
    if "severity" in disease:
        print(f"Severity: {disease['severity']}")
    
    if "symptoms" in disease:
        print(f"\nSymptoms:")
        for symptom in disease['symptoms']:
            print(f"  • {symptom}")
    
    if "actions" in disease:
        print(f"\nImmediate Actions:")
        for action in disease['actions']:
            print(f"  • {action}")
    
    if "treatment" in disease:
        print(f"\nTreatment:")
        for treatment in disease['treatment']:
            print(f"  • {treatment}")
    
    if "transmission" in disease:
        print(f"\nTransmission: {disease['transmission']}")
    
    if "prevention" in disease:
        print(f"\nPrevention:")
        for prevention in disease['prevention']:
            print(f"  • {prevention}")
    
    if "mortality" in disease:
        print(f"\nMortality Rate: {disease['mortality']}")
    
    if "types" in disease:
        print(f"\nTypes:")
        for disease_type in disease['types']:
            print(f"  • {disease_type}")
    
    print(f"\n{'='*70}\n")

def print_all_diseases():
    """Print information about all supported diseases."""
    diseases = list(DISEASE_DATABASE.keys())
    print(f"\n{'='*70}")
    print("SUPPORTED LIVESTOCK DISEASES")
    print(f"{'='*70}\n")
    for i, disease in enumerate(diseases, 1):
        print(f"{i}. {disease}")
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    import sys
    
    print("\nLIVESTOCK DISEASE INFORMATION DATABASE")
    print("="*70)
    
    if len(sys.argv) > 1:
        disease_name = " ".join(sys.argv[1:])
        print_disease_info(disease_name)
    else:
        print_all_diseases()
        print("Usage: python disease_info.py <disease_name>")
        print("Example: python disease_info.py \"Lumpy Skin Disease\"")
