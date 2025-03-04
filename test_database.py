import json

# Assuming you're fetching this from your database
unicode_string = "\u0645\u0631\u0627\u0642\u0628\u062a \u0627\u0632 \u06a9\u0648\u062f\u06a9\u0627\u0646"

def decode_unicode_string(s):
    try:
        # Check if the string has Unicode escape sequences
        if isinstance(s, str) and '\\u' in s:
            return json.loads('"' + s + '"')
        return s
    except json.JSONDecodeError:
        return s

print(decode_unicode_string(unicode_string))