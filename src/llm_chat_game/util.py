def print_with_border(content: str, border_char: str = '#'):
    lines = content.split('\n')  # 여러 줄로 나뉜 스트링도 처리
    max_length = max(len(line) for line in lines)  # 가장 긴 줄의 길이
    border_line = border_char * (max_length + 4)  # 테두리 위아래 선

    print(border_line)
    for line in lines:
        print(f"{border_char} {line.ljust(max_length)} {border_char}")  # 왼쪽 정렬
    print(border_line)