# sms-budgeting-pyscript
 
This is a simple program designed to help make budgeting easier for people. It requires a little bit of setup and technical know how but it gets the job done for me.
Using Twilio, Flask, Flask_HTTPAuth, python-dotenv, and openpyxl, users can keep track of their monthly budget simply by sending a text.

More to come.
Planned Features Updated (7/19/2022):
-    Command to export the spreadsheet and provide a download link
-    Automatic budget remaining reminder 1 week before user's billing cycle day
-    Down the line I would like to build a website to act as a signup for the service. Due to twilio trial limitations it would be a dummy  signnup but it is one of my goals for this project down the line.
-   Phone number hashing, so the filename can't be tied to a specific users phone number by the service

In development (7/19/2022):
-   Automated billing cycle turnover, will automatically copy the template and make a new sheet for a new billing period.
    -   Status: Working Prototype, needs more testing
-   Manual turnover, as a backup to manually turnover a new cycle, may require admin approval
    -   Status: Framework already in place, needs further implementation

New Features (7/14/2022):
- Email Command: Send a copy of the spreadsheet to an email address of your choosing!
    - Note: Current version gets filtered out by spam filters. I'll work on fixing this so the emails are not sent to spam or junk.
        - May be a little buggy, Management pushed the deadline up for this feature
- Refresh Sum: Refreshes the total amount of money  spent during this month.
    - Uses the "Refresh" command

Other Changes (7/14/2022):
- Refresh commannd:
    - The previous iteration of the refresh command has been changed.
    - It is now called Change Date and can be used to manually change the date of the budget period

New Features(7/9/2022)
- Setup form, let the user do an initial setup with their first text, allowing easier customization of billing cycle date and budget cap
- Refresh: Manually refresh and make a new sheet on a new day (limit one per day)

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

Init New Account:
    
    Format of text to send:
        Init : Day : Budge

    Will send a "wrong format text" if in correct format is used

Refresh:

    Format of text to send:
        Refresh

    Response:
        Total spent recalculated: call overview to get an updated value

Change Date:

    Format of text to send:
        Change Date MM/DD/YY

    Response:
        Succesful Date Change:
            Budget Date Changed to: MM/DD/YY
        Unsuccesfull Date Change (due to format of text):
            Incorrect Format: Use \"Change Date MM/DD/YY\" 

Email:

    Format of text to send:
        Email dummyemail@realemail.com
    
    Response:
        Succesful Email:
            Your sheet was sent to: dummyemail@realemail.com

        Unsuccesful Email (due to file missing):
            File not found, please generate a spreadsheet to email it to someone


This definitly isn't a user friendly program but that was never truly the intentions. It's purpose was to help me learn how to utilize Flask and learn more about Twilio's api and features