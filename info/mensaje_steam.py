from steamship import Steamship

#Obtiene un mensaje de steamship
# Load the package instance stub.
pkg = Steamship.use(
    "chatbot-qusek",
    instance_handle="chatbot-qusek-d49",
    api_key=""
)

# Invoke the method
resp = pkg.invoke(
    "send_message",
    message="Me gustaría saber cual es tu nombre",
    chat_history_handle="prueba1"
)

print(resp)