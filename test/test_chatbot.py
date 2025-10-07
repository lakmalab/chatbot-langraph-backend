# test_chatbot.py
import requests
import json

BASE_URL = "http://localhost:8000"


def test_chatbot():
    # 1. Create session
    print("1. Creating session...")
    response = requests.post(f"{BASE_URL}/api/v1/session/create")
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"✓ Session created: {session_id}\n")

    # 2. Test greeting
    print("2. Testing greeting...")
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        json={
            "session_id": session_id,
            "message": "Hello",
            "scheme_type": "pension"
        }
    )
    print(f"Bot: {response.json()['response']}\n")

    # 3. Test calculation with complete info
    print("3. Testing pension calculation...")
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        json={
            "session_id": session_id,
            "message": "I am 35 years old and want 50000 monthly pension",
            "scheme_type": "pension"
        }
    )
    result = response.json()
    print(f"Bot: {result['response']}\n")
    conversation_id = result['conversation_id']

    # 4. Test incomplete info
    print("4. Testing incomplete information...")
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        json={
            "session_id": session_id,
            "message": "What if I want 60k pension?",
            "scheme_type": "pension",
            "conversation_id": conversation_id
        }
    )
    print(f"Bot: {response.json()['response']}\n")

    # 5. Test question about scheme
    print("5. Testing scheme question...")
    response = requests.post(
        f"{BASE_URL}/api/v1/chat/message",
        json={
            "session_id": session_id,
            "message": "Who can join this pension scheme?",
            "scheme_type": "pension",
            "conversation_id": conversation_id
        }
    )
    print(f"Bot: {response.json()['response']}\n")

    # 6. Get chat history
    print("6. Getting chat history...")
    response = requests.get(f"{BASE_URL}/api/v1/chat/history/{conversation_id}")
    history = response.json()
    print(f"✓ Total messages in conversation: {len(history['messages'])}\n")

    # 7. Get calculations
    print("7. Getting all calculations...")
    response = requests.get(f"{BASE_URL}/api/v1/pension/calculations/{session_id}")
    calculations = response.json()
    print(f"✓ Total calculations: {len(calculations['calculations'])}")
    for calc in calculations['calculations']:
        print(f"  - Age {calc['current_age']}: Rs. {calc['monthly_contribution']}/month")


if __name__ == "__main__":
    test_chatbot()