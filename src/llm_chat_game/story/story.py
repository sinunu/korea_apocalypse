"""Objects to progress story."""

from __future__ import annotations

import random
import re
from abc import ABC, abstractmethod
from pathlib import Path
from pprint import pprint
from typing import List, Literal

import yaml
from llm_chat_game.context_var import DEBUG_MODE
from llm_chat_game.gpt_agent import GptAgent
from llm_chat_game.status_entity import StatusManager
from llm_chat_game.story.story_entity import Story, StoryOption
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel


class StoryNarrator(ABC):
    """Class which progresses a story."""

    @abstractmethod
    def play_story(self, user_status: StatusManager) -> StoryWithOptionNarrator | None:
        pass
    

class SituationSuggestionResponse(BaseModel):
    situation: str
    selections: List[str]


class SituationResultResponse(BaseModel):
    result: str
    health: Literal[-2, -1, 0, 1, 2]
    mental: Literal[-2, -1, 0, 1, 2]
    money: Literal[-2, -1, 0, 1, 2]


class PhaseEndResponse(BaseModel):
    is_phase_over: bool


class StoryWithoutOptionNarrator(StoryNarrator):
    """ Class which progresses a story. There is no option to select. LLM automatically creates result of the story.
    This class is for story which does not belong to main story branch.
    Args:
        StoryNarrator (_type_): _description_

    Raises:
        RuntimeError: _description_
        RuntimeError: _description_

    Returns:
        _type_: _description_
    """


    def _introduction(cls):
        return """
## 개요 ##
당신은 TRPG 사회자입니다. 
현재 당신은 핵폭탄이 터져 폐허가 된 서울을 배경으로 생존을 위한 탐험을 하는 TRPG를 진행하고 있습니다. 
<게임배경>
2020년대 이래로 세계의 각 나라들은 자국우선주의 전략을 펼치기 시작하고 이러한 기조가 이어지며 세계 곳곳에서는 전쟁이 터지기 시작합니다. 이러한 기조에서 북한도 남한에게 화성이라는 이름의 핵을 서울에 떨어트렸고 서울은 황폐화 됐고 무정부 상태와 다름없어 졌고 사람들은 서로를 약탈하고 있습니다. 다행히 현재 국군이 북한군을 밀어내며 서울을 탈환하기 위해 노력하고 있습니다. 주인공은 국군이 서울을 탈환할 때까지 생존하는 것을 목표로 서울을 돌아다니고 있습니다.
</게임배경>

주인공은 폐허가 된 서울을 돌아다니며 다양한 상황들을 만나고 그때마다 특정한 행동을 수행합니다.
지금부터, 당신은 주어진 ##상황## 을 자세히 설명하고 선택지 3개를 제공합니다.
그러나, 플레이어는 주어진 선택지 대신 자신의 선택지를 제시할 수도 있습니다.

상황과 선택지는 json 형식으로 제공해주세요.
아래의 양식을 따라주세요.
{
    "situation": "상황 설명",
    "selections": ["선택지1", "선택지2", "선택지3"]
}

## 예시 ##
{
    "situation": "지나가던 길에 작지만 깊어보이는 구멍을 발견했습니다. 구멍을 들여다보니 무언가 반짝이는 물체가 보입니다. 어떻게 할까요?"
    "selections": ["구멍을 더 자세히 들여다본다.", "구멍에 돌을 던져서 얼마나 깊은지 확인한다.", "구멍을 무시하고 지나간다."]
}
"""
    def _restriction(cls):
        return """
## 제약 ##
플레이어는 현실 세계에 살고 있으며, 따라서 초현실적인 행동은 불가능합니다.
또한 플레이어가 가지고 있는 능력 외에 다른 방법으로 문제를 해결할 수 없습니다.
사용자가 지나치게 현실을 벗어난 행동을 한다면, 실제로 그 행동을 할 수 없다는 이유로 실패합니다.
멸망한 현대 사회에서, 도시의 인프라는 무너져 있으며, 전기, 수도, 인터넷 등의 시설은 작동하지 않습니다.
"""
    def _start(cls):
        return """
## 결과 ##
위의 상황과 선택지, 그리고 플레이어의 선택에 대한 결과를 제공해주세요.
결과는 긍정적이거나 부정적이거나 중립적이어도 상관없습니다.

"""
    def _twist(cls):
        return """
## 결과 ##
위의 상황과 선택지, 그리고 플레이어의 선택에 대한 결과를 제공해주세요.
결과는 플레이어가 입력한 의도와는 다른 반전된 결과를 제공해주세요.
"""
    def _result(cls):
        return """
## 결과 ##
위의 상황과 선택지, 그리고 플레이어의 선택에 대한 결과를 제공해주세요.
결과는 긍정적이거나 부정적이거나 중립적이어도 상관없습니다.
결과에 대한 이야기, 그리고 결과에 따른 체력, 정신력, 돈의 변화를 알려주세요.
"""
    def _end_result_instructions(cls):
        return """
이야기가 너무 길어졌습니다.
이번 대답에서 이야기를 자연스럽게 마무리 지어주세요.
"""
    def _phase_end_instructions(cls):
        return """
주어진 ##상황## 에 대한 이야기가 끝났는지 확인해주세요.
이야기가 종료되었다면, 'True'를 입력해주세요.
이야기가 계속되어야 한다면, 'False'를 입력해주세요.
그 외의 입력은 절대로 하지 마세요.
"""
    
    def __init__(self, situation: str, end_condition: str):
        self._gpt_agent = GptAgent()
        self._situation = situation
        self._end_condition = end_condition
        self.console = Console()

    def play_story(self, user_status: StatusManager) -> StoryWithOptionNarrator | None:
        """Play the story. If user dies during story, return False. If not, return True."""
        prompt = self._introduction()  + self._restriction() + self._situation + self._start()
        is_phase_over = False
        messages = []
        messages.append({"role": "system", "content": prompt})
        phase_count = 0
        while not is_phase_over:
            res: SituationSuggestionResponse = self._gpt_agent.talk(messages, response_format=SituationSuggestionResponse)
            self.console.print(Panel(res.situation), style="bold")
            self.console.print("1 : " + res.selections[0], style="underline")
            self.console.print("2 : " + res.selections[1], style="underline")
            self.console.print("3 : " + res.selections[2], style="underline")
            print("\n")
            user_input = input("당신의 행동을 입력해주세요. ")
            
            
            if user_input.strip() in ['A','a','1']:
                user_ans = res.selections[0]
            elif user_input.strip() in ['B','b','2']:
                user_ans = res.selections[1]
            elif user_input.strip() in ['C','c','3']:
                user_ans = res.selections[2]
            else:
                user_ans = user_input
            self.console.print(user_ans, style="italic", end="\n\n")

            result_prompt = self._result() if random.randint(1, 10) <= 7 else self._twist()
            if phase_count > 2:
                result_prompt += self._end_result_instructions()
            messages.append({"role": "user", "content": user_ans})
            messages.append({"role": "system", "content": result_prompt + self._restriction()})

            res: SituationResultResponse = self._gpt_agent.talk(messages, response_format=SituationResultResponse)
            for status_name in ("health", "mental", "money"):
                if (status_change := getattr(res, status_name)) != 0:
                    print(f"{status_name} : {status_change:+}")
                    user_status.add_status(status_name, status_change)

            self.console.print(Panel(res.result))
            self.console.print(user_status, style="italic")
            
            if user_status.is_die():
                return

            messages.append({"role": "assistant", "content": res.result})
            messages.append({"role":"system", "content": self._phase_end_instructions() + self._end_condition})
            res: PhaseEndResponse = self._gpt_agent.talk(messages, response_format=PhaseEndResponse)
            is_phase_over = res.is_phase_over


class StoryWithOptionNarrator(StoryNarrator):
    """Class which progresses a story. Options are given for each situation and llm selects one of them.

    Args:
        story_file (Path): Story file path.
        user_status (StatusManager): User's status.

    Raises:
        RuntimeError: If there is no start point, error is raised.
    """

    def __init__(self, story_file: Path, start_id: str | None = None) -> None:
        self._story = self._load_story_file(story_file)
        self._gpt_agent = GptAgent(self._story)
        self.console = Console()
        self._start_id = start_id
        if isinstance(self._start_id, str) and self._start_id.isdigit():  # TODO[@eunwoo] need to refine later
            self._start_id = int(self._start_id)

        if self._start_id is None:
            for id, story in self._story.items():
                if story.start_point:
                    self._start_id = id
                    break

    @property
    def is_start_event(self) -> bool:
        return self._start_id is not None 

    @staticmethod
    def _load_story_file(story_file : Path) -> dict[int, Story]:
        if not story_file.exists():
            msg = f"{story_file} doesn't exist."
            raise RuntimeError(msg)

        with story_file.open("r", encoding="utf-8") as f:
            game_stories = yaml.safe_load(f)

        return {story_args["id"] : Story(**story_args) for story_args in game_stories}

    def play_story(self, user_status: StatusManager) -> StoryWithOptionNarrator | None:
        """Play the story. If there is next_story, return it. If not, return None."""
        cur_story_id = self._start_id
        accumulated_story: str = ""
        next_description: str = ""

        while True:
            cur_story = self._story[cur_story_id]
            if next_description:
                self.console.print(Panel(next_description), style="bold")
                next_description = ""
            else:
                self.console.print(Panel(cur_story.description), style="bold")

            self._update_status(user_status, cur_story)
            if user_status.is_die():
                return
                
            if not accumulated_story:
                accumulated_story = cur_story.description
            else:
                accumulated_story = accumulated_story + " " + cur_story.description

            if cur_story.goto is not None:
                cur_story_id = cur_story.goto
                continue

            if not cur_story.options:
                break

            visible_options: list[StoryOption] = [option for option in cur_story.options if option.visible]
            for i, visible_option in enumerate(visible_options, start=1):
                self.console.print(f"{i} : {visible_option.description}", style="underline")
            print("\n")
            user_input = self._get_user_input(len(visible_options))

            if isinstance(user_input, int):
                selected_option = visible_options[user_input - 1]
                self.console.print(selected_option.description, end="\n\n", style="italic")
                if selected_option.next_description:
                    next_description = selected_option.next_description
            else:  # use llm selection
                response = self._gpt_agent.make_story(user_input, accumulated_story, cur_story.options)
                selected_option = cur_story.options[response.option - 1]
                self.console.print(user_input, end="\n\n", style="italic")
                if DEBUG_MODE.get():
                    pprint(f"selected_option : {response.option}\n")
                    # pprint(f"reason : {response.reason}\n")
                next_description = str(response.story)
            cur_story_id = selected_option.goto

        return None if cur_story.next_event is None else self._get_next_event_narrator(cur_story.next_event)

    def _update_status(self, user_status: StatusManager, cur_story: Story) -> None:
        for status_name, val in cur_story.affect_status.items():
            print(f"{status_name} : {val:+}")
            user_status.add_status(status_name, val)
        self.console.print(user_status, end="\n\n", style="italic")

    @staticmethod
    def _get_user_input(max_val: int) -> int | str:
        while True:
            user_input = input("어떻게 하시겠습니까? ")
            print()
            try:
                user_input = int(user_input)
                if user_input < 1 or max_val < user_input:
                    print(f"1과 {max_val} 사이의 수를 선택하거나 당신만의 선택을 텍스트로 전달해주세요.")
                else:
                    break
            except ValueError: 
                break

        return user_input

    def _get_next_event_narrator(self, next_event: str) -> StoryWithOptionNarrator:
        if (ret := re.search(r"(.*\.yaml)\:(\d)", next_event)) is None:
            msg = f"{next_event} has wrong format. Format should be (file path):(start id)"
            raise ValueError(msg)
        file_path, start_id = ret.groups()
        return StoryWithOptionNarrator(Path("story_db") / file_path, start_id)
