import json

# Assuming you're fetching this from your database
unicode_string = "\u0627\u0645\u0648\u0631 \u0622\u0645\u0648\u0632\u0634\u06cc"

def decode_unicode_string(s):
    try:
        # Check if the string has Unicode escape sequences
        if isinstance(s, str) and '\\u' in s:
            return json.loads('"' + s + '"')
        return s
    except json.JSONDecodeError:
        return s

print(decode_unicode_string(unicode_string))