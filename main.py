import json
import time

from openai import OpenAI

from card_info import CardInfo
from trello_api import TrelloAPI

# from trello_api import create_board, get_lists_on_board, create_lists_on_board, create_card_for_list

client = OpenAI()

# Upload a file with an "assistants" purpose
file = client.files.create(
    file=open("test.csv", "rb"),
    purpose='assistants'
)

trello_api = TrelloAPI()

function_info = {
    'create_board': trello_api.create_board,
    'get_lists_on_board': trello_api.get_lists_on_board,
    'create_lists_on_board': trello_api.create_lists_on_board,
    'create_card_for_list': trello_api.create_card_for_list,
    'get_task_list': trello_api.get_task_list
}

# assistant = client.beta.assistants.create(
#     name="Math Tutor",
#     instructions="Your role as Daily Manager is to check if there is any files that is provided to you. If there is some file added please check the file. There should be some details about the tasks added onto the file. Your task is to return the data in a structured form",
#     # instructions="Your role as Daily Manager is to start by inquiring if the user has a project plan. If a project plan exists, your questions will be tailored to the specific tasks and their scheduled completion dates, ensuring the user is on track with their objectives. If there's no project plan, you will initially ask about the tasks and goals for the entire week, providing a structure for the user to organize their work. In the absence of a weekly plan, you'll encourage the user to focus on ad-hoc tasks, maintaining flexibility while ensuring productivity. You'll balance a professional demeanor with approachability, offering constructive hints and solutions for any obstacles encountered, ensuring the user feels supported and accountable. Your interactions will emphasize accomplishments, plans, obstacles, and project progress, with a focus on productivity and problem-solving.",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-3.5-turbo-0125",
#     file_ids=[file.id]
# )

card_info_schema = CardInfo.schema()

assistant = client.beta.assistants.create(
    instructions="Your role as Daily Manager is to check if there is any files that is provided to you. If there is some file added please check the file. There should be some details about the tasks added onto the file. Your task is to return the data in a structured form",
    model="gpt-4-turbo-preview",
    file_ids=[file.id],
    tools=[
        {
            "type": "code_interpreter"
        }, {
            "type": "function",
            "function": {
                "name": "create_board",
                "description": "create new board for new sheet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "board_name": {"type": "string", "description": "Name of the board. eg, standup etc"},
                    },
                    "required": ["board_name"]
                }
            }
        }, {
            "type": "function",
            "function": {
                "name": "create_lists_on_board",
                "description": "create lists on the board.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lists_details": {"type": "array", "items": {"type": "string"},
                                          "description": "Array of names for the new lists to be created on the board"}
                    },
                    "required": ["lists_details"]
                }
            }
        }, {
            "type": "function",
            "function": {
                "name": "create_card_for_list",
                "description": "create cards for a list on the board.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "list_name": {"type": "string", "description": "name of the list in the board"},
                        "cards_details": {
                            "type": "array",
                            "items": card_info_schema,
                            "description": "Array of card information to be created on the list"
                        }
                        # "cards_details": list[CardInfo.schema()]
                        # {"type": "array", "items": {"type": "string"},
                        #               "description": "Array of card names to be created on the list"}
                    },
                    "required": ["list_name", "cards_details"]
                }
            }
        }, {
            "type": "function",
            "function": {
                "name": "get_task_list",
                "description": "get all the tasks present in the list",
                # "parameters": {
                #     "type": "object",
                #     "properties": {
                #         "lists_details": {"type": "array", "items": {"type": "string"},
                #                           "description": "Array of names for the new lists to be created on the board"}
                #     },
                #     "required": ["lists_details"]
                # }
            }
        }]
)

assistant_id = assistant.id
thread = client.beta.threads.create()
keepAsking = True
print(assistant_id)
print("Welcome to daily manager")

while keepAsking:
    f_question = input("User: ")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f_question
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Start by asking about projects. If user asks to create board, ask boardname .Once board is created, create list from the status column from the file added. Then ask about the cards"
    )

    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    while run_status.status != 'completed':
        print(run_status.status)
        time.sleep(1)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run_status.status == 'requires_action':
            tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
            print(tool_calls)
            tool_outputs = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                print("Calling function {}".format(function_name))
                args = json.loads(tool_call.function.arguments)
                output = function_info.get(function_name)(**args)
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "output": output,
                    }
                )

            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        if run_status.status in ["failed", "expired", "cancelled"]:
            print("Unable to complte request. {}".format(run_status.status))
            break

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print(messages.data[0].content[0].text.value)
