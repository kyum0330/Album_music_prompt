import json
import random
import os
import re  # 🌟 정규표현식(강력한 텍스트 추출) 라이브러리 추가
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
        
        system_instruction = """너는 감성을 자극하는 세계적인 엔터테인먼트 음반 회사의 천재적인 작사가에요.
요즘 트렌드를 조사한 후에, 다음 주어진 상황, 장르, 감정을 바탕으로 독창적이고 음악의 리듬감이 느껴지는 노래 제목과 노래 가사를 만들어주세요.

모든 답변은 반드시 아래의 [구분자]를 사용하여 섹션을 나누어 작성해야 해요

###DETAIL###
이 칸에는 노래 제목(Subject), 장르(Genre), Tempo, Key, 악기 구성을 포함한 정보와 작사 배경 및 분위기 구성을 적어주세요. (띄어쓰기 포함 총 1000자 이내)
* 제목 및 정보 항목에 마크다운 굵게(**)는 절대 사용하지 마요.

###PURPOSE###
이 칸에는 '작사가의 한마디'를 통해 이 곡의 기획 의도와 종합적인 곡 소개를 적어주세요.

###LYRICS###
1. 섹션별 가사: Intro, Chorus, Verse, Bridge, Outro 등으로 구분하여 가사를 작성해. 가사 외의 정보(구간 시간, 악기/분위기)는 반드시 영어로 < > 속에 넣어 표현해주세요.
2. 클린 가사: 위 세부 항목이 끝난 후, 단을 나누어 순수 가사 내용만 다시 한 번 적어주세요.

###TAG###
이 곡과 어울리는 유튜브 노출용 트렌디 해쉬태그를 이용해서 한글과 영어 섞어서 정확히 30개 작성해줘요. 이때 번갈아가며 나오도록 하고, 해당 태크마다','를 붙여주고, 노출 가능성이 큰 순서대로 나열해주세요. (예: #하우스, #새벽감성, ...)

###UPLOAD###
유튜브 업로드용 요약 양식으로 작성해주세요. 
형식: [해쉬태그 5개] + [날짜와 감정 기반 짧은 소개글(한글)] + [날짜와 감정 기반 짧은 한글 소개글 영어로 번역] [곡 정보 요약(제목, 장르, Tempo, Key, 악기)] 순서로 가독성 있게 작성해줘요.
UPLOAD용 형식 예시는 다음과 같아요.

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

        # 🌟 파싱 로직 완벽 수정본: 정규표현식으로 알맹이만 100% 쏙쏙 빼냅니다!
        text = re.sub(r'###\s*DETAIL\s*###', '###DETAIL###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*PURPOSE\s*###', '###PURPOSE###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*LYRICS\s*###', '###LYRICS###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*TAG\s*###', '###TAG###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*UPLOAD\s*###', '###UPLOAD###', text, flags=re.IGNORECASE)

        markers = ["###DETAIL###", "###PURPOSE###", "###LYRICS###", "###TAG###", "###UPLOAD###"]
        extracted = {"detail": "", "purpose": "", "lyrics": "", "tag": "", "upload": ""}

        for marker in markers:
            if marker in text:
                # 1. 해당 마커 기준으로 텍스트를 자르고 뒷부분(알맹이)을 가져옴
                part = text.split(marker)[1]
                
                # 2. 가져온 알맹이에서 '다음 마커'가 등장하기 전까지만 안전하게 다시 자름
                min_idx = len(part)
                for other_marker in markers:
                    idx = part.find(other_marker)
                    if idx != -1 and idx < min_idx:
                        min_idx = idx
                
                # 3. 바구니에 저장
                key = marker.replace("#", "").lower()
                extracted[key] = part[:min_idx].strip()
        
        return extracted
        
    except Exception as e:
        print(f"Gemini 에러: {e}")
        return {}

def save_to_notion(date_str, genre, prompt, data_dict):
    notion_token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")
    
    # 데이터가 비어있으면 아예 저장을 시도하지 않음
    if not notion_token or not database_id or not data_dict.get("lyrics"): 
        print("❌ 저장할 가사(데이터)가 비어있어 Notion 호출을 취소합니다.")
        return

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    page_title = f"{date_str} ({genre})"
    
    children_blocks = [{"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🎶 Gemini 생성 가사 및 곡 구성"}}]}}]
    
    # 가사가 너무 길어질 경우를 대비한 안전 장치 복구
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
    children_blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": data_dict["tag"][:2000]}}]}})

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {"title": [{"text": {"content": f"{date_str} ({genre})"}}]},
            "Generated Prompt": {"rich_text": [{"text": {"content": prompt}}]},
            "Detail": {"rich_text": [{"text": {"content": data_dict["detail"][:2000]}}]},
            "Purpose": {"rich_text": [{"text": {"content": data_dict["purpose"][:2000]}}]},
            "Tag": {"rich_text": [{"text": {"content": data_dict["tag"][:2000]}}]},
            "Genre": {"rich_text": [{"text": {"content": genre}}]},
            "Upload": {"rich_text": [{"text": {"content": data_dict["upload"][:2000]}}]} 
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

    current_date = datetime.now().strftime("%Y년 %m월 %
