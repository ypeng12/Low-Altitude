#!/usr/bin/env python3
"""Check NRC tags for 'stellar'."""

from nrclex import NRCLex

nrc_dict = NRCLex().__lexicon__
tags = nrc_dict.get("stellar", [])
print(f"stellar in NRC tags: {tags}")
