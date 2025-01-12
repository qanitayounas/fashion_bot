from dotenv import load_dotenv
import warnings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import pandas as pd

# Load environment variables (for OpenAI API key)
load_dotenv()

# Ignore LangChainDeprecationWarning
warnings.simplefilter("ignore")

# Initialize LLM (ChatOpenAI)
LLM = ChatOpenAI(model="gpt-4o-mini")  # Use the correct OpenAI model

# Initialize memory with updated API
memory = ConversationBufferWindowMemory(k=5, return_messages=True, memory_key="history")

# Define the prompt template
prompt_template = ChatPromptTemplate.from_template(
    """You are a fashion assistant that answers questions only based on the content of the provided fashion dataset
    and the context of the previous conversation.

    The content from the dataset is:
    {dataset_content}

    Previous conversation:
    {history}

    Question:
    {input}

    Please answer the question using only the information from the fashion dataset and the context of the previous conversation.
    Format your response as follows:
    1. Start with a brief introduction or summary.
    2. List any relevant fashion items or suggestions as numbered points.
    3. End with a concluding statement or additional advice.
    """
)

# Function to load the fashion dataset
def load_fashion_data(file_path):
    try:
        # Read the Excel file
        data = pd.read_excel(file_path, engine='xlrd')  # Ensure xlrd is installed
        return data
    except Exception as e:
        print(f"Error loading fashion data: {e}")
        return None

# Function to format the response
def format_response(response):
    lines = response.split('\n')
    formatted_lines = []
    item_count = 1

    for line in lines:
        line = line.strip()
        if line.startswith('-'):
            formatted_lines.append(f"{item_count}. {line[1:].strip()}")
            item_count += 1
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)

# Function to generate a response using LangChain memory
def generate_response(question, fashion_data):
    try:
        # Convert dataset to a string for use in the prompt
        dataset_content = fashion_data.to_string(index=False)

        # Load conversation history
        history = memory.load_memory_variables({}).get("history", [])

        # Format the prompt
        formatted_prompt = prompt_template.format(
            dataset_content=dataset_content,
            history=history,
            input=question
        )

        # Generate a response using the LLM
        response = LLM.predict(formatted_prompt)

        # Format the response
        formatted_response = format_response(response)

        # Save the interaction to memory
        memory.save_context({"input": question}, {"output": formatted_response})

        return formatted_response
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"An error occurred: {e}"

# Main function to interact with the assistant
def main():
    # Load the fashion dataset
    fashion_data_path = "./fashion_data.xls"
    fashion_data = load_fashion_data(fashion_data_path)

    if fashion_data is None:
        print("Failed to load fashion dataset. Exiting.")
        return

    print("Fashion assistant is ready. Ask your questions!")
    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            print("Exiting the assistant. Goodbye!")
            break

        response = generate_response(question, fashion_data)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()