# PROJECT_BT

This is a simple program designed to help make budgeting easier for people. It requires a little bit of setup and technical know how but it gets the job done for me.
Using Twilio, Flask, Flask_HTTPAuth, python-dotenv, openpyxl, and Schedule by dbader, users can keep track of their monthly budget simply by sending a text.

Flask and Flask_HTTPAuth serve the webserver Twilio's API hooks into for getting the texts, python-dotenv is how I bring my environment variables in from a separate file, openpyxl to maniuplate excel sheets, and Schedule assists with automated budget cycle turnover.

***This definitly isn't the most user friendly program but that was never truly the intentions. It's purpose was to help me learn how to utilize Flask and learn more about Twilio's api and features while building something that would serve a role in my life and solve a problem of my own.***


## 10/9/22:

I have rebranded this to Project BT. While this is less descriptive than sms budgeting pyscript, it is less of a mouthfull.
Project BT (AKA Project BUDGET TEXTER/BUDGET TRACKER) is a budget tracking app that works entirely over sms texts!
It does have *somewhat* strict formatting to work properly but it's actually fairly simple to use. It walks you through the setup process and is feature rich. This whole thing started so I could more easily track my personal expenses and practice good financial habits and it evolved into so much more than I could have imgained. I have a lot more in store for this project, and I am excited to share this with the world.

I have more features planned for this but I won't be able to implement them for a little while as my acadmeic year progresses. Heres a preview of features I wish to implement by year's end. Its not everything, but its the top two I have planned next.

-   Multiple budgets!
    -   Right now this is fairly basic, and only lets you track one budget per account.
    -   I plan to implement the ability to track more than one budget. It would make this program overall more usefull and practical. The simplicity of tracking one budget made building the base program efficient and quick.
-   Custom cycle turn over!!
    -   For the people who don't want to track a monthly budget!
    -   There are instances where you may want to track their budget on a weekly, bimonthly, or even biweekly!
    -   This will add for greater flexibility and make this more practical for more people.

-   BONUS PLANNED FEATURES:
    -   A setup script!
        -   Since the Twilio number I use for this program personally is kept private, a setup script to let people test this out with their own twilio number would let people get a feel for the program! Especially since I don't have a terms of use written up for the proper handling and storage of users data, I figured it would be best to provide a way for people to set this up themselves on their own server!

    -    Command to export the spreadsheet and provide a download link
    -    Automatic budget remaining reminder 1 week before user's billing cycle day
    -    Down the line I would like to build a website to act as a signup for the service. Due to twilio trial limitations it would be a dummy  signnup but it is one of my goals for this project down the line.


### DEVELOPER/PERSONAL UPDATES

    It's been a while.
    I've been gone for a while, working on some stuff. Balancing this with my academic work has been a challenge but I've managed to get a lot done.
    Development on this will slow down for my academic year, but I still have features I want to implement and just plans for this project.
    Project BT and Project CR(Spin off project inspired by my work on BT) are going to be the main focus of my dev work outside of my academics.
    I have a lot more work I want to do with this, and theres a lot of potential with the ideas swirling in my brain.
    I've also started referring to this as Project BT, just to simplify communication about this.
    I have yet to setup a backup system for this, I've been busy with academics and I value my acutal development of this project more than a backup system for this.

### DEVELOPMENT UPDATES 10/9/22:
-   Refactored and redesigned the entire data storage system. There is no longer a direct way to just read the filename and know who it belongs to.
    -   This took a lot of work and an entire format restructure. I've spent the better part of a month developing and testing this to ensure this refactor would be compatible and on feature parity with the inital version.
-   Theres now a detailed setup process with instructions on how to setup an account.
    -   This still has some room for improvement. Right now the formatting required for setup is super strict, and I haven't quite had the time to loosen the formatting requirements for this. Overall the formatting of the program is kinda strict, so I will need to take some time and implement some flexibility in user control.
-   Help command!
    -   Yeah I finally added a help command. By sending `-Help` it'll send you a list of commands you can run.
-   Jsonify!
    -   There is one use case. One. It takes a prexisting account and converts it to the new format. This took a lot of work for a command that will be used at most twice, and has been tested extensively.
    -   If the name of this doesn't make the refactor obvious, I redesigned the backend storage system to store things like the user budget cap, and billing cycle date, in a json file *serving* as my user database. It stores the user's ID number, the filename stored on the server, filename that'll be emailed when the user requests to email the sheet, the budget cap and the billing cycle date. This limits the amount of personal information stored on the server, with the only thing being tied to the user the email filename, but that is user generated so it can be whatever the user wants. For testing purposes mine was "protect-the-turtles".


# Updates (07/27/2022):
-   Mainly backend stuff. Added an event log to log when the automated tasks are run. Have more logging stuff to do but it can wait for now. Thats about it.


New Features(07/19/2022):
-   Automated billing cycle turnover, will automatically copy the template and make a new sheet for a new billing period.
    -   Even accounts for the edge case caused by the delayed development of this feature
-   Manual turnover, as a backup to manually turnover a new cycle, may require admin approval
    -   Requires adminstrator approval

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
        Init : Day : Budget

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


Manual Override:

    Format of text to send:
        Manual Override *insert admin code*

    Response:
        Success:
            Cycle Override Succesful

        Failure:
            Contact Administrator

JSONIFY:

    Format of text to send:
        JSON : user_choice_filename

    Response:
        Success:
            Summary of last purchase

        Failure:
            Incorrect format.
            Correct Format: JSON : user_filename
            NOTES: You can make the filename can be anything you want!

HELP:

    Authorized Number:

        HELP: Here is an summary of some of the commands you can do!
        Overview: Returns an overview of your monthly budget
        Change Date MM/DD/YY: Changes the date of your billing cycle by using the provided format
        Item | Price : Makes a purchase
        Email email@address.com : Sends a copy of your data as a spreadsheet to the email address you provide!

    Unauthorized Number:

            Want to signup? Text back Init followed by a filename, billing date (just the day), and your budget cap!
            The format should be Init : your filename : your billing day : your budget cap
            Billing day should just be the day. So if your billing cycle ends on the 21st of the month, just say 21
            Same thing or your budget cap! If your budget is 500 USD, just send 500! The currency doesn't matter!

