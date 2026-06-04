import json
import random
import os
import re
from datetime import datetime
import requests
import google.generativeai as genai

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_random_item(data):
    if isinstance(data, dict):
        all_items = []
        for items_in_category in data.values():
            all_items.extend(items_in_category)
        return random.choice(all_items)
    elif isinstance(data, list):
        return random.choice(data)

def generate_lyrics_with_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {}
    
    genai.configure(api_key=api_key)
    
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((name for name in available_models if 'gemini-1.5-flash' in name), available_models[0] if available_models else None)
        
        if not target_model: return {}
            
        model = genai.GenerativeModel(target_model)
        
        system_instruction = """[멜로디 및 사운드 디자인 (Meta Tags) 강제 규칙]
너는 감성을 자극하는 세계적인 엔터테인먼트 음반 회사의 천재적인 작사가 뿐 아니라 곡의 다이내믹을 설계하는 총괄 프로듀서에요.
요즘 트렌드를 조사한 후에, 다음 주어진 상황, 장르, 감정을 바탕으로 독창적이고 음악의 리듬감이 느껴지는 노래 제목과 노래 가사를 만들어주세요.
###LYRICS### 섹션을 작성할 때, 가사 텍스트만 적지 말고 반드시 아래의 3가지 요소를 < > (악기/효과음/구조)와 [ ] (보컬 창법) 기호를 사용하여 촘촘하게 배치해주세요. 이때 3가지 요소와 가사의 총 글자수는 4900자를 넘어가지 않도록 해주세요.

1. 감정선에 맞춘 점진적 멜로디 빌드업 (Melodic Build-up)

Intro: 곡의 배경을 시각적으로 보여줄 수 있는 환경음이나 잔잔한 악기 톤을 지정해. (예: <비 내리는 소리와 로우파이 피아노>, [나른하고 읊조리는 듯한 보컬])

Verse & Pre-Chorus: 텐션을 서서히 끌어올리는 리듬 악기를 추가해. (예: <점점 빨라지는 킥 드럼과 베이스>, [감정이 고조되며 호흡이 짧아지는 창법])

Chorus: 주어진 감정과 장르의 에너지가 폭발하는 구간이야. 웅장한 사운드와 최고조의 보컬 기교를 지시해. (예: <풀 밴드 사운드 폭발, 화려한 신스 리드>, [파워풀한 진성 고음과 넓은 비브라토])

2. 보컬과 악기의 티키타카 (Call & Response)

보컬이 부르는 메인 가사 한 줄이 끝날 때마다, 빈 공간을 채우는 악기 연주나 코러스 애드립을 지시해. 곡이 절대 지루하지 않고 리드미컬하게 들려야 해.

(적용 예시): "오늘 밤은 유난히 길어 [애절한 가성] / <날카로운 일렉 기타 벤딩(Bending)>"

3. [장르]별 시그니처 멜로디 패턴 강제

주어진 [장르]의 정체성을 보여주는 '핵심 악기 + 보컬 스타일' 세트를 반드시 곡 전반에 깔아둬.

예) EDM/하우스: <강렬한 Build-up과 Drop>, [리듬감 있는 찹 보컬(Vocal Chop)]

예) 재즈/블루스: <스윙 리듬, 그루비한 콘트라베이스>, [스캣(Scatting)과 여유로운 뒤축 박자]

예) 발라드/오페라틱 팝: <웅장한 오케스트라 스트링>, [풍부한 성량, 호소력 짙은 흉성]

곡 중간(Bridge 이후 등)에 해당 장르를 가장 잘 나타내는 **<Instrumental Solo> (악기 솔로 구간)**를 최소 1회 이상 강제로 삽입해.
              

모든 답변은 반드시 아래의 [구분자]를 사용하여 섹션을 나누어 작성해야 해요

###DETAIL###
이 칸에는 노래 제목(Subject), 장르(Genre), Tempo, Key, 악기 구성을 포함한 정보와 작사 배경 및 분위기 구성을 적어주세요. (띄어쓰기 포함 총 1000자 이내) 이때 노래 제목은 소재의 나열보다는 키워드 위주로 한개 또는 두개의 단어로 표현해주세요.
* 제목 및 정보 항목에 마크다운 굵게(**)는 절대 사용하지 마요.

###PURPOSE###
이 칸에는 '작사가의 한마디'를 통해 이 곡의 기획 의도와 종합적인 곡 소개를 적어주세요.

###SUNO###
위 DETAIL 부분에 작성한 '장르, Tempo, 악기 구성, 분위기'를 음악 생성 AI(Suno)의 'Style of Music' 란에 바로 복사해 넣을 수 있도록, 영어 키워드 위주로 700자 이내로 번역 및 요약해주세요. (예: Melodic Electronic, Progressive House, 123 BPM, warm synth pad, emotional lead)

###VOCAL###
이 칸에는 해당 노래에 어울리는 보컬 스타일을 영어로 작성해주세요. 이때 톤과 스타일에 대해서는 자세하게 적어주세요.
형식: [성별], [톤], [스타일], [솔로/듀엣/그룹 여부]
* 예시: Female vocal, extremely low-pitched, dark contralto, very heavy chest voice, deep androgynous tone, resonant bassy female voice, husky and thick vocal, Solo.
* 전체 내용은 200~250자로 구체적으로 작성할 것.

###LYRICS###
섹션별 가사: Intro, Chorus, Verse, Bridge, Outro 등으로 구분하여 가사를 작성해. 가사 외의 정보(구간 시간, 악기/분위기)는 반드시 영어로 < > 속에 넣어 표현해주세요.
가사 내 지시어 (Meta Tags) 예시:
[Extremely low vocal], [Heavy and dark contralto singing], [Deep thick chest voice]

###CLEAN_LYRICS###
클린
