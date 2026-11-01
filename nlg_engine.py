"""
Pedestrian Turn-by-Turn Natural Language Generation (NLG) Engine
Translates mathematical graph node sequences into natural, human-readable directives.
Provides progressive checkpoint guidance, bilateral landmark orientation cues,
automatic corridor and multi-floor compression, natural disorientation recovery,
distance cues, and walking ETAs.
"""

import math
from typing import List, Dict, Any, Optional

class CampusNLGEngine:
    def __init__(self, locations_dict: Dict[str, Dict]):
        self.locations_dict = locations_dict

    def _get_localized_name(self, node_name: str, language: str) -> str:
        info = self.locations_dict.get(node_name, {})
        if language == "Kannada" and info.get("kannada_name"):
            return info["kannada_name"]
        elif language == "Hindi" and info.get("hindi_name"):
            return info["hindi_name"]
        return node_name

    def _get_landmark_verification(self, from_node: str, to_node: str, stype: str, to_floor: int, language: str = "English") -> Dict[str, str]:
        """
        Computes physical checkpoint landmarks and turn boundary verification conditions.
        Enforces concrete visual anchors: Plaques, Pillars, Doorways, Railings.
        """
        # 1. Main Entrance & Gate
        if from_node == "Main Gate":
            if to_node == "Main Reception Staircase":
                if language == "Kannada":
                    return {
                        "landmark": "ರಿಸೆಪ್ಷನ್ ಕೌಂಟರ್ ಮತ್ತು ಗಣೇಶ ವಿಗ್ರಹ",
                        "cue": "ರಿಸೆಪ್ಷನ್ ಕೌಂಟರ್ ಎದುರಿಗಿರುವ ಮುಖ್ಯ ಸ್ವಾಗತ ಮೆಟ್ಟಿಲಿನ ಮುಂದೆ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಮುಖ್ಯ ದ್ವಾರವು ನಿಮ್ಮ ಹಿಂಭಾಗದಲ್ಲಿರಬೇಕು ಮತ್ತು ಗಣೇಶ ವಿಗ್ರಹವಿರುವ ರಿಸೆಪ್ಷನ್ ಕೌಂಟರ್ ನೇರವಾಗಿ ಎದುರಿಗೆ ಇರಬೇಕು. ಪ್ರವೇಶ ದ್ವಾರವು ಮುಂದೆ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "रिसेप्शन काउंटर और गणेश प्रतिमा",
                        "cue": "रिसेप्शन काउंटर के ठीक सामने मुख्य स्वागत सीढ़ियों के पास रुकें। सत्यापन: मुख्य द्वार आपके पीछे होना चाहिए और गणेश प्रतिमा वाला रिसेप्शन काउंटर ठीक सामने होना चाहिए। यदि प्रवेश द्वार आगे दिखे, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Main Reception Desk & Ganesha Idol",
                    "cue": "Stop before the Main Reception Staircase directly opposite the reception desk. Check: The main entrance gate should be behind you and the reception counter with Ganesha idol directly ahead. If the entrance gate is ahead of you, simply turn around."
                }
            elif to_node == "College Garden Walkway":
                if language == "Kannada":
                    return {
                        "landmark": "ಉದ್ಯಾನವನ ಮಾರ್ಗ (Garden Walkway)",
                        "cue": "ಉದ್ಯಾನವನ ಮಾರ್ಗದ ಪ್ರಾರಂಭದಲ್ಲಿ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಹಸಿರು ಉದ್ಯಾನವನದ ಹಾದಿಯು ನಿಮ್ಮ ಬಲಭಾಗದಲ್ಲಿರಬೇಕು ಮತ್ತು ಮುಖ್ಯ ಕಟ್ಟಡ ಎಡಭಾಗದಲ್ಲಿರಬೇಕು. ವಿರುದ್ಧವಾಗಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "कॉलेज गार्डन वॉकवे",
                        "cue": "गार्डन प्रोमेनेड के मोड़ पर रुकें। सत्यापन: हरा-भरा गार्डन वॉकवे आपकी दाईं ओर और मुख्य इमारत बाईं ओर होनी चाहिए। यदि यह विपरीत है, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Lush College Garden Walkway",
                    "cue": "Stop at the start of the garden promenade. Check: The green garden walkway should be on your right hand side and the main building on your left. If the garden is on your left, simply turn around."
                }
            elif to_node == "Administrative Block Foyer":
                if language == "Kannada":
                    return {
                        "landmark": "ಸಂಸ್ಥಾಪಕ ಡಾ. ಎಂ.ಸಿ. ಶಾಸ್ತ್ರಿ ಅವರ ಪ್ರತಿಮೆ",
                        "cue": "ಮುಖಮಂಟಪದಲ್ಲಿರುವ ಸಂಸ್ಥಾಪಕರ ಪ್ರತಿಮೆಯ ಬಳಿ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಸಂಸ್ಥಾಪಕ ಡಾ. ಎಂ.ಸಿ. ಶಾಸ್ತ್ರಿ ಅವರ ಪ್ರತಿಮೆ ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲೂ, ರಿಸೆಪ್ಷನ್ ಡೆಸ್ಕ್ ನೇರವಾಗಿ ಮುಂದಿರಬೇಕು. ಭದ್ರತಾ ದ್ವಾರವು ಮುಂದೆ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "संस्थापक डॉ. एम.सी. शास्त्री की प्रतिमा",
                        "cue": "फ़ोयर में संस्थापक की प्रतिमा के पास रुकें। सत्यापन: संस्थापक डॉ. एम.सी. शास्त्री की प्रतिमा आपकी बाईं ओर और मुख्य रिसेप्शन डेस्क सीधे आगे होनी चाहिए। यदि सुरक्षा द्वार आगे दिखे, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Security Check Post & Founder's Bust",
                    "cue": "Stop at the founder's memorial bust inside the foyer. Check: Founder Director Dr. M. C. Sastri's bust should be on your left hand side and the main reception desk directly ahead. If the security gate is ahead, simply turn around."
                }

        # 2. Administrative Foyer Turns
        if from_node == "Administrative Block Foyer":
            if to_node == "Main Reception Staircase":
                if language == "Kannada":
                    return {
                        "landmark": "ರಿಸೆಪ್ಷನ್ ಕೌಂಟರ್ ಮತ್ತು ಗಣೇಶ ವಿಗ್ರಹ",
                        "cue": "ರಿಸೆಪ್ಷನ್ ಎದುರಿನ ಮೆಟ್ಟಿಲಿನ ಮುಂದೆ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಗಣೇಶ ವಿಗ್ರಹವಿರುವ ಆಡಳಿತ ರಿಸೆಪ್ಷನ್ ಕೌಂಟರ್ ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲೂ, ಮೆಟ್ಟಿಲು ನೇರವಾಗಿ ಮುಂದಿರಬೇಕು. ಹೊರಗಿನ ಉದ್ಯಾನವನ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "रिसेप्शन काउंटर और गणेश प्रतिमा",
                        "cue": "रिसेप्शन के सामने सीढ़ियों के पास रुकें। सत्यापन: गणेश प्रतिमा वाला प्रशासनिक रिसेप्शन काउंटर आपकी बाईं ओर और सीढ़ियाँ ठीक आगे होनी चाहिए। यदि बगीचा दिखे, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Main Reception Counter & Ganesha Idol",
                    "cue": "Stop before the staircase opposite the reception desk. Check: The administrative reception desk with Ganesha idol should be directly on your left and the staircase directly ahead. If the outdoor garden is ahead, simply turn around."
                }
            elif "Classroom G" in to_node or to_node == "PU College Stairs":
                if language == "Kannada":
                    return {
                        "landmark": "ಸುವರ್ಣ ಮಹೋತ್ಸವ ಸಭಾಂಗಣ (Golden Jubilee Hall)",
                        "cue": "ಸುವರ್ಣ ಮಹೋತ್ಸವ ಸಭಾಂಗಣದ ಪ್ರವೇಶದ್ವಾರದ ಬಳಿ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಸಂಸ್ಥಾಪಕರ ಪ್ರತಿಮೆ ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲೂ, ಆಡಳಿತ ಕಚೇರಿ ಬಲಭಾಗದಲ್ಲೂ ಇರಬೇಕು. ಕಚೇರಿ ಎಡಭಾಗದಲ್ಲಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "स्वर्ण जयंती संगोष्ठी हॉल (Golden Jubilee Hall)",
                        "cue": "स्वर्ण जयंती सेमिनार हॉल के प्रवेश द्वार पर रुकें। सत्यापन: संस्थापक की प्रतिमा बाईं ओर और प्रशासनिक कार्यालय दाईं ओर होना चाहिए। यदि कार्यालय बाईं ओर है, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Golden Jubilee Seminar Hall & Founder's Bust",
                    "cue": "Stop at the entrance of Golden Jubilee Seminar Hall. Check: The Founder's bust should be on your left hand side and Administrative Office on your right. If the office is on your left, simply turn around."
                }

        # 3. Ground Floor Quadrangle Shortcut (Reception <-> Classroom G11)
        if (("Main Reception" in from_node or "Administrative Block Foyer" in from_node) and to_node == "Classroom G11") or \
           (from_node == "Classroom G11" and ("Main Reception" in to_node or "Administrative Block Foyer" in to_node)):
            if "Classroom G11" in to_node:
                if language == "Kannada":
                    return {
                        "landmark": "ತರಗತಿ ಜಿ ೧೧ ನಾಮಫಲಕ ಮತ್ತು ತೆರೆದ ಅಂಗಳ",
                        "cue": "ತರಗತಿ ಜಿ ೧೧ ರ ನಾಮಫಲಕ ಕಂಡಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ತರಗತಿ ಜಿ ೧೧ ಅಂಗಳದ ನಡಿಗೆ ಹಾದಿಯ ಬಲಭಾಗದಲ್ಲಿದೆ ಮತ್ತು ತೆರೆದ ಆಕಾಶದ ಅಂಗಳವು ನೇರವಾಗಿ ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲಿದೆ. ಅಂಗಳವು ಬಲಭಾಗದಲ್ಲಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "कक्षा जी 11 नेमप्लेट और खुला आंगन",
                        "cue": "कक्षा जी 11 का नेमप्लेट दिखने पर रुकें। सत्यापन: क्लासरूम G11 प्रांगण के रास्ते पर आपकी दाईं ओर स्थित है और खुला आंगन ठीक आपकी बाईं ओर है। यदि आंगन दाईं ओर है, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Classroom G11 Plaque & Open-Sky Quadrangle",
                    "cue": "Stop when you see the Classroom G11 door plaque. Check: Classroom G11 is located on your right along the courtyard walkway, and the open-sky courtyard is directly on your left. If the courtyard is on your right, simply turn around."
                }
            else:
                if language == "Kannada":
                    return {
                        "landmark": "ಮುಖ್ಯ ರಿಸೆಪ್ಷನ್ ಡೆಸ್ಕ್ ಮತ್ತು ಗಣೇಶ ವಿಗ್ರಹ",
                        "cue": "ಮುಖ್ಯ ರಿಸೆಪ್ಷನ್ ಡೆಸ್ಕ್‌ನ ಮುಂದೆ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ರಿಸೆಪ್ಷನ್ ಕೌಂಟರ್ ನಿಮ್ಮ ಎದುರಿಗಿರಬೇಕು ಮತ್ತು ಗಣೇಶ ವಿಗ್ರಹ ಕಾಣಿಸಬೇಕು. ವಿರುದ್ಧವಾಗಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "मुख्य रिसेप्शन डेस्क और गणेश प्रतिमा",
                        "cue": "मुख्य रिसेप्शन डेस्क के सामने रुकें। सत्यापन: रिसेप्शन काउंटर ठीक सामने होना चाहिए और गणेश प्रतिमा दिखनी चाहिए। यदि विपरीत है, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Main Reception Desk & Ganesha Idol",
                    "cue": "Stop at the Main Reception desk. Check: The reception counter with Ganesha idol should be directly ahead and the main entrance gate beyond it. If the courtyard is in front of you, simply turn around."
                }

        # 4. Ground Floor Classroom Corridor (G1 to G11)
        if "Classroom G" in from_node or "Classroom G" in to_node:
            if language == "Kannada":
                return {
                    "landmark": "ತರಗತಿಗಳ ಕಾರಿಡಾರ್ ಮತ್ತು ಆವರಣದ ಕಿಟಕಿಗಳು",
                    "cue": f"{to_node} ರ ನಾಮಫಲಕ ಕಂಡಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ನಡೆಯುವಾಗ ತರಗತಿ ಕೊಠಡಿಗಳು ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲೂ, ಮುಕ್ತ ಆವರಣದ ಕಿಟಕಿಗಳು ಬಲಭಾಗದಲ್ಲೂ ಇರಬೇಕು. ಕಿಟಕಿಗಳು ಎಡಭಾಗದಲ್ಲಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                }
            elif language == "Hindi":
                return {
                    "landmark": "क्लासरूम कॉरिडोर और प्रांगण की खिड़कियां",
                    "cue": f"{to_node} का नेमप्लेट दिखने पर रुकें। सत्यापन: गलियारे में चलते समय क्लासरूम आपकी बाईं ओर और आंगन की खिड़कियां दाईं ओर होनी चाहिए। यदि खिड़कियां बाईं ओर हैं, तो पीछे मुड़ें।"
                }
            return {
                "landmark": "Classroom Wing Corridor & Courtyard Windows",
                "cue": f"Stop when you see the door plaque for {to_node}. Check: Classrooms should be on your left hand side and the open courtyard windows on your right. If classrooms are on your right, you are heading back toward reception — simply turn around."
            }

        # 5. Vertical Transitions (Stairs & Elevator)
        if stype == "vertical":
            if "Main Reception Staircase" in to_node or "Main Reception Staircase" in from_node:
                if language == "Kannada":
                    return {
                        "landmark": "ಮುಖ್ಯ ಸ್ವಾಗತ ಮೆಟ್ಟಿಲು ಲ್ಯಾಂಡಿಂಗ್",
                        "cue": f"ಮಹಡಿ {to_floor} ರ ಮೇಲ್ಭಾಗದ ಲ್ಯಾಂಡಿಂಗ್‌ನಲ್ಲಿ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ನೆಲಮಹಡಿಯ ರಿಸೆಪ್ಷನ್ ಡೆಸ್ಕ್ ನಿಮ್ಮ ಹಿಂಭಾಗದಲ್ಲಿರಬೇಕು ಮತ್ತು ಮಹಡಿ {to_floor} ರ ಕಾರಿಡಾರ್ ಎದುರಿಗೆ ತೆರೆಯುತ್ತದೆ. ಮುಖ್ಯ ದ್ವಾರ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "मुख्य स्वागत सीढ़ी लैंडिंग",
                        "cue": f"मंजिल {to_floor} की ऊपरी लैंडिंग पर रुकें। सत्यापन: भूतल का रिसेप्शन डेस्क आपके ठीक पीछे और नीचे होना चाहिए और मंजिल {to_floor} का गलियारा सामने खुलता है। यदि मुख्य द्वार दिखे, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Main Reception Staircase Landing & Railing",
                    "cue": f"Stop at the top landing of Floor {to_floor}. Check: The ground-floor reception desk is directly behind and below you, and the Floor {to_floor} hallway opens immediately ahead. If you see the ground floor garden, simply turn around."
                }
            else:
                if language == "Kannada":
                    return {
                        "landmark": f"ಮಹಡಿ {to_floor} ರ ಕಾರಿಡಾರ್ ಪ್ರವೇಶ",
                        "cue": f"ಮಹಡಿ {to_floor} ರ ಲ್ಯಾಂಡಿಂಗ್ ತಲುಪಿದ ತಕ್ಷಣ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಗೋಡೆಯ ಮೇಲಿನ 'ಮಹಡಿ {to_floor}' ಫಲಕವನ್ನು ನೋಡಿ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ. ಕಾರಿಡಾರ್ ನೇರವಾಗಿ ಎದುರಿಗೆ ಇರಬೇಕು. ತಪ್ಪಾದ ಮಹಡಿಯಲ್ಲಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": f"मंजिल {to_floor} कॉरिडोर प्रवेश",
                        "cue": f"मंजिल {to_floor} की लैंडिंग पर कदम रखते ही रुकें। सत्यापन: दीवार पर लगे 'मंजिल {to_floor}' साइन बोर्ड को देखकर पुष्टि करें। गलियारा ठीक सामने होना चाहिए। यदि गलत मंजिल पर हैं, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": f"Floor {to_floor} Corridor Landing",
                    "cue": f"Stop upon stepping onto the Floor {to_floor} landing. Check: Confirm Floor {to_floor} by reading the prominent floor level sign on the wall opposite the stairs/lift. If you are on the wrong floor, simply turn around."
                }

        # 6. First Floor Corridor & Labs
        if to_floor == 1 or "Classroom F" in to_node or "Botany" in to_node or "Physics" in to_node or "Chemistry" in to_node:
            if "Botany" in to_node or "Journalism" in to_node or "Classroom F" in to_node:
                if language == "Kannada":
                    return {
                        "landmark": "ಪತ್ರಿಕೋದ್ಯಮ ವಿಭಾಗ (Dept. of Journalism)",
                        "cue": "ವಿಭಾಗಗಳ ಬಾಗಿಲುಗಳ ನಡುವೆ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಸಸ್ಯಶಾಸ್ತ್ರ (Botany) ಕೊಠಡಿಯು ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲೂ, ಪತ್ರಿಕೋದ್ಯಮ ವಿಭಾಗ (Journalism) ಬಲಭಾಗದಲ್ಲೂ ಇರಬೇಕು. ಪತ್ರಿಕೋದ್ಯಮ ಎಡಭಾಗದಲ್ಲಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "पत्रकारिता विभाग (Dept. of Journalism)",
                        "cue": "विभाग के दरवाजों के बीच रुकें। सत्यापन: वनस्पति विज्ञान (Botany) बाईं ओर और पत्रकारिता विभाग दाईं ओर होना चाहिए। यदि पत्रकारिता विभाग बाईं ओर है, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Dept. of Botany & Dept. of Journalism",
                    "cue": "Stop between the department doors. Check: The Department of Botany should be on your left hand side and Department of Journalism on your right. If Journalism is on your left, simply turn around."
                }
            elif "Physics" in to_node:
                if language == "Kannada":
                    return {
                        "landmark": "ಭೌತಶಾಸ್ತ್ರ ಲ್ಯಾಬ್‌ಗಳ ನೀಲಿ ನಾಮಫಲಕಗಳು",
                        "cue": "ನೀಲಿ ದ್ವಿಭಾಷಾ ಫಲಕಗಳು ಕಂಡಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಭೌತಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯಗಳು ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲಿ ನೀಲಿ ಫಲಕಗಳೊಂದಿಗೆ ಇರಬೇಕು. ಅವು ಬಲಭಾಗದಲ್ಲಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "भौतिकी लैब के नीले नेमप्लेट",
                        "cue": "नीले द्विभाषी बोर्ड दिखने पर रुकें। सत्यापन: भौतिक विज्ञान प्रयोगशालाएं आपकी बाईं ओर नीले बोर्ड के साथ होनी चाहिए। यदि वे दाईं ओर हैं, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Physics Labs & Blue Overhead Nameplates",
                    "cue": "Stop when you see the blue bilingual nameplates. Check: Physics Labs I and II should be on your left hand side. If they are on your right, simply turn around."
                }

        # 7. Second Floor (Library, CS Department, BBA, Classrooms S1-S12)
        if to_floor == 2 or "Library" in to_node or "Computer" in to_node or "Classroom S" in to_node or "BBA" in to_node or "Commerce & Management" in to_node:
            if "BBA" in to_node or "Commerce & Management" in to_node:
                if language == "Kannada":
                    return {
                        "landmark": "ವಾಣಿಜ್ಯ ಮತ್ತು ನಿರ್ವಹಣಾ ವಿಭಾಗ (ಬಿಬಿಎ) ನಾಮಫಲಕ",
                        "cue": "ವಾಣಿಜ್ಯ ಮತ್ತು ನಿರ್ವಹಣಾ ವಿಭಾಗ (ಬಿಬಿಎ) ನಾಮಫಲಕ ಕಂಡಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಬಿಬಿಎ ವಿಭಾಗದ ಪ್ರವೇಶದ್ವಾರವು ನೇರವಾಗಿ ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲಿರಬೇಕು. ಮೆಟ್ಟಿಲುಗಳು ಎದುರಿಗೆ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "वाणिज्य एवं प्रबंधन विभाग (BBA) नेमप्लेट",
                        "cue": "वाणिज्य एवं प्रबंधन विभाग (BBA) के नेमप्लेट पर रुकें। सत्यापन: BBA विभाग का प्रवेश द्वार ठीक आपकी बाईं ओर होना चाहिए। यदि सीढ़ियाँ ठीक सामने दिखें, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Dept. of Commerce & Management (BBA) Plaque",
                    "cue": "Stop when you see the Department of Commerce & Management (BBA) overhead nameplate. Check: The BBA Department entrance should be directly on your left hand side. If the stairs are directly in front of you, simply turn around."
                }
            elif "Computer" in to_node or "CS" in to_node:
                if language == "Kannada":
                    return {
                        "landmark": "ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಮತ್ತು ಸಿಬ್ಬಂದಿ ಕೊಠಡಿಯ ನೀಲಿ ನಾಮಫಲಕ",
                        "cue": "ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಮತ್ತು ಸಿಬ್ಬಂದಿ ಕೊಠಡಿಯ ನೀಲಿ ಫಲಕ ಕಂಡಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಮತ್ತು ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್‌ಗಳು ನೇರವಾಗಿ ನಿಮ್ಮ ಬಲಭಾಗದಲ್ಲಿರಬೇಕು. ಬಿಬಿಎ ವಿಭಾಗವು ಎದುರಿಗೆ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "कंप्यूटर विज्ञान विभाग और स्टाफ रूम का नीला बोर्ड",
                        "cue": "कंप्यूटर विज्ञान विभाग और स्टाफ रूम के नीले बोर्ड के पास रुकें। सत्यापन: कंप्यूटर साइंस विभाग और कंप्यूटर लैब ठीक आपकी दाईं ओर होने चाहिए। यदि BBA विभाग सामने दिखे, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Computer Science Department & Computer Lab 1 Blue Plaque",
                    "cue": "Stop when you see the blue bilingual plaque for the Department of Computer Science & Staff Room. Check: The Computer Science Department and Computer Labs should be directly on your right hand side. If the BBA department is in front of you, simply turn around."
                }
            elif "Library" in to_node:
                if language == "Kannada":
                    return {
                        "landmark": "ಸೆಂಟ್ರಲ್ ಲೈಬ್ರರಿಯ ಗಾಜಿನ ಮುಖ್ಯ ದ್ವಾರ",
                        "cue": "ಗಾಜಿನ ಬಾಗಿಲುಗಳ ಮುಂದೆ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ಸೆಂಟ್ರಲ್ ಲೈಬ್ರರಿಯ ಗಾಜಿನ ಪ್ರವೇಶದ್ವಾರವು ನಿಮ್ಮ ಬಲಭಾಗದಲ್ಲೂ, ತೆರೆದ ಅಂಗಳದ ಕಟಾಂಜನವು ಎಡಭಾಗದಲ್ಲೂ ಇರಬೇಕು. ವಿರುದ್ಧವಾಗಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "सेंट्रल लाइब्रेरी का ग्लास गेट",
                        "cue": "कांच के दरवाजों के सामने रुकें। सत्यापन: सेंट्रल लाइब्रेरी का कांच का मुख्य प्रवेश द्वार आपकी दाईं ओर और आंगन की रेलिंग बाईं ओर होनी चाहिए। यदि रेलिंग दाईं ओर है, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Central Library Glass Entrance & Turnstiles",
                    "cue": "Stop before the double glass doors. Check: The Central Library glass entrance should be on your right hand side and the quadrangle balcony railing on your left. If the railing is on your right, simply turn around."
                }
            elif "Classroom S" in to_node:
                if language == "Kannada":
                    return {
                        "landmark": "ಎರಡನೇ ಮಹಡಿ ತರಗತಿ ಕಾರಿಡಾರ್ (S1-S12)",
                        "cue": f"{to_node} ರ ನಾಮಫಲಕ ಕಂಡಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ತರಗತಿ ಕೊಠಡಿಗಳು ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲೂ, ತೆರೆದ ಅಂಗಳದ ಬಾಲ್ಕನಿ ಕಟಾಂಜನವು ಬಲಭಾಗದಲ್ಲೂ ಇರಬೇಕು. ಲೈಬ್ರರಿ ಎದುರಿಗೆ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                    }
                elif language == "Hindi":
                    return {
                        "landmark": "दूसरी मंजिल क्लासरूम कॉरिडोर (S1-S12)",
                        "cue": f"{to_node} का नेमप्लेट दिखने पर रुकें। सत्यापन: क्लासरूम आपकी बाईं ओर और खुले आंगन की बालकनी की रेलिंग दाईं ओर होनी चाहिए। यदि लाइब्रेरी सामने दिखे, तो पीछे मुड़ें।"
                    }
                return {
                    "landmark": "Second Floor Classroom Corridor & Balcony",
                    "cue": f"Stop when you see the door plaque for {to_node}. Check: Classrooms should be on your left hand side and the open courtyard balcony railing on your right. If the library entrance is in front of you, simply turn around."
                }

        # 8. Third Floor (Student Lounge & Lecture Hall)
        if to_floor == 3 or "Lounge" in to_node or "Third Floor" in to_node:
            if language == "Kannada":
                return {
                    "landmark": "ಮೂರನೇ ಮಹಡಿಯ ವಿದ್ಯಾರ್ಥಿ ಲೌಂಜ್ (Student Lounge)",
                    "cue": "ಮರದ ಪಟ್ಟೆಗಳ ನೆಲಹಾಸಿನ ಮೇಲೆ ಹೆಜ್ಜೆಯಿಟ್ಟಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: ತೆರೆದ ಟೆರೇಸ್ ಲೌಂಜ್ ಆಸನಗಳು ನೇರವಾಗಿ ಎದುರಿಗಿರಬೇಕು, ಕಪ್ಪು ಕಟಾಂಜನ ಬಲಭಾಗದಲ್ಲೂ, ಲೆಕ್ಚರ್ ಹಾಲ್ ೩ ಎಡಭಾಗದಲ್ಲೂ ಇರಬೇಕು. ಮೆಟ್ಟಿಲು ಹಿಂಭಾಗದಲ್ಲಿರಬೇಕು. ಮೆಟ್ಟಿಲು ಮುಂದೆ ಕಂಡರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
                }
            elif language == "Hindi":
                return {
                    "landmark": "ओपन स्टूडेंट लाउंज (तीसरी मंजिल)",
                    "cue": "लकड़ी की धारीदार फर्श पर कदम रखते ही रुकें। सत्यापन: ओपन टेरेस लाउंज सिटिंग ठीक सामने होनी चाहिए, काली रेलिंग दाईं ओर और लेक्चर हॉल 3 बाईं ओर होना चाहिए। सीढ़ियाँ ठीक पीछे होनी चाहिए। यदि सीढ़ियाँ आगे दिखें, तो पीछे मुड़ें।"
                }
            return {
                "landmark": "Student Open Terrace Lounge & Terrace Railing",
                "cue": "Stop when you step onto the wooden striped flooring. Check: The open terrace student lounge seating should be directly ahead with black railings on your right and Lecture Hall 3 on your left. The staircase should be directly behind you. If the stairs are ahead, simply turn around."
            }

        # Dynamic Generic Fallback for Landmark Verification
        if language == "Kannada":
            return {
                "landmark": to_node,
                "cue": f"{to_node} ನಾಮಫಲಕ ಕಂಡಾಗ ನಿಲ್ಲಿ. ದೃಢೀಕರಣ: {to_node} ನೇರವಾಗಿ ನಿಮ್ಮ ಪಕ್ಕದಲ್ಲಿರಬೇಕು. ಹತ್ತಿರದ ಫಲಕವನ್ನು ನೋಡಿ ದೃಢಪಡಿಸಿಕೊಳ್ಳಿ. ಅದು ಹಿಂಭಾಗದಲ್ಲಿದ್ದರೆ, ಹಿಂದಕ್ಕೆ ತಿರುಗಿ."
            }
        elif language == "Hindi":
            return {
                "landmark": to_node,
                "cue": f"{to_node} का नेमप्लेट दिखने पर रुकें। सत्यापन: {to_node} ठीक आपके पास होना चाहिए। निकटतम साइन बोर्ड देखकर पुष्टि करें। यदि यह पीछे है, तो पीछे मुड़ें।"
            }
        return {
            "landmark": to_node,
            "cue": f"Stop when you see the door plaque for {to_node}. Check: {to_node} should be directly beside you. Confirm by checking the nearest door plaque or sign board. If it is behind you, simply turn around."
        }

    def _compress_path_segments(self, path: List[str], graph) -> List[Dict[str, Any]]:
        """
        Groups raw node paths into balanced, human-friendly wayfinding segments:
        - Maintains 3 to 6 intuitive checkpoints per route.
        - Keeps distinct steps for departures, turns, vertical transitions, and arrivals.
        - Compresses noisy straight hallway hops without collapsing the entire route.
        """
        if not path:
            return []
        
        fl_start = self.locations_dict.get(path[0], {}).get("floor", 0)
        if len(path) == 1:
            return [{
                "type": "arrival",
                "from_node": path[0],
                "to_node": path[0],
                "nodes": [path[0]],
                "distance": 0,
                "path_type": "Standing",
                "from_floor": fl_start,
                "to_floor": fl_start
            }]

        segments = []
        i = 0
        n = len(path)

        def get_edge_meta(u: str, v: str) -> Dict[str, Any]:
            if hasattr(graph, 'get_edge_data'):
                data = graph.get_edge_data(u, v)
                if data:
                    return data
            if isinstance(graph, dict):
                return graph.get(u, {}).get(v, {})
            return {}

        def is_vertical_node(node_name: str) -> bool:
            low = node_name.lower()
            return any(k in low for k in ["stair", "lift", "elevator", "ಮೆಟ್ಟಿಲು", "ಲಿಫ್ಟ್"])

        while i < n - 1:
            curr_node = path[i]
            next_node = path[i + 1]
            c_info = self.locations_dict.get(curr_node, {"floor": 0})
            n_info = self.locations_dict.get(next_node, {"floor": 0})
            c_floor = c_info.get("floor", 0)
            n_floor = n_info.get("floor", 0)

            # 1. Floor transitions (Stairs & Elevators)
            # Only trigger vertical segment when there is an actual floor change OR movement between two vertical infrastructure nodes
            is_vert_c = is_vertical_node(curr_node)
            is_vert_n = is_vertical_node(next_node)
            if c_floor != n_floor or (is_vert_c and is_vert_n):
                seg_nodes = [curr_node, next_node]
                init_e = get_edge_meta(curr_node, next_node)
                total_dist = init_e.get("distance", 15)
                p_type = init_e.get("path_type", "Stairs")
                
                j = i + 1
                while j < n - 1:
                    step_c = path[j]
                    step_n = path[j + 1]
                    step_c_fl = self.locations_dict.get(step_c, {}).get("floor", 0)
                    step_n_fl = self.locations_dict.get(step_n, {}).get("floor", 0)
                    if step_c_fl != step_n_fl or (is_vertical_node(step_c) and is_vertical_node(step_n)):
                        seg_nodes.append(step_n)
                        e = get_edge_meta(step_c, step_n)
                        total_dist += e.get("distance", 15)
                        j += 1
                    else:
                        break
                target_floor = self.locations_dict.get(seg_nodes[-1], {}).get("floor", n_floor)
                segments.append({
                    "type": "vertical",
                    "from_node": curr_node,
                    "to_node": seg_nodes[-1],
                    "nodes": seg_nodes,
                    "distance": total_dist,
                    "path_type": p_type,
                    "from_floor": c_floor,
                    "to_floor": target_floor
                })
                i = j
                continue

            # 2. Main Gate Entrance Consolidation
            if curr_node == "Main Gate" and i + 1 < n:
                entrance_dest = path[min(i + 2, n - 1)] if (i + 2 < n and "Security" in next_node) else next_node
                skip_count = 2 if entrance_dest != next_node else 1
                e_dist = sum(get_edge_meta(path[i + k], path[i + k + 1]).get("distance", 15) for k in range(skip_count))
                segments.append({
                    "type": "entrance_walk",
                    "from_node": "Main Gate",
                    "to_node": entrance_dest,
                    "nodes": path[i:i + skip_count + 1],
                    "distance": max(15, e_dist),
                    "path_type": "Paved Walkway",
                    "from_floor": 0,
                    "to_floor": 0
                })
                i += skip_count
                continue

            # 3. Same-floor corridor movement: Compress consecutive hops up to a sensible limit (max 40m or 3 nodes)
            # This avoids collapsing the whole floor into 1 step while eliminating single-hop noise.
            seg_nodes = [curr_node, next_node]
            init_e = get_edge_meta(curr_node, next_node)
            accum_dist = init_e.get("distance", 10)
            p_type = init_e.get("path_type", "Corridor")

            j = i + 1
            while j < n - 1:
                step_c = path[j]
                step_n = path[j + 1]
                step_c_fl = self.locations_dict.get(step_c, {}).get("floor", 0)
                step_n_fl = self.locations_dict.get(step_n, {}).get("floor", 0)

                # Stop compression if hitting stairs, floor changes, or reaching final destination
                if step_c_fl != step_n_fl or (is_vertical_node(step_c) and is_vertical_node(step_n)) or (j + 1 == n - 1):
                    break

                # Limit straight compression distance so users have checkpoints
                if accum_dist >= 40 or len(seg_nodes) >= 3:
                    break

                edge_meta = get_edge_meta(step_c, step_n)
                seg_nodes.append(step_n)
                accum_dist += edge_meta.get("distance", 10)
                j += 1

            if len(seg_nodes) > 2:
                segments.append({
                    "type": "corridor_chain",
                    "from_node": curr_node,
                    "to_node": seg_nodes[-1],
                    "nodes": seg_nodes,
                    "distance": accum_dist,
                    "path_type": p_type,
                    "from_floor": c_floor,
                    "to_floor": c_floor
                })
                i = j
            else:
                # Single step
                segments.append({
                    "type": "single_step",
                    "from_node": curr_node,
                    "to_node": next_node,
                    "nodes": [curr_node, next_node],
                    "distance": accum_dist,
                    "path_type": p_type,
                    "from_floor": c_floor,
                    "to_floor": n_floor
                })
                i += 1

        # 4. Ensure the final destination arrival step is never swallowed
        if segments and segments[-1]["to_node"] != path[-1]:
            last_edge = get_edge_meta(segments[-1]["to_node"], path[-1])
            segments.append({
                "type": "single_step",
                "from_node": segments[-1]["to_node"],
                "to_node": path[-1],
                "nodes": [segments[-1]["to_node"], path[-1]],
                "distance": last_edge.get("distance", 10),
                "path_type": "Corridor",
                "from_floor": self.locations_dict.get(path[-1], {}).get("floor", 0),
                "to_floor": self.locations_dict.get(path[-1], {}).get("floor", 0)
            })

        return segments

    def generate_turn_by_turn(self, path: List[str], graph, language: str = "English", wheelchair_mode: bool = False) -> List[Dict[str, Any]]:
        """
        Converts a list of graph nodes into rich checkpoint objects with bilateral landmark orientation.
        """
        if not path:
            return []

        if len(path) == 1:
            loc_name = self._get_localized_name(path[0], language)
            if language == "Kannada":
                msg = f"ನೀವು ಈಗಾಗಲೆ **{loc_name}** ತಲುಪಿದ್ದೀರಿ."
            elif language == "Hindi":
                msg = f"आप पहले से ही **{loc_name}** पर मौजूद हैं।"
            else:
                msg = f"You are already at **{loc_name}**."

            fl = self.locations_dict.get(path[0], {}).get("floor", 0)
            return [{
                "step": 1,
                "checkpoint_title": f"Destination: {loc_name}",
                "action": msg,
                "verification": "You are currently standing at your destination.",
                "landmark_name": loc_name,
                "action_type": "Arrival",
                "instruction": msg,
                "audio_text": msg.replace("*", ""),
                "distance": 0,
                "icon": "🎯",
                "current_floor": f"Floor {fl}",
                "target_floor": f"Floor {fl}",
                "from_node": path[0],
                "to_node": path[0],
                "path_type": "Standing"
            }]

        segs = self._compress_path_segments(path, graph)
        instructions = []

        for idx, seg in enumerate(segs):
            stype = seg["type"]
            from_n = seg["from_node"]
            to_n = seg["to_node"]
            dist = int(seg["distance"])
            is_last = (idx == len(segs) - 1)
            is_first = (idx == 0)

            f_name = self._get_localized_name(from_n, language)
            t_name = self._get_localized_name(to_n, language)

            # Bilateral Landmark Verification
            landmark_info = self._get_landmark_verification(
                from_node=from_n,
                to_node=to_n,
                stype=stype,
                to_floor=seg["to_floor"],
                language=language
            )

            # Mandatory 3-Part Step Schema (Action -> Visual Anchor Trail -> Checkpoint & Boundary Verification)
            part1 = ""
            part2 = ""
            part3 = landmark_info["cue"]
            icon = "🚶"
            action_type = "Navigation"

            if stype == "vertical":
                curr_fl = seg.get("from_floor", 0)
                to_fl = seg.get("to_floor", 0)
                t_mode_en = "elevator" if wheelchair_mode or "Elevator" in seg["path_type"] else "stairs"
                t_mode_kn = "ಲಿಫ್ಟ್" if wheelchair_mode or "Elevator" in seg["path_type"] else "ಮೆಟ್ಟಿಲು"
                t_mode_hi = "लिफ्ट" if wheelchair_mode or "Elevator" in seg["path_type"] else "सीढ़ियों"

                icon = "🛗" if "Elevator" in seg["path_type"] or wheelchair_mode else "🪜"
                action_type = "Floor Transition"

                if "Main Reception Staircase" in from_n or "Main Reception Staircase" in to_n:
                    if to_fl < curr_fl:
                        if language == "Kannada":
                            part1 = f"ಮಹಡಿ {curr_fl} ರಿಂದ ಮುಖ್ಯ ಸ್ವಾಗತ {t_mode_kn} ಇಳಿದು ಮಹಡಿ {to_fl} ರ ಲ್ಯಾಂಡಿಂಗ್ ತಲುಪಿ."
                            part2 = f"ಕಟಾಂಜನದ ಬಲಬದಿಯಲ್ಲಿ {t_mode_kn}ಗಳನ್ನು ಇಳಿದು ಕೆಳಗೆ ಸಾಗಿ."
                        elif language == "Hindi":
                            part1 = f"मंजिल {curr_fl} से मुख्य स्वागत {t_mode_hi} से नीचे उतरकर मंजिल {to_fl} की लैंडिंग पर पहुँचें।"
                            part2 = f"रेलिंग के साथ दाईं ओर रहते हुए {t_mode_hi} से नीचे उतरें।"
                        else:
                            part1 = f"Descend the Main Reception {t_mode_en.capitalize()} from Floor {curr_fl} down to the Floor {to_fl} landing."
                            part2 = f"Descend the {t_mode_en} keeping to the right along the railing."
                    else:
                        if language == "Kannada":
                            part1 = f"ಮಹಡಿ {curr_fl} ರಿಂದ ಮುಖ್ಯ ಸ್ವಾಗತ {t_mode_kn} ಹತ್ತಿ ನೇರವಾಗಿ ಮಹಡಿ {to_fl} ರ ಲ್ಯಾಂಡಿಂಗ್ ತಲುಪಿ."
                            part2 = f"ಕಟಾಂಜನದ ಬಲಬದಿಯಲ್ಲಿ {t_mode_kn}ಗಳನ್ನು ಹತ್ತಿ ಮಧ್ಯದ ಮಹಡಿಗಳನ್ನು ದಾಟಿ ಮೇಲೆ ಹೋಗಿ."
                        elif language == "Hindi":
                            part1 = f"मंजिल {curr_fl} से मुख्य स्वागत {t_mode_hi} को चढ़कर सीधे मंजिल {to_fl} की लैंडिंग पर पहुँचें।"
                            part2 = f"रेलिंग के साथ दाईं ओर रहते हुए {t_mode_hi} चढ़ें और बीच की मंजिलों को पार करते हुए ऊपर जाएँ।"
                        else:
                            part1 = f"Climb the Main Reception {t_mode_en.capitalize()} directly from Floor {curr_fl} to the Floor {to_fl} landing."
                            part2 = f"Ascend the {t_mode_en} keeping to the right along the railing, bypassing intermediate floor landings."
                    part3 = landmark_info["cue"]
                else:
                    if to_fl < curr_fl:
                        if language == "Kannada":
                            part1 = f"ಮಹಡಿ {curr_fl} ರಿಂದ {t_mode_kn} ಇಳಿದು ಮಹಡಿ {to_fl} ಗೆ ಹೋಗಿ."
                            part2 = f"ಕಟಾಂಜನದ ಬಲಬದಿಯಲ್ಲಿ {t_name} ಕಡೆಗೆ ಮುನ್ನಡೆಯಿರಿ."
                        elif language == "Hindi":
                            part1 = f"मंजिल {curr_fl} से {t_mode_hi} से नीचे उतरकर मंजिल {to_fl} पर जाएं।"
                            part2 = f"रेलिंग के दाईं ओर रहते हुए {t_name} की ओर बढ़ें।"
                        else:
                            part1 = f"Take the {t_mode_en} from Floor {curr_fl} down to Floor {to_fl}."
                            part2 = f"Descend the flight of stairs towards {t_name}, keeping to the right hand side along the railing."
                    else:
                        if language == "Kannada":
                            part1 = f"ಪ್ರವೇಶದ್ವಾರದಿಂದ ತಕ್ಷಣ {t_mode_kn} ಬಳಸಿ ಮಹಡಿ {curr_fl} ರಿಂದ ಮಹಡಿ {to_fl} ಗೆ ಹೋಗಿ."
                            part2 = f"ಕಟಾಂಜನದ ಬಲಬದಿಯಲ್ಲಿ {t_name} ಕಡೆಗೆ ಮುನ್ನಡೆಯಿರಿ."
                        elif language == "Hindi":
                            part1 = f"प्रवेश द्वार से तुरंत {t_mode_hi} का उपयोग करके मंजिल {curr_fl} से मंजिल {to_fl} पर जाएं।"
                            part2 = f"रेलिंग के दाईं ओर रहते हुए {t_name} की ओर बढ़ें।"
                        else:
                            part1 = f"Take the {t_mode_en} from Floor {curr_fl} up to Floor {to_fl} immediately at the staircase entrance."
                            part2 = f"Ascend the flight of stairs towards {t_name}, keeping to the right hand side along the railing."
                    part3 = landmark_info["cue"]

            elif stype == "entrance_walk":
                action_type = "Entrance Direction"
                if to_n == "Main Reception Staircase":
                    icon = "🪜"
                    if language == "Kannada":
                        part1 = "ಮುಖ್ಯ ಪ್ರವೇಶ ದ್ವಾರದಿಂದ ಭದ್ರತಾ ಕೊಠಡಿಯನ್ನು ದಾಟಿ ನೇರವಾಗಿ ಮುನ್ನಡೆಯಿರಿ."
                        part2 = "ಮುಖಮಂಟಪದ ಪಾದಚಾರಿ ಹಾದಿಯಲ್ಲಿ ನೇರವಾಗಿ ಸಾಗಿ. ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲಿ ಭದ್ರತಾ ಕೊಠಡಿ ಮತ್ತು ಬಲಭಾಗದಲ್ಲಿ ಕಾಲೇಜು ಉದ್ಯಾನವನದ ಹಾದಿಯನ್ನು ದಾಟುತ್ತೀರಿ."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = "मुख्य प्रवेश द्वार से सुरक्षा केबिन को पार करते हुए सीधे आगे बढ़ें।"
                        part2 = "पक्के प्रवेश पोर्च से सीधे चलें। आप अपनी बाईं ओर सुरक्षा केबिन और दाईं ओर कॉलेज गार्डन वॉकवे पार करेंगे।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = "Go straight through the main entrance gate past the security post."
                        part2 = "Walk straight across the paved entrance porch. You will pass the security cabin on your left and the campus garden walkway on your right."
                        part3 = landmark_info["cue"]
                elif to_n == "College Garden Walkway":
                    icon = "➡️"
                    if language == "Kannada":
                        part1 = "ಮುಖ್ಯ ದ್ವಾರದ ಒಳಗಿನ ಭದ್ರತಾ ಕೊಠಡಿಯನ್ನು ದಾಟಿದ ತಕ್ಷಣ ಬಲಕ್ಕೆ ತಿರುಗಿ."
                        part2 = "ಉದ್ಯಾನವನದ ಹಾದಿಯಲ್ಲಿ ನೇರವಾಗಿ ಸಾಗಿ. ನಿಮ್ಮ ಬಲಭಾಗದಲ್ಲಿ ಹಸಿರು ಗಿಡಮರಗಳು ಮತ್ತು ಎಡಭಾಗದಲ್ಲಿ ಮುಖ್ಯ ಮುಖಮಂಟಪವಿರುತ್ತದೆ."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = "मुख्य द्वार के अंदर सुरक्षा केबिन को पार करने के तुरंत बाद दाएं मुड़ें।"
                        part2 = "बगीचे के पक्के रास्ते पर सीधे चलें। आपकी दाईं ओर हरे-भरे पौधे और बाईं ओर मुख्य प्रशासनिक पोर्च होगा।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = "Turn right immediately after passing the security cabin inside the main gate."
                        part2 = "Walk straight along the paved garden walkway. You will pass lush flowering plants on your right and the main administrative porch on your left."
                        part3 = landmark_info["cue"]
                else:
                    icon = "⬆️"
                    if language == "Kannada":
                        part1 = "ಮುಖ್ಯ ಪ್ರವೇಶದ್ವಾರದ ಗಾಜಿನ ಬಾಗಿಲುಗಳ ಮೂಲಕ ನೇರವಾಗಿ ಮುಖಮಂಟಪಕ್ಕೆ ಪ್ರವೇಶಿಸಿ."
                        part2 = "ಪ್ರವೇಶದ್ವಾರದ ಮೂಲಕ ನೇರವಾಗಿ ಸಾಗಿ. ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲಿ ಭದ್ರತಾ ಕೊಠಡಿ ಮತ್ತು ಬಲಭಾಗದಲ್ಲಿ ಸೂಚನಾ ಫಲಕಗಳನ್ನು ಕಾಣಬಹುದು."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = "मुख्य कांच के प्रवेश द्वारों से सीधे फ़ोयर के अंदर जाएं।"
                        part2 = "प्रवेश द्वार से सीधे आगे बढ़ें। आप बाईं ओर सुरक्षा चौकी और दाईं ओर प्रशासनिक नोटिस बोर्ड देखेंगे।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = "Go straight through the main entrance glass doors into the foyer."
                        part2 = "Walk straight across the threshold. You will pass the security post on your left and the administrative notice boards on your right."
                        part3 = landmark_info["cue"]

            elif (("Main Reception" in from_n or "Administrative Block Foyer" in from_n) and to_n == "Classroom G11") or \
                 (from_n == "Classroom G11" and ("Main Reception" in to_n or "Administrative Block Foyer" in to_n)):
                icon = "➡️"
                action_type = "Quadrangle Shortcut"
                if "Classroom G11" in to_n:
                    if language == "Kannada":
                        part1 = "ಮುಖ್ಯ ರಿಸೆಪ್ಷನ್ ಡೆಸ್ಕ್‌ನಿಂದ, ಹೊರಗಿನ ಉದ್ಯಾನವನದ ಕಡೆಗೆ ಹೋಗಬೇಡಿ. ಒಳಗಿನ ಅಂಗಳದ ಹಾದಿಯ ಕಡೆಗೆ ಬಲಕ್ಕೆ ತಿರುಗಿ."
                        part2 = "ರಿಸೆಪ್ಷನ್ ಮೆಟ್ಟಿಲನ್ನು ದಾಟಿ ತೆರೆದ ಆಕಾಶದ ಅಂಗಳಕ್ಕೆ (Quadrangle) ಹೋಗುವ ಸುಸಜ್ಜಿತ ತೆರೆದ ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ಮುನ್ನಡೆಯಿರಿ. ಅಂಗಳದ ನಡಿಗೆ ಹಾದಿಯಲ್ಲಿ ನೇರವಾಗಿ ಸಾಗಿ."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = "मुख्य रिसेप्शन डेस्क से, बाहर बगीचे की ओर न जाएं। आंतरिक प्रांगण के रास्ते की ओर दाएं मुड़ें।"
                        part2 = "रिसेप्शन सीढ़ियों के पास से होते हुए खुले प्रांगण (Quadrangle) की ओर जाने वाले पक्के खुले गलियारे में चलें। प्रांगण के रास्ते पर सीधे चलते रहें।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = "From the Main Reception desk, do not go outside towards the garden. Turn right toward the inner courtyard walkway."
                        part2 = "Walk past the reception staircase and take the paved open corridor leading into the quadrangle / open-sky courtyard. Walk straight along the courtyard walkway."
                        part3 = landmark_info["cue"]
                else:
                    if language == "Kannada":
                        part1 = "ತರಗತಿ ಜಿ ೧೧ ರಿಂದ ಹೊರಬಂದು, ತೆರೆದ ಅಂಗಳದ ಹಾದಿಯಲ್ಲಿ ನೇರವಾಗಿ ರಿಸೆಪ್ಷನ್ ಕಡೆಗೆ ಸಾಗಿ."
                        part2 = "ತೆರೆದ ಆಕಾಶದ ಅಂಗಳದ ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ನೇರವಾಗಿ ಮುನ್ನಡೆಯಿರಿ. ಅಂಗಳವು ನಿಮ್ಮ ಬಲಭಾಗದಲ್ಲಿದ್ದು ರಿಸೆಪ್ಷನ್ ಮೆಟ್ಟಿಲು ಎದುರಿಗೆ ಕಾಣಿಸುತ್ತದೆ."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = "कक्षा जी 11 से बाहर निकलकर, खुले प्रांगण के रास्ते से सीधे रिसेप्शन की ओर चलें।"
                        part2 = "खुले प्रांगण के गलियारे में सीधे बढ़ें। आंगन आपकी दाईं ओर होगा और रिसेप्शन सीढ़ियाँ सामने दिखाई देंगी।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = "Exit Classroom G11 and take the paved courtyard walkway straight towards the reception."
                        part2 = "Walk straight along the open-sky quadrangle corridor. The central courtyard will be on your right hand side."
                        part3 = landmark_info["cue"]

            elif "Main Reception Staircase" in from_n and ("BBA" in to_n or "Commerce & Management" in to_n):
                icon = "⬅️"
                action_type = "Corridor Turn"
                if language == "Kannada":
                    part1 = "ಮೆಟ್ಟಿಲಿನ ಮೇಲ್ಭಾಗದ ಲ್ಯಾಂಡಿಂಗ್‌ನಲ್ಲಿ ತಕ್ಷಣವೇ ಎಡಕ್ಕೆ ತಿರುಗಿ ಪಶ್ಚಿಮ ಕಾರಿಡಾರ್‌ಗೆ ಪ್ರವೇಶಿಸಿ."
                    part2 = "ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ನೇರವಾಗಿ ಸಾಗಿ. ಬಿಬಿಎ ವಿಭಾಗದ ಪ್ರವೇಶದ್ವಾರ ನೇರವಾಗಿ ಮುಂಭಾಗದಲ್ಲಿಲ್ಲ; ಸ್ವಲ್ಪ ದೂರ ನಡೆದ ನಂತರ ತರಗತಿ ಎಸ್ ೧೨ ಮತ್ತು ಕಿಟಕಿಯನ್ನು ನಿಮ್ಮ ಎಡಭಾಗದಲ್ಲಿ ದಾಟುತ್ತೀರಿ."
                    part3 = landmark_info["cue"]
                elif language == "Hindi":
                    part1 = "सीढ़ियों की ऊपरी लैंडिंग से तुरंत बाईं ओर मुड़कर पश्चिमी गलियारे में प्रवेश करें।"
                    part2 = "गलियारे में सीधे चलें। BBA विभाग का प्रवेश द्वार ठीक सामने नहीं है; थोड़ी दूरी चलने के बाद कक्षा S12 और खिड़की आपके बाईं ओर से गुजरेगी।"
                    part3 = landmark_info["cue"]
                else:
                    part1 = "Turn left immediately at the top landing of the stairs into the west hallway."
                    part2 = "Walk straight along the corridor. The BBA Department entrance is not directly in front; you will pass Classroom S12 and the connector window on your left side after a short walk."
                    part3 = landmark_info["cue"]

            elif "Main Reception Staircase" in from_n and ("Computer Science" in to_n or "CS" in to_n):
                icon = "➡️"
                action_type = "Corridor Movement"
                if language == "Kannada":
                    part1 = "ಎರಡನೇ ಮಹಡಿಯ ಮುಖ್ಯ ಸ್ವಾಗತ ಮೆಟ್ಟಿಲಿನಿಂದ ಇಳಿದು ಈಶಾನ್ಯ ಕಾರಿಡಾರ್ ಕಡೆಗೆ ಬಲಕ್ಕೆ ತಿರುಗಿ."
                    part2 = "ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಮತ್ತು ಸಿಬ್ಬಂದಿ ಕೊಠಡಿಯ ಕಡೆಗೆ ನೇರವಾಗಿ ಸಾಗಿ. ಬಲಭಾಗದಲ್ಲಿ ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ಅಧ್ಯಾಪಕರ ಕೊಠಡಿ ಮತ್ತು ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ ೧ ಇರುತ್ತವೆ. ನೀವು ಭಾಷಾ ಪ್ರಯೋಗಾಲಯ (Language Lab) ದಾಟುವ ಮೊದಲೇ ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಸಿಗುತ್ತದೆ."
                    part3 = landmark_info["cue"]
                elif language == "Hindi":
                    part1 = "द्वितीय तल की मुख्य स्वागत सीढ़ियों से उतरकर ईस्ट विंग गलियारे की ओर दाएं मुड़ें।"
                    part2 = "कंप्यूटर विज्ञान विभाग और स्टाफ रूम की ओर सीधे चलें। कंप्यूटर साइंस संकाय कक्ष और कंप्यूटर लैब 1 गलियारे के प्रवेश पर ही आपकी दाईं ओर स्थित हैं। भाषा प्रयोगशाला (Language Lab) पहुँचने से पहले ही आपको कंप्यूटर साइंस विभाग मिल जाएगा।"
                    part3 = landmark_info["cue"]
                else:
                    part1 = "Step off the Main Reception Staircase onto the Floor 2 landing and turn right into the East Wing hallway."
                    part2 = "Walk directly toward the Department of Computer Science & Staff Room. The faculty consultation rooms and Computer Lab 1 are located right at the entrance of the corridor on your right. You will reach the Computer Science Department immediately before reaching the Language Lab or other labs."
                    part3 = landmark_info["cue"]

            elif ("BBA" in from_n or "Commerce & Management" in from_n or "Language Lab" in from_n) and ("Computer Science" in to_n or "CS" in to_n):
                icon = "⬆️"
                action_type = "Corridor Movement"
                if language == "Kannada":
                    part1 = "ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗದ ಕಡೆಗೆ ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ."
                    part2 = "ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ನೇರವಾಗಿ ಸಾಗಿ. ಎಲೆಕ್ಟ್ರಾನಿಕ್ಸ್ ಲ್ಯಾಬ್, ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ ೨ ಮತ್ತು ತರಗತಿ ಎಸ್ ೮ ದಾಟಿ ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ತಲುಪಿ."
                    part3 = landmark_info["cue"]
                elif language == "Hindi":
                    part1 = "गलियारे में कंप्यूटर साइंस विभाग की ओर सीधे आगे बढ़ें।"
                    part2 = "गलियारे में सीधे चलें। इलेक्ट्रॉनिक्स लैब, कंप्यूटर लैब 2 और कक्षा S8 पार करते हुए कंप्यूटर साइंस विभाग तक पहुँचें।"
                    part3 = landmark_info["cue"]
                else:
                    part1 = "Continue straight along the corridor towards the Department of Computer Science."
                    part2 = "Walk straight along the corridor past the Electronics & Hardware Lab, Computer Lab 2, and Classroom S8 until you reach the Computer Science Department."
                    part3 = landmark_info["cue"]

            elif ("Computer Science" in from_n or "CS" in from_n) and ("Language Lab" in to_n or "BBA" in to_n or "Commerce & Management" in to_n):
                icon = "⬆️"
                action_type = "Corridor Movement"
                if language == "Kannada":
                    part1 = "ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗದಿಂದ ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ದಕ್ಷಿಣದ ಕಡೆಗೆ ನೇರವಾಗಿ ಸಾಗಿ."
                    part2 = "ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ನೇರವಾಗಿ ಸಾಗಿ. ತರಗತಿ ಎಸ್ ೮, ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ ೨ ಮತ್ತು ಎಲೆಕ್ಟ್ರಾನಿಕ್ಸ್ ಲ್ಯಾಬ್ ದಾಟಿದ ನಂತರ ಭಾಷಾ ಪ್ರಯೋಗಾಲಯ (Language Lab) ತಲುಪುತ್ತೀರಿ."
                    part3 = landmark_info["cue"]
                elif language == "Hindi":
                    part1 = "कंप्यूटर साइंस विभाग से गलियारे में दक्षिण की ओर सीधे चलें।"
                    part2 = "गलियारे में सीधे बढ़ें। कक्षा S8, कंप्यूटर लैब 2 और इलेक्ट्रॉनिक्स लैब पार करने के बाद आप भाषा प्रयोगशाला तक पहुँचेंगे।"
                    part3 = landmark_info["cue"]
                else:
                    part1 = "From the Department of Computer Science, continue straight south down the East Wing corridor."
                    part2 = "Walk straight along the corridor past Classroom S8, Computer Lab 2, and the Electronics & Hardware Lab before reaching the Language Lab."
                    part3 = landmark_info["cue"]

            elif stype == "corridor_chain":
                icon = "⬆️"
                action_type = "Corridor Movement"
                intermediates = seg.get("nodes", [])[1:-1]
                passed_names = [self._get_localized_name(nd, language) for nd in intermediates]

                if language == "Kannada":
                    part1 = f"ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ನೇರವಾಗಿ {t_name} ಕಡೆಗೆ ಮುನ್ನಡೆಯಿರಿ."
                    if passed_names:
                        passed_str = " ಮತ್ತು ".join(passed_names) if len(passed_names) <= 2 else (", ".join(passed_names[:-1]) + ", ಮತ್ತು " + passed_names[-1])
                        part2 = f"ಕಾರಿಡಾರ್‌ನಲ್ಲಿ {passed_str} ಗಳನ್ನು ದಾಟಿ ಸುಮಾರು {dist} ಮೀಟರ್ ನೇರವಾಗಿ {t_name} ಕಡೆಗೆ ಸಾಗಿ."
                    else:
                        part2 = f"ಕಾರಿಡಾರ್‌ನಲ್ಲಿ ಸುಮಾರು {dist} ಮೀಟರ್ ನೇರವಾಗಿ {t_name} ಕಡೆಗೆ ಸಾಗಿ."
                    part3 = landmark_info["cue"]
                elif language == "Hindi":
                    part1 = f"गलियारे में सीधे {t_name} की तरफ बढ़ें।"
                    if passed_names:
                        passed_str = " और ".join(passed_names) if len(passed_names) <= 2 else (", ".join(passed_names[:-1]) + ", और " + passed_names[-1])
                        part2 = f"गलियारे में {passed_str} को पार करते हुए लगभग {dist} मीटर सीधे {t_name} की ओर बढ़ें।"
                    else:
                        part2 = f"गलियारे में लगभग {dist} मीटर सीधे {t_name} की ओर बढ़ें।"
                    part3 = landmark_info["cue"]
                else:
                    part1 = f"Continue straight along the corridor towards {t_name}."
                    if passed_names:
                        passed_str = " and ".join(passed_names) if len(passed_names) <= 2 else (", ".join(passed_names[:-1]) + ", and " + passed_names[-1])
                        part2 = f"Walk straight past {passed_str} for about {dist} meters until you reach {t_name}."
                    else:
                        part2 = f"Walk straight along the corridor for about {dist} meters towards {t_name}."
                    part3 = landmark_info["cue"]

            else:  # single_step
                action_type = "Arrival" if is_last else ("Departure" if is_first else "Navigation")
                if is_last:
                    icon = "🎯"
                    if language == "Kannada":
                        part1 = f"{t_name} ರ ಪ್ರವೇಶದ್ವಾರದ ಕಡೆಗೆ ನೇರವಾಗಿ ಸಾಗಿ."
                        part2 = f"ಕಾರಿಡಾರ್‌ನ ಕೊನೆಯವರೆಗೂ ನೇರವಾಗಿ ಸಾಗಿ {t_name} ರ ಬಾಗಿಲನ್ನು ಸಮೀಪಿಸಿ."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = f"{t_name} के प्रवेश द्वार की ओर सीधे चलें।"
                        part2 = f"गलियारे के अंत तक सीधे चलते हुए {t_name} के दरवाजे के पास पहुँचें।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = f"Walk straight to the entrance of {t_name}."
                        part2 = f"Walk straight until you reach the doorway of {t_name}."
                        part3 = landmark_info["cue"]
                elif is_first:
                    icon = "🚶"
                    if language == "Kannada":
                        part1 = f"{f_name} ನಿಂದ ಪ್ರಾರಂಭಿಸಿ {t_name} ಕಡೆಗೆ ಹೋಗುವ ಹಾದಿಗೆ ತಿರುಗಿ."
                        part2 = "ಕಾರಿಡಾರ್‌ನ ಉದ್ದಕ್ಕೂ ಇರುವ ಮಾರ್ಗದರ್ಶಿ ನಾಮಫಲಕಗಳನ್ನು ಗಮನಿಸುತ್ತಾ ನೇರವಾಗಿ ಸಾಗಿ."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = f"{f_name} से शुरू करें और {t_name} की ओर जाने वाले रास्ते पर मुड़ें।"
                        part2 = "गलियारे में लगे दिशा-निर्देश बोर्ड को देखते हुए सीधे आगे बढ़ें।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = f"Start at {f_name} and turn into the corridor towards {t_name}."
                        part2 = "Walk straight along the corridor, following the directional sign boards."
                        part3 = landmark_info["cue"]
                else:
                    icon = "🚶"
                    if language == "Kannada":
                        part1 = f"{f_name} ಅನ್ನು ದಾಟಿ ಕಾರಿಡಾರ್‌ನಲ್ಲಿ {t_name} ಕಡೆಗೆ ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ."
                        part2 = "ಕಾರಿಡಾರ್‌ನ ಮಾರ್ಗದಲ್ಲಿ ನೇರವಾಗಿ ಸಾಗಿ, ಬದಿಯ ಕೊಠಡಿಗಳ ನಾಮಫಲಕಗಳನ್ನು ಗಮನಿಸಿ."
                        part3 = landmark_info["cue"]
                    elif language == "Hindi":
                        part1 = f"{f_name} को पार करते हुए गलियारे में सीधे {t_name} की तरफ बढ़ें।"
                        part2 = "गलियारे के रास्ते पर सीधे चलें और कमरों के बोर्ड को देखते हुए आगे बढ़ें।"
                        part3 = landmark_info["cue"]
                    else:
                        part1 = f"Continue straight past {f_name} along the corridor towards {t_name}."
                        part2 = "Walk straight along the hallway, watching for wall plaques and room numbers."
                        part3 = landmark_info["cue"]

            # Compose Action, Verification, Combined Instruction, and Spoken Audio Text
            text = f"{part1} {part2}"
            cue = part3

            if language == "Kannada":
                combined_instruction = f"**೧. ದೈಹಿಕ ಕ್ರಿಯೆ (Action):** {part1}\n\n**೨. ದೃಶ್ಯ ಹಾದಿ (Visual Trail):** {part2}\n\n🧭 **೩. ಭೌತಿಕ ತಪಾಸಣೆ ಮತ್ತು ದೃಢೀಕರಣ (Verification):** {part3}"
            elif language == "Hindi":
                combined_instruction = f"**1. शारीरिक क्रिया (Action):** {part1}\n\n**2. दृश्य निशान (Visual Trail):** {part2}\n\n🧭 **3. चेकपॉइंट और सत्यापन (Verification):** {part3}"
            else:
                combined_instruction = f"**1. Action:** {part1}\n\n**2. Visual Trail:** {part2}\n\n🧭 **3. Checkpoint & Verification:** {part3}"

            # Clean spoken audio text
            p1_clean = part1.rstrip('. ').rstrip('।').strip()
            p2_clean = part2.rstrip('. ').rstrip('।').strip()
            p3_clean = part3.rstrip('. ').rstrip('।').strip()
            sep = "। " if language == "Hindi" else ". "
            end_mark = "।" if language == "Hindi" else "."
            audio_sentences = [p for p in [p1_clean, p2_clean, p3_clean] if p]
            full_audio = (sep.join(audio_sentences) + end_mark).replace("*", "").replace("🧭", "").strip()

            instructions.append({
                "step": idx + 1,
                "checkpoint_title": f"Checkpoint {idx + 1}: {to_n}",
                "action": text,
                "verification": cue,
                "part1_action": part1,
                "part2_trail": part2,
                "part3_verification": part3,
                "landmark_name": landmark_info["landmark"],
                "action_type": action_type,
                "instruction": combined_instruction,
                "audio_text": full_audio,
                "distance": dist,
                "icon": icon,
                "current_floor": f"Floor {seg['from_floor']}",
                "target_floor": f"Floor {seg['to_floor']}",
                "from_node": from_n,
                "to_node": to_n,
                "path_type": seg.get("path_type", "Corridor")
            })

        return instructions

    def calculate_eta(self, total_distance: float, floor_changes: int = 0, wheelchair_mode: bool = False) -> float:
        """
        Calculates Estimated Time of Arrival (minutes) factoring walking speed and vertical lift/ramp delays.
        """
        speed_m_per_min = 55.0 if wheelchair_mode else 65.0
        walk_time = total_distance / speed_m_per_min
        floor_delay = floor_changes * 0.5  # 30 seconds per floor transition
        return max(0.5, round(walk_time + floor_delay, 1))
