import os
from typing import Tuple
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller # Browser-use has a deprectation warning, which was bugging me
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from scripts.models import InputRow, OutputRow


def get_agent(input_row: InputRow, output_dir: str) -> Tuple[Agent, Browser]:
	download_path = os.path.join(output_dir, input_row.siteName.replace(" ", "_"))
	os.makedirs(download_path)

	browser = Browser(
		config=BrowserConfig(
			new_context_config=BrowserContextConfig(
				save_downloads_path=download_path,
				browser_window_size={'width': 1280, 'height': 1100},
				locale='en-UK',
				user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
			)
		)
	)

	sensitive_data = {
		"x_name": str(input_row.username),
		"x_password": str(input_row.password),
	}
	
	initial_actions = [{"go_to_url": {"url": str(input_row.siteURL)}}]

	task = "Login with x_name and x_password if required. " + str(input_row.navHelper)

	agent_instance =  Agent(
		browser=browser,
		initial_actions=initial_actions,
		max_actions_per_step=10,
		task=task,
		llm=ChatOpenAI(model="gpt-4o"),
		sensitive_data=sensitive_data,
		use_vision=True,
	)

	return agent_instance, browser