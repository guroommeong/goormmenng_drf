from openai import OpenAI
import json
import re
import os

# OpenAI 클라이언트 설정
client = OpenAI(api_key=os.environ.get('OPEN_AI_API'))

# 새로운 쓰레드 생성 함수
def create_thread():
    try:
        response = client.beta.threads.create()
        return response.id
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None

# OpenAI API 기능 함수
def wait_on_run(run, thread_id):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    return run

def submit_message(assistant_id, thread_id, user_message):
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_message
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run

def get_response(thread_id):
    return client.beta.threads.messages.list(thread_id=thread_id, order="asc")

def parse_json_from_response(response_text):
    # 정규식을 사용하여 json 블록 추출
    match = re.search(r"```json\n(.*)\n```", response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            parsed_response = json.loads(json_str)
            return parsed_response
        except json.JSONDecodeError:
            return {"error": "응답을 JSON으로 파싱할 수 없습니다."}
    else:
        return {"error": "JSON 응답을 찾을 수 없습니다."}

def print_response(response):
    # 어시스턴트의 마지막 응답 (사용자 메시지는 제외)
    assistant_response = [res for res in response if res.role == "assistant"]
    if not assistant_response:
        return {"error": "응답을 찾을 수 없습니다."}

    # 어시스턴트의 마지막 응답을 추출
    last_response = assistant_response[-1].content[0].text.value

    # 응답에서 JSON 블록 추출 및 파싱
    parsed_response = parse_json_from_response(last_response)

    return parsed_response

def ask(assistant_id, thread_id, user_message):
    run = submit_message(
        assistant_id,
        thread_id,
        user_message,
    )

    run = wait_on_run(run, thread_id)
    response = print_response(get_response(thread_id).data)

    print("Parsed response:", response)  # 이 출력문으로 JSON 응답을 디버깅하세요.


    # 응답이 딕셔너리 형태라면 사용자 요청에 맞게 가공
    if isinstance(response, dict) and "error" not in response:
        return {
            "ai_text": response.get("ai_text", ""),
            "tags": response.get("tags", []),
            "recommendations": response.get("recommendations", [])
        }
    else:
        return response

