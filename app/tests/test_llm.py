from pathlib import Path

from loguru import logger
from dotenv import load_dotenv

load_dotenv()

logger.add(
    Path(__file__).with_suffix(".log"), mode="w", encoding="utf-8", level="DEBUG"
)

from llm import LLMClient

def main():
    user_query = 'Do causal discovery on this dataset'
    client = LLMClient()
    prompt = (f"Based on the query that I provided: {user_query} \n\n; "
              "extract the following information and summarize them in a json format, and output this json object."
              "Within the output, the key, the corresponding value options and their meanings are: \n\n "
              "1. Describe whether the relationship between the variables are assumed to be linear or not:"
              "Key: 'linearity'. \n\n"
              "Options of value (bool): True, False. \n\n"
              "2. Describe whether the fitting models between two variables, the error terms are assumed to be Gaussian or not:"
              "Key: 'gaussian_error'. \n\n"
              "Options of value (bool): True, False. \n\n"
              "3. The significance level (denoted as alpha) for doing statistical testing in the following analysis:"
              "Key: 'alpha'. \n\n"
              "Options of value (float): A numeric value that is greater than 0 and less than 1. \n\n"
              "4. Describe whether the dataset is heterogeneous or not:"
              "Key: 'heterogeneous'. \n\n"
              "Options of value (bool): True, False. \n\n"
              "5. If the dataset is heterogeneous, what is the name of the column in the dataset that represents the domain index:"
              "Key: 'domain_index'. \n\n"
              "Options of value (str): The name of the column that represents the domain index. \n\n"
              "6. Which algorithm the user would like to use to do causal discovery:"
              "Key: 'selected_algorithm'. \n\n"
              "7. How many minutes the user can wait for the causal discovery algorithm:"
              "Key: 'waiting_minutes'. \n\n"
              "Options of value (float): A numeric value that is greater than 0. \n\n"
              "8. Does the user accept the output graph including undirected edges/undeterministic directions:"
              "Key: 'accept_CPDAG'. \n\n"
              "Options of value (bool, by default is True, only if the user explicitly asks for it to be False): True, False. \n\n"
              "9. Is the dataset a time-series dataset or a tabular dataset:"
              "Key: 'time_series'. \n\n"
              "Options of value (bool, by default is False, only if the user explicitly asks for it to be True): True, False. \n\n"
              "However, for each key, if the value extracted from queries does not match provided options, or if the queries do not provide enough information and you cannot summarize them,"
              "the value for such key should be set to None! \n\n"
              "Just give me the output in a json format, do not provide other information! \n\n")

    response = client.chat_completion(
        prompt=prompt,
        system_prompt="You are a helpful assistant. You are a causal discovery expert. You are given a user query and you need to extract the information from the query and return a json object.",
        json_response=True
    )
    info_extracted = response

    logger.info(f"Info extracted: {info_extracted = }, {type(info_extracted) = }")    
    logger.info("end")


if __name__ == "__main__":
    main()
