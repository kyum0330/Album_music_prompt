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

def get_seoul_weather():
    api_key = os.environ.get("WEATHER_API_KEY") 
    if api_key:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={api_key}&lang=kr"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data['weather'][0]['description']
        except Exception as e:
            print(f"날씨 정보를 가져오는 중 에러 발생: {e}")
    return "날씨 정보가 오류가 생겼음"

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
요즘 트렌드를 조사한 후에, 다음 주어진 상황, 장르, 감정, 날씨를 바탕으로 독창적이고 음악의 리듬감이 느껴지는 노래 제목과 노래 가사를 만들어주세요.
###LYRICS### 섹션을 작성할 때, 가사 텍스트만 적지 말고 반드시 아래의 3가지 요소를 < > (악기/효과음/구조)와 [ ] (보컬 창법) 기호를 사용하여 촘촘하게 배치해주세요. 이때 3가지 요소와 가사의 총 글자수는 4900자를 넘어가지 않도록 해주세요.

1. 감정선에 맞춘 점진적 멜로디 빌드업 (Melodic Build-up)

Intro: 곡의 배경과 날씨를 시각적으로 보여줄 수 있는 환경음이나 잔잔한 악기 톤을 지정해. (예: <비 내리는 소리와 로우파이 피아노>, [나른하고 읊조리는 듯한 보컬])

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
클린 가사: 위 세부 항목이나 음악 구조(< > 부분)가 모두 제외된, 순수 가사 내용만 복사하기 쉽게 적어주세요.

###TAG###
이 곡과 어울리는 유튜브 노출용 트렌디 해쉬태그를 이용해서 한글과 영어 섞어서 정확히 30개 작성해줘요. 이때 번갈아가며 나오도록 하고, 해당 태크마다','를 붙여주고, 노출 가능성이 큰 순서대로 나열해주세요. (예: #하우스, #새벽감성, ...)

###UPLOAD###
유튜브 업로드용 요약 양식으로 작성해주세요. 
형식: [해쉬태그 5개] + [날짜와 감정 기반 짧은 소개글(한글)] + [날짜와 감정 기반 짧은 한글 소개글 영어로 번역] [곡 정보 요약(제목, 장르, Tempo, Key, 악기)] 순서로 가독성 있게 작성해줘요.
UPLOAD용 형식 예시는 다음과 같아요. 이때, 해쉬태그에 노래 제목은 제외하고 유튜브에서 노출이 많은 순서대로 넣어주세요.

#감성 #playlist #인디  #멜로딕일렉트로닉 #프로그레시브하우스

2026년 5월 15일, 거칠게 정지된 삶의 캔버스 앞에서 불완전함을 성찰하고, 그 속에서 끝없이 맑고 명료한 희망을 발견하는 감정을 바탕으로 만들어졌습니다.

Based on the feeling of 'Rough and Stopped Canvas on an Endless Clear Day' on May 15, 2026.

* 노래 제목(Subject) : 정지된 투명함 (Stopped Transparency)

* 장르(Genre) : Melodic Electronic / Progressive House

* Tempo : 123 BPM

* Key : E Major, 내면의 고요한 성찰에서 시작해 벅찬 해방감으로 뻗어나가는 맑고 투명한 희망을 담기 위함.

* 악기 구성(Instrument composition) : 웜하고 몽환적인 신스 패드, 리드미컬한 베이스라인, 섬세한 하이햇과 킥 드럼, 아르페지오 신스, 이모셔널한 신스 리드, 미니멀한 보컬 이펙트."""

        full_prompt = f"{system_instruction}\n\n[작사 배경]\n{prompt}"
        response = model.generate_content(full_prompt)
        text = response.text

        # 🌟 강력한 정규표현식: 제미나이가 어떤 특수문자나 띄어쓰기를 섞어놔도 깔끔하게 통일시킵니다.
        markers_base = ["DETAIL", "PURPOSE", "SUNO", "VOCAL", "LYRICS", "CLEAN_LYRICS", "TAG", "UPLOAD"]
        for m in markers_base:
            text = re.sub(r'[*_]*#+\s*' + m + r'\s*#*[*_]*', f'###{m}###', text, flags=re.IGNORECASE)

        markers = [f"###{m}###" for m in markers_base]
        extracted = {m.lower(): "" for m in markers_base}
        extracted["image"] = ""

        for marker in markers:
            if marker in text:
                part = text.split(marker)[1]
                min_idx = len(part)
                for other_marker in markers:
                    if other_marker != marker:
                        idx = part.find(other_marker)
                        if idx != -1 and idx < min_idx:
                            min_idx = idx
                
                key = marker.replace("#", "").lower()
                extracted[key] = part[:min_idx].strip()
        
        extracted["image"] = (
            f"이 노래에 맞는 16:9 의 영상 제작에 맞는 썸네일 하나 트랜디한 느낌을 살려서 사람들의 시선을 끌 수 있게 제작 부탁할게요. 이때, 노래에 대한 제목과 설명은 글로 표현하지 말아주세요.\n\n"
            f"[곡 상세 정보]\n{extracted.get('detail', '')}\n\n"
            f"[기획 의도]\n{extracted.get('purpose', '')}"
        )

        # 🌟 디버깅 로그 출력: 제미나이가 만든 항목별 글자 수를 GitHub 액션 화면에 보여줍니다.
        print("\n[4] 파싱된 섹션별 글자 수 (0이면 AI가 생성을 빼먹은 것입니다):")
        for k, v in extracted.items():
            print(f" - {k}: {len(v)}자")

        return extracted
        
    except Exception as e:
        print(f"Gemini 에러: {e}")
        return {}

# 🌟 가사 쪼개기 도우미 함수를 가장 바깥쪽으로 안전하게 뺐습니다!
def get_chunks(text):
    return [{"text": {"content": text[i:i+2000]}} for i in range(0, max(1, len(text)), 2000)]

def save_to_notion(date_str, genre, weather, prompt, data_dict):
    notion_token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")
    
    # 가사가 정말로 비어있다면 아예 전송을 하지 않고 멈춥니다.
    if not notion_token or not database_id or not data_dict.get("lyrics", "").strip(): 
        print("❌ 저장할 가사(LYRICS) 데이터가 비어있어 Notion 호출을 취소합니다.")
        return

    # 🌟 들여쓰기 위치를 올바르게 수정했습니다!
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    page_title = f"{date_str} ({genre})"
    
    children_blocks = [{"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🎶 Gemini 생성 가사 및 곡 구성"}}]}}]
    
    for para in data_dict["lyrics"].split('\n\n'):
        para = para.strip()
        if not para: continue
        
        if len(para) > 2000:
            while len(para) > 2000:
                split_idx = para.rfind('\n', 0, 2000)
                if split_idx == -1: split_idx = para.rfind(' ', 0, 2000)
                if split_idx == -1: split_idx = 2000 
                
                chunk = para[:split_idx].strip()
                children_blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": chunk}}]}})
                para = para[split_idx:].strip()
                
        if para:
            children_blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": para}}]}})
    
    children_blocks.append({"object": "block", "type": "divider", "divider": {}})
    children_blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": data_dict.get("tag", "")[:2000]}}]}})

    clean_lyrics_content = data_dict.get("clean_lyrics", "")
    clean_lyrics_chunks = [{"text": {"content": clean_lyrics_content[i:i+2000]}} for i in range(0, max(1, len(clean_lyrics_content)), 2000)] if clean_lyrics_content else [{"text": {"content": " "}}]

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {"title": [{"text": {"content": f"{date_str} ({genre})"}}]},
            "Weather": {"rich_text": [{"text": {"content": weather}}]},
            "Generated Prompt": {"rich_text": [{"text": {"content": prompt}}]},
            "Detail": {"rich_text": [{"text": {"content": data_dict.get("detail", "")[:2000]}}]},
            "Purpose": {"rich_text": [{"text": {"content": data_dict.get("purpose", "")[:2000]}}]},
            "Suno": {"rich_text": [{"text": {"content": data_dict.get("suno", "")[:2000]}}]},    
            "Image": {"rich_text": [{"text": {"content": data_dict.get("image", "")[:2000]}}]},   
            "Vocal": {"rich_text": [{"text": {"content": data_dict.get("vocal", "")[:2000]}}]},
            "Lyrics": {"rich_text": clean_lyrics_chunks}, 
            "E_Lyrics": {"rich_text": get_chunks(data_dict.get("lyrics", " "))},
            "Tag": {"rich_text": [{"text": {"content": data_dict.get("tag", "")[:2000]}}]},
            "Genre": {"rich_text": [{"text": {"content": genre}}]},
            "Upload": {"rich_text": [{"text": {"content": data_dict.get("upload", "")[:2000]}}]} 
        },
        "children": children_blocks
    }
    
    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=payload)
    
    print(f"📊 [결과] HTTP 상태 코드: {response.status_code}")
    if response.status_code == 200:
        print("✅ Notion 저장 성공! 모든 데이터가 들어갔습니다.")
    else:
        print(f"❌ Notion 저장 실패! 상세 사유: {response.text}")
        
def main():
    try:
        genres = load_data('data/genres.json')
        times = load_data('data/times.json')
        emotions1 = load_data('data/emotions1.json')
        actions = load_data('data/actions.json')
        places = load_data('data/places.json')
        emotions2 = load_data('data/emotions2.json')
    except Exception as e:
        print(f"데이터 로드 실패: {e}")
        return

    selected_genre = get_random_item(genres)
    selected_time = get_random_item(times)
    selected_emotion1 = get_random_item(emotions1)
    selected_action = get_random_item(actions)
    selected_place = get_random_item(places)
    selected_emotion2 = get_random_item(emotions2)

    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    current_weather = get_seoul_weather()

    final_prompt = f"""
<Current_Status>
- 진행 단계: 초기 컨셉 브레인스토밍 및 최종 음원 데이터 완성
- 타겟 결과물: 유튜브 및 오디오 플랫폼 업로드용 기획안 및 가사
</Current_Status>

<Brainstorming_Seed>
- 장르: {selected_genre}
- 배경/시간: {current_date}, {selected_time}
- 날씨: {current_weather}
- 장소 및 상황: {selected_place}에서 {selected_action} 하는 중
- 감정선: {selected_emotion1} 분위기 속에서 느껴지는 {selected_emotion2}
</Brainstorming_Seed>

<Action_Steps>
위의 <Brainstorming_Seed>를 바탕으로 다음 단계를 거쳐 작업을 수행해 줘.

1) [내부 구상]: 이 키워드들을 엮어서 만들 수 있는 매력적인 스토리라인과 시각적 테마를 스스로 3가지 정도 깊이 있게 브레인스토밍 해봐. (이 과정은 너의 내부 추론을 위한 것이며 출력하지 않아도 됨)
2) [최종 도출]: 네가 구상한 아이디어 중 가장 훌륭하고 트렌디한 1가지를 확정해.
3) [포맷 출력]: 확정한 아이디어를 바탕으로, 시스템 프롬프트에서 요구한 ###DETAIL### 부터 ###UPLOAD### 까지의 8가지 필수 구분자 포맷에 맞추어 완벽한 최종 결과물만 출력해.
</Action_Steps>
"""
    print(f"\n[1] 생성된 프롬프트: {final_prompt}")
    print("\n[2] Gemini 가사 생성 중...")
    
    result_data = generate_lyrics_with_gemini(final_prompt)
    
    print("\n[3] Notion 저장 시도...")
    save_to_notion(current_date, selected_genre, current_weather, final_prompt, result_data)

if __name__ == "__main__":
    main()
