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
        print("🚨 GEMINI_API_KEY가 설정되지 않았습니다.")
        return {}
    
    genai.configure(api_key=api_key)
    
    system_instruction = """[멜로디 및 사운드 디자인 (Meta Tags) 강제 규칙]
너는 감성을 자극하는 세계적인 엔터테인먼트 음반 회사의 천재적인 작사가 뿐 아니라 곡의 다이내믹을 설계하는 총괄 프로듀서에요.
요즘 트렌드를 조사한 후에, 제시된 [장르], [시간], [장소], [감정], [행동] 데이터를 활용해, 비트감과 감정선이 가장 매력적으로 어우러지는 세련된 곡을 만들어야 해요.

[작사 핵심 및 메타 태그 규칙]
1. 보컬 및 페르소나: [Smooth alto female vocal, deep calm voice, low octave, subdued pitch, clean natural voice, clear diction, effortless singing, gentle resonance, subtle vocal runs, relaxed delivery, mellow dynamics, soft instrumentation, chill R&B, Solo]. 
Suno AI가 흔한 중-고음 소프라노를 출력하지 않도록, 과도한 기교 없이 담백하고 매력적인 중저음 보컬 톤을 강제해요. 보컬과 코러스 부분에 대해서는 다음 내용을 참고해주세요.

    1-1. 메타 태그 적용 (Lyrics 영역)
        곡이 고조되는 코러스(후렴구)나 브릿지 부분에 단순히 [Chorus]라고만 적으면 AI가 마음대로 소리를 내지를 확률이 높습니다. 이럴 때는 대괄호 안에 보컬의 창법을 직접 제한해 주세요. 상황에 맞게 아래 태그 중 하나를 선택하여 적용하십시오.
- [Soft Chorus]: 부드럽게 부르는 후렴구
- ​[Clear Smooth Falsetto]: 공기 소리를 줄이고 목소리의 선명도를 높인 맑고 부드러운 가성
- ​[Warm Gentle High Notes]: 쨍하지 않고 따뜻하게 감싸듯 올라가는 편안한 고음
- ​[Controlled Vocal]: 감정은 담되 에너지가 과하지 않게 절제된 보컬
- [mellow dynamics]: 튀는 구간 없이 차분하고 부드러운 다이내믹
- [soft vocal delivery]: 처음부터 끝까지 부드럽게 내뱉는 보컬 표현
- [laid-back]: 여유롭고 힘을 뺀 스타일
- [intimate vocal]: 귀에 대고 속삭이듯 가까운 느낌의 보컬

    1-2. 음악 스타일 제한 (Style of Music 영역 - 보컬)
        곡 전체의 스타일을 지정하는 칸에도 보컬의 에너지를 낮춰주는 긍정형 키워드를 추가하여 AI가 과호흡을 하지 않도록 진정시켜야 합니다.
- mellow dynamics: 튀는 구간 없이 차분하고 부드러운 다이내믹
- soft vocal delivery: 처음부터 끝까지 부드럽게 내뱉는 보컬 표현
- laid-back: 여유롭고 힘을 뺀 스타일
- intimate vocal: 귀에 대고 속삭이듯 가까운 느낌의 보컬

    1-3. 악기 및 장르의 에너지 조절 (Style of Music 영역 - 반주)
        보컬이 쨍해지는 또 다른 결정적인 이유는 반주(악기) 소리가 너무 크거나 강하기 때문입니다. 이를 방지하기 위해 아래 키워드를 추가하여 반주의 에너지를 살짝 낮춰주십시오.
- chill, lo-fi, soft instrumentation, minimalist 

    1-4. 고음이 들어가는 부분에서는 단어 사이 사이에 ',', '.'를 삽입하여 의도적으로 숨을 고르게 만들게 합니다.

    1-5. 고음부에서 AI가 쨍하게 소리를 내지르는 현상(Belting)을 방지하고 싶다면, 아래의 규칙을 엄격히 적용하십시오.
- 도입부/1절 (확실하게 깔아주는 저음): [Low Calm Female Vocal] 또는 [Deep Spoken Vocal]
- 말하듯 힘을 완전히 빼는 파트: [Subdued Vocal]
- 코러스/고음 진입 파트 (에너지 억제): [Controlled Alto Vocal] 
              
2. 비트 및 다이내믹 : 제시된 [장르]에 알맞게 비트 및 다이내믹을 적용해주면 좋겠어요. 

3. 이스터 에그 (행동 교차 룰): Verse 파트 중 한 곳에 반드시 '~할 겸' (예: 바람 쐴 겸, 생각 지울 겸 등)이라는 표현을 딱 한 번 자연스럽게 삽입해서 주인공의 무심하고 여유로운 태도를 연출해요.

4. 곡 중간(Bridge 이후 등)에 해당 장르를 가장 잘 나타내는 **<Instrumental Solo> (악기 솔로 구간)**를 최소 1회 이상 강제로 삽입해요.

5. 전체적으로 매 가사 부분마다 보컬에 대한 상세한 내용을 []을 통해서 최대한 상세하게 표현합니다. 이때 [한국어 가사 전용 규칙 - 로마자 표기 절대 금지]
   - 모든 한국어 가사를 작성할 때, 가사 뒤나 옆에 알파벳으로 된 발음 표기(예: Romanization)를 절대 추가하지 마십시오.
   - 오직 순수한 한국어 문장과 의도된 영단어 훅(Hook)으로만 가사를 구성해야 합니다.

6. 해당 장르에 알맞는 최근 노래의 트랜드에 알맞는 단어들을 서칭하여 분석한 후에, 노래 가사 안에 일부 녹여서 표현해주세요.

모든 답변은 반드시 아래의 [구분자]를 사용하여 섹션을 나누어 작성해야 해요

###DETAIL###
이 칸에는 노래 제목(Subject), 장르(Genre), Tempo, Key, 악기 구성을 포함한 정보와 작사 배경 및 분위기 구성을 적어주세요. (띄어쓰기 포함 총 800자 이내) 

###PURPOSE###
이 칸에는 '작사가의 한마디'를 통해 이 곡의 기획 의도와 종합적인 곡 소개를 적어주세요.

###SUNO###
위 DETAIL 부분에 작성한 '장르, Tempo, 악기 구성, 분위기'를 음악 생성 AI(Suno)의 'Style of Music' 란에 바로 복사해 넣을 수 있도록, 영어 키워드 위주로 700~850자로 번역 및 요약해주세요. (절대 1000자 넘기지 말 것)

###EXCLUDE_STYLES###
이 칸에는 Suno AI가 곡을 생성할 때 절대 사용하지 말아야 할(피해야 할) 요소들을 영어 키워드로 쉼표로 구분하여 작성해주세요. (예: high pitch vocal, belting, screaming, loud brass). 200자 이내.

###VOCAL###
이 칸에는 해당 노래에 어울리는 보컬 스타일을 영어로 작성해주세요. 이때 톤과 스타일에 대해서는 자세하게 적어주세요.
형식: [성별], [톤], [스타일], [솔로/듀엣/그룹 여부] (250~280자 구체적으로 작성)

###LYRICS###
섹션별 가사: 곡의 구조는 반드시 [Intro] - [Verse 1] - [Pre-Chorus 1] - [Chorus 1] - [Verse 2] - [Pre-Chorus 2] - [Chorus 2] - [Bridge] - [Guitar Solo] - [Chorus 3] - [Outro]의 11개 섹션으로 구성해요. 섹션 표시에 마크다운 굵게(**)는 절대 사용하지 마요. 가사 외의 정보(구간 시간, 악기/분위기)는 반드시 영어로 [ ] 속에 넣어 표현해주세요. 
* [절대 규칙]: 전체 내용은 띄어쓰기와 지시어, 가사를 모두 포함하여 총 3500자 ~ 4500자 사이로 작성하세요. 절대 4900자를 넘기지 마세요.

###CLEAN_LYRICS###
클린 가사: 위 세부 항목이나 음악 구조(< > 부분) 및 [ ] 메타태그가 모두 제외된, 순수 가사 내용만 복사하기 쉽게 적어주세요.

###TAG###
이 곡과 어울리는 유튜브 노출용 트렌디 해쉬태그를 이용해서 한글과 영어 섞어서 정확히 30개 작성해줘요.

###UPLOAD###
유튜브 업로드용 요약 양식으로 작성해주세요. 
형식: [해쉬태그 5개] + [날짜와 감정 기반 짧은 소개글(한글)] + [날짜와 감정 기반 짧은 한글 소개글 영어로 번역] [곡 정보 요약(제목, 장르, Tempo, Key, 악기)] 순서.
"""

    full_prompt = f"{system_instruction}\n\n[작사 배경]\n{prompt}"
    text = ""
    
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"🧐 [참고] 사용 가능한 모델 총 {len(available_models)}개 확인 완료")
        
        preferred_models = [
            'models/gemini-2.5-flash',       
            'models/gemini-1.5-flash',
            'models/gemini-flash-latest'
        ]
        
        success = False
        for model_name in preferred_models:
            matched = [m for m in available_models if model_name.split('/')[-1] in m]
            
            if matched:
                target = matched[0]
                try:
                    print(f"🚀 [{target}] 모델로 생성을 시도합니다...")
                    model = genai.GenerativeModel(target)
                    response = model.generate_content(full_prompt)
                    text = response.text
                    print(f"✅ {target} 생성 성공!")
                    success = True
                    break
                except Exception as e:
                    print(f"⚠️ {target} 실패 (사유: 할당량 초과 등) -> 다음 모델로 넘어갑니다.")
            else:
                print(f"⚠️ {model_name} 모델은 현재 목록에 없어 건너뜁니다.")
                
        if not success:
            print("❌ 준비된 모든 대체 모델이 할당량 초과로 실패했습니다. 자정이 지나길 기다리거나 결제 연동이 필요합니다.")
            return {}
            
    except Exception as api_e:
        print(f"❌ API 모델 리스트를 불러오지 못했습니다: {api_e}")
        return {}

    try:
        markers_base = ["DETAIL", "PURPOSE", "SUNO", "EXCLUDE_STYLES", "VOCAL", "LYRICS", "CLEAN_LYRICS", "TAG", "UPLOAD"]
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

        print("\n[4] 파싱된 섹션별 글자 수 (0이면 AI가 생성을 빼먹은 것입니다):")
        for k, v in extracted.items():
            print(f" - {k}: {len(v)}자")

        return extracted
        
    except Exception as e:
        print(f"Gemini 데이터 파싱 에러: {e}")
        return {}

def get_chunks(text):
    return [{"text": {"content": text[i:i+2000]}} for i in range(0, max(1, len(text)), 2000)]

def save_to_notion(date_str, genre, prompt, data_dict):
    notion_token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")
    
    if not notion_token or not database_id or not data_dict.get("lyrics", "").strip(): 
        print("❌ 저장할 가사(LYRICS) 데이터가 비어있어 Notion 호출을 취소합니다.")
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
    children_blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": data_dict.get("tag", "")[:2000]}}]}})

    clean_lyrics_content = data_dict.get("clean_lyrics", "")
    clean_lyrics_chunks = [{"text": {"content": clean_lyrics_content[i:i+2000]}} for i in range(0, max(1, len(clean_lyrics_content)), 2000)] if clean_lyrics_content else [{"text": {"content": " "}}]

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {"title": [{"text": {"content": f"{date_str} ({genre})"}}]},
            "Generated Prompt": {"rich_text": [{"text": {"content": prompt}}]},
            "Detail": {"rich_text": [{"text": {"content": data_dict.get("detail", "")[:2000]}}]},
            "Purpose": {"rich_text": [{"text": {"content": data_dict.get("purpose", "")[:2000]}}]},
            "Suno": {"rich_text": [{"text": {"content": data_dict.get("suno", "")[:2000]}}]},
            "Exclude_styles": {"rich_text": [{"text": {"content": data_dict.get("exclude_styles", "")[:2000]}}]}, 
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

    final_prompt = f"""
<Current_Status>
- 진행 단계: 초기 컨셉 브레인스토밍 및 최종 음원 데이터 완성
- 타겟 결과물: 유튜브 및 오디오 플랫폼 업로드용 기획안 및 가사
</Current_Status>

<Brainstorming_Seed>
- 장르: {selected_genre}
- 배경/시간: {current_date}, {selected_time}
- 장소 및 상황: {selected_place}에서 {selected_action} 하는 중
- 감정선: {selected_emotion1} 분위기 속에서 느껴지는 {selected_emotion2}
</Brainstorming_Seed>

<Action_Steps>
위의 <Brainstorming_Seed>를 바탕으로 다음 단계를 거쳐 작업을 수행해 줘.

1) [내부 구상]: 이 키워드들을 엮어서 만들 수 있는 매력적인 스토리라인과 시각적 테마를 스스로 3가지 정도 깊이 있게 브레인스토밍 해봐. (이 과정은 너의 내부 추론을 위한 것이며 출력하지 않아도 됨)
2) [최종 도출]: 네가 구상한 아이디어 중 가장 훌륭하고 트렌디한 1가지를 확정해.
3) [포맷 출력]: 확정한 아이디어를 바탕으로, 시스템 프롬프트에서 요구한 ###DETAIL### 부터 ###UPLOAD### 까지의 9가지 필수 구분자 포맷에 맞추어 완벽한 최종 결과물만 출력해.
</Action_Steps>
"""
    print(f"\n[1] 생성된 프롬프트: {final_prompt}")
    
    max_retries = 5 
    result_data = {}
    
    for attempt in range(max_retries):
        print(f"\n[2] Gemini 가사 생성 중... (시도 {attempt + 1}/{max_retries})")
        result_data = generate_lyrics_with_gemini(final_prompt)
        
        suno_content = result_data.get("suno", "")
        lyrics_content = result_data.get("lyrics", "")
        
        suno_len = len(suno_content)
        lyrics_len = len(lyrics_content)
        
        print(f"   -> 생성된 Style(Suno) 글자 수: {suno_len}자")
        print(f"   -> 생성된 가사(Lyrics) 글자 수: {lyrics_len}자")
        
        if suno_len < 1000 and 2500 <= lyrics_len <= 4950:
            print("   ✅ 글자 수 한계치 통과! 완벽합니다.")
            break 
        else:
            print("   ⚠️ 글자 수 제한 초과 또는 미달! 다시 생성합니다.")
            if suno_len >= 1000:
                print("      - 사유: Style(Suno) 1000자 초과")
            if lyrics_len > 4950:
                print("      - 사유: 가사(Lyrics) 5000자 초과 위험")
            if lyrics_len < 2500:
                print("      - 사유: 가사(Lyrics)가 너무 짧음 (생략 발생 의심)")
                
    if not result_data.get("lyrics", "").strip():
        print("❌ 유효한 길이의 데이터를 생성하는 데 실패했습니다. 파이프라인을 종료합니다.")
        return

    print("\n[3] Notion 저장 시도...")
    save_to_notion(current_date, selected_genre, final_prompt, result_data)

if __name__ == "__main__":
    main()
