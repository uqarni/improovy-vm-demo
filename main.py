import streamlit as st
from functions import ideator
import json
import os
import sys
from datetime import datetime
from supabase import create_client, Client

#connect to supabase database
urL: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(urL, key)
data, count = supabase.table("bots_dev").select("*").eq("id", "mike_voicemail").execute()
bot_info = data[1][0]

def main():

    # Create a title for the chat interface
    st.title("Improovy Bot")
    st.write("This is a testing website to play around with Mike’s conversational examples. The following script is going to be used for responding to customers who left a voicemail.")
    
    #variables for system prompt
    name = 'Mike'
    booking_link = 'https://calendly.com/d/y7c-t9v-tnj/15-minute-meeting-with-improovy-painting-expert'

    voicemail = st.text_input("Enter Voicemail transcript")
    
    #from booking
    resched_link='N/A'
    meeting_booked='No'
    meeting_time='N/A'

    system_prompt = bot_info['system_prompt']
    system_prompt = system_prompt.format(name = name, booking_link = booking_link, resched_link = resched_link, meeting_booked = meeting_booked, meeting_time = meeting_time, voicemail = voicemail)

    
    if st.button('Click to Start or Restart'):
        restart_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('database.jsonl', 'r') as db, open('archive.jsonl','a') as arch:
        # add reset 
            arch.write(json.dumps({"restart": restart_time}) + '\n')
        #copy each line from db to archive
            for line in db:
                arch.write(line)

        #clear database to only first line
        with open('database.jsonl', 'w') as f:
        # Override database with initial json files
            messages = [
                {"role": "system", "content": system_prompt}         
            ]
            f.write(json.dumps(messages[0])+'\n')




    #initialize messages list and print opening bot message
    #st.write("Hi! This is Tara. Seems like you need help coming up with an idea! Let's do this. First, what's your job?")

    # Create a text input for the user to enter their message and append it to messages
    userresponse = st.text_input("Enter your message")
    

    # Create a button to submit the user's message
    if st.button("Send"):
        #prep the json
        if len(userresponse) > 0:
            newline = {"role": "user", "content": userresponse}

            #append to database
            with open('database.jsonl', 'a') as f:
            # Write the new JSON object to the file
                f.write(json.dumps(newline) + '\n')

        #extract messages out to list
        messages = []

        with open('database.jsonl', 'r') as f:
            for line in f:
                json_obj = json.loads(line)
                messages.append(json_obj)

        #generate OpenAI response
        messages, count = ideator(messages)

        #append to database
        with open('database.jsonl', 'a') as f:
                for i in range(count):
                    f.write(json.dumps(messages[-count + i]) + '\n')



        # Display the response in the chat interface
        string = ""

        for message in messages[1:]:
            string = string + message["role"] + ": " + message["content"] + "\n\n"
        st.write(string)
            

if __name__ == '__main__':
    main()
