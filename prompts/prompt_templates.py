from langchain.prompts import PromptTemplate

def get_prompt_template():
    return PromptTemplate(
        template="Once upon a time {input}",
        input_variables=["input"]
    )
