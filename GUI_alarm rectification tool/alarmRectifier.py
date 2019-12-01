import glob, os
import csv
import re
import tkinter as tk
import subprocess

alarmFile='files/AlarmBrowseResult.csv'
allAlarmFile='files/allAlarm.csv'
linkReportInsideDhk='files/Microwave Link Report Inside DHK.csv'
linkReportOutSideDhk='files/Microwave Link Report OutSide DHK.csv'

outputFileName="result/Result_alarm_rectification_tool.csv"

def openFile(path):
	path=os.path.realpath(path)
	subprocess.Popen(r'explorer /select,'+path)

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

	if board is None or site is None:
		return None
	else:
		site=site.upper()
		board=board.upper()

		with open(linkReportInsideDhk,'rU') as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			header=(csvfile.next()).lower()

			header=header.split(',')

			sourceNeCol=header.index('source ne name')
			sourceBoardCol=header.index('source board')
			sinkNeCol=header.index('sink ne name')
			sinkNeBoardCol=header.index('sink board')

			# print(sourceNeCol,sourceBoardCol,sinkNeCol,sinkNeBoardCol)
			for row in readCSV:
				if site in ( row[sourceNeCol].upper() ) and board in ( row[sourceBoardCol].upper() ):
					return row[sinkNeCol]

				elif site in ( row[sinkNeCol].upper() ) and board in ( row[sinkNeBoardCol].upper() ):
					return row[sourceNeCol]

		with open(linkReportOutSideDhk,'rU') as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			header=(csvfile.next()).lower()

			header=header.split(',')

			sourceNeCol=header.index('source ne name')
			sourceBoardCol=header.index('source board')
			sinkNeCol=header.index('sink ne name')
			sinkNeBoardCol=header.index('sink board')

			# print(sourceNeCol,sourceBoardCol,sinkNeCol,sinkNeBoardCol)
			for row in readCSV:
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

def mainFunc(button1,resultLocation,Lb):
	global targetAlarms,allData

	targetAlarms={}
	allData=[]

	try:

		Lb.insert(tk.END, "Working ... please wait .. ")
		Lb.yview(tk.END)

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
			alarmLocation=header.index('location information')

			for row in readCSV:
				try:

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
							dataObj.alarmType = 'BOTH'
							dataObj.alarmSource = getSiteCodeFromString( row[alarmSourceCol] )

							if 'ODU' in row[alarmLocation] or 'ISV3' in row[alarmLocation] or 'ISM6' in row[alarmLocation]:
								dataObj.alarmType += ' (LINK BASED)'
								dataObj.card = getBoardFromLocation( row[alarmLocation] )
								site2=getSiteFromCard( dataObj.alarmSource, dataObj.card )

								if dataObj.alarmSource is not None and dataObj.card is not None and site2 is not None:
									dataObj.impactedLink = dataObj.alarmSource+'-'+ getSiteCodeFromString( site2 )
									allData.append(dataObj)
							else:
								dataObj.alarmType += ' (NE BASED)'
								dataObj.alarmSource = getSiteCodeFromString( row[alarmSourceCol] )
								dataObj.impactedNE = dataObj.alarmSource
								dataObj.card = getBoardFromLocation( row[alarmLocation] )

								if dataObj.card is None:
									dataObj.card = row[alarmLocation]

								if dataObj.alarmSource is not None:
									allData.append(dataObj)

							# print(targetAlarms[alarmNameInRow])

				except Exception as e:
				    Lb.insert(tk.END, 'In '+row[alarmSourceCol]+' Error is : '+str(e))
				    Lb.yview(tk.END)


		j=0					
		with open(outputFileName, 'wb') as myfile:
			wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
			wr.writerow(["Alarm Name","Alarm Type","Alarm Source Node","Card/Board Location","Impacted Link","Impacted NE"])
			while j<len(allData):
				wr.writerow([allData[j].alarmName,allData[j].alarmType,allData[j].alarmSource,allData[j].card,allData[j].impactedLink,allData[j].impactedNE])
				j+=1

		Lb.insert(tk.END, 'Done !!! please click - Open Result Location')
		Lb.insert(tk.END, 'Total Links : '+str( len(allData) )+' . ')
		Lb.insert(tk.END, '	---------------------------- X ----------------------------- ')
		Lb.yview(tk.END)

		resultLocation["state"] = "normal"
		resultLocation.config( command=lambda: openFile(outputFileName) )

	except Exception as e:
	    Lb.insert(tk.END, 'Error!! '+str(e))
	    Lb.yview(tk.END)

	button1["state"] = "normal"