# sms-budgeting-pyscript
 
This is a simple program designed to help make budgeting easier for people. It requires a little bit of setup and technical know how but it gets the job done for me.
Using Twilio, Flask, Flask_HTTPAuth, python-dotenv, and openpyxl, users can keep track of their monthly budget simply by sending a text.

More to come.
Planned features (6/29/2022):
    Markup: *Command to export the spreadsheet and provide a download link
            *Automatic budget remaining reminder 1 week before user's billing cycle day
            *Setup form, let the user do an initial setup with their first text, allowing easier customization of billing cycle date and budget cap


Basic Purchase Text

    Format of the text to send:
        Item/Loc | Price

    Format of Response
        Item: ##
        Price: ##
        Total Spent(USD): ##
        Total Remaining(USD): ##

Overview Command:

    Format of the text to send:
        Overview

    Format of Response:
        Item | Price | Date Purchased (Repeats on new line for every item)

    After every item is listed:
        Total Spent(USD): ##
        Total Remaining(USD): ##

This definitly isn't a user friendly program but that was never truly the intentions. It's purpose was to help me learn how to utilize Flask and learn more about Twilio's api and features