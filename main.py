import json
import random
import os
import re
from datetime import datetime
import requests

# 🌟 보기 싫은 단순 경고(Warning) 메시지 숨기기
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

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
        print("🚨 [에러] GEMINI_API_KEY를 불러오지 못했습니다! GitHub Secrets를 확인하세요.", flush=True)
        return {}
    
    genai.configure(api_key=api_key)
    print("  -> 🤖 Gemini API 연결 완료. 모델을 찾습니다...", flush=True)
    
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((name for name in available_models if 'gemini-1.5-flash' in name), available_models[0] if available_models else None)
        
        if not target_model: 
            print("🚨 [에러] 사용할 수 있는 Gemini 모델이 없습니다.", flush=True)
            return {}
            
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
"""
        full_prompt = f"{system_instruction}\n\n[작사 배경]\n{prompt}"
        
        print("  -> ✍️ Gemini에게 가사 작성을 요청합니다. (약 10~20초 소요)", flush=True)
        response = model.generate_content(full_prompt)
        text = response.text
        print(f"  -> ✅ Gemini 응답 완료! (총 {len(text)}자 생성됨)", flush=True)

        # 파싱 로직
        text = re.sub(r'###\s*DETAIL\s*###', '###DETAIL###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*PURPOSE\s*###', '###PURPOSE###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*LYRICS\s*###', '###LYRICS###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*TAG\s*###', '###TAG###', text, flags=re.IGNORECASE)
        text = re.sub(r'###\s*UPLOAD\s*###', '###UPLOAD###', text, flags=re.IGNORECASE)

        markers = ["###DETAIL###", "###PURPOSE###", "###LYRICS###", "###TAG###", "###UPLOAD###"]
        extracted = {"detail": "", "purpose": "", "lyrics": "", "tag": "", "upload": ""}

        for marker in markers:
            if marker in text:
                parts = text.split(marker)
                if len(parts) > 1:
                    part = parts[1]
                    min_idx = len(part)
                    for other_marker in markers:
                        idx = part.find(other_marker)
                        if idx != -1 and idx < min_idx:
                            min_idx = idx
                    key = marker.replace("#", "").lower()
                    extracted[key] = part[:min_idx].strip()
        
        # 가사가 비어있는지 체크
        if not extracted.get("lyrics"):
            print("  -> 🚨 [경고] 가사 파싱 실패! Gemini가 양식에 맞춰 답변하지 않았습니다.", flush=True)
            print("  -> [Gemini 원본 답변 내용]:\n", text[:500], "...(후략)...", flush=True)

        return extracted
        
    except Exception as e:
        print(f"🚨 [에러] Gemini 처리 중 문제 발생: {e}", flush=True)
        return {}

def save_to_notion(date_str, genre, prompt, data_dict):
    notion_token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")
    
    if not notion_token or not database_id:
        print("🚨 [에러] NOTION_TOKEN 또는 NOTION_DATABASE_ID 환경 변수가 없습니다!", flush=True)
        return

    if not data_dict.get("lyrics"): 
        print("❌ 저장할 가사(데이터)가 비어있어 Notion 호출을 취소합니다.", flush=True)
        return

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

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
    
    print(f"📊 [결과] HTTP 상태 코드: {response.status_code}", flush=True)
    if response.status_code == 200:
        print("✅ Notion 저장 성공! 모든 데이터가 들어갔습니다.", flush=True)
    else:
        print(f"❌ Notion 저장 실패! 상세 사유: {response.text}", flush=True)
        
def main():
    print("🚀 [1/3] 데이터 로드 시작...", flush=True)
    try:
        genres = load_data('data/genres.json')
        times = load_data('data/times.json')
        emotions1 = load_data('data/emotions1.json')
        actions = load_data('data/actions.json')
        places = load_data('data/places.json')
        emotions2 = load_data('data/emotions2.json')
    except Exception as e:
        print(f"🚨 데이터 로드 실패: {e}", flush=True)
        return

    selected_genre = get_random_item(genres)
    selected_time = get_random_item(times)
    selected_emotion1 = get_random_item(emotions1)
    selected_action = get_random_item(actions)
    selected_place = get_random_item(places)
    selected_emotion2 = get_random_item(emotions2)

    current_date = datetime.now().strftime("%Y년 %m월 %d일")

    final_prompt = (
        f"{selected_genre} 장르의 {current_date} {selected_time}의 "
        f"{selected_emotion1} 한 {selected_action} 하는 {selected_place}에서의 "
        f"{selected_emotion2} 날'의 느낌으로 가사를 작성해줘요."
        f"Intro, Chorus, Verse1, Verse2, Bridge, Outro 등으로 구분해서 한곡 완성해주세요."
    )

    print(f"✅ 생성된 프롬프트: {final_prompt}", flush=True)
    
    print("\n🚀 [2/3] Gemini 가사 생성 중...", flush=True)
    result_data = generate_lyrics_with_gemini(final_prompt)
    
    print("\n🚀 [3/3] Notion 저장 시도...", flush=True)
    save_to_notion(current_date, selected_genre, final_prompt, result_data)

if __name__ == "__main__":
    main()
