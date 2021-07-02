#Scan the STM and get log file send to server
#Ver.1 : Basic task, check log file and printout only

import os, time, datetime
from datetime import date
from datetime import datetime
import requests

#Luu so serial cua may
sn = 'CF75081602'

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

#Luu thoi gian cua mau benh nhan cuoi cung
lastPatientMeasuresTime = ''

#init gia tri tam thoi
temp_patientmeasure =''
temp_qcmeasure =''
temp_productsloading = ''
temp_errorlog = ''
temp_cuvette =''

#init gia tri dem du 10 ph thi ping server 1 lan
timercount = 0

#Load Error Dictionary
errorDict = dict()
errordict = open("ErrorDictCM.txt",'r')
for line in errordict :
    error = line.rstrip().split(';')
    errorDict[error[0]] = error[1]

while True:
    today = date.today()
    today_string = today.strftime("%Y%m%d")
    today_string2 = today.strftime("%d/%m/%y")
    str_day = today.strftime("%d")
    str_month = today.strftime("%m")
    str_year = today.strftime("%Y")
    #print("Today: ", today_string)
    #print("Today: ", today_string2)
    #print("Day: ", str_day)
    #print("Month: ", str_month)
    #print("Year: ", str_year)
    trace_path = "C:\\STM\Trace\\" + str_year +"\\" + str_month
    #print("Trace Path: ", trace_path)
    trace_path_patientmeasures = trace_path + "\\" + today_string + "PatientMeasures.CSV"
    #print(trace_path_patientmeasures)
    trace_path_productsloading = trace_path + "\\" + today_string + "ProductsLoading.CSV"
    #print(trace_path_productsloading)
    trace_path_cuvettesloading = trace_path + "\\" + today_string + "CuvettesLoading.CSV"
    #print(trace_path_cuvettesloading)
    trace_path_cqmeasures = trace_path + "\\" + today_string + "CQMeasures.CSV"
    #print(trace_path_cqmeasures)
    trace_path_cqoperations = trace_path + "\\" + today_string + "CQOperations.CSV"
    #print(trace_path_cqoperations)
    error_path = "C:\\STM\\STB\\ETATERR.DAT"
    now = datetime.now()
    print('Now:', now)
    

    #Read CuvetteTracking.log de biet lot cuvette dang su dung
    CuvetteTracking = open('CuvetteTracking.log','r')
    for line in CuvetteTracking:
        currentCuvette = line.rstrip()

    #Read temp log de biet thoi gian doc cuoi cung
    try:
        lastread = open("log.temp","r")
        for line in lastread:
            try:
                if line.startswith("Patient=") :
                    last_patientmeasure = line.split("=")[1].replace('"','').split(';')[0]
                    #print("Last patient: " ,last_patientmeasure)
                    timelast_patientmeasure = datetime.strptime(last_patientmeasure[:19],'%d/%m/%Y %H:%M:%S')
                    #print("Halal",timelast_patientmeasure)
            except:
                 timelast_patientmeasure = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
            try:
                if line.startswith("QC=") :
                    last_qcmeasure = line.split("=")[1].replace('"','').split(';')[0]
                    #print("Last QC: " ,last_qcmeasure)
                    timelast_qcmeasure = datetime.strptime(last_qcmeasure[:19],'%d/%m/%Y %H:%M:%S')
            except:
                 timelast_qcmeasure = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
            try:
                if line.startswith("Product="):
                    last_productsloading = line.split('=')[1].replace('"','').split(';')[0]
                    #print("Last product: " ,last_productsloading)
                    timelast_productsloading = datetime.strptime(last_productsloading[:19],'%d/%m/%Y %H:%M:%S')
            except:
                    timelast_productsloading = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
            try:    
                if line.startswith("Errorlog="):
                    last_errorlog = line.split('=')[1].replace('"','')[0:17]
                    #print("Last error: " ,last_errorlog)
                    timelast_errorlog = datetime.strptime(last_errorlog,'%d/%m/%y %H:%M:%S')
            except:
                 timelast_errorlog = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
            try:    
                if line.startswith("Cuvette="):
                    last_cuvette = line.split('=')[1].replace('"','').split(';')[0]
                    timelast_cuvette = datetime.strptime(last_cuvette[:19],'%d/%m/%Y %H:%M:%S')
                    #print("Last cuvette: " ,last_cuvette)
            except:
                 timelast_cuvette = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
    except:
        timelast_patientmeasure = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
        timelast_qcmeasure = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
        timelast_productsloading = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')
        timelast_errorlog = datetime.strptime(today_string2 + " 00:00:00",'%d/%m/%y %H:%M:%S')

        
    # Read and process Patient Measures log
    try:
        patientmeasures = open(trace_path_patientmeasures,"r")
        print("Processing Patient Measure file:", today_string + "PatientMeasure.CSV")
        for line in patientmeasures:
            temp_patientmeasure = line
            testtime = line.split(";")[0].replace('"','')[:19]
            if testtime == "DateHeure" :
                continue
            testtime = datetime.strptime(testtime,'%d/%m/%Y %H:%M:%S')
            if testtime <= timelast_patientmeasure :
                continue
            #Test send patient result to server
            #print("Test time ", testtime)
            #print("last stored time ", timelast_patientmeasure) 
            url = 'http://datamedigroup.com/MG/addstago.php?sn='+sn+'&flag=result&data=' + line.rstrip() + '&cuvlot=' + currentCuvette
            #print(url)
            print("..foundPat..")
            #print("CurCuvLot: ",currentCuvette)
            x=requests.get(url)
        patientmeasures.close()    
    except:
        print("..errPat..")
    #print("-------------------")

    # Read and process QC Measures log
    try:
        qcmeasures = open(trace_path_cqmeasures, "r")
        print("Processing CQ Measures file:", today_string + "CQMeasures.CSV")
        for line in qcmeasures:
            #print(line)
            temp_qcmeasure = line
            if line.startswith('"DateHeure"') :
                continue
            temp_qcmeasure = line
            testtime = line.split(";")[0].replace('"','')[:19]
            testtime = datetime.strptime(testtime,'%d/%m/%Y %H:%M:%S')
            if testtime <= timelast_qcmeasure :
                continue
            #Get the qc range from CQOperations file
            qcline = line.replace('"','').split(';')
            testname = qcline[2]
            controlid = qcline[1]
            qcoperations = open(trace_path_cqoperations,'r')
            for sline in qcoperations:
                ssline = sline.replace('"','').split(';')
                if ssline[3] == testname and ssline[2] == controlid:
                    range = sline.split('[')[1].split(']')[0]
                    break
            #Test send patient result to server
            url = 'http://datamedigroup.com/MG/addstago.php?sn='+sn+'&flag=qc&data=' + line.rstrip() + '&cuvlot=' + currentCuvette + '&range=' + range
            #print(url)
            print("..foundQC..")
            #print("CurCuvLot: ",currentCuvette)
            x=requests.get(url)
        qcmeasures.close()
    except:
        print("..errQCM..")
    #print("-------------------")

    # Read and process Products Loading log
    try:
        productsloading = open(trace_path_productsloading, "r")
        print("Processing Products Loading file:", today_string + "PatientMeasure.CSV")
        for line in productsloading:
            temp_productsloading = line
            testtime = line.split(";")[0].replace('"','')[:19]
            if testtime == "DateHeure" :
                continue
            testtime = datetime.strptime(testtime,'%d/%m/%Y %H:%M:%S')
            if testtime <= timelast_productsloading :
                continue
            url = 'http://datamedigroup.com/MG/addstago.php?sn='+sn+'&flag=product&data=' + line
            x=requests.get(url)
            print("..foundPro..")
        productsloading.close()
        
    except:
        print("..errPro..")
    #print("-------------------")

    # Read and process Cuvettes Loading log
    try:
        cuvettesloading = open(trace_path_cuvettesloading,"r")
        print("Processing Cuvettes Loading file:", today_string + "CuvettesLoading.CSV")
        for line in cuvettesloading:
            temp_cuvette = line
            testtime = line.split(";")[0].replace('"','')[:19]
            if testtime == "DateHeure" :
                continue
            testtime = datetime.strptime(testtime,'%d/%m/%Y %H:%M:%S')
            if testtime <= timelast_cuvette :
                continue
            line = line.rstrip().replace('"','')
            newCuvetteLot = line.split(';')[1]
            print("New Cuvette Lot: ",newCuvetteLot)
            cuvettefile = open("CuvetteTracking.log","w")
            cuvettefile.write(newCuvetteLot)
            cuvettefile.close()
            url = 'http://datamedigroup.com/MG/addstago.php?sn='+sn+'&flag=cuvette&data=' + line
            x=requests.get(url)
            print("..foundCu..")
        cuvettesloading.close()
    except:
        print("..errCu..")
    #print("-------------------")

    # Read and process Error log
    try:
        errorlog = open(error_path,"r")
        print("Processing Error log file: ETATERR.DAT")
        for line in errorlog:
            temp_errorlog = line
            if line.split('"')[1] != today_string2:
                continue
            testtime = line.replace('"','')[0:17]
            testtime = datetime.strptime(testtime,'%d/%m/%y %H:%M:%S')
            if testtime <= timelast_errorlog :
                continue
            error = line.replace('"','')[18:]
            errorcode = error.split('  ')[0]
            errordetail = error.split('  ')[1]
            print("Found error: " , error) 
            if errorcode in errorDict:
                errordetail = errorDict[errorcode] + ' ' + errordetail
                errordetail = errordetail.replace('#','')
                #print(errordetail)
            
            url = 'http://datamedigroup.com/MG/adderror.php?sn='+sn+'&code='+errorcode+'&name='+errordetail+'&type=1'
            x= requests.post(url)
        errorlog.close()
    except:
        print("..errErr..")
    print("-------------------")

    #write temp data to log.temp
    #print(temp_patientmeasure)
    #print(temp_productsloading)
    #print(temp_errorlog)
    temp = open("log.temp","w")
    temp.write("Patient=" + temp_patientmeasure)
    temp.write("QC=" + temp_qcmeasure)
    temp.write("Product=" + temp_productsloading)
    temp.write("Errorlog=" + temp_errorlog)
    temp.write("Cuvette=" + temp_cuvette)
    temp.close()

    print("Connected STA COMPACT MAX ...")
    
    #ping to server
    if timercount == 10:
        timercount = 0
        try:
            url = 'http://datamedigroup.com/MG/onlinecheck.php?sn='+sn
            ping = requests.post(url)
        except:
            continue
    time.sleep(60)
    clearConsole()
    timercount = timercount+1
