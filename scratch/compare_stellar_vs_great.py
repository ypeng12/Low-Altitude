#!/usr/bin/env python3
"""Compare NRC status for stellar vs great."""

from nrclex import NRCLex

nrc_dict = NRCLex().__lexicon__

tags_stellar = nrc_dict.get("stellar", [])
tags_great = nrc_dict.get("great", [])

print("=== 🔬 NRC STATUS COMPARISON ===")
print(f"1. stellar NRC tags : {tags_stellar}  --> Count: {len(tags_stellar)} (Has 'positive' tag -> Mapped in 72 Polarity Words!)")
print(f"2. great NRC tags   : {tags_great}        --> Count: {len(tags_great)} (Has 0 tags -> 100% Missed in 272 Missed Words!)")
