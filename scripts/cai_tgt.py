"""
This script is used to get the tgt of a character.
"""

import asyncio
import sys

from characterai.pyasynccai import PyAsyncCAI


async def main():
    """
    Main function
    """

    if len(sys.argv) != 3:
        print("Usage: python cai_tgt.py <token> <character_id>")
        sys.exit(1)

    client = PyAsyncCAI(sys.argv[1])
    json = await client.character.info(sys.argv[2])

    if "status" in json:
        raise RuntimeError(json["status"])

    print("tgt:", json["character"]["participant__user__username"])


if __name__ == "__main__":
    asyncio.run(main())
