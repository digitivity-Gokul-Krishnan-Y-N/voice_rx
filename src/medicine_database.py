"""
Medicine Database and Drug Interaction Registry
Comprehensive database of known drugs, dangerous combinations, and valid dose patterns
"""

import sqlite3
import os

# Drug database - comprehensive list across multiple categories
def _load_known_drugs():
    # Base hardcoded drugs
    drugs = {
        # Antibiotics
        'erythromycin', 'amoxicillin', 'amoxicillin-clavulanic acid', 'augmentin',
        'azithromycin', 'ciprofloxacin', 'levofloxacin', 'cephalexin', 'doxycycline',
        'metronidazole', 'norfloxacin', 'cefixime',
        
        # Analgesics & NSAIDs
        'paracetamol', 'acetaminophen', 'ibuprofen', 'aspirin', 'diclofenac',
        'naproxen', 'mefenamic acid', 'indomethacin',
        
        # Cough & Cold
        'cough syrup', 'dextromethorphan', 'promethazine', 'codeine', 'terbutaline',
        'levosalbutamol', 'salbutamol', 'albuterol', 'bromhexine', 'guaifenesin',
        
        # Antihistamines
        'antihistamine', 'cetirizine', 'loratadine', 'fexofenadine', 'meclizine',
        'chlorpheniramine', 'pheniramine', 'diphenhydramine',
        
        # Gastrointestinal
        'antacid', 'omeprazole', 'pantoprazole', 'ranitidine', 'famotidine',
        'domperidone', 'metoclopramide', 'ondansetron', 'loperamide',
        
        # Cardiovascular
        'lisinopril', 'enalapril', 'ramipril', 'amlodipine', 'nifedipine',
        'metoprolol', 'atenolol', 'bisoprolol', 'atorvastatin', 'simvastatin',
        'losartan', 'valsartan', 'spironolactone', 'furosemide', 'hydrochlorothiazide',
        
        # Antihistamine/Decongestant
        'phenylephrine', 'pseudoephedrine', 'oxymetazoline', 'xylometazoline',
        
        # Vitamins & Minerals
        'vitamin', 'vitamin-c', 'vitamin-d', 'vitamin-b12', 'calcium', 'iron', 'zinc',
        'multivitamin', 'ascorbic acid',
        
        # Antifungal
        'fluconazole', 'ketoconazole', 'miconazole', 'clotrimazole', 'terbinafine',
        
        # Antiinflammatory
        'corticosteroid', 'dexamethasone', 'methylprednisolone', 'prednisone',
        'hydrocortisone', 'betamethasone',
        
        # Respiratory
        'bronchodilator', 'inhaler', 'montelukast', 'theophylline',
        
        # Thyroid
        'levothyroxine', 'liothyronine',
        
        # Diabetes
        'metformin', 'glipizide', 'glyburide', 'sitagliptin', 'insulin',
        
        # Antibacterial Ointments
        'antibiotic ointment', 'neomycin', 'bacitracin', 'polymyxin',
        
        # Arabic transliterated medicines (for speech recognition)
        'aspireen', 'paracetal', 'amoxysilan', 'azithro', 'ciprofloxacine',
        'levoceti', 'omeprazol', 'domeperidone', 'levocetirizine',
    }
    
    # Try to load from SQLite database if available
    db_path = os.path.join(os.path.dirname(__file__), 'medicine_master.db')
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT Medicine FROM medicines")
            rows = cursor.fetchall()
            for row in rows:
                drugs.add(row[0].lower())
            conn.close()
        except Exception as e:
            print(f"Warning: Could not load medicines from database: {e}")
            
    return drugs

KNOWN_DRUGS = _load_known_drugs()

# Dangerous combinations - drugs that should not be prescribed together
DANGEROUS_COMBINATIONS = {
    ('aspirin', 'ibuprofen'): 'Both are NSAIDs - avoid together',
    ('ibuprofen', 'diclofenac'): 'Both are NSAIDs - avoid together',
    ('metoprolol', 'verapamil'): 'Both lower heart rate - high risk',
    ('atorvastatin', 'simvastatin'): 'Both are statins - avoid together',
    ('metformin', 'contrast dye'): 'Risk of kidney damage - avoid',
    ('lisinopril', 'potassium'): 'Risk of hyperkalemia - monitor',
    ('warfarin', 'aspirin'): 'Increased bleeding risk',
    ('fluconazole', 'cisapride'): 'Risk of QT prolongation',
}

# Valid dose patterns for validation
DOSE_PATTERNS = {
    'mg': r'\d+(?:\.\d+)?\s*mg',
    'ml': r'\d+(?:\.\d+)?\s*ml',
    'mcg': r'\d+(?:\.\d+)?\s*mcg',
    'gm': r'\d+(?:\.\d+)?\s*g(?:m|ram)?',
    'iu': r'\d+\s*iu',
    'tablet': r'\d+\s*tablet',
    'capsule': r'\d+\s*capsule',
    'drops': r'\d+\s*drops?',
    'units': r'\d+\s*units?',
}

# Drug name corrections - maps transcription errors to correct names
DRUG_CORRECTIONS = {
    # Pharyngitis variations
    r'\bfrangitis\b': 'pharyngitis',
    r'\bfrangi\b': 'pharyngitis',
    r'\bfrench\s+dices\b': 'pharyngitis',
    r'\bfiren\s+nets\b': 'pharyngitis',
    r'\bphyren\w*\b': 'pharyngitis',
    r'\bfirennets\b': 'pharyngitis',
    r'\bfaryng\w*\b': 'pharyngitis',
    # Antibiotic names
    r'\berytho\s+mice\s+in\b': 'erythromycin',
    r'\berytho(?!mycin)\b': 'erythromycin',  # Avoid double replacement
    r'\berito\b': 'erythromycin',  # Transcription: "erito" -> erythromycin
    r'\bmaisin\b': 'erythromycin',  # Transcription: "maisin" -> erythromycin (likely part of "erito maisin")
    r'\barithromycin\b': 'erythromycin',
    r'\berythromicin\b': 'erythromycin',
    r'\berithromycin\b': 'erythromycin',
    r'\bamoxycillin\b': 'amoxicillin',
    r'\bampicillin\b': 'amoxicillin',
    r'\baugmentin\b': 'amoxicillin-clavulanic acid',
    # More antibiotic variations
    r'\bazithro\w*\b': 'azithromycin',
    r'\bcipro\w*\b': 'ciprofloxacin',
    r'\blevoflox\w*\b': 'levofloxacin',
    r'\blevocet\w*\b': 'levocetirizine',
    r'\blevosid\w*\b': 'levocetirizine',
    r'\bcephalex\w*\b': 'cephalexin',
    r'\bdoxyc\w*\b': 'doxycycline',
    r'\bmetro\w*\b': 'metronidazole',
    # Analgesic variations
    r'\bpraceta\w*\b': 'paracetamol',
    r'\bacetamin\w*\b': 'acetaminophen',
    r'\bibupr\w*\b': 'ibuprofen',
    # New medicines mentions
    r'\bbenzid\w*\b': 'benzydamine',
    r'\bbenzodiazine\b': 'benzydamine',
    r'\btrepsil\w*\b': 'strepsils',
    r'\blozenge\w*\b': 'throat lozenges',
    r'\bvitamin\s+c\b': 'vitamin c',
    r'\bzinc\b': 'zinc supplement',
    r'\bdic\w*\b': 'diclofenac',
    # Cough syrup variations
    r'\bterbutal\w*\b': 'terbutaline',
    r'\bsalbutam\w*\b': 'salbutamol',
    r'\blevosalb\w*\b': 'levosalbutamol',
    r'\bbrohmex\w*\b': 'bromhexine',
    # Antihistamine variations
    r'\bcetir\w*\b': 'cetirizine',
    r'\blora\w*\b': 'loratadine',
    r'\bfexof\w*\b': 'fexofenadine',
    # Cardiovascular variations
    r'\bamlod\w*\b': 'amlodipine',
    r'\bangioten\w*\b': 'angiotensin inhibitor',
    r'\bstatin\b': 'statin',
    # GI variations
    r'\bomepr\w*\b': 'omeprazole',
    r'\bpanto\w*\b': 'pantoprazole',
    r'\bromep\w*\b': 'omeprazole',
    r'\bdomper\w*\b': 'domperidone',
    # Transcription artifacts
    r'\byear-layer\b': '',
    r'\buaz\b': 'your',
    r'\bprescuring\b': 'prescribing',
    r'\balgeric\b': 'allergic',
    r'\bdiarrhea\b': 'diarrhea',
    r'\bacute\s+fr\w*': 'acute pharyngitis',
    r'\binflamm\w*': 'inflammation',
}

# Complaint keywords mapping
COMPLAINT_KEYWORDS = {
    ('difficulty breathing', 'difficulty breathing', 1),
    ('difficulty swallowing', 'difficulty swallowing', 1),
    ('throat pain', 'throat pain', 2),
    ('fever', 'fever', 2),
    ('cough', 'cough', 2),
    ('infection', 'infection', 3),
    ('discomfort', 'discomfort', 3),
    ('pain', 'pain', 3),  # Generic - lowest priority
}

# Diagnosis keywords mapping
DIAGNOSIS_KEYWORDS = {
    ('pharyngitis', 'acute pharyngitis', 1),
    ('bacterial throat infection', 'bacterial throat infection', 1),
    ('throat infection', 'bacterial throat infection', 1),  # Map to more specific
    ('bacterial infection', 'bacterial infection', 2),
    ('infection', 'infection', 3),  # Generic - lowest priority
}

# Standard medical advice phrases (for throat/infection conditions)
STANDARD_ADVICE = [
    "Take medicine after food to avoid stomach discomfort",
    "Complete the full 5 day course if prescribed antibiotics",
    "Drink plenty of warm fluids",
    "Do warm salt water gargles 3-4 times a day",
    "Avoid very cold drinks",
    "Avoid spicy food",
    "Avoid oily food",
    "Rest your voice as much as possible",
    "Watch for side effects like nausea, loose stools, or stomach upset",
    "Contact doctor if you develop severe diarrhea, vomiting, skin rash, itching, swelling, or difficulty breathing",
    "Come for review follow up after 5 days or earlier if symptoms do not improve",
    "If fever persists beyond 2-3 days or if you have difficulty swallowing or breathing, seek medical attention",
]

# Advice mapping - keywords in transcript to advice indices
ADVICE_MAPPING = {
    0: ['food', 'stomach', 'discomfort', 'after food'],
    1: ['course', 'complete'],
    2: ['drink', 'plenty', 'warm'],
    3: ['gargle'],
    4: ['cold', 'drink'],
    5: ['spicy', 'food'],
    6: ['oily', 'food'],
    7: ['rest', 'voice'],
    8: ['side effect', 'nausea'],
    9: ['severe', 'diarrhea'],
    10: ['follow', 'review'],
    11: ['fever', 'persist'],
}

__all__ = [
    'KNOWN_DRUGS',
    'DANGEROUS_COMBINATIONS',
    'DOSE_PATTERNS',
    'DRUG_CORRECTIONS',
    'COMPLAINT_KEYWORDS',
    'DIAGNOSIS_KEYWORDS',
    'STANDARD_ADVICE',
    'ADVICE_MAPPING',
]
