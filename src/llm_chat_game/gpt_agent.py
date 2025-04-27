"""GPT agent repated objects."""

from __future__ import annotations

from pprint import pprint
from typing import Any, TYPE_CHECKING

import openai
from llm_chat_game.context_var import DEBUG_MODE
from pydantic import BaseModel

if TYPE_CHECKING:
    from llm_chat_game.story import Story, StoryOption

from os import environ

try:
    with open("../../openai_key.txt", "r") as f:
        API_KEY = f.readline()
except:
    API_KEY = environ.get("OPENAI_API_KEY")

_OPEN_AI_CLIENT = openai.OpenAI(api_key=API_KEY)


class TrpgHostResponse(BaseModel):
    option: int
    reason: str
    story: str


HostSetting = """당신은 TRPG 사회자입니다. 현재 당신은 핵폭탄이 터져 폐허가 된 서울을 배경으로 생존을 위한 탐험을 하는 TRPG를 진행하고 있습니다. 
현재 게임배경은 아래와 같습니다
<게임배경>
2020년대 이래로 세계의 각 나라들은 자국우선주의 전략을 펼치기 시작하고 이러한 기조가 이어지며 세계 곳곳에서는 전쟁이 터지기 시작합니다. 이러한 기조에서 북한도 남한에게 화성이라는 이름의 핵을 서울에 떨어트렸고 서울은 황폐화 됐고 무정부 상태와 다름없어 졌고 사람들은 서로를 약탈하고 있습니다. 다행히 현재 국군이 북한군을 밀어내며 서울을 탈환하기 위해 노력하고 있습니다. 주인공은 국군이 서울을 탈환할 때까지 생존하는 것을 목표로 서울을 돌아다니고 있습니다.
</게임배경>
주인공은 폐허가 된 서울을 돌아다니며 다양한 상황들을 만나고 그때마다 특정한 행동을 수행합니다. 당신은 상황에 대한 정보를 받고 해당 상황에 할 수 있는 선택지들와 각각의 선택지에 대한 설명과 결과가 주어집니다. 당신의 역할은 주인공이 어떠한 행동을 하면 주어진 선택지 중 하나를 골라 주인공의 행동과 선택지의 설명과 그리고 선택지의 결과를 자연스럽게 이어 이야기를 만드는 것입니다. 주인공의 행동이 상황에 맞지 않더라도 당신은 어떻게든 유저의 행동을 당신이 선택한 선택지와 자연스럽게 이어서 이야기를 만들어야 합니다.
주인공의 행동이 주어지면 아래 2단계의 방법을 수행하세요.
1. 주인공의 행동과 선택지의 설명이 가장 자연스럽게 이어질 단 한개의 선택지를 고르고 몇 번을 골랐는지 말합니다. 자연스럽게 이어질 선택지가 없더라도 주어진 선택지 중 항상 한가지를 결정해야 합니다.
2. 주인공의 행동으로 시작해서 선택지의 설명으로 이어진 다음 최종적으로 선택한 선택지의 결과로 이야기가 귀결되도록 정말 재미있고 흥미롭게 그리고 자세하게 이야기를 만듭니다. 이야기를 만들 때는 항상 아래에 모든 원칙을 지켜야 합니다.
<원칙>
1. 이야기는 항상 주인공의 행동으로 시작합니다. 설사 유저의 행동이 자연스럽지 않고 비이성적은 행동이라고 할지라도 이야기의 시작은 항상 주인공의 행동이어야 합니다. 어떠한 경우에도 주인공의 행동이 이야기에서 빠져선 안됩니다.
2. 주인공의 행동으로 시작 된 이야기는 항상 선택지의 설명으로 이어집니다. 어떠한 경우에도 선택지의 설명이 이야기에 빠져선 안됩니다.
3. 이야기의 마지막은 항상 당신이 선택한 선택지의 결과로 마무리 됩니다. 선택지의 결과 이후의 이유기를 만들면 안됩니다. 어떠한 경우에도 선택지의 결과가 이야기에 빠져선 안됩니다.
4. 주인공의 행동과 선택지의 설명, 그리고 설멱지의 결과가 자연스럽게 이어져야 합니다.
5. 이야기는 정말 재미있고 흥미로워야 하며 그리고 자세해야 서술되어야 합니다.
6. 이야기는 상황에 담겨있는 내용만 담겨있어야 합니다. 선택한 선택지의 설명과 결과를 제외한 다른 선택지의 내용이 담겨선 안됩니다.
6. 당신은 존댓말을 써야합니다.
</원칙>
"""


class GptAgent:
    API_KEY = API_KEY
    MODEL = "gpt-4o-mini"
    # MODEL = "gpt-4o"

    def __init__(self, story_db: dict[int, Story] | None = None):
        self._client = _OPEN_AI_CLIENT
        self._story_db = story_db

    def make_story(self, user_behavior: str, accumulated_story: str, options: list[StoryOption]) -> TrpgHostResponse:
        message = self._make_message(user_behavior, accumulated_story, options)
        if DEBUG_MODE.get():
            pprint(message)
        completion = self._client.beta.chat.completions.parse(
            model=self.MODEL,
            messages=message,
            response_format=TrpgHostResponse,
            temperature=0.3,  # 0.0 ~ 2.0
            # top_p=1.0, # 0.0 ~ 1.0  do not change both temperature and top_p
            # frequency_penalty=0, # -2.0 ~ 2.0
            # presence_penalty=0, # -2.0 ~ 2.0
        )
        return completion.choices[0].message.parsed

    def _make_message(self, user_behavior: str, accumulated_story: str, options: list[StoryOption]) -> list[dict[str, str]]:
        system_message = HostSetting + "\n" + "<상황>" + accumulated_story + "</상황>\n"

        system_message += "<선택지>\n"
        for i, option in enumerate(options, start=1):
            system_message += f"<{i}>\n"
            system_message += f"<설명>{option.description}</설명>\n"
            if option.goto is not None:
                system_message += f"<결과>{option.next_description or self._story_db[option.goto].description}</결과>\n"
            system_message += f"</{i}>\n"
        system_message += "</선택지>\n"

        return [
            {"role" : "system", "content" : system_message},
            {"role" : "user", "content" : f"<주인공의 행동>{user_behavior}</주인공의 행동>"},
        ]

    def talk(self, messages: list[dict[str, str]], **kwarg) -> Any:
        res = self._client.beta.chat.completions.parse(
            model=self.MODEL,
            messages=messages,
            **kwarg
        )
        return res.choices[0].message.parsed
