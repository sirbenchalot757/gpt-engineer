import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

def load_env_variables(env_path):
    load_dotenv(dotenv_path=env_path)

def get_prompt_template(script_dir, filename):
    prompt_path = os.path.join(script_dir, filename)
    with open(prompt_path, 'r') as file:
        return file.read()

def format_prompt(prompt_template, text):
    try:
        return prompt_template.format(text=text), None
    except KeyError as e:
        return "", f"Key error in formatting the prompt: {e}"
    except IndexError as e:
        return "", f"Index error in formatting the prompt: {e}"

def calculate_cost(response):
    input_token_count = response.usage.total_tokens
    output_token_count = len(response.choices[0].message.content.split())

    input_cost_per_token = 0.001
    output_cost_per_token = 0.002

    return ((input_token_count * input_cost_per_token) + (output_token_count * output_cost_per_token)) / 1000

def gpt_process(text):
    env_path = '../../.env'
    load_env_variables(env_path)

    openai_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=openai_api_key)

    script_dir = os.path.dirname(__file__)
    prompt_template = get_prompt_template(script_dir, 'prompt_template.txt')

    formatted_prompt, error = format_prompt(prompt_template, text)
    if error:
        print(error)
        return "", 0

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": formatted_prompt}
            ]
        )

        processed_text = response.choices[0].message.content.strip()
        total_cost = calculate_cost(response)

        return processed_text, total_cost

    except openai.OpenAIError as e:
        error_message = f"OpenAI API error: {e}"
        print(error_message)
        log_error(error_message)
        return "", 0

def log_error(message, filename="error_log.txt"):
    with open(filename, "a") as log_file:
        log_file.write(message + "\n")

# Add any additional error handling as needed
