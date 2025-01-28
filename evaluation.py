from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import AspectCritic, BleuScore
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from ragas import EvaluationDataset
import requests, json, argparse, os, time
from pprint import pprint


def completion_request(prompt, model):
    url = "http://127.0.0.1:1234/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 50
    }
    start_time = time.time()
    response = requests.post(url, headers=headers, json=data)
    end_time = time.time()
    prompt_time = end_time - start_time
    return response.json()['choices'][0]['message']['content'], prompt_time

def evaluate(scorer, samples, result_json, aspect_name):
    score = 0
    for idx, sample in enumerate(samples):
        point = scorer.single_turn_score(sample=sample)
        score += point
        result_json['result_list'][idx][aspect_name] = point

    score /= len(samples)
    result_json[f'{aspect_name}_score'] = score
    return result_json

parser = argparse.ArgumentParser()

parser.add_argument(
    '--model', 
    type=str, 
    required=True, 
    help='Name of the model to evaluate'
)

args = parser.parse_args()

model_name = args.model

samples = []
data_json_list =[]
prompt_time_list = []
file_path = 'test.jsonl'


with open(file_path, 'r') as file:
    for line in file:
        data_json_list.append(json.loads(line))
        
for line in data_json_list:
    completion, prompt_time = completion_request(line['prompt'], model=model_name)
    sample = SingleTurnSample(
        user_input=line['prompt'],
        reference=line['completion'],
        response=completion,
    )
    prompt_time_list.append(prompt_time)
    samples.append(sample)

openai = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", api_key=os.environ['OPENAI_API_KEY']))

result_json = {'model':model_name,
              'generating_time_overall': f'{sum(prompt_time_list):.5f}',
              'bleu_score': 0,
              'style_score': 0,
              'closure_score': 0,
              'relevance_score': 0,
              'coherence_score': 0,
              'result_list':[]}

for idx, sample in enumerate(samples):
    result_json['result_list'].append({'id':idx,
                                       'generation_time': f'{prompt_time_list[idx]:.5f}',
                                       'bleu': 0,
                                       'style': 0,
                                       'closure': 0,
                                       'relevance': 0,
                                       'coherence': 0,
                                       'prompt':sample.user_input, 
                                       'completion':sample.response
                                       })


bleu_scorer = BleuScore()

style_scorer =  AspectCritic(
        name="style",
        definition="Is the submission maintains a consistent and appropriate tone, language, and manner that matches the desired character?",
        llm=openai
    )

closure_scorer =  AspectCritic(
        name="closure",
        definition="Is the submission fully concluded, without leaving any unfinished statements?",
        llm=openai
    )

relevance_scorer =  AspectCritic(
        name="relevance",
        definition="Is the submission aligns with the user input, staying true to context?",
        llm=openai
    )

coherence_scorer =  AspectCritic(
        name="coherence",
        definition="Is the submission coherent with received message?",
        llm=openai
    )

result_json = evaluate(scorer=bleu_scorer,samples=samples,result_json=result_json,aspect_name='bleu')
result_json = evaluate(scorer=style_scorer,samples=samples,result_json=result_json,aspect_name='style')
result_json = evaluate(scorer=closure_scorer,samples=samples,result_json=result_json,aspect_name='closure')
result_json = evaluate(scorer=relevance_scorer,samples=samples,result_json=result_json,aspect_name='relevance')
result_json = evaluate(scorer=coherence_scorer,samples=samples,result_json=result_json,aspect_name='coherence')

with open(f'metrics/metrics_{model_name}.json', 'w') as f:
    json.dump(result_json, f)
pprint(result_json)
