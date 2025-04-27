"""Main entry point for game."""

from __future__ import annotations

import argparse
import random
import inspect
from pathlib import Path
from typing import TYPE_CHECKING

import pyfiglet
import llm_chat_game
from llm_chat_game.context_var import DEBUG_MODE
from llm_chat_game.status_entity import StatusManager
from llm_chat_game.story import StoryWithOptionNarrator, StoryWithoutOptionNarrator
from llm_chat_game.story_db.random_events import situation_end_conditions, situations
from rich.console import Console
from rich.panel import Panel

console = Console()

if TYPE_CHECKING:
    from llm_chat_game.story import StoryNarrator


def load_story_narrators() -> list[StoryNarrator]:
    story_db_dir = Path(inspect.getfile(llm_chat_game)).parent / "story_db"
    narrators = []
    for story_file in story_db_dir.glob("event*.yaml"):
        narrator = StoryWithOptionNarrator(story_file)
        if narrator.is_start_event:
            narrators.append(narrator)
    return narrators


def load_sub_story_narrators() -> list[StoryNarrator] | None:
    try:
        return [
            StoryWithoutOptionNarrator(
                random_event,
                end_condition
            ) for random_event, end_condition in zip(situations, situation_end_conditions)
        ]
    except Exception as e:
        print(e)


def get_total_stories(
    story_narrators: list[StoryNarrator],
    sub_story_narrators: list[StoryNarrator],
) -> list[StoryNarrator]:
    arr = []
    while story_narrators and sub_story_narrators:
        if random.choice([True, False]):
            arr.append(story_narrators.pop())
        else:
            arr.append(sub_story_narrators.pop())

    arr.extend(story_narrators)
    arr.extend(sub_story_narrators)

    return arr


def play_game():
    story_narrators = load_story_narrators()
    sub_story_narrators = load_sub_story_narrators()

    user_status = StatusManager()

    console.print(Panel("2050년 서울에 화성이 떨어졌다.\n별같은 것이 아니다. 그것은 북한에서 발사한 핵이다.\n2020년대 이래로 너나할것없이 모든 나라들은 자국우선주의 전략을 펼치기 시작했다.\n이러한 기조가 진행될 수록 세계 곳곳에서 전쟁이 터지기 시작했고 종국에는 한반도에도 전운이 감돌기 시작하더니 북한에서 선제타격을 한 것이다.\n현재 서울은 황폐화 되었고 현재는 무정부상태와 다름없다.\n각 나라가 그러했듯 모든 사람들은 자신의 생존을 최우선하며 다른 사람들을 약탈하고 있다.\n다행인 점은 현재 국군이 북한군을 밀어내며 서울을 곧 탈환할 수 있다는 소식을 들은 것이다. 당신은 그 날을 기다리며 하루하루 생존을 위해 분투해야 한다.\n"))

    story_narrators_combined = get_total_stories(story_narrators, sub_story_narrators)
    random.shuffle(story_narrators_combined)
    day = 1
    while story_narrators_combined:
        ascii_art = pyfiglet.figlet_format(f"Day {day}...")
        print(ascii_art)
        story_narrator = story_narrators_combined.pop(0)
        next_story = story_narrator.play_story(user_status)

        if user_status.is_die():
            print(f"당신은 {day}일차에 죽었습니다.\nGame over.")
            break

        if next_story is not None:
            idx_to_insert = random.randint(0, len(story_narrators_combined)-1) if story_narrators_combined else 0
            story_narrators_combined.insert(idx_to_insert, next_story)
        day += 1
    else:
        print("국군이 서울을 탈환했습니다.\n많은 역경이 있었지만 당신은 당신의 능력을 증명하고 생존했습니다.\nGame end.")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action="store_true")
    return parser.parse_args()


def main() -> None:
    args = get_args()
    DEBUG_MODE.set(args.debug)

    play_game()


if __name__ == "__main__":
    main()
