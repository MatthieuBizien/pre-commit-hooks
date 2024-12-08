from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from difflib import unified_diff


def createShiftArr(step: int) -> list[str]:
    if isinstance(step, int):
        space = ' ' * step
    else:
        space = step
    shift = ['\n']
    for ix in range(100):
        shift.append(shift[ix] + space)
    return shift


def pretty_format_xml(text: str, step: int) -> str:
    # Closely mimic the replace chains from JS:
    text = re.sub(r'>\s{0,}<', '><', text)
    text = text.replace('<', '~::~<')
    text = re.sub(r'\s*xmlns\:', '~::~xmlns:', text)
    text = re.sub(r'\s*xmlns\=', '~::~xmlns=', text)

    ar = text.split('~::~')
    length = len(ar)
    inComment = False
    deep = 0
    result_str = ''
    ix = 0

    shift = createShiftArr(step)

    for ix in range(length):
        line = ar[ix]

        # start comment or <![CDATA[...]]> or <!DOCTYPE
        if re.search(r'<!', line):
            result_str += shift[deep] + line
            inComment = True
            if (
                re.search(r'-->', line) or
                re.search(r'\]>', line) or
                re.search(r'!DOCTYPE', line)
            ):
                inComment = False
        # end comment or <![CDATA[...]]>
        elif re.search(r'-->', line) or re.search(r'\]>', line):
            result_str += line
            inComment = False
        # <elm></elm>
        elif (
            ix > 0 and
            re.match(r'<\w', ar[ix - 1]) and
            re.match(r'</\w', line) and
            re.match(r'<[\w:\-\.\,]+', ar[ix - 1]) and
            re.match(r'</[\w:\-\.\,]+', line) and
            (m1 := re.match(r'<[\w:\-\.\,]+', ar[ix - 1])) and
            (m2 := re.match(r'</[\w:\-\.\,]+', line)) and
            m1.group(0) == m2.group(0).replace('/', '')
        ):
            result_str += line
            if not inComment:
                deep -= 1
        # <elm>
        elif (
            re.search(r'<\w', line) and not re.search(r'</', line) and
            not re.search(r'/>', line)
        ):
            if not inComment:
                result_str += shift[deep] + line
                deep += 1
            else:
                result_str += line
        # <elm>...</elm>
        elif re.search(r'<\w', line) and re.search(r'</', line):
            result_str += shift[deep] + line if not inComment else line
        # </elm>
        elif re.search(r'</', line):
            deep -= 1
            result_str += shift[deep] + line if not inComment else line
        # <elm/>
        elif re.search(r'/>', line):
            result_str += shift[deep] + line if not inComment else line
        # <? xml ... ?>
        elif re.search(r'<\?', line):
            result_str += shift[deep] + line
        # xmlns
        elif re.search(r'xmlns\:', line) or re.search(r'xmlns=', line):
            result_str += shift[deep] + line
        else:
            result_str += line

    return result_str[1:] if result_str.startswith('\n') else result_str


def _autofix(filename: str, new_contents: str) -> None:
    print(f'Fixing file {filename}')
    with open(filename, 'w', encoding='UTF-8') as f:
        f.write(new_contents)


def get_diff(source: str, target: str, file: str) -> str:
    source_lines = source.splitlines(True)
    target_lines = target.splitlines(True)
    diff = unified_diff(source_lines, target_lines, fromfile=file, tofile=file)
    return ''.join(diff)


def parse_num_to_int(s: str) -> int | str:
    try:
        return int(s)
    except ValueError:
        return s


def parse_topkeys(s: str) -> list[str]:
    # Not used for XML formatting, but we keep the parser
    return s.split(',')


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--autofix',
        action='store_true',
        dest='autofix',
        help='Automatically fixes encountered not-pretty-formatted files',
    )
    parser.add_argument(
        '--indent',
        type=parse_num_to_int,
        default='4',
        help=(
            'The number of indent spaces or a string to be used as delimiter'
            ' for indentation level e.g. 4 or "\\t" (Default: 2)'
        ),
    )
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    status = 0

    for xml_file in args.filenames:
        with open(xml_file, encoding='UTF-8') as f:
            contents = f.read()

        # For XML, no JSON logic is needed. Just try formatting.
        pretty_contents = pretty_format_xml(contents, step=args.indent)

        if contents != pretty_contents:
            if args.autofix:
                _autofix(xml_file, pretty_contents)
            else:
                diff_output = get_diff(contents, pretty_contents, xml_file)
                sys.stdout.buffer.write(diff_output.encode())

            status = 1

    return status


if __name__ == '__main__':
    raise SystemExit(main())
