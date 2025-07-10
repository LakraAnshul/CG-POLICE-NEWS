import re
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


police_crime_types_input = ["पुलिस की लापरवाही", "पुलिस द्वारा अपराध", "गंभीर अपराध", "कानून व्यवस्था", "विभागीय नकारात्मक समाचार"]
police_crime_examples = ["रिपोर्ट दर्ज न करना", "अपराधी को जानते हुए भी उसे गिरफ्तार न करना", "शिकायत पर कार्यवाही नहीं करना", "प्रार्थी/पीड़ितों/गवाहों के साथ दुर्व्यवहार", "जुआ/सट्टेबाजों को संरक्षण देना", "आपात स्थिति मे कोई प्रतिक्रिया नहीं देना", "झूठे मामले में निर्दोष के विरूद्ध कार्यवाही करना", "आरोपी के साथ अमानवीय व्यवहार", "रिश्वत/भ्रष्टाचार कर आरोपी पक्ष को लाभ पहुंचाना", "अपराध दर्ज करने के लिए पैसे की मांग करना", "कानूनी प्रक्रिया की अनदेखी करना", "न्यायालय के आदेषों का अवहेलना करना", "मादक पदार्थों की तस्करी में संलिप्तता", "गुण्डा/बदमाषों को संरक्षण देना", "पुलिस अधिकारी/कर्मचारियों द्वारा कारित अपराध", "अवैध गतिविधियों की अनदेखा करना", "साम्प्रदायिक हिंसा", "धर्मान्तरण", "अवैध/अनाधिकृत प्रवासी", "कमजोर आसूचना तंत्र", "जनता के साथ संवादहीनता", "पुलिसकर्मियों द्वारा आत्महत्या", "ट्रांसफर/पोस्टिंग से जुड़ा असंतोष", "अनुकंपा नियुक्ति नहीं मिलना", "हत्या", "बलात्कार", "डकैती", "लूट", "गैंगवार", "चाकूबाजी", "फायरिंग", "गैंगरेप", "गौ-तस्करी", "मानव तस्करी", "गुमषुदा बच्चे/महिला"]
additional_police_crimes = ["हिरासत में मौत", "हिरासत में प्रताड़ना", "न्यायेतर हत्याएं", "दुरुपयोग", "VIP संस्कृति", "नैतिक पुलिसिंग", "झूठी मुठभेड़", "राजनीतिक हस्तक्षेप", "जाँच में देरी", "सबूतों से छेड़छाड़", "पक्षपातपूर्ण जाँच", "जनता को धमकाना"]
summarized_police_crimes = ["लापरवाही", "भ्रष्टाचार", "अमानवीयता", "उत्पीड़न", "संरक्षण", "निष्क्रियता", "फर्जीवाड़ा", "षड्यंत्र", "उल्लंघन", "हत्या", "बलात्कार", "हिंसा", "तस्करी", "भेदभाव", "आत्महत्या", "असंतुष्टि", "प्रताड़ना", "दुरुपयोग", "पक्षपात", "धमकी"]
alternative_police_crimes = ["पुलिसिया ज़्यादती", "पुलिस दुराचार", "अवैध पुलिस कार्रवाई", "पुलिस उत्पीड़न", "पुलिस की मिलीभगत", "पुलिस की अनदेखी", "पुलिस की निष्क्रियता", "पुलिस द्वारा फर्जी केस", "पुलिस रिश्वतखोरी", "हिरासत में अत्याचार", "फर्जी मुठभेड़", "पुलिस का राजनीतिकरण", "जाँच में विलंब", "सबूतों से खिलवाड़", "जाँच में पक्षपात", "पुलिस द्वारा धमकी"]
crimes_by_police = list(set(police_crime_types_input + police_crime_examples + additional_police_crimes + summarized_police_crimes + alternative_police_crimes))

chhattisgarh_districts = ["बालोद", "बलौदाबाजार", "बलरामपुर", "बस्तर", "बेमेतरा", "बिलासपुर", "दंतेवाड़ा", "धमतरी", "दुर्ग", "गौरेला-पेंड्रा-मरवाही", "गरियाबंद", "जांजगीर-चांपा", "जशपुर", "कवर्धा", "कांकेर", "कोरबा", "कोरिया", "महासमुंद", "मुंगेली", "नारायणपुर", "रायगढ़", "रायपुर", "राजनांदगांव", "सुकमा", "सूरजपुर", "सरगुजा", "बीजापुर", "कोंडागांव", "खैरागढ़-छुईखदान-गंडई", "मोहला-मानपुर-अंबागढ़ चौकी", "सारंगढ़-बिलाईगढ़", "मनीन्द्रगढ़-चिरमिरी-भरतपुर"]

crime_severity_en = {"Murder": 10, "Attempt to Murder": 8, "Rape": 9, "Robbery": 7, "Assault": 5, "Theft": 3, "Other": 1}

crime_severity_hi = {"हत्या": 10, "हत्या का प्रयास": 8, "बलात्कार": 9, "डकैती": 7, "हमला": 5, "चोरी": 3, "गैंग": 8, "गैंगस्टर": 8, "सामूहिक अपराध": 7, "बंदी": 6, "फिरौती": 7, "हत्या की कोशिश": 8, "अन्य": 1}

crime_type = ["हत्या", "हत्या का प्रयास", "बलात्कार", "बलात्कार का प्रयास", "छेड़छाड़", "दुष्कर्म", "अपहरण", "डकैती", "लूट", "चोरी", "गृहभेदन", "मारपीट", "धोखाधड़ी", "ठगी", "घूसखोरी", "साइबर अपराध", "नकली नोट", "नशीली दवाओं की तस्करी", "शराब तस्करी", "मानव तस्करी", "घरेलू हिंसा", "आतंकवाद", "देशद्रोह", "धार्मिक उन्माद", "नाबालिग से दुष्कर्म", "पत्नि पर अत्याचार", "आत्महत्या के लिए उकसाना", "धमकी देना", "अवैध हथियार रखना", "हथियारों की तस्करी", "जुआ", "मादक पदार्थ तस्करी", "नशीली दवाओं की तस्करी", "तस्करी", "नक्सली", "आत्मसमर्पण", "ईनामी", "पुनर्वास नीति", "माओवाद", "गांजा", "मादक पदार्थ", "एनडीपीएस", "बिक्री", "अवैध परिवहन", "नक्सलवाद", "देशद्रोह", "गौ हत्या", "गौ तस्करी"]

crime_severity_sorted = {
    'शराब तस्करी': 6, 'जुआ': 2, 'गौ हत्या': 6, 'गौ तस्करी': 5, 'नशीली दवाओं की तस्करी': 9, 'हथियारों की तस्करी': 9,
    'मादक पदार्थ तस्करी': 9, 'अवैध हथियार रखना': 8, 'एनडीपीएस': 8, 'मादक पदार्थ': 7, 'वन्यजीव तस्करी': 7,
    'अवैध उत्पादों की तस्करी': 7, 'फेंटेनिल': 4, 'एमडी ड्रग': 4, 'मेफेड्रोन': 4, 'कोकीन': 4, 'ब्राउन शुगर': 4,
    'हेरोइन': 4, 'गांजा': 4, 'धार्मिक उन्माद': 7, 'नकली नोट': 7, 'आतंकवाद': 10, 'देशद्रोह': 10, 'माओवाद': 9,
    'नक्सली': 9, 'नक्सलवाद': 9, 'पुनर्वास नीति': 2, 'साइबर अपराध': 6, 'डिजिटल गिरफ्तारी': 2, 'साइबर धोखाधड़ी': 6,
    'डकैती': 9, 'लूट': 8, 'गृहभेदन': 6, 'धोखाधड़ी': 6, 'चोरी': 5, 'ठगी': 5, 'सांप्रदायिक हत्या': 6, 'हत्या': 10,
    'बलात्कार': 10, 'दुष्कर्म': 10, 'मानव तस्करी': 10, 'नाबालिग से दुष्कर्म': 10, 'हत्या का प्रयास': 9,
    'बलात्कार का प्रयास': 9, 'अपहरण': 8, 'घरेलू हिंसा': 4, 'आत्महत्या के लिए उकसाना': 4, 'छेड़छाड़': 6,
    'मारपीट': 6, 'पत्नि पर अत्याचार': 7, 'धमकी देना': 5, 'ईनामी': 0, 'अवैध परिवहन': 0, 'बिक्री': 0, 'आत्मसमर्पण': 0
}

weapons_keywords = ['पिस्तौल', 'रिवॉल्वर', 'बंदूक', 'चाकू', 'तलवार', 'हथियार']

score_match = [
    "व्यापार", "एक से अधिक व्यक्तियों की संलिप्तता", "वाहनों का उपयोग", "हथियारों का उपयोग", "पुलिस अधिकारियों की संलिप्तता",
    "प्रमुख व्यक्तियों की संलिप्तता", "राजनीतिक व्यक्तियों की संलिप्तता", "अंतरराष्ट्रीय संबंध", "आपराधिक गिरोह की संलिप्तता",
    "अंतर्राज्यीय गिरोह की संलिप्तता", "राजनीतिक दलों से संबंधित", "प्रमुख व्यक्तियों से संबंधित", "पाँच से अधिक बच्चों से संबंधित",
    "पाँच से अधिक व्यक्तियों से संबंधित", "अवैध/नकली शराब से संबंधित", "सरकारी कार्यालयों और संपत्तियों की संलिप्तता",
    "विशेष अवसर से संबंधित", "महिलाओं से संबंधित", "अनुसूचित जाति और अनुसूचित जनजाति से संबंधित",
    "आरोपी के विरुद्ध पहले से कोई सजा, FIR या चार्जशीट", "आरोपी या दोषी पर इनाम घोषित था",
    "पीड़ित पहले भी अपराध का शिकार रह चुका था", "साइबर डोमेन से संबंधित"
]

occasion = {
    "दीवाली": 10, "होली": 10, "ईद": 9, "क्रिसमस": 8, "रक्षा बंधन": 8, "दशहरा": 9, "ईद-उल-अजहा (बकरीद)": 8,
    "नवरात्रि": 8, "गणेश चतुर्थी": 9, "मकर संक्रांति": 7, "लोहड़ी": 6, "बैसाखी": 6, "महाशिवरात्रि": 7,
    "गुरु नानक जयंती": 6, "रामनवमी": 6, "ईद मिलाद-उन-नबी": 5, "जन्माष्टमी": 7, "बसंत पंचमी": 6, "गुड फ्राइडे": 5,
    "बुद्ध पूर्णिमा": 5, "महावीर जयंती": 5, "शब-ए-बरात": 4, "ओणम": 6, "पोंगल": 6, "तुलसी विवाह": 3,
    "छठ पूजा": 7, "इंटरनेशनल वीमन्स डे": 4, "स्वतंत्रता दिवस": 9, "गणतंत्र दिवस": 9, "गांधी जयंती": 7,
    "शहीद दिवस": 5, "शादी": 10, "सगाई": 6, "गृह प्रवेश": 6, "उपनयन संस्कार": 5, "नामकरण": 4,
    "अंतिम संस्कार/तेरहवीं": 8, "धार्मिक यात्रा/तीर्थ यात्रा": 6, "राजनीतिक रैली": 7, "स्कूल का कार्यक्रम": 5,
    "कॉलेज फेस्ट": 6, "लोकल मेला": 5, "खेलकूद का आयोजन": 6
}

ambikapur_police_stations = [
    "कोतवाली अंबिकापुर",
    "गांधी नगर थाना",
    "महिला थाना",
    "दरिमा थाना",
    "उजियारपुर थाना",
    "सीतापुर थाना",
    "लुण्ड्रा थाना",
    "मैनपाट थाना",
    "बतौली थाना",
    "ओडगी थाना",
    "झारखंडी थाना",
    "प्रतापपुर थाना",
    "राजपुर थाना",
    "कुशमी थाना",
    "भटगांव थाना",
    "बिश्रामपुर थाना",
    "भटगांव कोयलरी थाना",
    "अभनपुर",
    "आजाद चौक",
    "आरंग",
    "उरला",
    "आमानाका",
    "सिविल लाइन्स",
    "टिकरापारा",
    "धरसीवां",
    "देवेन्द्रनगर",
    "दीनदयाल नगर",
    "गोल बाजार",
    "गंज",
    "गोबरा नवापारा",
    "गुढ़ियारी",
    "खमतराई",
    "खरोरा",
    "माना कैम्प",
    "मौदहापारा",
    "मंदिर हसौद",
    "तिल्दा नेवरा",
    "पुरानी बस्ती",
    "पंडरी",
    "महिला थाना",
    "कोतवाली",
    "राजेंद्रनगर",
    "सरस्वतीनगर",
    "तेलीबांधा",
    "विधानसभा",
    "राखी",
    "अनुसूचित जाति कल्याण रायपुर",
    "अपराध अन्वेषण विभाग, पुलिस मुख्यालय रायपुर",
    "राज्य साईबर पुलिस थाना",
    "कबीर नगर",
    "मुजगहन",
    "ए टी एस",
    "खम्हारडीह",
    "सायबर पुलिस थाना, रेंज रायपुर"
]


# Load NER model
model_name = "ai4bharat/IndicNER"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

def extract_date(text):
    # Convert Hindi digits to Western numerals
    hindi_to_num = str.maketrans("०१२३४५६७८९", "0123456789")
    text = text.translate(hindi_to_num)

    # Match common date formats: dd/mm/yyyy, dd-mm-yyyy, dd.mm.yyyy, dd/mm/yy etc.
    match = re.search(r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b', text)
    return match.group() if match else "N/A"

def extract_district(text):
    for district in chhattisgarh_districts:
        if district in text:
            return district
    return "N/A"
    
def extract_police_station(text):
    for ps in ambikapur_police_stations:
        if ps in text:
            return ps
    return "N/A"    
    
    # Try both 'थाना' and 'चौकी'
    # match = re.search(r'(थाना|चौकी)\s+([^\n।:,]*)', text)
    # return f'{match.group(1)} {match.group(2).strip()}' if match else "N/A"

def extract_fir_number(text):
    match = re.search(r'(अपराध क्रमांक|FIR|एफआईआर)\s*[:\-]?\s*([0-9\/\-]+)', text)
    return match.group(2) if match else "N/A"

def extract_complainant(text):
    # List of common patterns to detect complainant in Hindi FIRs
    patterns = [
        r'प्रार्थी\s*[:-]?\s*([^\n]*)',
        r'शिकायतकर्ता\s*[:-]?\s*([^\n]*)',
        r'फरियादी\s*[:-]?\s*([^\n]*)',
        r'Complainant\s*[:-]?\s*([^\n]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            matched_text = match.group(1).strip()
            words = re.findall(r'[\w\u0900-\u097F]+', matched_text)
            limited_words = words[:8]
            name = ' '.join(limited_words)
            if name:
                return name
    
    return "N/A"


def extract_accused(text):
    # List of regex patterns covering different common Hindi patterns
    patterns = [
        r'गिरफ्तार आरोपी\s*-\s*([^\n]*)',
        r'आरोपी का नाम\s*[:-]?\s*([^\n]*)',
        r'आरोपी\s*[:-]?\s*([^\n]*)',
        # r'नाम\s*[:-]?\s*([^\n]*)',
        r'अभियुक्त\s*[:-]?\s*([^\n]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            matched_text = match.group(1).strip()
            # Remove common suffixes like 'पिता', 'पुत्र', etc.
            matched_text = re.split(r'पिता|पुत्र|पति|Father|Son|Husband', matched_text)[0].strip()
            # Extract words (Hindi, Latin letters, digits)
            words = re.findall(r'[\w\u0900-\u097F]+', matched_text)
            # Take at most first 5 words
            limited_words = words[:5]
            name = ' '.join(limited_words)
            if name:
                return name

    # Fallback: use NER (e.g., transformers pipeline)
    try:
        ner_results = ner_pipeline(text)
        persons = [ent['word'] for ent in ner_results if ent['entity_group'] == 'PER']
        if persons:
            return persons[0]
    except Exception:
        pass  # fail silently if NER isn't available

    return "N/A"

def extract_weapons(text):
    weapons_keyword = weapons_keywords
    found = [word for word in weapons_keyword if word in text]
    return ', '.join(found) if found else "N/A"

def extract_crime_type(text):
    for crime in crime_severity_sorted.keys():
        if crime in text:
            return crime
    return "N/A" 

def extract_score(text):
    score=0
    for i in score_match:
        if i in text:
            score += 1
    
    for i in occasion.keys():
        if i in text:
            score += occasion[i]
               
    word_to_number = {
            "शून्य": 0, "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5,
            "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10, "ग्यारह": 11,
            "बारह": 12, "तेरह": 13, "चौदह": 14, "पंद्रह": 15, "सोलह": 16,
            "सत्रह": 17, "अठारह": 18, "उन्नीस": 19, "बीस": 20
        }

    def convert_hindi_numerals(s):
        return s.translate(str.maketrans('०१२३४५६७८९', '0123456789'))

    def extract_number_from_words(w):
        return word_to_number.get(w.strip(), 0)

    crime = extract_crime_type(text)
    if crime in crime_severity_sorted:
        score += crime_severity_sorted[crime]

        if crime == "साइबर धोखाधड़ी":
            # लाख
            lakh = re.search(r'([\d०१२३४५६७८९]+|[अ-ह]+)\s*लाख', text)
            if lakh:
                lakh_word = lakh.group(1)
                if lakh_word.isdigit() or all(ch in '०१२३४५६७८९' for ch in lakh_word):
                    lakh_value = convert_hindi_numerals(lakh_word)
                else:
                    lakh_value = extract_number_from_words(lakh_word)
                score += int(lakh_value) * 2
            # करोड़
            crore = re.search(r'([\d०१२३४५६७८९]+|[अ-ह]+)\s*करोड़', text)
            if crore:
                crore_word = crore.group(1)
                if crore_word.isdigit() or all(ch in '०१२३४५६७८९' for ch in crore_word):
                    crore_value = convert_hindi_numerals(crore_word)
                else:
                    crore_value = extract_number_from_words(crore_word)
                score += int(crore_value) * 20

    return score
    
def extract_summary_string(text):
    heading = f"🗞 {extract_district(text)},  {extract_police_station(text)}{extract_date(text)}__प्राथमिकी संख्या {extract_fir_number(text)}"
    summary = (
        f"{extract_accused(text)} को {extract_crime_type(text)} के मामले में आरोपी बनाया गया है। "
        f"इस प्रकरण में शिकायतकर्ता का नाम {extract_complainant(text)} है। "
    ) 
    
    return heading,summary



def analyze_articles(article_list):
    all_info_2d_list = []
    for news in article_list:
        heading, summary = extract_summary_string(news)
        # crime_category = extract_crime_category(news)
        info_row = [
            extract_police_station(news),
            extract_district(news),
            extract_date(news),
            extract_fir_number(news),
            extract_complainant(news),
            extract_accused(news),
            extract_weapons(news),
            extract_crime_type(news),
            extract_score(news),
            heading,
            summary
            
        ]
        all_info_2d_list.append(info_row)
    return all_info_2d_list