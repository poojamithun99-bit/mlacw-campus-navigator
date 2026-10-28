"""
Multilingual Conversational AI & NLP Module
Supports English, Kannada (ಕನ್ನಡ), and Hindi (हिन्दी)
Extracts user intent (Navigate, Locate, Information) and resolves entities to canonical campus landmarks.
"""

import re
import difflib
from typing import Dict, Tuple, Optional, List

class CampusNLPEngine:
    def __init__(self, locations_dict: Dict[str, Dict]):
        self.locations_dict = locations_dict
        self._build_lexicon()

    def _build_lexicon(self):
        """Constructs multilingual aliases and canonical mapping."""
        self.alias_to_canonical = {}

        # Add exact location names and case-folded versions
        for name, info in self.locations_dict.items():
            self.alias_to_canonical[name.lower()] = name
            if "kannada_name" in info and info["kannada_name"]:
                self.alias_to_canonical[info["kannada_name"].strip()] = name
            if "hindi_name" in info and info["hindi_name"]:
                self.alias_to_canonical[info["hindi_name"].strip()] = name

        # Colloquial & multilingual synonym dictionary
        custom_synonyms = {
            # Library synonyms
            "library": "Central Library",
            "central library": "Central Library",
            "reading room": "Central Library",
            "reading hall": "Central Library",
            "digital library": "Central Library",
            "books": "Central Library",
            "ಗ್ರಂಥಾಲಯ": "Central Library",
            "ಲೈಬ್ರರಿ": "Central Library",
            "ಪುಸ್ತಕಾಲಯ": "Central Library",
            "ಓದುವ ಕೊಠಡಿ": "Central Library",
            "ಲೈಬ್ರರಿ ಎಲ್ಲಿದೆ": "Central Library",
            "पुस्तकालय": "Central Library",
            "लाइब्रेरी": "Central Library",
            "वाचनालय": "Central Library",

            # Sanskrit Department & Classrooms
            "sanskrit": "Sanskrit Department",
            "sanskrit department": "Sanskrit Department",
            "sanskrit classroom": "Sanskrit Classrooms",
            "sanskrit classrooms": "Sanskrit Classrooms",
            "sanskrit class": "Sanskrit Classrooms",
            "valmiki hall": "Sanskrit Classrooms",
            "ಸಂಸ್ಕೃತ": "Sanskrit Department",
            "ಸಂಸ್ಕೃತ ವಿಭಾಗ": "Sanskrit Department",
            "ಸಂಸ್ಕೃತ ಕೊಠಡಿ": "Sanskrit Classrooms",
            "ಸಂಸ್ಕೃತ ತರಗತಿ": "Sanskrit Classrooms",
            "ಸಂಸ್ಕೃತ ಕ್ಲಾಸ್": "Sanskrit Classrooms",
            "ವಾಲ್ಮೀಕಿ ಭವನ": "Sanskrit Classrooms",
            "संस्कृत": "Sanskrit Department",
            "संस्कृत विभाग": "Sanskrit Department",
            "संस्कृत कक्षा": "Sanskrit Classrooms",
            "संस्कृत कक्षाएं": "Sanskrit Classrooms",

            # Computer Science & Labs
            "cs": "Dept. of Computer Science & Staff Room",
            "computer science": "Dept. of Computer Science & Staff Room",
            "cs department": "Dept. of Computer Science & Staff Room",
            "computer science department": "Dept. of Computer Science & Staff Room",
            "comp sci": "Dept. of Computer Science & Staff Room",
            "bca": "Dept. of Computer Science & Staff Room",
            "computer lab": "Computer Lab 1",
            "computer lab 1": "Computer Lab 1",
            "computer lab 2": "Computer Lab 2",
            "turing lab": "Computer Lab 1",
            "ada lovelace lab": "Computer Lab 2",
            "pc lab": "Computer Lab 1",
            "ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್": "Dept. of Computer Science & Staff Room",
            "ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ": "Dept. of Computer Science & Staff Room",
            "ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್": "Computer Lab 1",
            "ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ 1": "Computer Lab 1",
            "ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ 2": "Computer Lab 2",
            "ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ ೧": "Computer Lab 1",
            "ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ ೨": "Computer Lab 2",
            "ಕಂಪ್ಯೂಟರ್ ವಿಭಾಗ": "Dept. of Computer Science & Staff Room",
            "कंप्यूटर साइंस": "Dept. of Computer Science & Staff Room",
            "कंप्यूटर साइंस विभाग": "Dept. of Computer Science & Staff Room",
            "कंप्यूटर लैब": "Computer Lab 1",
            "कंप्यूटर लैब 1": "Computer Lab 1",
            "कंप्यूटर लैब 2": "Computer Lab 2",
            "कंप्यूटर विभाग": "Dept. of Computer Science & Staff Room",

            # Science Labs & Departments
            "physics": "Physics Department",
            "physics lab": "Physics Lab",
            "chemistry": "Chemistry Department",
            "chemistry lab": "Chemistry Lab",
            "biotechnology": "Biotechnology Department",
            "biotechnology lab": "Biotechnology Lab",
            "biotech": "Biotechnology Department",
            "biotech lab": "Biotechnology Lab",
            "microbiology": "Microbiology Department",
            "microbiology lab": "Microbiology Department",
            "language lab": "Language Lab",
            "ಭಾಷಾ ಲ್ಯಾಬ್": "Language Lab",
            "ಭಾಷಾ ಪ್ರಯೋಗಾಲಯ": "Language Lab",
            "ಭೌತಶಾಸ್ತ್ರ": "Physics Department",
            "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್": "Physics Lab",
            "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 3": "Physics Lab III",
            "ಭೌತಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೩": "Physics Lab III",
            "ರಸಾಯನಶಾಸ್ತ್ರ": "Chemistry Department",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್": "Chemistry Lab",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 3": "Chemistry Lab III",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೩": "Chemistry Lab III",
            "ಜೈವಿಕ ತಂತ್ರಜ್ಞಾನ": "Biotechnology Department",
            "ಬಯೋಟೆಕ್ ಲ್ಯಾಬ್": "Biotechnology Lab",
            "ಸೂಕ್ಷ್ಮ ಜೀವವಿಜ್ಞಾನ": "Microbiology Department",
            "भौतिकी": "Physics Department",
            "भौतिकी लैब": "Physics Lab",
            "भौतिक विज्ञान लैब 3": "Physics Lab III",
            "भौतिक विज्ञान प्रयोगशाला 3": "Physics Lab III",
            "रसायन विज्ञान": "Chemistry Department",
            "रसायन लैब": "Chemistry Lab",
            "रसायन विज्ञान लैब 3": "Chemistry Lab III",
            "रसायन विज्ञान प्रयोगशाला 3": "Chemistry Lab III",
            "chemistry lab 3": "Chemistry Lab III",
            "chemistry lab iii": "Chemistry Lab III",
            "physics lab 3": "Physics Lab III",
            "physics lab iii": "Physics Lab III",
            "बायोटेक्नोलॉजी": "Biotechnology Department",
            "बायोटेक लैब": "Biotechnology Lab",
            "माइक्रोबायोलॉजी": "Microbiology Department",
            "भाषा प्रयोगशाला": "Language Lab",

            # Administration & Principal
            "principal": "Principal Office",
            "principal office": "Principal Office",
            "principal room": "Principal Office",
            "admin": "Administrative Block Foyer",
            "admin block": "Administrative Block Foyer",
            "administrative office": "Administrative Office",
            "admin office": "Administrative Office",
            "accounts": "Administrative Office",
            "fee counter": "Administrative Office",
            "fee payment": "Administrative Office",
            "exam cell": "Controller of Examination",
            "examination": "Controller of Examination",
            "marks card": "Controller of Examination",
            "medical": "Medical & First Aid Room",
            "doctor": "Medical & First Aid Room",
            "first aid": "Medical & First Aid Room",
            "security": "Security Cabin",
            "main gate": "Main Gate",
            "gate": "Main Gate",
            "entrance": "Main Gate",
            "parking": "Parking Area & Ramp",
            "ಪ್ರಾಂಶುಪಾಲರ ಕೊಠಡಿ": "Principal Office",
            "ಪ್ರಿನ್ಸಿಪಾಲ್ ಆಫೀಸ್": "Principal Office",
            "ಆಡಳಿತ ಭವನ": "Administrative Block Foyer",
            "ಆಡಳಿತ ಕಚೇರಿ": "Administrative Office",
            "ಅಕೌಂಟ್ಸ್": "Administrative Office",
            "ಶುಲ್ಕ ಕೌಂಟರ್": "Administrative Office",
            "ಪರೀಕ್ಷಾ ವಿಭಾಗ": "Controller of Examination",
            "ವೈದ್ಯಕೀಯ ಕೊಠಡಿ": "Medical & First Aid Room",
            "ಮುಖ್ಯ ದ್ವಾರ": "Main Gate",
            "ಗೇಟ್": "Main Gate",
            "ಸೆಕ್ಯುರಿಟಿ": "Security Cabin",
            "ಪಾರ್ಕಿಂಗ್": "Parking Area & Ramp",
            "प्राचार्य कार्यालय": "Principal Office",
            "प्रिंसिपल ऑफिस": "Principal Office",
            "प्रशासन": "Administrative Block Foyer",
            "प्रशासनिक कार्यालय": "Administrative Office",
            "लेखा": "Administrative Office",
            "परीक्षा विभाग": "Controller of Examination",
            "चिकित्सा कक्ष": "Medical & First Aid Room",
            "मुख्य द्वार": "Main Gate",
            "गेट": "Main Gate",
            "सुरक्षा केबिन": "Security Cabin",
            # Restrooms, Washrooms & Toilets (Gents, Girls, Faculty, Multi-Floor)
            "gents washroom": "Gents Washroom",
            "gents toilet": "Gents Washroom",
            "gents restroom": "Gents Washroom",
            "men washroom": "Gents Washroom",
            "mens washroom": "Gents Washroom",
            "men toilet": "Gents Washroom",
            "mens toilet": "Gents Washroom",
            "boys washroom": "Gents Washroom",
            "boys toilet": "Gents Washroom",
            "male washroom": "Gents Washroom",
            "male restroom": "Gents Washroom",
            "ಪುರುಷರ ಶೌಚಾಲಯ": "Gents Washroom",
            "ಗಂಡಸರ ಶೌಚಾಲಯ": "Gents Washroom",
            "ಪುರುಷರ ವಾಶ್‌ರೂಂ": "Gents Washroom",
            "पुरुष शौचालय": "Gents Washroom",
            "जेंट्स वॉशरूम": "Gents Washroom",
            "जेंट्स टॉयलेट": "Gents Washroom",
            "पुरुषों का शौचालय": "Gents Washroom",

            "girls washroom": "Girls Washroom",
            "ladies washroom": "Girls Washroom",
            "ladies toilet": "Girls Washroom",
            "women washroom": "Girls Washroom",
            "womens washroom": "Girls Washroom",
            "women toilet": "Girls Washroom",
            "female washroom": "Girls Washroom",
            "female restroom": "Girls Washroom",
            "ಮಹಿಳೆಯರ ಶೌಚಾಲಯ": "Girls Washroom",
            "ಹೆಣ್ಣುಮಕ್ಕಳ ಶೌಚಾಲಯ": "Girls Washroom",
            "ಮಹಿಳಾ ಶೌಚಾಲಯ": "Girls Washroom",
            "महिला शौचालय": "Girls Washroom",
            "गर्ल्स वॉशरूम": "Girls Washroom",
            "लेडीज वॉशरूम": "Girls Washroom",
            "महिलाओं का शौचालय": "Girls Washroom",

            "washroom": "Girls Washroom",
            "restroom": "Girls Washroom",
            "toilet": "Girls Washroom",
            "bathroom": "Girls Washroom",
            "loo": "Girls Washroom",
            "ಶೌಚಾಲಯ": "Girls Washroom",
            "ಟಾಯ್ಲೆಟ್": "Girls Washroom",
            "ವಾಶ್‌ರೂಂ": "Girls Washroom",
            "ಶೌಚಗೃಹ": "Girls Washroom",
            "शौचालय": "Girls Washroom",
            "टॉयलेट": "Girls Washroom",
            "वॉशरूम": "Girls Washroom",
            "प्रसाधन": "Girls Washroom",

            "floor 1 washroom": "Floor 1 Student Washroom",
            "first floor washroom": "Floor 1 Student Washroom",
            "first floor toilet": "Floor 1 Student Washroom",
            "1st floor washroom": "Floor 1 Student Washroom",
            "faculty washroom": "Faculty Washroom (First Floor)",
            "teachers washroom": "Faculty Washroom (First Floor)",
            "floor 2 washroom": "Floor 2 West Restroom",
            "second floor washroom": "Floor 2 West Restroom",
            "second floor toilet": "Floor 2 West Restroom",
            "2nd floor washroom": "Floor 2 West Restroom",
            "floor 3 washroom": "Girls Wash Room (Student Lounge)",
            "third floor washroom": "Girls Wash Room (Student Lounge)",
            "lounge washroom": "Girls Wash Room (Student Lounge)",
            "3rd floor washroom": "Girls Wash Room (Student Lounge)",

            # IQAC & Quality Assurance (Video 1 Floor 2)
            "iqac": "IQAC (Internal Quality Assurance Cell)",
            "iqac office": "IQAC (Internal Quality Assurance Cell)",
            "iqac room": "IQAC (Internal Quality Assurance Cell)",
            "internal quality assurance cell": "IQAC (Internal Quality Assurance Cell)",
            "quality cell": "IQAC (Internal Quality Assurance Cell)",
            "quality assurance": "IQAC (Internal Quality Assurance Cell)",
            "ಐಕ್ಯುಎಸಿ": "IQAC (Internal Quality Assurance Cell)",
            "ಐಕ್ಯೂಎಸಿ": "IQAC (Internal Quality Assurance Cell)",
            "ಗುಣಮಟ್ಟ ಕೋಶ": "IQAC (Internal Quality Assurance Cell)",
            "आईक्यूएसी": "IQAC (Internal Quality Assurance Cell)",
            "गुणवत्ता प्रकोष्ठ": "IQAC (Internal Quality Assurance Cell)",

            # Mushroom Cultivation Facility (Video 2 Ground Floor)
            "mushroom": "Mushroom Cultivation Facility",
            "mushroom cultivation": "Mushroom Cultivation Facility",
            "mushroom facility": "Mushroom Cultivation Facility",
            "mushroom lab": "Mushroom Cultivation Facility",
            "ಅಣಬೆ ಬೇಸಾಯ ಕೇಂದ್ರ": "Mushroom Cultivation Facility",
            "ಅಣಬೆ ಕೃಷಿ": "Mushroom Cultivation Facility",
            "ಮಶ್ರೂಮ್ ಲ್ಯಾಬ್": "Mushroom Cultivation Facility",
            "मशरूम की खेती": "Mushroom Cultivation Facility",
            "मशरूम केंद्र": "Mushroom Cultivation Facility",

            # Food, Culture & Sports
            "canteen": "Canteen Area",
            "canteen area": "Canteen Area",
            "cafeteria": "Canteen Area",
            "food": "Canteen Area",
            "snacks": "Canteen Area",
            "lunch": "Canteen Area",
            "auditorium": "Golden Jubilee Seminar Hall",
            "audi": "Golden Jubilee Seminar Hall",
            "seminar hall": "Golden Jubilee Seminar Hall",
            "golden jubilee": "Golden Jubilee Seminar Hall",
            "sports": "Sports & Gym",
            "sports ground": "Sports & Gym",
            "ground": "Sports & Gym",
            "gym": "Sports & Gym",
            "gymnasium": "Sports & Gym",
            "fitness": "Sports & Gym",
            "ಕ್ಯಾಂಟೀನ್": "Canteen Area",
            "ಊಟದ ಕೊಠಡಿ": "Canteen Area",
            "ಆಡಿಟೋರಿಯಂ": "Golden Jubilee Seminar Hall",
            "ಸಭಾಂಗಣ": "Golden Jubilee Seminar Hall",
            "ಕ್ರೀಡಾಂಗಣ": "Sports & Gym",
            "ಗ್ರೌಂಡ್": "Sports & Gym",
            "ಜಿಮ್": "Sports & Gym",
            "ವ್ಯಾಯಾಮಶಾಲೆ": "Sports & Gym",
            "कैंटीन": "Canteen Area",
            "सभागार": "Golden Jubilee Seminar Hall",
            "ऑडिटोरियम": "Golden Jubilee Seminar Hall",
            "खेल का मैदान": "Sports & Gym",
            "ग्राउंड": "Sports & Gym",
            "जिम": "Sports & Gym",
            "व्यायामशाला": "Sports & Gym",

            # Other departments
            "commerce": "Commerce Department",
            "bcom": "Commerce Department",
            "management": "Management Department",
            "bba": "Management Department",
            "english": "English Department",
            "kannada": "Kannada Department",
            "psychology": "Language Lab",
            "journalism": "Dept. of Journalism",
            "journalism department": "Dept. of Journalism",
            "ವಾಣಿಜ್ಯ": "Commerce Department",
            "ಇಂಗ್ಲಿಷ್": "English Department",
            "ಕನ್ನಡ": "Kannada Department",
            "ಮನಃಶಾಸ್ತ್ರ": "Language Lab",
            "ಪತ್ರಿಕೋದ್ಯಮ": "Dept. of Journalism",
            "ಪತ್ರಿಕೋದ್ಯಮ ವಿಭಾಗ": "Dept. of Journalism",
            "वाणिज्य": "Commerce Department",
            "अंग्रेजी": "English Department",
            "कन्नड़": "Kannada Department",
            "मनोविज्ञान": "Language Lab",
            "पत्रकारिता": "Dept. of Journalism",
            "पत्रकारिता विभाग": "Dept. of Journalism",

            # Ground Floor Blueprint Additions (Classrooms G1 - G8)
            "g1": "Classroom G1", "classroom g1": "Classroom G1", "g1 classroom": "Classroom G1", "room g1": "Classroom G1",
            "g2": "Classroom G2", "classroom g2": "Classroom G2", "g2 classroom": "Classroom G2", "room g2": "Classroom G2",
            "g3": "Classroom G3", "classroom g3": "Classroom G3", "g3 classroom": "Classroom G3", "room g3": "Classroom G3",
            "g4": "Classroom G4", "classroom g4": "Classroom G4", "g4 classroom": "Classroom G4", "room g4": "Classroom G4",
            "g5": "Classroom G5", "classroom g5": "Classroom G5", "g5 classroom": "Classroom G5", "room g5": "Classroom G5",
            "g6": "Classroom G6", "classroom g6": "Classroom G6", "g6 classroom": "Classroom G6", "room g6": "Classroom G6",
            "g7": "Classroom G7", "classroom g7": "Classroom G7", "g7 classroom": "Classroom G7", "room g7": "Classroom G7",
            "g8": "Classroom G8", "classroom g8": "Classroom G8", "g8 classroom": "Classroom G8", "room g8": "Classroom G8",
            "g9": "Classroom G9", "classroom g9": "Classroom G9", "g9 classroom": "Classroom G9", "room g9": "Classroom G9",
            "g10": "Classroom G10", "classroom g10": "Classroom G10", "g10 classroom": "Classroom G10", "room g10": "Classroom G10",
            "g11": "Classroom G11", "classroom g11": "Classroom G11", "g11 classroom": "Classroom G11", "room g11": "Classroom G11",
            "ತರಗತಿ g1": "Classroom G1", "ತರಗತಿ ಜಿ ೧": "Classroom G1", "ತರಗತಿ g8": "Classroom G8", "ತರಗತಿ ಜಿ ೮": "Classroom G8",
            "ತರಗತಿ g9": "Classroom G9", "ತರಗತಿ ಜಿ ೯": "Classroom G9", "ತರಗತಿ g10": "Classroom G10", "ತರಗತಿ ಜಿ ೧೦": "Classroom G10",
            "ತರಗತಿ g11": "Classroom G11", "ತರಗತಿ ಜಿ ೧೧": "Classroom G11",
            "कक्षा g1": "Classroom G1", "कक्षा जी 1": "Classroom G1", "कक्षा जी 5": "Classroom G5", "कक्षा g8": "Classroom G8",
            "कक्षा g9": "Classroom G9", "कक्षा जी 9": "Classroom G9", "कक्षा g10": "Classroom G10", "कक्षा जी 10": "Classroom G10",
            "कक्षा g11": "Classroom G11", "कक्षा जी 11": "Classroom G11",

            # Golden Jubilee Seminar Hall, Reprography, Mushroom Cultivation
            "golden jubilee": "Golden Jubilee Seminar Hall",
            "golden jubilee hall": "Golden Jubilee Seminar Hall",
            "golden jubilee seminar hall": "Golden Jubilee Seminar Hall",
            "ಗೋಲ್ಡನ್ ಜುಬಿಲಿ": "Golden Jubilee Seminar Hall",
            "ಗೋಲ್ಡನ್ ಜುಬಿಲಿ ಹಾಲ್": "Golden Jubilee Seminar Hall",
            "ಗೋಲ್ಡನ್ ಜುಬಿಲಿ ಸೆಮಿನಾರ್ ಹಾಲ್": "Golden Jubilee Seminar Hall",
            "गोल्डन जुबली": "Golden Jubilee Seminar Hall",
            "गोल्डन जुबली सेमिनार हॉल": "Golden Jubilee Seminar Hall",
            "reprography": "Reprography Room",
            "reprography room": "Reprography Room",
            "printing room": "Reprography Room",
            "ರಿಪ್ರೋಗ್ರಫಿ": "Reprography Room",
            "ರಿಪ್ರೋಗ್ರಫಿ ಕೊಠಡಿ": "Reprography Room",
            "ರಿಪ್ರೊಗ್ರಾಫಿ": "Reprography Room",
            "रिप्रोग्राफी": "Reprography Room",
            "रिप्रोग्राफी कक्ष": "Reprography Room",
            "mushroom": "Mushroom Cultivation Facility",
            "mushroom cultivation": "Mushroom Cultivation Facility",
            "mushroom cultivation lab": "Mushroom Cultivation Facility",
            "mushroom cultivation facility": "Mushroom Cultivation Facility",
            "mushroom room": "Mushroom Cultivation Facility",
            "ಅಣಬೆ ಕೃಷಿ": "Mushroom Cultivation Facility",
            "ಅಣಬೆ ಕೊಠಡಿ": "Mushroom Cultivation Facility",
            "मशरूम": "Mushroom Cultivation Facility",
            "मशरूम की खेती": "Mushroom Cultivation Facility",

            # Controller of Examination, Sports & Gym, Washroom, Canteen Area
            "controller of examination": "Controller of Examination",
            "coe": "Controller of Examination",
            "coe office": "Controller of Examination",
            "controller office": "Controller of Examination",
            "ಪರೀಕ್ಷಾ ನಿಯಂತ್ರಕರು": "Controller of Examination",
            "ಪರೀಕ್ಷಾ ನಿಯಂತ್ರಕರ ಕಚೇರಿ": "Controller of Examination",
            "परीक्षा नियंत्रक": "Controller of Examination",
            "परीक्षा नियंत्रक कार्यालय": "Controller of Examination",
            "sports & gym": "Sports & Gym",
            "sports and gym": "Sports & Gym",
            "gym & sports": "Sports & Gym",
            "ಕ್ರೀಡೆ ಮತ್ತು ಜಿಮ್": "Sports & Gym",
            "खेलकूद एवं जिम": "Sports & Gym",
            "girls washroom": "Girls Washroom",
            "washroom": "Girls Washroom",
            "restroom": "Girls Washroom",
            "ladies washroom": "Girls Washroom",
            "toilet": "Girls Washroom",
            "ಶೌಚಾಲಯ": "Girls Washroom",
            "ಮಹಿಳಾ ಶೌಚಾಲಯ": "Girls Washroom",
            "महिला प्रसाधन गृह": "Girls Washroom",
            "canteen area": "Canteen Area",
            "canteen kitchen": "Canteen Kitchen",
            "kitchen": "Canteen Kitchen",
            "ಕ್ಯಾಂಟೀನ್ ಆವರಣ": "Canteen Area",
            "ಕ್ಯಾಂಟೀನ್ ಅಡುಗೆಮನೆ": "Canteen Kitchen",
            "कैंटीन परिसर": "Canteen Area",
            "कैंटीन रसोई": "Canteen Kitchen",

            # Courtyard Kiosk & Stairs
            "xerox": "Xerox & Stationery Kiosk",
            "stationery": "Xerox & Stationery Kiosk",
            "stationery kiosk": "Xerox & Stationery Kiosk",
            "xerox shop": "Xerox & Stationery Kiosk",
            "ಜೆರಾಕ್ಸ್": "Xerox & Stationery Kiosk",
            "ಸ್ಟೇಷನರಿ": "Xerox & Stationery Kiosk",
            "ज़ेरॉक्स": "Xerox & Stationery Kiosk",
            "pu stairs": "PU College Stairs",
            "pu college stairs": "PU College Stairs",
            "south stairs": "South Staircase",
            "south staircase": "South Staircase",
            "main reception staircase": "Main Reception Staircase",
            "main reception stairs": "Main Reception Staircase",
            "reception stairs": "Main Reception Staircase",
            "stairs opposite reception": "Main Reception Staircase",
            "staircase opposite reception": "Main Reception Staircase",
            "main stairs": "Main Reception Staircase",
            "main staircase": "Main Reception Staircase",
            "foyer stairs": "Main Reception Staircase",
            "entrance stairs": "Main Reception Staircase",
            "ಮುಖ್ಯ ಮೆಟ್ಟಿಲು": "Main Reception Staircase",
            "ರಿಸೆಪ್ಷನ್ ಎದುರಿನ ಮೆಟ್ಟಿಲು": "Main Reception Staircase",
            "ಸ್ವಾಗತ ಕೌಂಟರ್ ಮೆಟ್ಟಿಲು": "Main Reception Staircase",
            "ಪ್ರವೇಶ ಮೆಟ್ಟಿಲು": "Main Reception Staircase",
            "रिसेप्शन की सीढ़ियाँ": "Main Reception Staircase",
            "मुख्य सीढ़ियाँ": "Main Reception Staircase",
            "स्वागत काउंटर सीढ़ियाँ": "Main Reception Staircase",

            # First Floor Classrooms F1 - F5
            "f1": "Classroom F1", "classroom f1": "Classroom F1", "f1 classroom": "Classroom F1", "room f1": "Classroom F1",
            "f2": "Classroom F2", "classroom f2": "Classroom F2", "f2 classroom": "Classroom F2", "room f2": "Classroom F2",
            "f3": "Classroom F3", "classroom f3": "Classroom F3", "f3 classroom": "Classroom F3", "room f3": "Classroom F3",
            "f4": "Classroom F4", "classroom f4": "Classroom F4", "f4 classroom": "Classroom F4", "room f4": "Classroom F4",
            "f5": "Classroom F5", "classroom f5": "Classroom F5", "f5 classroom": "Classroom F5", "room f5": "Classroom F5",
            "ತರಗತಿ f1": "Classroom F1", "ತರಗತಿ ಎಫ್ ೧": "Classroom F1", "ತರಗತಿ f5": "Classroom F5", "ತರಗತಿ ಎಫ್ ೫": "Classroom F5",
            "ಕಕ್ಷೆ f1": "Classroom F1", "ಕಕ್ಷೆ ಎಫ್ ೧": "Classroom F1", "ಕಕ್ಷೆ f5": "Classroom F5", "ಕಕ್ಷೆ ಎಫ್ ೫": "Classroom F5",
            "ಎಫ್ ೧": "Classroom F1", "ಎಫ್ ೨": "Classroom F2", "ಎಫ್ ೩": "Classroom F3", "ಎಫ್ ೪": "Classroom F4", "ಎಫ್ ೫": "Classroom F5",
            "कक्षा f1": "Classroom F1", "कक्षा एफ 1": "Classroom F1", "कक्षा f5": "Classroom F5", "कक्षा एफ 5": "Classroom F5",
            "एफ 1": "Classroom F1", "एफ 2": "Classroom F2", "एफ 3": "Classroom F3", "एफ 4": "Classroom F4", "एफ 5": "Classroom F5",

            # First Floor Chemistry Laboratories & Department
            "chemistry lab 1": "Chemistry Lab I", "chemistry lab i": "Chemistry Lab I",
            "chemistry lab 2": "Chemistry Lab II", "chemistry lab ii": "Chemistry Lab II",
            "chemistry lab 3": "Chemistry Lab III", "chemistry lab iii": "Chemistry Lab III",
            "chemistry research": "Chemistry Research Centre", "chemistry research centre": "Chemistry Research Centre",
            "chemistry research lab": "Chemistry Research Centre", "chemistry research center": "Chemistry Research Centre",
            "dept of chemistry": "Dept. of Chemistry & Staff Room", "chemistry staff room": "Dept. of Chemistry & Staff Room",
            "chemistry staff": "Dept. of Chemistry & Staff Room", "dept of chemistry & staff room": "Dept. of Chemistry & Staff Room",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 1": "Chemistry Lab I", "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ ೧": "Chemistry Lab I",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 2": "Chemistry Lab II", "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ ೨": "Chemistry Lab II",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 3": "Chemistry Lab III", "ರಸಾಯನಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ ೩": "Chemistry Lab III",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಸಂಶೋಧನೆ": "Chemistry Research Centre",
            "ರಸಾಯನಶಾಸ್ತ್ರ ಸಿಬ್ಬಂದಿ ಕೊಠಡಿ": "Dept. of Chemistry & Staff Room",
            "रसायन लैब 1": "Chemistry Lab I", "रसायन लैब 2": "Chemistry Lab II", "रसायन लैब 3": "Chemistry Lab III",
            "रसायन अनुसंधान": "Chemistry Research Centre", "रसायन स्टाफ रूम": "Dept. of Chemistry & Staff Room",

            # First Floor Physics Laboratories & Departments
            "physics lab 1": "Physics Lab I", "physics lab i": "Physics Lab I",
            "physics lab 2": "Physics Lab II", "physics lab ii": "Physics Lab II",
            "physics lab 3": "Physics Lab III", "physics lab iii": "Physics Lab III",
            "pu physics": "Dept. of Physics (PU)", "dept of physics pu": "Dept. of Physics (PU)",
            "ug physics": "Dept. of Physics (UG) & Faculty Chamber", "dept of physics ug": "Dept. of Physics (UG) & Faculty Chamber",
            "physics staff room": "Dept. of Physics (UG) & Faculty Chamber",
            "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 1": "Physics Lab I", "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ ೧": "Physics Lab I",
            "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 2": "Physics Lab II", "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ ೨": "Physics Lab II",
            "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ 3": "Physics Lab III", "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್ ೩": "Physics Lab III",
            "ಪಿಯು ಭೌತಶಾಸ್ತ್ರ": "Dept. of Physics (PU)", "ಪದವಿ ಭೌತಶಾಸ್ತ್ರ": "Dept. of Physics (UG) & Faculty Chamber",
            "भौतिकी लैब 1": "Physics Lab I", "भौतिकी लैब 2": "Physics Lab II", "भौतिकी लैब 3": "Physics Lab III",
            "पीयू भौतिकी": "Dept. of Physics (PU)", "यूजी भौतिकी": "Dept. of Physics (UG) & Faculty Chamber",

            # First Floor Life Sciences & Botany
            "biotech pg": "Biotechnology Lab (PG)", "biotechnology pg": "Biotechnology Lab (PG)", "biotech pg lab": "Biotechnology Lab (PG)",
            "biotech ug": "Biotechnology Lab (UG)", "biotechnology ug": "Biotechnology Lab (UG)", "biotech ug lab": "Biotechnology Lab (UG)",
            "zoology lab": "Zoology Lab (UG)", "zoology ug": "Zoology Lab (UG)", "zoology ug lab": "Zoology Lab (UG)",
            "life sciences staff room": "Dept. of Life Sciences Staff Room", "zoology staff room": "Dept. of Life Sciences Staff Room",
            "biochem pg": "Biochemistry Lab (PG)", "biochemistry pg": "Biochemistry Lab (PG)", "biochemistry lab": "Biochemistry Lab (PG)",
            "biochemistry lab pg": "Biochemistry Lab (PG)",
            "botany pg": "Botany Lab (PG)", "botany pg lab": "Botany Lab (PG)", "botany lab pg": "Botany Lab (PG)",
            "botany ug": "Botany Lab (UG)", "botany ug lab": "Botany Lab (UG)", "botany lab ug": "Botany Lab (UG)",
            "botany dept": "Dept. of Botany", "dept of botany": "Dept. of Botany", "botany": "Dept. of Botany",
            "microbiology floor 1": "Microbiology Lab (Floor 1)", "first floor microbiology": "Microbiology Lab (Floor 1)",
            "journalism dept": "Dept. of Journalism", "dept of journalism": "Dept. of Journalism",
            "faculty washroom": "Faculty Washroom (First Floor)", "staff washroom": "Faculty Washroom (First Floor)",
            "floor 1 washroom": "Floor 1 Student Washroom", "first floor washroom": "Floor 1 Student Washroom",
            "ಸಸ್ಯಶಾಸ್ತ್ರ": "Dept. of Botany", "ಸಸ್ಯಶಾಸ್ತ್ರ ವಿಭಾಗ": "Dept. of Botany",
            "ಪ್ರಾಣಿಶಾಸ್ತ್ರ": "Zoology Lab (UG)", "ಪ್ರಾಣಿಶಾಸ್ತ್ರ ಲ್ಯಾಬ್": "Zoology Lab (UG)",
            "ಬಯೋಕೆಮಿಸ್ಟ್ರಿ": "Biochemistry Lab (PG)", "ಬಯೋಕೆಮಿಸ್ಟ್ರಿ ಲ್ಯಾಬ್": "Biochemistry Lab (PG)",
            "वनस्पति विज्ञान": "Dept. of Botany", "जंतु विज्ञान": "Zoology Lab (UG)", "जैव रसायन": "Biochemistry Lab (PG)",

            # Garden Walkway
            "garden": "College Garden Walkway", "college garden": "College Garden Walkway", "garden walkway": "College Garden Walkway",
            "garden path": "College Garden Walkway", "garden side": "College Garden Walkway",
            "ಗಾರ್ಡನ್": "College Garden Walkway", "ಉದ್ಯಾನವನ": "College Garden Walkway", "ಕಾಲೇಜು ಗಾರ್ಡನ್": "College Garden Walkway",
            "गार्डन": "College Garden Walkway", "बगीचा": "College Garden Walkway",

            # Second Floor Classrooms S1 - S12
            "s1": "Classroom S1", "classroom s1": "Classroom S1", "s1 classroom": "Classroom S1", "room s1": "Classroom S1",
            "s2": "Classroom S2", "classroom s2": "Classroom S2", "s2 classroom": "Classroom S2", "room s2": "Classroom S2",
            "s3": "Classroom S3", "classroom s3": "Classroom S3", "s3 classroom": "Classroom S3", "room s3": "Classroom S3",
            "s4": "Classroom S4", "classroom s4": "Classroom S4", "s4 classroom": "Classroom S4", "room s4": "Classroom S4",
            "s5": "Classroom S5", "classroom s5": "Classroom S5", "s5 classroom": "Classroom S5", "room s5": "Classroom S5",
            "s6": "Classroom S6", "classroom s6": "Classroom S6", "s6 classroom": "Classroom S6", "room s6": "Classroom S6",
            "s7": "Classroom S7", "classroom s7": "Classroom S7", "s7 classroom": "Classroom S7", "room s7": "Classroom S7",
            "s8": "Classroom S8", "classroom s8": "Classroom S8", "s8 classroom": "Classroom S8", "room s8": "Classroom S8",
            "s9": "Classroom S9", "classroom s9": "Classroom S9", "s9 classroom": "Classroom S9", "room s9": "Classroom S9",
            "s10": "Classroom S10", "classroom s10": "Classroom S10", "s10 classroom": "Classroom S10", "room s10": "Classroom S10",
            "s11": "Classroom S11", "classroom s11": "Classroom S11", "s11 classroom": "Classroom S11", "room s11": "Classroom S11",
            "s12": "Classroom S12", "classroom s12": "Classroom S12", "s12 classroom": "Classroom S12", "room s12": "Classroom S12",
            "ತರಗತಿ s1": "Classroom S1", "ತರಗತಿ ಎಸ್ ೧": "Classroom S1", "ಎಸ್ ೧": "Classroom S1",
            "ತರಗತಿ s9": "Classroom S9", "ತರಗತಿ ಎಸ್ ೯": "Classroom S9", "ಎಸ್ ೯": "Classroom S9",
            "ತರಗತಿ s10": "Classroom S10", "ತರಗತಿ ಎಸ್ ೧೦": "Classroom S10", "ಎಸ್ ೧೦": "Classroom S10",
            "ತರಗತಿ s11": "Classroom S11", "ತರಗತಿ ಎಸ್ ೧೧": "Classroom S11", "ಎಸ್ ೧೧": "Classroom S11",
            "ತರಗತಿ s12": "Classroom S12", "ತರಗತಿ ಎಸ್ ೧೨": "Classroom S12", "ಎಸ್ ೧೨": "Classroom S12",
            "कक्षा s1": "Classroom S1", "कक्षा एस 1": "Classroom S1", "एस 1": "Classroom S1",
            "कक्षा s9": "Classroom S9", "कक्षा एस 9": "Classroom S9", "एस 9": "Classroom S9",
            "कक्षा s10": "Classroom S10", "कक्षा एस 10": "Classroom S10", "एस 10": "Classroom S10",
            "कक्षा s11": "Classroom S11", "कक्षा एस 11": "Classroom S11", "एस 11": "Classroom S11",
            "कक्षा s12": "Classroom S12", "कक्षा एस 12": "Classroom S12", "एस 12": "Classroom S12",

            # Third Floor Student Lounge & Lecture Hall
            "lounge": "Student Open Lounge (Third Floor Level)",
            "student lounge": "Student Open Lounge (Third Floor Level)",
            "open lounge": "Student Open Lounge (Third Floor Level)",
            "third floor lounge": "Student Open Lounge (Third Floor Level)",
            "rest lounge": "Student Open Lounge (Third Floor Level)",
            "student rest area": "Student Open Lounge (Third Floor Level)",
            "student rest room": "Student Open Lounge (Third Floor Level)",
            "girls lounge": "Student Open Lounge (Third Floor Level)",
            "ಲೌಂಜ್": "Student Open Lounge (Third Floor Level)",
            "ವಿಶ್ರಾಂತಿ ಲೌಂಜ್": "Student Open Lounge (Third Floor Level)",
            "ವಿದ್ಯಾರ್ಥಿನಿಯರ ವಿಶ್ರಾಂತಿ ಲೌಂಜ್": "Student Open Lounge (Third Floor Level)",
            "ಲಾಉಂಜ್": "Student Open Lounge (Third Floor Level)",
            "लाउंज": "Student Open Lounge (Third Floor Level)",
            "ओपन लाउंज": "Student Open Lounge (Third Floor Level)",
            "छात्रा लाउंज": "Student Open Lounge (Third Floor Level)",
            "विश्राम लाउंज": "Student Open Lounge (Third Floor Level)",

            "lecture hall": "Third Floor Lecture Hall",
            "third floor lecture hall": "Third Floor Lecture Hall",
            "lecture hall 3": "Third Floor Lecture Hall",
            "lh3": "Third Floor Lecture Hall",
            "ಉಪನ್ಯಾಸ ಭವನ": "Third Floor Lecture Hall",
            "ಲೆಕ್ಚರ್ ಹಾಲ್": "Third Floor Lecture Hall",
            "व्याख्यान हॉल": "Third Floor Lecture Hall",
            "लेक्चर हॉल": "Third Floor Lecture Hall",

            # Second & Third Floor Science / Computer Facilities
            "cs department": "Dept. of Computer Science & Staff Room",
            "computer science department": "Dept. of Computer Science & Staff Room",
            "cs staff room": "Dept. of Computer Science & Staff Room",
            "electronics lab": "Electronics & Hardware Lab",
            "hardware lab": "Electronics & Hardware Lab",
            "electronics & hardware lab": "Electronics & Hardware Lab",
            "tissue culture": "Tissue Culture Lab & Media Room",
            "tissue culture lab": "Tissue Culture Lab & Media Room",
            "biotech research": "Biotechnology Research Lab",
            "biotech research lab": "Biotechnology Research Lab",
            "microbiology research": "Microbiology Department & Research Lab",
            "microbiology research lab": "Microbiology Department & Research Lab",
            "scholars lab": "Scholars Research Lab",
            "scholars research lab": "Scholars Research Lab",
            "project lab": "Project & Analytical Lab",
            "analytical lab": "Project & Analytical Lab",
            "project & analytical lab": "Project & Analytical Lab",
            "store room": "Instrumentation & Store Room",
            "knv shastri auditorium": "KNV Shastri Auditorium",
            "knv shastri": "KNV Shastri Auditorium",
            "knv sastri auditorium": "KNV Shastri Auditorium",
            "knv sastri": "KNV Shastri Auditorium",
            "knv auditorium": "KNV Shastri Auditorium",
            "shastri auditorium": "KNV Shastri Auditorium",
            "second floor auditorium": "KNV Shastri Auditorium",
            "2nd floor auditorium": "KNV Shastri Auditorium",
            "floor 2 auditorium": "KNV Shastri Auditorium",
            "auditorium gallery": "KNV Shastri Auditorium",
            "gallery": "KNV Shastri Auditorium",
            "south-east auditorium gallery": "KNV Shastri Auditorium",
            "south east auditorium gallery": "KNV Shastri Auditorium",
            "ಕೆಎನ್‌ವಿ ಶಾಸ್ತ್ರಿ ಸಭಾಂಗಣ": "KNV Shastri Auditorium",
            "ಕೆಎನ್‌ವಿ ಶಾಸ್ತ್ರಿ": "KNV Shastri Auditorium",
            "ಕೆಎನ್‌ವಿ ಆಡಿಟೋರಿಯಂ": "KNV Shastri Auditorium",
            "2ನೇ ಮಹಡಿ ಆಡಿಟೋರಿಯಂ": "KNV Shastri Auditorium",
            "ಸಭಾಂಗಣ 2ನೇ ಮಹಡಿ": "KNV Shastri Auditorium",
            "केएनवी शास्त्री ऑडिटोरियम": "KNV Shastri Auditorium",
            "केएनवी शास्त्री": "KNV Shastri Auditorium",
            "केएनवी ऑडिटोरियम": "KNV Shastri Auditorium",
            "दूसरी मंजिल ऑडिटोरियम": "KNV Shastri Auditorium",
        }

        for k, v in custom_synonyms.items():
            self.alias_to_canonical[k.strip().lower()] = v

    def detect_language(self, text: str) -> str:
        """Identifies language based on Unicode character blocks."""
        kannada_chars = len(re.findall(r'[\u0C80-\u0CFF]', text))
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))

        if kannada_chars > 0:
            return "Kannada"
        elif devanagari_chars > 0:
            return "Hindi"
        return "English"

    def detect_intent(self, text: str) -> str:
        """Determines if query is Navigate, Locate, or General Information."""
        t = text.lower()
        navigate_indicators = [
            "take me", "guide me", "how to reach", "route to", "way to", "directions to", "walk to", "go to",
            "ಹೋಗುವುದು ಹೇಗೆ", "ಹೋಗಬೇಕು", "ದಾರಿ", "ತೋರಿಸಿ", "ಮಾರ್ಗ", "ಕರ್ಕೊಂಡು ಹೋಗಿ",
            "जाना है", "रास्ता बताओ", "कैसे पहुंचे", "दिशा बताओ", "ले चलो"
        ]
        locate_indicators = [
            "where is", "locate", "where", "location of", "find",
            "ಎಲ್ಲಿದೆ", "ಎಲ್ಲಿ", "ಸ್ಥಳ", "ಎಲ್ಲಿ ಬರುತ್ತದೆ",
            "कहाँ है", "किधर है", "कहाँ स्थित है", "कहा है"
        ]

        for ind in navigate_indicators:
            if ind in t:
                return "Navigate"
        for ind in locate_indicators:
            if ind in t:
                return "Locate"

        return "Navigate" if len(text.strip()) > 3 else "Locate"

    def parse_query(self, query_text: str) -> Dict:
        """
        Parses user query and maps to canonical node.
        Returns:
            dict: {
                "detected_language": str,
                "intent": str,
                "matched_node": Optional[str],
                "confidence": float,
                "is_wheelchair_mode": bool,
                "clean_query": str
            }
        """
        raw_text = query_text.strip()
        if not raw_text:
            return {
                "detected_language": "English",
                "intent": "None",
                "matched_node": None,
                "confidence": 0.0,
                "is_wheelchair_mode": False,
                "clean_query": ""
            }

        lang = self.detect_language(raw_text)
        intent = self.detect_intent(raw_text)

        # Check for wheelchair mode trigger in query
        wheelchair_triggers = ["wheelchair", "accessible", "barrier free", "ramp", "ಲಿಫ್ಟ್", "ವೀಲ್ ಚೇರ್", "व्हीलचेयर", "रैंप"]
        is_wheelchair = any(w in raw_text.lower() for w in wheelchair_triggers)

        # Strip common punctuation
        clean_text = re.sub(r'[?!.,;:"\'()\-]', ' ', raw_text).strip()
        lower_clean = clean_text.lower()

        best_node = None
        best_confidence = 0.0

        # Pass 1: Direct Substring matching across synonyms (longest key match first)
        sorted_keys = sorted(self.alias_to_canonical.keys(), key=lambda x: len(x), reverse=True)
        for alias in sorted_keys:
            if len(alias) >= 3 and alias in lower_clean:
                best_node = self.alias_to_canonical[alias]
                best_confidence = 0.98 if len(alias) > 5 else 0.90
                break

        # Pass 2: Fuzzy match if no direct substring match found
        if not best_node:
            words = lower_clean.split()
            # Try 3-gram, 2-gram, then 1-gram
            candidates = []
            for n in [3, 2, 1]:
                for i in range(len(words) - n + 1):
                    candidates.append(" ".join(words[i:i+n]))

            for cand in candidates:
                matches = difflib.get_close_matches(cand, self.alias_to_canonical.keys(), n=1, cutoff=0.75)
                if matches:
                    matched_alias = matches[0]
                    best_node = self.alias_to_canonical[matched_alias]
                    best_confidence = 0.85
                    break

        # Pass 3: Check against raw location names in English
        if not best_node:
            for loc_name in self.locations_dict.keys():
                if loc_name.lower() in lower_clean:
                    best_node = loc_name
                    best_confidence = 0.95
                    break

        # Safety verification: ensure matched node exists in locations_dict
        if best_node and best_node not in self.locations_dict:
            best_node = None
            best_confidence = 0.0

        return {
            "detected_language": lang,
            "intent": intent,
            "matched_node": best_node,
            "confidence": best_confidence if best_node else 0.0,
            "is_wheelchair_mode": is_wheelchair,
            "clean_query": clean_text
        }
