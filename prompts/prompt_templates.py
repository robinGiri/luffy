from langchain.prompts import PromptTemplate

def get_prompt_template():
    return PromptTemplate(
        template="{input}",
        input_variables=["input"]
    )
