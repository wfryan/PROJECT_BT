from dotenv import load_dotenv

import os, openpyxl
from datetime import date
from openpyxl import Workbook
from openpyxl import load_workbook
load_dotenv()
#itemLoc = 'A'
priceLoc = 'B'
minRow = '2'

def handleTurn(sender):
    wb = 0
    sheetP = os.getenv("sheetpath")
    sheetP = sheetP + str(sender)[2:] + ".xlsx"
    if os.path.exists(sheetP):
        wb = load_workbook(sheetP, data_only=True)
    else:
        wb = Workbook()
    if "Template" not in wb.sheetnames:
        wsTemp = wb.create_sheet("Template")
        wsTemp['A1'] =  "Item / Location"
        wsTemp['B1'] = "Price"
        wsTemp['C1'] = "Date"
        wsTemp['D1'] = "Remaining"
        wsTemp['F1'] = "Money Spent"
    else:
        ws = wb["Template"]
        wb._add_sheet(wb, wb.copy_worksheet(ws), 0)
        ws = wb["Template Copy"]
        if str(date.today()) in wb.sheetnames:
            ws.title = "Test title" #debug tool
        else:
            ws.title = str(date.today())
        if "Template" in wb.sheetnames:
            wb.remove(wb["Test title"])
        wb.move_sheet(ws, )
    #ws = wb.active()
    wb.save(sheetP)
    print(wb.sheetnames)
    wb.close()


def setupSum(sender):
    wb = 0
    sheetP = os.getenv("sheetpath")
    sheetP = sheetP + str(sender)[2:] + ".xlsx"
    if os.path.exists(sheetP):
        wb = load_workbook(sheetP, data_only=True)
    else:
        wb = Workbook()
    ws = wb.active
    nums = []
    sum = 0.0
    for i in range(int(ws.max_row)):
        if ws['B' + str(i + 2)].value == None:
            break
        else:
            nums.append(float(ws['B' +  str(i + 2)].value))
    for x in range(len(nums)):
        sum= sum + float(nums[x])
    ws['G3'] = round(sum, 2)
    wb.save(sheetP)
    wb.close()
    

def handleData(text, sender):
    billDate = os.getenv("billDate")
    sheetP = os.getenv("sheetpath")
    sheetP = sheetP + str(sender)[2:] + ".xlsx"
    vals = text.split('|')
    wb = 0
    if os.path.exists(sheetP):
        if date.today().day == billDate:
            handleTurn(sender)
        wb = load_workbook(sheetP, data_only=True)

        #print(date.today().day)
    else:
        handleTurn(sender)
        wb = Workbook()
        
    ws = wb.active
    if ws['G3'].value == None:
        wb.save(sheetP)
        wb.close()
        setupSum(sender)
    wb =  load_workbook(sheetP, data_only=True)
    ws = wb.active
    if len(vals) > 1:
        price = vals[1][1:]
        itemLoc = 'A' + str(ws.max_row + 1)
        priceLoc= 'B' + str(ws.max_row + 1)
        dateLoc = 'C' + str(ws.max_row + 1)
        sum = float(ws['G3'].value)
        sum+= float(price)
        ws['G3'] = sum
        ws[itemLoc] = vals[0]
        ws[priceLoc] = float(price)
        ws[dateLoc] = str(date.today())
    wb.save(sheetP)
    wb.close()


def genOverview(sender):
    msg = ""
    sheetP = os.getenv("sheetpath")
    sheetP = sheetP + str(sender)[2:] + ".xlsx"
    wb = load_workbook(sheetP, data_only=True)
    ws = wb.active
    msg = " \n Item | Price | Date "
    for i in range(ws.max_row):
        msg+="\n"
        if ws['A'  + str(i + 1)].value is not None:
            msg+= str(ws['A'  + str(i + 1)].value) + " | "
        else:
            msg+= "Item Missing | "
        if ws['B'  + str(i + 1)].value is not None:
            msg+=  str(ws['B'  + str(i + 1)].value) + " | "
        else:
            msg+= "Price Missing | "
        if ws['C'  + str(i + 1)].value is  None:
            msg+= "Date Missing "
        else:
            msg+=  str(ws['C'  + str(i + 1)].value)
    totalSpent = float(ws['G3'].value)
    if totalSpent is None:
        totalSpent =  0
    totalRemaining = round(200 - totalSpent, 2)
    wb.save(sheetP)
    wb.close()
    msg+= "\nTotal Spent ($USD): " + str(round(totalSpent, 2))
    msg+= "\nTotal Remaining ($USD): " + str(totalRemaining)
    return msg

def formatMsg(sender):
    sheetP = os.getenv("sheetpath")
    sheetP = sheetP + str(sender)[2:] + ".xlsx"
    #print(sheetP)
    wb = 0
    if os.path.exists(sheetP):
        wb = load_workbook(sheetP, data_only=True)
    else:
        wb = Workbook()
    ws = wb.active
    mr = ws.max_row
    pLoc = 'B' + str(mr)
    iLoc = 'A' + str(mr)
    item = ws[iLoc].value
    cost = ws[pLoc].value
    if ws['G3'].value == None:
        ws['G3'] = 0.0
        setupSum(sender)
    totalSpent = float(ws['G3'].value)
    if totalSpent is None:
        totalSpent =  0
    totalRemaining = round(200 - totalSpent, 2)
    wb.save(sheetP)
    wb.close()

    if item is None or cost is None:
        msg =  "Empty Sheet"
    else:
        msg = "\nItem: " + str(item)
        msg+= "\nPrice ($USD): " + str(round(cost, 2))
        msg+= "\nTotal Spent ($USD): " + str(round(totalSpent, 2))
        msg+= "\nTotal Remaining ($USD): " + str(totalRemaining)
    return msg

