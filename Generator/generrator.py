import json
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

class RAGGenerator:
    def __init__(self, docs, openai_api_key, memory_file='conversation_memory.json'):
        self.docs = docs
        self.openai_api_key = openai_api_key
        self.memory_file = memory_file
        # Initialize the language model with OpenAI
        # model_name=model_name
        self.llm = OpenAI(api_key=openai_api_key, temperature=0)
        self.memory = ConversationBufferMemory(max_size=2000) 
        self.load_memory()

    
    def generate_response(self, question):
        retrieved_docs = self.docs
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        conversation_history = self.memory.load_memory()  # Get the full conversation context
        
        template = ChatPromptTemplate.from_template(
            "You are a knowledgeable assistant for finding out about speeches and history of them. Given the following context and chat history, answer the user's question comprehensively.\n\n"
            "Context:\n{context}\n\n"
            "Chat History:\n{history}\n\n"
            "User's Question: {question}\n\n"
            "Assistant's Answer:"
        )
        
        # Format the prompt with the provided context, history, and question
        formatted_prompt = template.format_prompt(
            context=context,
            history=conversation_history,
            question=question
        )
        
        chain = LLMChain(llm=self.llm, prompt_template=ChatPromptTemplate.from_string(formatted_prompt))
        
        response = chain.run(question)
        
        self.memory.add_interaction(question, response)
        self.save_memory()

        return response

    def save_memory(self):
        """
        Save the conversation buffer memory to a JSON file.
        """
        with open(self.memory_file, 'w') as file:
            json.dump(self.memory.load_memory(), file)

    def load_memory(self):
        """
        Load the conversation buffer memory from a JSON file.
        """
        try:
            with open(self.memory_file, 'r') as file:
                memory_data = json.load(file)
                self.memory.load_memory(memory_data)
        except (FileNotFoundError, json.JSONDecodeError):
            self.memory.clear()

# if __name__ == "__main__":
    
    # rag_generator = RAGGenerator(index_file, docs_folder, openai_api_key)
    
    # question = "What are the recent advancements in renewable energy?"
    
    # response = rag_generator.generate_response(question)
    # print("Assistant's Answer:", response)
