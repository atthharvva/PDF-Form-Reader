import pandas as pd

FIELDS = { 
        "Name": None, "Account number": None, "Last four digits of card": None, "Transaction date": None, 
        "Amount": None, "Merchant name": None, "Transaction was not authorized": None,  
        "My card was": None, "Date you lost your card": None, "Time you lost your card": None,
        "Date you realised card was stolen": None, "Time you realised card was stolen": None,
        "Do you know who made the transaction": None, "Have you given permission to anyone to use your card": None,
        "When was the last time you used your card": None, "Last transaction amount": None,
        "Where do you normally store your card": None, "Where do you normally store your PIN": None,
        "Other items that were stolen": None, "Have you filed police report": None, "Officer name": None,
        "Report number": None, "Suspect name": None, "Date": None, "Contact number": None, "Reason for dispute": None
    }



def find_field_values(text_by_page, FIELDS, field_mappings):
    for page_num, page_text in text_by_page.items():
        print(f"Processing Page {page_num}")
        
        for field, variations in field_mappings.items():
            if variations:  
                for variation in variations:
                    if variation.lower() in page_text.lower():
                        field_index = page_text.lower().find(variation.lower())
                        right_text = page_text[field_index + len(variation):].strip().split("\n")[0]
                        if right_text:
                            if FIELDS[field] is None:
                                FIELDS[field] = right_text.strip()
                                print(f"Found value for '{field}': {FIELDS[field]}")
    print(f"\nFinal Extracted FIELDS:\n{FIELDS}")
    post_process_dates_and_reasons(FIELDS)

def post_process_dates_and_reasons(FIELDS):
    if "Date you lost your card" in FIELDS and FIELDS["Date you lost your card"]:
        FIELDS["Date you lost your card"] = FIELDS["Date you lost your card"].split()[0]

    if "Time you lost your card" in FIELDS and FIELDS["Time you lost your card"]:
        FIELDS["Time you lost your card"] = FIELDS["Time you lost your card"].split()[1]

    if "Date you realised card was stolen" in FIELDS and FIELDS["Date you realised card was stolen"]:
        FIELDS["Date you realised card was stolen"] = FIELDS["Date you realised card was stolen"].split()[2]

    if "Time you realised card was stolen" in FIELDS and FIELDS["Time you realised card was stolen"]:
        FIELDS["Time you realised card was stolen"] = FIELDS["Time you realised card was stolen"].split()[3]

    if "Reason for dispute" in FIELDS and FIELDS["Reason for dispute"]:
        if FIELDS["Merchant name"] and FIELDS["Merchant name"].lower() in FIELDS["Reason for dispute"].lower():
            x = FIELDS["Merchant name"]
            index_after_x = FIELDS["Reason for dispute"].lower().find(x.lower()) + len(x)
            FIELDS["Reason for dispute"] = FIELDS["Reason for dispute"][index_after_x:].strip()

    if "When was the last time you used your card" in FIELDS and FIELDS["When was the last time you used your card"]:
        parts = FIELDS["When was the last time you used your card"].split()
        if len(parts) >= 3:
            FIELDS["When was the last time you used your card"] = ' '.join(parts[:3])
    pass

def save_to_excel(data, filename):
    data = {
        "Field Name": list(data.keys()), 
        "Extracted Value": list(data.values())
    }
    df = pd.DataFrame(data)
    df = df.T
    df.to_excel(filename, index=False, header=False)
    print(f"Data saved to {filename}")
