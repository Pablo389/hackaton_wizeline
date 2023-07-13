import requests

from steamship import Steamship
    
# Load the package instance stub.
pkg = Steamship.use(
    "test-chat",
    instance_handle="test-chat-59g",
    api_key=""
)

# Invoke the method
resp = pkg.invoke(
    "send_message",
    message="hola",
    chat_history_handle="asda"
)

print(resp)
url = "https://graph.facebook.com/v16.0/118631901236098/messages"
headers = {
    "Authorization": "Bearer ...",
    "Content-Type": "application/json"
}
data = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": "number",
      "type": "text",
      "text": { 
        "preview_url": False,
        "body": resp
        }
    }

response = requests.post(url, headers=headers, json=data)
print(response.text)
