# Standard library import
import logging

# Third-party imports
from twilio.rest import Client
from decouple import config
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
#from steamship import Steamship


#Librerias para las cadenas y memoria
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory


#Librerias para el embedding y retrieval
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

#Librerias para los prompts de chat
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config("TWILIO_ACCOUNT_SID")
auth_token = config("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
twilio_number = config('TWILIO_NUMBER')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sending message logic through Twilio Messaging API
def send_message(to_number, body_text):
    try:
        message = client.messages.create(
            from_=f"whatsapp:{twilio_number}",
            body=body_text,
            to=f"whatsapp:{to_number}"
            )
        logger.info(f"Message sent to {to_number}: {message.body}")
    except Exception as e:
        logger.error(f"Error sending message to {to_number}: {e}")


def vector_qa(direc_marca):
    #Directorio donde se guarda toda la info de los embeddings en chroma
    persist_directory=direc_marca
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    #Template que se le va a pasar ael retrieval para que obtenga la info que quiero (A/B test)
    prompt_template = """Usa el siguiente contexto para responder la pregunta al final. Si no la sabes o la encuentras no la trates de inventar.

    {context}

    Pregunta: {question}
    Tu respuesta:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    #qa impulse es la herramienta con la que haremos retrieval de documentos, retorna texto
    qa_marca = RetrievalQA.from_chain_type(llm=ChatOpenAI(), chain_type= "stuff", retriever = vectordb.as_retriever(), chain_type_kwargs=chain_type_kwargs)
    
    return qa_marca

def chat_prompt():
    #Template del prompt que va a ser enviado al modelo de texto para que me regrese el mejor mensaje
    template="""Eres un chatbot especializado en atención al cliente. Tu trabajo es responder al cliente de la manera mas concisa y segura posible. Este es el historial de mensajes:
    {chat_history}
    Y esta es la información que recabaste para poder responder la pregunta:
    {qa_answer}

    A continuacion esta el mensaje del cliente:
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    cht_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    return cht_prompt

def chat(pregunta, memory):
    #Inicializar la memoria
    chat=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    chain = LLMChain(llm=chat, prompt=chat_prompt(), memory=memory, verbose=True)
    directorio = "impulse_chroma"
    qa_marca = vector_qa(directorio)
    respuesta_impulse = qa_marca.run(pregunta)
    resp_ia = chain.run(question = pregunta, text = pregunta, qa_answer = respuesta_impulse)
    return resp_ia

       