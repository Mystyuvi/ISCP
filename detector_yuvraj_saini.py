import csv
import json
import re
import sys

patterns = {
    "phone": re.compile(r"\b\d{10}\b"),
    "aadhar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "passport": re.compile(r"\b[A-PR-WY][1-9]\d{6}\b"),
    "upi": re.compile(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}")
}

def mask_value(key, value):
    if not value:
        return value
    if key == "phone" and re.match(patterns["phone"], value):
        return value[:2] + "XXXXXX" + value[-2:]
    elif key == "aadhar":
        digits = value.replace(" ", "")
        return digits[:2] + "XXXXXXXX" + digits[-2:]
    elif key == "passport":
        return value[0] + "XXXXXXX"
    elif key == "upi":
        parts = value.split("@")
        return parts[0][:2] + "XXXX@" + parts[1]
    elif key == "name":
        parts = value.split()
        return " ".join([p[0] + "XXX" for p in parts])
    elif key == "email":
        user, domain = value.split("@")
        return user[:2] + "XXX@" + "X" * (len(domain.split('.')[0])) + "." + ".".join(domain.split('.')[1:])
    elif key == "address":
        return "[REDACTED_ADDRESS]"
    elif key in ["ip_address", "device_id"]:
        return "[REDACTED_ID]"
    return value

def detect_and_redact(record):
    is_pii = False
    data = json.loads(record["Data_json"])
    combinatorial_flags = {
        "name": False, "email": False,
        "address": False, "ip_address": False, "device_id": False
    }
    for key, value in data.items():
        if not isinstance(value, str):
            continue
        for ptype, pattern in patterns.items():
            if pattern.search(value):
                is_pii = True
                data[key] = mask_value(key, value)
        if key in combinatorial_flags and value.strip():
            combinatorial_flags[key] = True
    if sum(combinatorial_flags.values()) >= 2:
        is_pii = True
        for key, flag in combinatorial_flags.items():
            if flag and key in data:
                data[key] = mask_value(key, data[key])
    return {
        "record_id": record["record_id"],
        "redacted_data_json": json.dumps(data),
        "is_pii": str(is_pii)
    }

def main(input_file):
    output_file = "redacted_output_yuvraj_saini.csv"
    with open(input_file, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        with open(output_file, "w", newline='', encoding="utf-8") as outfile:
            fieldnames = ["record_id", "redacted_data_json", "is_pii"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                result = detect_and_redact(row)
                writer.writerow(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    else:
        main(sys.argv[1])
