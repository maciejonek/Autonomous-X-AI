import autogen
import requests
import tweepy
from requests_oauthlib import OAuth1
import json
from news_search import Search

f = open('api_keys.json')
api_keys = json.load(f)

NEWS_API_KEY = api_keys["NEWS_API_KEY"]
WNEWS_API_KEY = api_keys["WORLD_NEWS_API_KEY"]
PIXABAY_API_KEY = api_keys["PIXABAY_API_KEY"]
TWITTER_API_KEY = api_keys["TWITTER_API_KEY"]
TWITTER_API_SECRET = api_keys["TWITTER_API_SECRET"]
TWITTER_ACCESS_TOKEN = api_keys["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET = api_keys["TWITTER_ACCESS_SECRET"]

twitter_client = tweepy.Client(consumer_key=TWITTER_API_KEY,
                               consumer_secret=TWITTER_API_SECRET,
                               access_token=TWITTER_ACCESS_TOKEN,
                               access_token_secret=TWITTER_ACCESS_SECRET)

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



news_agent = autogen.AssistantAgent(
    name="NewsAgent",
    system_message="Fetch the latest news. Return 'TERMINATE' when done.",
    llm_config=llm_config
)

summary_agent = autogen.AssistantAgent(
    name="SummaryAgent",
    system_message="Summarize the given news article. Your summary can not be longer that 279 symbols. Don't add any links to you summary. 'TERMINATE' when done.",
    llm_config=llm_config_summary_agent
)


image_agent = autogen.AssistantAgent(
    name="ImageAgent",
    system_message="Find a relevant image for the given topic. Return 'TERMINATE' when done.",
    llm_config=llm_config
)


twitter_agent = autogen.AssistantAgent(
    name="TwitterAgent",
    system_message="Post the summary and image to Twitter. Return 'TERMINATE' when done.",
    llm_config=llm_config
)

user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="TERMINATE", 
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
    search = Search(WNEWS_API_KEY)
    response = search.search_news(query=query)
    article = response.get("news", [])
    result = {"title":"", "content":""}
    result["title"] = article[0].get("title", "No news found")
    result["content"] = article[0].get("text", "")
    return result

# @user_proxy.register_for_execution()
# @news_agent.register_for_llm(description="Fetch the news")
# def fetch_news():
#     url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
#     response = requests.get(url).json()
#     articles = response.get("articles", [])
#     return articles[0] if articles else {"title": "No news found", "content": ""}

@user_proxy.register_for_execution()
@image_agent.register_for_llm(description="Find image and save it to file")
def find_image(query:str):
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=photo&per_page=3"
    response = requests.get(url).json()
    hits = response.get("hits", [])

    data = requests.get(hits[0]["webformatURL"]).content
    f = open('img.jpg','wb')
    f.write(data)
    f.close()
    return "Image saved to img.jpg"


@user_proxy.register_for_execution()
@twitter_agent.register_for_llm(description="Post tweet")
def post_to_twitter(summary:str):
    if not summary:
        return "Cannot post: Missing summary"
    response = twitter_client.create_tweet(text=summary)
    return response

group_chat = autogen.GroupChat(
    agents=[user_proxy, news_agent, summary_agent, image_agent, twitter_agent], messages=[], max_round=12
)
manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

user_proxy.initiate_chat(
    manager,
    message="""
Find news with one of this words '','','' , if cannot find article find query related to this word, summarize it, find image related to news topic and download it and finally post tweet without image on Twitter
""",
)