import gradio as gr
from bsky_agents import Agents
from atproto import Client, models
import yaml, shutil, time

def loop_ai_agents(session_string):
    client = Client()
    client.login(session_string=session_string)
    team = Agents(client=client)
    tweets = []
    while 1:
        with gr.Tab("Outputs"):
            tweet = team(prompt="",option=1)
            tweets.append(tweet.summary)
            time.sleep(5) 
            if len(tweets) >= 5:
                break
    return tweets


def stop_loop():
    return "Loop stopped."

def create_post(prompt, session_string):
    client = Client()
    client.login(session_string=session_string)
    team = Agents(client=client)
    return team(prompt=prompt, option=2).summary

with gr.Blocks() as user_interface:
    
    with open('bsky_config.yaml', 'r') as file:
        bsky_config = yaml.safe_load(file)
        

    client = Client()
    client.login(bsky_config['handle'], bsky_config['password'])
    session_string = client.export_session_string()
    
    print(client.me.display_name)
    
    gr.Markdown("# Gandalf AI")
    with gr.Tab("Create Post"):
        
        gr.Textbox(label="User", value=client.me.display_name, interactive=False)
        state = gr.State(value=session_string)
        prompt_input = gr.Textbox(label="Task for agents")
        output = gr.Textbox(label="Generated Post", interactive=False)
        print(type(session_string))
        generate_button = gr.Button("Generate")
        generate_button.click(fn=create_post, inputs=[prompt_input,state], outputs=output)
        

    with gr.Tab("Run AI Loop"):
        start_button = gr.Button("Start")
        stop_button = gr.Button("Stop")
        state = gr.State(value=session_string)
        loop_output = gr.Textbox(label="Generated Replies", interactive=False)

        run = start_button.click(fn=loop_ai_agents,inputs=state, outputs=loop_output)
        stop_button.click(fn=None, inputs=None, outputs=None, cancels=[run])

user_interface.launch()
