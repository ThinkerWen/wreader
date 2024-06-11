import asyncio
import json

from net.novel import search_novel


def main():
    with open("/Users/wxw/Work/Project/PyCharmProjects/wreader/source.json", "r", encoding="utf-8") as f:
        source = json.load(f)
        asyncio.run(search_novel("我有一身被动技", source))


if __name__ == '__main__':
    main()
