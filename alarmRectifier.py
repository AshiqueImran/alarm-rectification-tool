import glob, os
import csv
import re
import math
import tkinter as tk
import subprocess

alarmFile='AlarmBrowseResult.csv'
allAlarmFile='allAlarm.csv'
linkReport='Microwave Link Report.csv'

outputFileName="Result_alarm_rectification_tool.csv"

sourceNeCol = None
sourceBoardCol = None
sinkNeCol = None
sinkNeBoardCol = None

targetAlarms={}
allData=[]

def getBoardFromLocation(location):
	if re.search("(\d{1,2}-[a-z,A-Z,0-9]{1,4})",location):
		return re.search("(\d{1,2}-[a-z,A-Z,0-9]{1,4})",location).group(1)

def getSiteCodeFromString(siteString):
	siteString=siteString.upper()
	# print(siteString)

	if re.search("([a-z,A-Z,_]+\d{2,4}_NE_\d)|([A-Z,a-z]+\d{2}_NE_\d)",siteString):
		return re.search("([a-z,A-Z,_]+\d{2,4}_NE_\d)|([A-Z,a-z]+\d{2}_NE_\d)",siteString).group(1)

	elif re.search("([A-Z,a-z]+\d{2}_NE_\d)",siteString):
		return re.search("([A-Z,a-z]+\d{2}_NE_\d)",siteString).group(1)
	elif re.search("([a-z,A-Z,_]+\d{2,4})",siteString):
		return re.search("([a-z,A-Z,_]+\d{2,4})",siteString).group(1)
	elif re.search("([a-z,A-Z,_]_NE_\d)",siteString):
		return re.search("([a-z,A-Z,_]_NE_\d)",siteString).group(1)

def getSiteFromCard(site,board):
	# print(site,board)

	global sourceNeCol,sourceBoardCol,sinkNeCol,sinkNeBoardCol

	if board is None or site is None:
		return None
	else:
		site=site.upper()
		board=board.upper()

		with open(linkReport,'rU') as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')

			for row in readCSV:

				if sourceNeCol == None or sourceBoardCol == None or sinkNeCol == None or sinkNeBoardCol == None:
					
					for index, x in enumerate(row):

						x = x.lower()
						if 'source' in x and 'ne' in x and 'name' in x :
							sourceNeCol= index # 'source ne name'
						elif 'source' in x and 'board' in x:
							sourceBoardCol= index # 'source board'
						elif 'sink' in x and 'ne' in x and 'name' in x :
							sinkNeCol= index # 'sink ne name'
						elif 'sink' in x and 'board' in x:
							sinkNeBoardCol= index # 'sink board'
				elif len(row) >= 9 and row[0] != '' and row[0] != ' ':

					if site in ( row[sourceNeCol].upper() ) and board in ( row[sourceBoardCol].upper() ):
						return row[sinkNeCol]

					elif site in ( row[sinkNeCol].upper() ) and board in ( row[sinkNeBoardCol].upper() ):
						return row[sourceNeCol]



# print(getBoardFromLocation('7-CSHO-OTHER-Protect Group ID:1'))

class data:
	alarmName=''
	alarmType=''
	alarmSource=''
	card=''
	impactedLink=''
	impactedNE=''

with open(allAlarmFile,'rU') as csvfile:
	readCSV = csv.reader(csvfile, delimiter=',')
	csvfile.next()

	for row in readCSV:
		targetAlarms[ ( row[0].upper() ) ]=(row[1].upper())

with open(alarmFile,'rU') as csvfile:
	readCSV = csv.reader(csvfile, delimiter=',')
	header=(csvfile.next()).lower()

	header=header.split(',')

	alarmNameCol=header.index('name')
	alarmSourceCol=header.index('alarm source')

	if 'location information' in header:
		alarmLocation=header.index('location information')
	elif 'location info' in header:
		alarmLocation=header.index('location info')


	for row in readCSV:

		alarmNameInRow=row[alarmNameCol].upper()

		if alarmNameInRow in targetAlarms:

			if 'LINK BASED' in targetAlarms[alarmNameInRow]:

				dataObj = data()
				dataObj.alarmName = alarmNameInRow
				dataObj.alarmType = 'LINK BASED'
				dataObj.alarmSource = getSiteCodeFromString( row[alarmSourceCol] )
				dataObj.card = getBoardFromLocation( row[alarmLocation] )
				# print(dataObj.alarmSource, row[alarmLocation])

				if dataObj.card is None:
					dataObj.card = row[alarmLocation]

				site2=getSiteCodeFromString( row[alarmLocation] )
				if dataObj.alarmSource is not None and site2 is not None:
					dataObj.impactedLink = dataObj.alarmSource+'-'+site2

					allData.append(dataObj)

			elif 'NE BASED' in targetAlarms[alarmNameInRow]:
				dataObj = data()
				dataObj.alarmName = alarmNameInRow
				dataObj.alarmType = 'NE BASED'
				dataObj.alarmSource = getSiteCodeFromString( row[alarmSourceCol] )
				dataObj.impactedNE = dataObj.alarmSource
				dataObj.card = getBoardFromLocation( row[alarmLocation] )

				if dataObj.card is None:
					dataObj.card = row[alarmLocation]

				if dataObj.alarmSource is not None:
					allData.append(dataObj)

			elif 'BOTH' in targetAlarms[alarmNameInRow]:
				# print(alarmNameInRow,row[alarmSourceCol],row[alarmLocation])
				# print( getSiteCodeFromString( row[alarmSourceCol] ) )
				# print( getBoardFromLocation( row[alarmLocation] ) )

				dataObj = data()
				dataObj.alarmName = alarmNameInRow
				dataObj.alarmSource = getSiteCodeFromString( row[alarmSourceCol] )

				if 'ODU' in row[alarmLocation] or 'ISV3' in row[alarmLocation] or 'ISM6' in row[alarmLocation]:
					dataObj.alarmType = 'LINK BASED'
					dataObj.card = getBoardFromLocation( row[alarmLocation] )
					site2=getSiteFromCard( dataObj.alarmSource, dataObj.card )

					if dataObj.alarmSource is not None and dataObj.card is not None and site2 is not None:
						dataObj.impactedLink = dataObj.alarmSource+'-'+ getSiteCodeFromString( site2 )
						allData.append(dataObj)
				else:
					dataObj.alarmType = 'NE BASED'
					dataObj.alarmSource = getSiteCodeFromString( row[alarmSourceCol] )
					dataObj.impactedNE = dataObj.alarmSource
					dataObj.card = getBoardFromLocation( row[alarmLocation] )

					if dataObj.card is None:
						dataObj.card = row[alarmLocation]

					if dataObj.alarmSource is not None:
						allData.append(dataObj)

				# print(targetAlarms[alarmNameInRow])

j=0					
with open(outputFileName, 'wb') as myfile:
	wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
	wr.writerow(["Alarm Name","Alarm Type","Alarm Source Node","Card/Board Location","Impacted Link","Impacted NE"])
	while j<len(allData):
		wr.writerow([allData[j].alarmName,allData[j].alarmType,allData[j].alarmSource,allData[j].card,allData[j].impactedLink,allData[j].impactedNE])
		j+=1

# for dataInstance in allData:
# 	print(dataInstance.alarmName,dataInstance.alarmType,dataInstance.alarmSource,dataInstance.card,dataInstance.impactedLink,dataInstance.impactedNE)

allData=[]

with open(outputFileName,'rU') as csvfile:
	readCSV = csv.reader(csvfile, delimiter=',')
	csvfile.next()

	for row in readCSV:

		alarmName=row[0]
		alarmType=row[1]
		alarmSource=row[2]
		card=row[3]
		impactedLink=row[4]
		impactedNE=row[5]

		notFoundData=True

		if 'LINK BASED' in alarmType:
			for obj in allData:
				if alarmType in obj.alarmType and obj.alarmSource in alarmSource and obj.impactedLink in impactedLink:
					notFoundData=False
					if alarmName not in obj.alarmName:
						obj.alarmName=obj.alarmName+';'+alarmName
					if card not in obj.card:
						obj.card=obj.card+';'+card

		elif 'NE BASED' in alarmType:
			for obj in allData:
				if alarmType in obj.alarmType and obj.alarmSource in alarmSource and obj.impactedNE in impactedNE:
					notFoundData=False
					if alarmName not in obj.alarmName:
						obj.alarmName=obj.alarmName+';'+alarmName
					if card not in obj.card:
						obj.card=obj.card+';'+card

		if notFoundData:
			dataObj = data()

			dataObj.alarmName=alarmName
			dataObj.alarmType=alarmType
			dataObj.alarmSource=alarmSource
			dataObj.card=card
			dataObj.impactedLink=impactedLink
			dataObj.impactedNE=impactedNE

			allData.append(dataObj)

j=0					
with open(outputFileName, 'wb') as myfile:
	wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
	wr.writerow(["Alarm Name","Alarm Type","Alarm Source Node","Card/Board Location","Impacted Link","Impacted NE"])
	while j<len(allData):
		wr.writerow([allData[j].alarmName,allData[j].alarmType,allData[j].alarmSource,allData[j].card,allData[j].impactedLink,allData[j].impactedNE])
		j+=1

for dataInstance in allData:
	print(dataInstance.alarmName,dataInstance.alarmType,dataInstance.alarmSource,dataInstance.card,dataInstance.impactedLink,dataInstance.impactedNE)


# print(targetAlarms)