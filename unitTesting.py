import dataEntryScript
from dotenv import load_dotenv
import os
from myLogger import myLogger
import EmailSheet
import openpyxl as opxl
import sendMsgs

load_dotenv()

sheetP = os.getenv("sheetpath")
sheetPOne = sheetP + "1234567890"+ ".xlsx"
testingLog = myLogger("Testing-Logger", 10, "Testing-Log")

#TESTING INIT NEW ACCOUNT AND HANDLE DATA
dataEntryScript.initNewAccount("1234567890", 17, 6969)
dataEntryScript.handleData("Mike's Crack | 25", "1234567890")
dataEntryScript.handleData("Taza | 50", "1234567890")
dataEntryScript.handleData("Chipotle | 25", "1234567890")
dataEntryScript.handleData("Baja Blasted Vodka| 60", "1234567890")
dataEntryScript.handleData("Fairlife IceCream | 4.59", "1234567890")
testingLog.logInfo(dataEntryScript.genOverview("1234567890"))
testingLog.logInfo(dataEntryScript.formatMsg("1234567890"))

#TESTING EMAILING
testingLog.logInfo(dataEntryScript.sendSheet("williamryan978@icloud.com", "1234567890"))
EmailSheet.sendMail("williamryan978@icloud.com", sheetPOne, "1234567890")

#TESTING SETUP SUM
dataEntryScript.setupSum("1234567890")
testingLog.logInfo(dataEntryScript.genOverview("1234567890"))
wb = opxl.load_workbook(sheetPOne, data_only=True)
ws = wb[wb.sheetnames[0]]
ws['G1'] = 5555
wb.save(sheetPOne)
wb.close()

testingLog.logInfo(dataEntryScript.genOverview("1234567890"))
dataEntryScript.setupSum("1234567890")
testingLog.logInfo(dataEntryScript.genOverview("1234567890"))

#TESTING HANDLE TURN, TURNOVER, CHANGEDATE, AND MAN OVERRIDE
dataEntryScript.turnOver()
dataEntryScript.changeDate("12", "1234567890")
dataEntryScript.manualOverride("1234567890")
testingLog.logInfo(dataEntryScript.genOverview("1234567890"))
testingLog.logInfo(dataEntryScript.formatMsg("1234567890"))
testingLog.logInfo(dataEntryScript.sendSheet("williamryan978@icloud.com", "1234567890"))
dataEntryScript.handleTurn(sheetPOne)

#TESTING SENDUSGNOTIF
#sendMsgs.sendUsgNotif("\n\n\tUnit Testing \n\n")