import os
import random
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ------------------------------------------------------------------
# OUTPUT DIRECTORY
# ------------------------------------------------------------------
BASE_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "report",
    "reports"
)
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------------
# FONT PATH (CORRECT)
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # points to /src

FONT_DIR = BASE_DIR  # fonts are directly inside src/

pdfmetrics.registerFont(
    TTFont("Devanagari", os.path.join(FONT_DIR, "NotoSansDevanagari-Regular.ttf"))
)

pdfmetrics.registerFont(
    TTFont("Bengali", os.path.join(FONT_DIR, "NotoSansBengali-Regular.ttf"))
)

# ------------------------------------------------------------------
# TRANSLATIONS & LABELS
# ------------------------------------------------------------------
RAW_LABELS = {
    'English': {
        'Hospital': 'GOVERNMENT GENERAL HOSPITAL',
        'Title_LIVER': 'LIVER FUNCTION TEST REPORT',
        'Title_KIDNEY': 'KIDNEY FUNCTION TEST REPORT (KFT)',
        'Title_BLOOD': 'COMPLETE BLOOD COUNT (CBC)',
        'Name': 'Patient Name',
        'AgeSex': 'Age/Sex',
        'ID': 'Patient ID',
        'Date': 'Date',
        'Col_Test': 'TEST',
        'Col_Result': 'RESULT',
        'Col_Unit': 'UNITS',
        'Col_Ref': 'REFERENCE RANGE',
        'Test_Names': {} # English is the key, no translation needed
    },
    'Spanish': {
        'Hospital': 'HOSPITAL GENERAL DEL GOBIERNO',
        'Title_LIVER': 'INFORME DE PRUEBA DE FUNCIÓN HEPÁTICA',
        'Title_KIDNEY': 'INFORME DE PRUEBA DE FUNCIÓN RENAL (KFT)',
        'Title_BLOOD': 'HEMOGRAMA COMPLETO (CBC)',
        'Name': 'Nombre del Paciente',
        'AgeSex': 'Edad/Sexo',
        'ID': 'ID del Paciente',
        'Date': 'Fecha',
        'Col_Test': 'PRUEBA',
        'Col_Result': 'RESULTADO',
        'Col_Unit': 'UNIDADES',
        'Col_Ref': 'RANGO DE REFERENCIA',
        'Test_Names': {
            'Blood Urea': 'Urea en Sangre',
            'Serum Creatinine': 'Creatinina Sérica',
            'BUN (Blood Urea Nitrogen)': 'BUN (Nitrógeno Ureico)',
            'BUN/Creatinine Ratio': 'Relación BUN/Creatinina',
            'Uric Acid': 'Ácido Úrico',
            'Serum Calcium': 'Calcio Sérico',
            'Serum Phosphorus': 'Fósforo Sérico',
            'Sodium (Na+)': 'Sodio (Na+)',
            'Potassium (K+)': 'Potasio (K+)',
            'Chloride (Cl-)': 'Cloruro (Cl-)',
            'Serum Bilirubin Total': 'Bilirrubina Total',
            'Serum Bilirubin Direct': 'Bilirrubina Directa',
            'Serum Bilirubin Indirect': 'Bilirrubina Indirecta',
            'SGPT (ALT)': 'SGPT (ALT)',
            'SGOT (AST)': 'SGOT (AST)',
            'Alkaline Phosphatase (ALP)': 'Fosfatasa Alcalina (ALP)',
            'Serum Protein Total': 'Proteína Total Sérica',
            'Serum Albumin': 'Albúmina Sérica',
            'A/G Ratio': 'Relación A/G',
            'Hemoglobin': 'Hemoglobina',
            'Total Leukocyte Count (WBC)': 'Recuento Leucocitos (WBC)',
            'Platelet Count': 'Recuento de Plaquetas',
            'Total RBC Count': 'Recuento Total de GR',
            'Hematocrit (Hct)': 'Hematocrito (Hct)',
            'Mean Corpuscular Volume (MCV)': 'Volumen Corpuscular Medio (VCM)'
        }
    },
    'German': {
        'Hospital': 'STAATLICHES ALLGEMEINES KRANKENHAUS',
        'Title_LIVER': 'LEBERFUNKTIONSTEST BERICHT',
        'Title_KIDNEY': 'NIERENFUNKTIONSTEST BERICHT (KFT)',
        'Title_BLOOD': 'GROSSES BLUTBILD (CBC)',
        'Name': 'Patientenname',
        'AgeSex': 'Alter/Geschlecht',
        'ID': 'Patienten-ID',
        'Date': 'Datum',
        'Col_Test': 'TEST',
        'Col_Result': 'ERGEBNIS',
        'Col_Unit': 'EINHEITEN',
        'Col_Ref': 'REFERENZBEREICH',
        'Test_Names': {
            'Blood Urea': 'Blutharnstoff',
            'Serum Creatinine': 'Serumkreatinin',
            'BUN (Blood Urea Nitrogen)': 'BUN (Blutharnstoffstickstoff)',
            'BUN/Creatinine Ratio': 'BUN/Kreatinin-Verhältnis',
            'Uric Acid': 'Harnsäure',
            'Serum Calcium': 'Serumkalzium',
            'Serum Phosphorus': 'Serumphosphor',
            'Sodium (Na+)': 'Natrium (Na+)',
            'Potassium (K+)': 'Kalium (K+)',
            'Chloride (Cl-)': 'Chlorid (Cl-)',
            'Serum Bilirubin Total': 'Serum-Bilirubin Gesamt',
            'Serum Bilirubin Direct': 'Serum-Bilirubin Direkt',
            'Serum Bilirubin Indirect': 'Serum-Bilirubin Indirekt',
            'SGPT (ALT)': 'SGPT (ALT)',
            'SGOT (AST)': 'SGOT (AST)',
            'Alkaline Phosphatase (ALP)': 'Alkalische Phosphatase (ALP)',
            'Serum Protein Total': 'Serumprotein Gesamt',
            'Serum Albumin': 'Serumalbumin',
            'A/G Ratio': 'A/G-Verhältnis',
            'Hemoglobin': 'Hämoglobin',
            'Total Leukocyte Count (WBC)': 'Leukozytenzahl (WBC)',
            'Platelet Count': 'Thrombozytenzahl',
            'Total RBC Count': 'Erythrozytenzahl (RBC)',
            'Hematocrit (Hct)': 'Hämatokrit (Hct)',
            'Mean Corpuscular Volume (MCV)': 'Mittleres Korpuskularvolumen (MCV)'
        }
    },
    'French': {
        'Hospital': 'HÔPITAL GÉNÉRAL DU GOUVERNEMENT',
        'Title_LIVER': 'RAPPORT DE TEST DE LA FONCTION HÉPATIQUE',
        'Title_KIDNEY': 'RAPPORT DE TEST DE LA FONCTION RÉNALE (KFT)',
        'Title_BLOOD': 'NUMÉRATION FORMULE SANGUINE (NFS)',
        'Name': 'Nom du Patient',
        'AgeSex': 'Âge/Sexe',
        'ID': 'ID du Patient',
        'Date': 'Date',
        'Col_Test': 'TEST',
        'Col_Result': 'RÉSULTAT',
        'Col_Unit': 'UNITÉS',
        'Col_Ref': 'INTERVALLE DE RÉFÉRENCE',
        'Test_Names': {
            'Blood Urea': 'Urée Sanguine',
            'Serum Creatinine': 'Créatinine Sérique',
            'BUN (Blood Urea Nitrogen)': 'BUN (Azote Uréique Sanguin)',
            'BUN/Creatinine Ratio': 'Rapport BUN/Créatinine',
            'Uric Acid': 'Acide Urique',
            'Serum Calcium': 'Calcium Sérique',
            'Serum Phosphorus': 'Phosphore Sérique',
            'Sodium (Na+)': 'Sodium (Na+)',
            'Potassium (K+)': 'Potassium (K+)',
            'Chloride (Cl-)': 'Chlorure (Cl-)',
            'Serum Bilirubin Total': 'Bilirubine Sérique Totale',
            'Serum Bilirubin Direct': 'Bilirubine Sérique Directe',
            'Serum Bilirubin Indirect': 'Bilirubine Sérique Indirecte',
            'SGPT (ALT)': 'SGPT (ALT)',
            'SGOT (AST)': 'SGOT (AST)',
            'Alkaline Phosphatase (ALP)': 'Phosphatase Alcaline (ALP)',
            'Serum Protein Total': 'Protéines Sériques Totales',
            'Serum Albumin': 'Albumine Sérique',
            'A/G Ratio': 'Rapport A/G',
            'Hemoglobin': 'Hémoglobine',
            'Total Leukocyte Count (WBC)': 'Leucocytes Totaux (WBC)',
            'Platelet Count': 'Plaquettes',
            'Total RBC Count': 'Globules Rouges (RBC)',
            'Hematocrit (Hct)': 'Hématocrite (Hct)',
            'Mean Corpuscular Volume (MCV)': 'Volume Globulaire Moyen (VGM)'
        }
    },
        'Hindi': {
        'Hospital': 'सरकारी सामान्य अस्पताल',
        'Title_LIVER': 'यकृत कार्य परीक्षण रिपोर्ट',
        'Title_KIDNEY': 'गुर्दा कार्य परीक्षण रिपोर्ट (KFT)',
        'Title_BLOOD': 'पूर्ण रक्त गणना (CBC)',
        'Name': 'रोगी का नाम',
        'AgeSex': 'आयु/लिंग',
        'ID': 'रोगी आईडी',
        'Date': 'तारीख',
        'Col_Test': 'परीक्षण',
        'Col_Result': 'परिणाम',
        'Col_Unit': 'इकाई',
        'Col_Ref': 'संदर्भ सीमा',
        'Test_Names': {
            'Blood Urea': 'रक्त यूरिया',
            'Serum Creatinine': 'सीरम क्रिएटिनिन',
            'BUN (Blood Urea Nitrogen)': 'ब्लड यूरिया नाइट्रोजन (BUN)',
            'BUN/Creatinine Ratio': 'BUN/क्रिएटिनिन अनुपात',
            'Uric Acid': 'यूरिक एसिड',
            'Serum Calcium': 'सीरम कैल्शियम',
            'Serum Phosphorus': 'सीरम फॉस्फोरस',
            'Sodium (Na+)': 'सोडियम (Na⁺)',
            'Potassium (K+)': 'पोटैशियम (K⁺)',
            'Chloride (Cl-)': 'क्लोराइड (Cl⁻)',

            'Serum Bilirubin Total': 'सीरम बिलीरुबिन (कुल)',
            'Serum Bilirubin Direct': 'सीरम बिलीरुबिन (डायरेक्ट)',
            'Serum Bilirubin Indirect': 'सीरम बिलीरुबिन (इनडायरेक्ट)',
            'SGPT (ALT)': 'एसजीपीटी (ALT)',
            'SGOT (AST)': 'एसजीओटी (AST)',
            'Alkaline Phosphatase (ALP)': 'अल्कलाइन फॉस्फेटेज (ALP)',
            'Serum Protein Total': 'कुल सीरम प्रोटीन',
            'Serum Albumin': 'सीरम एल्ब्यूमिन',
            'A/G Ratio': 'A/G अनुपात',

            'Hemoglobin': 'हीमोग्लोबिन',
            'Total Leukocyte Count (WBC)': 'कुल श्वेत रक्त कोशिका संख्या (WBC)',
            'Platelet Count': 'प्लेटलेट संख्या',
            'Total RBC Count': 'कुल लाल रक्त कोशिका संख्या (RBC)',
            'Hematocrit (Hct)': 'हीमैटोक्रिट (Hct)',
            'Mean Corpuscular Volume (MCV)': 'औसत कणिकीय आयतन (MCV)'
        }
    },

    'Bengali': {
        'Hospital': 'সরকারি সাধারণ হাসপাতাল',
        'Title_LIVER': 'যকৃত কার্যক্ষমতা পরীক্ষার রিপোর্ট',
        'Title_KIDNEY': 'কিডনি কার্যক্ষমতা পরীক্ষার রিপোর্ট (KFT)',
        'Title_BLOOD': 'সম্পূর্ণ রক্ত পরীক্ষা (CBC)',
        'Name': 'রোগীর নাম',
        'AgeSex': 'বয়স/লিঙ্গ',
        'ID': 'রোগী আইডি',
        'Date': 'তারিখ',
        'Col_Test': 'পরীক্ষা',
        'Col_Result': 'ফলাফল',
        'Col_Unit': 'একক',
        'Col_Ref': 'রেফারেন্স পরিসীমা',
        'Test_Names': {
            'Blood Urea': 'রক্ত ইউরিয়া',
            'Serum Creatinine': 'সিরাম ক্রিয়াটিনিন',
            'BUN (Blood Urea Nitrogen)': 'ব্লাড ইউরিয়া নাইট্রোজেন (BUN)',
            'BUN/Creatinine Ratio': 'BUN/ক্রিয়াটিনিন অনুপাত',
            'Uric Acid': 'ইউরিক অ্যাসিড',
            'Serum Calcium': 'সিরাম ক্যালসিয়াম',
            'Serum Phosphorus': 'সিরাম ফসফরাস',
            'Sodium (Na+)': 'সোডিয়াম (Na⁺)',
            'Potassium (K+)': 'পটাসিয়াম (K⁺)',
            'Chloride (Cl-)': 'ক্লোরাইড (Cl⁻)',

            'Serum Bilirubin Total': 'সিরাম বিলিরুবিন (মোট)',
            'Serum Bilirubin Direct': 'সিরাম বিলিরুবিন (ডাইরেক্ট)',
            'Serum Bilirubin Indirect': 'সিরাম বিলিরুবিন (ইনডাইরেক্ট)',
            'SGPT (ALT)': 'SGPT (ALT)',
            'SGOT (AST)': 'SGOT (AST)',
            'Alkaline Phosphatase (ALP)': 'অ্যালকালাইন ফসফাটেজ (ALP)',
            'Serum Protein Total': 'মোট সিরাম প্রোটিন',
            'Serum Albumin': 'সিরাম অ্যালবুমিন',
            'A/G Ratio': 'A/G অনুপাত',

            'Hemoglobin': 'হিমোগ্লোবিন',
            'Total Leukocyte Count (WBC)': 'মোট শ্বেত রক্তকণিকা সংখ্যা (WBC)',
            'Platelet Count': 'প্লেটলেট সংখ্যা',
            'Total RBC Count': 'মোট লোহিত রক্তকণিকা সংখ্যা (RBC)',
            'Hematocrit (Hct)': 'হেমাটোক্রিট (Hct)',
            'Mean Corpuscular Volume (MCV)': 'গড় কণিকাকার আয়তন (MCV)'
        }
    },

    'Marathi': {
        'Hospital': 'शासकीय सामान्य रुग्णालय',
        'Title_LIVER': 'यकृत कार्य चाचणी अहवाल',
        'Title_KIDNEY': 'मूत्रपिंड कार्य चाचणी अहवाल (KFT)',
        'Title_BLOOD': 'पूर्ण रक्त तपासणी (CBC)',
        'Name': 'रुग्णाचे नाव',
        'AgeSex': 'वय/लिंग',
        'ID': 'रुग्ण आयडी',
        'Date': 'दिनांक',
        'Col_Test': 'तपासणी',
        'Col_Result': 'निकाल',
        'Col_Unit': 'एकक',
        'Col_Ref': 'संदर्भ श्रेणी',
        'Test_Names': {
            'Blood Urea': 'रक्त युरिया',
            'Serum Creatinine': 'सीरम क्रिएटिनिन',
            'BUN (Blood Urea Nitrogen)': 'ब्लड युरिया नायट्रोजन (BUN)',
            'BUN/Creatinine Ratio': 'BUN/क्रिएटिनिन गुणोत्तर',
            'Uric Acid': 'युरिक आम्ल',
            'Serum Calcium': 'सीरम कॅल्शियम',
            'Serum Phosphorus': 'सीरम फॉस्फरस',
            'Sodium (Na+)': 'सोडियम (Na⁺)',
            'Potassium (K+)': 'पोटॅशियम (K⁺)',
            'Chloride (Cl-)': 'क्लोराईड (Cl⁻)',

            'Serum Bilirubin Total': 'सीरम बिलीरुबिन (एकूण)',
            'Serum Bilirubin Direct': 'सीरम बिलीरुबिन (डायरेक्ट)',
            'Serum Bilirubin Indirect': 'सीरम बिलीरुबिन (इंडायरेक्ट)',
            'SGPT (ALT)': 'SGPT (ALT)',
            'SGOT (AST)': 'SGOT (AST)',
            'Alkaline Phosphatase (ALP)': 'अल्कलाइन फॉस्फेटेस (ALP)',
            'Serum Protein Total': 'एकूण सीरम प्रोटीन',
            'Serum Albumin': 'सीरम अल्ब्युमिन',
            'A/G Ratio': 'A/G गुणोत्तर',

            'Hemoglobin': 'हिमोग्लोबिन',
            'Total Leukocyte Count (WBC)': 'एकूण पांढऱ्या रक्तपेशी संख्या (WBC)',
            'Platelet Count': 'प्लेटलेट संख्या',
            'Total RBC Count': 'एकूण लाल रक्तपेशी संख्या (RBC)',
            'Hematocrit (Hct)': 'हिमॅटोक्रिट (Hct)',
            'Mean Corpuscular Volume (MCV)': 'सरासरी कणिकीय आयतन (MCV)'
        }
    }

}

# ------------------------------------------------------------------
# TEST DEFINITIONS (COMPLETE INFO FROM IMAGES)
# Format: 'English Key': [Min, Max, Unit, Reference String]
# ------------------------------------------------------------------
TEST_DEFINITIONS = {
    'KIDNEY': {
        'Blood Urea': [15, 45, 'mg/dL', '15 – 45'],
        'Serum Creatinine': [0.6, 1.1, 'mg/dL', '0.6 – 1.1'],
        'BUN (Blood Urea Nitrogen)': [7, 20, 'mg/dL', '7 – 20'],
        'BUN/Creatinine Ratio': [10, 20, '(Ratio)', '10 – 20'],
        'Uric Acid': [3.5, 7.2, 'mg/dL', '3.5 – 7.2'],
        'Serum Calcium': [8.5, 10.5, 'mg/dL', '8.5 – 10.5'],
        'Serum Phosphorus': [2.5, 4.5, 'mg/dL', '2.5 – 4.5'],
        'Sodium (Na+)': [135, 145, 'mmol/L', '135 – 145'],
        'Potassium (K+)': [3.5, 5.0, 'mmol/L', '3.5 – 5.0'],
        'Chloride (Cl-)': [96, 106, 'mmol/L', '96 – 106'],
    },
    'LIVER': {
        'Serum Bilirubin Total': [0.1, 1.2, 'mg/dL', '0.1 – 1.2'],
        'Serum Bilirubin Direct': [0.0, 0.3, 'mg/dL', '< 0.3'],
        'Serum Bilirubin Indirect': [0.2, 0.8, 'mg/dL', '0.2 – 0.8'],
        'SGPT (ALT)': [7, 56, 'U/L', '7 – 56'],
        'SGOT (AST)': [10, 40, 'U/L', '10 – 40'],
        'Alkaline Phosphatase (ALP)': [44, 147, 'U/L', '44 – 147'],
        'Serum Protein Total': [6.0, 8.3, 'g/dL', '6.0 – 8.3'],
        'Serum Albumin': [3.5, 5.5, 'g/dL', '3.5 – 5.5'],
        'A/G Ratio': [1.1, 2.5, '', '1.1 – 2.5']
    },
    'BLOOD': {
        'Hemoglobin': [12.0, 15.5, 'g/dL', '12.0 – 15.5'],
        'Total Leukocyte Count (WBC)': [4500, 11000, '/cumm', '4,500 – 11,000'],
        'Platelet Count': [1.5, 4.5, 'Lakhs/cumm', '1.5 – 4.5'],
        'Total RBC Count': [3.90, 5.03, 'mill/cumm', '3.90 – 5.03'],
        'Hematocrit (Hct)': [35.5, 44.9, '%', '35.5 – 44.9'],
        'Mean Corpuscular Volume (MCV)': [80, 100, 'fL', '80 – 100']
    }
}

WESTERN_NAMES = [
    "John Smith", "Emily Johnson", "Michael Brown",
    "Jessica Davis", "David Wilson", "Sarah Miller",
    "James Taylor", "Linda Anderson", "Robert Thomas"
]
INDIAN_NAMES = [
    "Amit Sharma", "Pooja Verma", "Rahul Gupta", "Neha Singh",
    "Sourav Mukherjee", "Ananya Chatterjee", "Arindam Das", "Riya Banerjee",
    "Pratik Patil", "Sneha Kulkarni", "Akash Deshpande", "Pallavi Joshi",
    "Rohit Iyer", "Kavya Nair", "Arjun Reddy", "Anjali Rao",
    "Ayaan Khan", "Zara Ahmed", "Imran Sheikh", "Fatima Ansari"
]

# ------------------------------------------------------------------
# VALUE GENERATOR
# ------------------------------------------------------------------
def get_val(min_v, max_v, condition, test_name):
    # Determine value based on condition
    if condition == 'normal':
        val = random.uniform(min_v, max_v)
    else:
        # If abnormal, push values high. 
        # For ratios or electrolytes, this is a simplification but fits the "abnormal" flag requirement.
        val = max_v * random.uniform(1.2, 2.5)

    # Formatting rules based on test type matching the images
    if "WBC" in test_name:
        return f"{int(val):,}"
    if "Platelet" in test_name:
        return f"{val:.1f}"
    
    # Default to 2 decimal places for most others (KFT, LFT, RBC, MCV etc)
    return f"{val:.2f}"

# ------------------------------------------------------------------
# PDF CREATION
# ------------------------------------------------------------------
def create_pdf(language, category, condition, idx):
    labels = RAW_LABELS[language]
    test_name_map = labels.get('Test_Names', {})
    # --- Footer ---
    footer_text = "** Electronic Report. Reference ranges vary by laboratory method."


    lang_dir = os.path.join(BASE_OUTPUT_DIR, language)
    os.makedirs(lang_dir, exist_ok=True)

    filename = os.path.join(
        lang_dir,
        f"{language}_{category}_{condition}_{idx}.pdf"
    )

    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    # --- Font selection based on language ---
    if language in ('Hindi', 'Marathi'):
        font_name = 'Devanagari'
    elif language == 'Bengali':
        font_name = 'Bengali'
    else:
        font_name = 'Helvetica'

    # --- Base Paragraph Style with proper font ---
    base = ParagraphStyle(
        'Base',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10
    )

    header_style = ParagraphStyle(
        'Header',
        parent=base,
        fontSize=16,
        alignment=1,
        spaceAfter=6
    )

    title_style = ParagraphStyle(
        'Title',
        parent=base,
        fontSize=14,
        alignment=1,
        spaceAfter=12
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=base,
        fontSize=8,
        spaceBefore=10
    )


    elements = []

    # --- Header Information ---
    elements.append(Paragraph(labels['Hospital'], header_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(labels[f'Title_{category}'], title_style))

    elements.append(Paragraph(footer_text, footer_style))


    # --- Patient Details ---
    if language in INDIAN_LANGUAGES:
        name = random.choice(INDIAN_NAMES)
    else:
        name = random.choice(WESTERN_NAMES)

    age = random.randint(20, 70)
    sex = random.choice(['M', 'F'])
    pid = random.randint(100000, 999999)
    date_str = datetime.now().strftime('%d-%b-%Y')

    # Formatting patient info block
    patient_info = [
        [f"{labels['Name']}: {name}", f"{labels['Date']}: {date_str}"],
        [f"{labels['AgeSex']}: {age} Y / {sex}", f"{labels['ID']}: {pid}"]
    ]

    pt = Table(patient_info, colWidths=[300, 200])
    pt.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('FONTNAME', (0,0), (-1,-1), font_name),
    ]))
    elements.append(pt)
    elements.append(Spacer(1, 12))

    # --- Test Results Table ---
    # Header Row
    table_data = [[
        labels['Col_Test'],
        labels['Col_Result'],
        labels['Col_Unit'],
        labels['Col_Ref']
    ]]

    abnormal_rows = []
    row_idx = 1

    # Loop through the expanded test definitions
    for test_key, spec in TEST_DEFINITIONS[category].items():
        min_v, max_v, unit, ref = spec
        
        # Get translated name, default to English Key if not found
        display_name = test_name_map.get(test_key, test_key)
        
        val = get_val(min_v, max_v, condition, test_key)

        # Highlight if abnormal condition matches
        if condition == 'abnormal':
            abnormal_rows.append(row_idx)

        table_data.append([display_name, val, unit, ref])
        row_idx += 1

    # Table Formatting to match the image style (Light blue header, grid)
    table = Table(table_data, colWidths=[200, 80, 80, 150])
    
    ts = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.Color(0.89, 0.93, 0.96)), # Light Blueish Gray
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),   # Test names Left
        ('ALIGN', (1,0), (-1,-1), 'LEFT'),  # Results/Units/Ref Left (as per images)
        ('FONTNAME', (0,0), (-1,0), font_name),
        ('FONTNAME', (0,1), (-1,-1), font_name),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.Color(0.6, 0.6, 0.6)),
        ('topPadding', (0,0), (-1,-1), 6),
        ('bottomPadding', (0,0), (-1,-1), 6),
    ])

    # Apply Red color to Result column if abnormal
    for r in abnormal_rows:
        # Only color the Result column (index 1) red, or the whole row? 
        # Usually only the result is red in standard reports, keeping it simple.
        ts.add('TEXTCOLOR', (0, r), (-1, r), colors.black) # Default black
        if condition == 'abnormal':
             # Here we assume the generated value is actually out of range logic
             pass 

    table.setStyle(ts)
    elements.append(table)
    
    elements.append(Spacer(1, 20))
    
    if language == 'Spanish':
        footer_text = "** Informe electrónico. Los rangos de referencia varían según el método de laboratorio."
    elif language == 'German':
        footer_text = "** Elektronischer Bericht. Referenzbereiche variieren je nach Labormethode."
    elif language == 'French':
        footer_text = "** Rapport électronique. Les intervalles de référence varient selon la méthode de laboratoire."
    elif language == 'Hindi':
        footer_text = "** इलेक्ट्रॉनिक रिपोर्ट। संदर्भ सीमाएं प्रयोगशाला विधि के अनुसार भिन्न हो सकती हैं।"
    elif language == 'Bengali':
        footer_text = "** ইলেকট্রনিক প্রতিবেদন। রেফারেন্স সীমা পরীক্ষাগার পদ্ধতির উপর নির্ভর করে পরিবর্তিত হতে পারে।"
    elif language == 'Marathi':
        footer_text = "** इलेक्ट्रॉनिक अहवाल. संदर्भ मर्यादा प्रयोगशाळा पद्धतीनुसार बदलू शकतात."

    elements.append(Paragraph(footer_text, ParagraphStyle('F', parent=base, fontSize=8)))

    doc.build(elements)
    print(f"Generated: {filename}")

# ------------------------------------------------------------------
# BATCH GENERATION
# ------------------------------------------------------------------
languages = ['English', 'Spanish', 'German', 'French', 'Hindi', 'Bengali', 'Marathi']
INDIAN_LANGUAGES = ['Hindi', 'Bengali', 'Marathi']

categories = ['BLOOD', 'KIDNEY', 'LIVER']

for lang in languages:
    for cat in categories:
        # Generate 4 Normal
        for i in range(1, 5):
            create_pdf(lang, cat, 'normal', i)
        # Generate 4Abnormal
        for i in range(1, 5):
            create_pdf(lang, cat, 'abnormal', i)

print("Reports generated successfully.")

















