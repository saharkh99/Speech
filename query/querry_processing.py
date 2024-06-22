# Query Translation and transformation (hyde(similarity based on hypothesis answers), follow up questions, step back, multiquery)
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda

# Multi Query: Different Perspectives
def generate_alternative_queries(question):
    """
    Generates three alternative versions of a given question to enhance document retrieval
    from a vector database using a distance-based similarity search approach.
    
    Parameters:
    - question (str): The original question provided by the user.
    
    Returns:
    - list: A list of three alternative questions.
    """
    # Define the template
    template = """You are an AI language model assistant. Your task is to generate three
    different versions of the given user question to retrieve relevant documents from a vector
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search.
    Provide these alternative questions separated by newlines. Original question: {question}"""
    
    # Create the prompt using the template
    prompt_perspectives = ChatPromptTemplate.from_template(template.format(question=question))
    
    # Use the AI model to generate the responses
    ai_model = ChatOpenAI(temperature=0)
    generated_output = ai_model(prompt_perspectives)
    
    # Parse the output to split by newlines and return as a list
    parsed_output = StrOutputParser()(generated_output)
    alternative_queries = parsed_output.split("\n")
    
    return alternative_queries


def step_back_prompting(question):
    examples = [

    {
        "input": "What is the birthplace of Albert Einstein?",
        "output": "what is Albert Einstein's personal history?",
    },
    {
        "input": "Can a Tesla car drive itself?",
        "output": "what can a Tesla car do?",
    },
    {
        "input": "Did Queen Elizabeth II ever visit Canada?",
        "output": "what is Queen Elizabeth II's travel history?",
    },
    {
        "input": "Can a SpaceX rocket land itself?",
        "output": "what can a SpaceX rocket do?",
    }
]
# We now transform these to example messages
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at world knowledge. Your task is to step back and paraphrase a question to a more generic step-back question, which is much easier to answer. Here are few examples:""",
        ),
        few_shot_prompt,
        ("user", "{question}"),
    ]
) 
    question_gen = prompt | ChatOpenAI(temperature=0) | StrOutputParser()
    results = question_gen.invoke({"question": question})
    return results

