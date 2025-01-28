import autogen
import requests
from requests_oauthlib import OAuth1
import json
from news_search import Search
from atproto import models


class Agents():
    def __init__(self, client=None):
        self.client = client
        

        f = open('api_keys.json')
        api_keys = json.load(f)

        self.WNEWS_API_KEY = api_keys["WORLD_NEWS_API_KEY"]
    
    def __call__(self, prompt=' ', option=1):
        
        llm_config = {
            "cache_seed": 43,
            "temperature": 0,
            "config_list": autogen.config_list_from_json(
                env_or_file="OAI_CONFIG_LIST.json",
                filter_dict={"model": ["gpt-4o-mini"]}
            ),
            "timeout": 120
        }

        llm_config_summary_agent = {
            "cache_seed": 43,
            "temperature": 0.7,
            "config_list": autogen.config_list_from_json(
                env_or_file="OAI_CONFIG_LIST.json",
                filter_dict={"model": ["gpt-4o-mini"]}
            ),
            "timeout": 120
        }

        llm_config_writer_agent = {
            "cache_seed": 43,
            "temperature": 1,
            "config_list": autogen.config_list_from_json(
                env_or_file="OAI_CONFIG_LIST.json",
                filter_dict={"model": ["mistral-7b-gandalf"]}
            ),
            "timeout": 12000
        }

        news_agent = autogen.AssistantAgent(
            name="NewsAgent",
            system_message="Fetch the latest news. Return 'TERMINATE' when done.",
            llm_config=llm_config
        )
        
        
        summary_agent = autogen.AssistantAgent(
            name="SummaryAgent",
            description="Agent who summary fetched information for writer",
            system_message="Summarize received message from fetching agents. Provide summary in format: Text: 'text' 'TERMINATE' when done.",
            llm_config=llm_config_summary_agent
        )
        
        prompt_preparation_agent = autogen.AssistantAgent(
            name="PromptPreparationAgent",
            description="An AI agent designed to analyze input (post text or summary) and create a structured, contextually relevant prompt for WritingAgentGandalf.",
            system_message=(
                "You are PromptPreparationAgent, an expert in crafting clear and concise prompts for WritingAgentGandalf. "
                "Your role is to take input text, analyze its context and tone, and prepare a prompt that guides Gandalf to write an engaging reply. "
                "Focus on clarity, ensure relevance, and provide any key points or directions needed for Gandalf to excel in the task. "
                "Avoid overloading the prompt with unnecessary information, and keep it concise and actionable."
            ),
            llm_config=llm_config
        )
        

        writer_agent = autogen.AssistantAgent(
            name="WritingAgentGandalf",
            description="An AI agent specialized in crafting thoughtful and engaging post replies based on the provided prompt or summary from other agents.",
            system_message=(
                "You are WritingAgentGandalf, a creative and articulate assistant skilled at writing concise, engaging, and contextually appropriate replies. "
                "Your goal is to craft replies that resonate with the post content or summary provided to you. "
                "Focus on clarity, tone, and relevance. Avoid adding unnecessary details and stay on task."
            ),
            llm_config=llm_config_writer_agent
        )

        bluesky_fetch_agent = autogen.AssistantAgent(
            name="SocialMediaReadingAgent",
            system_message=("Fetch Blue Sky random post. Provide text gotten from request. Return 'TERMINATE' when done."),
            llm_config=llm_config
        )
        
        bluesky_post_agent = autogen.AssistantAgent(
            name="SocialMediaPostingAgent",
            description="Team member who post content on social media. Task: Receive content from writer and upload is without any changes",
            system_message="You are Social Media Manager who receive text from Writer. Your task is to post on BlueSky platform.. Return 'TERMINATE' when done.",
            llm_config=llm_config
        )


        user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            human_input_mode="NEVER", 
            max_consecutive_auto_reply=5,
            code_execution_config={
                "last_n_messages": 3,
                "work_dir": "code",
                "use_docker": False,
            },
        )



        @user_proxy.register_for_execution()
        @news_agent.register_for_llm(description="Search and fetch news by query")
        def fetch_news(query:str):
            search = Search(self.WNEWS_API_KEY)
            response = search.search_news(query=query)
            article = response.get("news", [])
            result = {"title":"", "content":""}
            result["title"] = article[0].get("title", "No news found")
            result["content"] = article[0].get("text", "")
            return result


        @user_proxy.register_for_execution()
        @bluesky_fetch_agent.register_for_llm(description="Fetch post information from Blue Sky")
        def fetch_post():
            data = self.client.app.bsky.feed.get_feed({
                'feed': 'at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot',
                'limit': 1,
            }, headers={'Accept-Language': 'en'})
            
            return data.feed[0]
        
        @user_proxy.register_for_execution()
        @bluesky_post_agent.register_for_llm(description="Create post on Blue Sky")
        def create_post(option:int, text:str, uri:str, cid:str):
            if option == 1:
                if not text:
                    return "Cannot post: Missing summary"
                record = models.AppBskyFeedPost.CreateRecordResponse(uri=uri, cid=cid)
                strong_ref = models.create_strong_ref(record)
                response = self.client.send_post(text=text,reply_to=models.AppBskyFeedPost.ReplyRef(parent=strong_ref, root=strong_ref))
            if option == 2:
                response = self.client.send_post(text=text)
            return response
            
        

        group_chat = autogen.GroupChat(
            agents=[user_proxy, bluesky_fetch_agent, writer_agent, summary_agent, bluesky_post_agent, news_agent, prompt_preparation_agent], messages=[], max_round=12
        )
        manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)


        result = user_proxy.initiate_chat(
            manager,
            message=f"""
            
            As a Social Media team, your task is to reply under Blue Sky posts (It is social media platform similar to Twitter) or create own posts.
            Posts have to be written by WritingAgentGandalf. 
            Depending on user arguments, choose one of the following paths to complete the task.
            
            ### Option 1: Blue Sky Post Reply Task  

            Your task is to fetch a random post from Blue Sky and write a reply based on the content of the fetched post. Follow these steps to complete the task:

            1. Fetch the Post
            - Retrieve a random post from Blue Sky.  
            - If the post fetch fails, retry until successful.  

            2. Extract Post Text
            - From the response received from the API call, extract the `text` field from the post.  

            3. Prepare the Prompt for Gandalf
            - Pass the extracted text to PromptPreparationAgent.  
            - The agent will analyze the text and prepare a structured prompt for WriterAgentGandalf. This prompt should guide Gandalf in crafting a thoughtful and engaging reply.  

            4. Generate the Reply 
            - Once PromptPreparationAgent has prepared the prompt, pass it to WriterAgentGandalf.  
            - Gandalf will create the reply based on the provided prompt. The reply generated by Gandalf is final and cannot be changed by any other team members.  

            5. Prepare the Reply Post
            - To create the reply, gather the following components:  
                - Parent post URI  
                - Parent post CID  
                - Reply text generated by Gandalf  
                - Selected option (if applicable)  

            - Writing Specialist: The reply text should be crafted by WriterAgentGandalf, but do not provide any extra context or information to him. He should focus only on the provided prompt and stay on task.

            6. Post the Reply 
            - With the URI, CID, and reply text, post the reply under the original post.

            7. Output the Result 
            - Present the result in the following format:  
                Post Text: 'text from the original post'  
                Team Reply: 'reply generated by WriterAgentGandalf'  
            
            
            ### Option 2
            Your task is to create Blue Sky post, based on user prompt. 
            Post cannot be longer that 250 characters.
            If there is need to find some information, search in news.
            
            To create post you need text written by your scribe and selected option.
            Remember it is a post on your timeline not a reply under another user.
            
            Post should be written by your Writing Specialist but do not provide him any extra information he has to stay focused on his task and write wise reply.
            
            As a result write your post text.
            
            Result format:
            Post text: 'text from post'
            
            ### User arguments:
            Selected option: {option}
            User prompt: {prompt}
            
            ### Important
            - If user selected option 1 and provided prompt, ignore this prompt.
            - If post was successful, summarize your task and finish
            
            """
        )
        
        return result


