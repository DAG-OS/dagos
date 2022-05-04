#!/bin/bash
# Downloads the gitmojis for offline development

curl https://raw.githubusercontent.com/carloscuesta/gitmoji/master/src/data/gitmojis.json \
    | jq '.gitmojis[] | "* ", .emoji, " ", .description,  "\n"' -r -j \
    > gitmojis.md
