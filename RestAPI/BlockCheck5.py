# Python 
""" read the CAST statistics, net out the violations, and then generate a return code."""
#*****************************************************************************************
# Rather simple - uses the batch file to extract the RESTAPI
# then evaluate the results 
# only one rule now (1) but more possible
#*****************************************************************************************

__author__ = "Bill Dickenson"
__copyright__ = "Copyright 2017, CAST Software"
__credits__ = ["Nevin Kaplan", "Yun Liu"]
__license__ = "GPL"
__version__ = "1.0a"
__maintainer__ = "Bill Dickenson"
__email__ = "WDI"
__status__ = "Demonstrator"
__date__ = '2017-6-22'
__updated__ = '2017-6-22'


import os
import logging
import sys
import argparse
import requests

BUS_CRITERIA = {}




def setup_logging(APP_NAME, _console='info'):
    """ Initialization of the logging capability """
    # *******************************************************************
    # Step 2: create the log file
    # *******************************************************************
    _logname='blocker-' + APP_NAME
    
    try:
        with open(_logname, 'w'):
            pass
        #    logging.basicConfig(filename=logname, filemode='a',format='%(asctime)s,%(msecs)d %(name)s,
        #    %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.CST_Debug)

        logging.root.handlers = []
        if _console == "debug":
            logging.basicConfig(format='%(asctime)s, %(msecs)d %(name)s, %(levelname)s %(message)s', level=logging.DEBUG,
                                filename=_logname, filemode='a', datefmt='%H:%M:%S')
            # set up logging to console
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            # set a format which is simpler for console use
            formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
            console.setFormatter(formatter)
            logging.getLogger("").addHandler(console)
        else:
            logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s, %(levelname)s %(message)s', level=logging.INFO,
                                filename=_logname, filemode='a', datefmt='%H:%M:%S')
    except IOError:
        print("Logging failed to initialize")
        sys.exit(13)

def xml_add_vs_delete(_added, _removed, _reportname):
    """ Simple report showing what was wrong"""
    report = open(_reportname, 'w')
    report.write('<section name="Violation Summary" fontcolor="#ffffff">\n')
    report.write("<field name='Violations Added' titlecolor='black' value='"+str(_added) + "'></field>\n")
    report.write("<field name='Violations Removed' titlecolor='black' value='"+str(_removed) + "'></field>\n")
    report.write("</section>")
	
#    report.write('The criteria failed because the number of violations added in this snapshot')
#    report.write("\n")
#    report.write("exceeded or equaled the number removed. This is not an improvement in the quality ")
#    report.write("\n")
#    report.write("and should be avoided. There were "+str(_added) + " violations added, and "+str(_removed)+ " removed.")
#    report.write("\n")
#    report.write("It is recommended that the deploy process stop until some of the violations are rectified.")
    report.close()

def start_logging():
    """ Once logging is set up there is some information we want in the logs"""
    logging.info("Starting CAST Blocker Check - Logging is now engaged")
    logging.info("version " + str(__version__))
    return(0)

def check_rule(_rule, _app,  auth, apiurl):
    """ put the logic in here """
    headers = {'Accept':'application/json'}
  
#    apiurl = 'http://demo-us.castsoftware.com/AAD/rest/'
    logging.info('->' +str( headers) + ' ->' + str(apiurl))
    logging.info('Rule is :' + str(_rule))
    _reportname = 'results.xml'
    with open(_reportname, 'w'):
        pass

    logging.info(auth)
 
    if _rule == "new_vs_old":
        RESTCALL = 'AAD/results?select=(evolutionSummary)&quality-indicators=(60017)&snapshots=(-1)&applications=(' +_app + ')'
        logging.info(RESTCALL)        
        try:
            data = requests.get(apiurl+RESTCALL, headers = headers, auth=auth)
            BUS_CRITERIA = data.json()
        except:
            logging.error('Failed on RESTAPI')
#        logging.info(pp.pprint(BUS_CRITERIA))
        try:
            _results = (BUS_CRITERIA[0])
        except IndexError:
            logging.error("Likely invalid application name")
            return(100)             
        _data = _results.get('applicationResults')
        _results = _data[0].get('result')
        _added =    _results.get('evolutionSummary').get('addedCriticalViolations')
        _removed =  _results.get('evolutionSummary').get('removedCriticalViolations')
        logging.info(str(_added) + ' violations added, and  ' + str(_removed) + ' were removed')
        if _added <= _removed:
            logging.info(str(_added) + ' were added and ' + str(_removed) + ' were removed')
            xml_add_vs_delete(_added, _removed,_reportname)     
            return(0)
        else:
            logging.info('build failed')
            xml_add_vs_delete(_added, _removed,_reportname)     
            return(10)
    if _rule == "TQI_change":
        try:
            RESTCALL = "AAD/applications"
            data = requests.get(apiurl+RESTCALL, headers = headers, auth=auth)
            BUS_CRITERIA = data.json()

        except:
            logging.error('Failed on RESTAPI')  
        
#        logging.info(pp.pprint(BUS_CRITERIA))
        _results = (BUS_CRITERIA[0])
        _added =    _results.get('result').get('applicationResults').get('evolutionSummary').get('addedCriticalViolations')
        _removed =  _results.get('result').get('applicationResults').get('evolutionSummary').get('removedCriticalViolations')
        print(str(_added) + ' ' + str(_removed))
		
        if _added <= _removed:
            return(0)
        else:
            return(10)        
    else:
        logging.error("invalid rule - failing")
        return(10)              
            
        

if __name__ == "__main__":
    """ Access RESTAPI, then check results """
    apiurl = ''
    Curr_dir = os.getcwd()
    overridepath = Curr_dir
    parser = argparse.ArgumentParser(description="""\n\nCAST Blocking Rule Check - \n Reads RestAPI, Pulls scores, runs a test and returns 0 if all is ok, and 10 if not""")
    parser.add_argument('-a', '--aadname', action='store', dest='aad_name', default='Webgoat', required=False,
                        help='Name of the target application as shown in AAD')
    parser.add_argument('-u', '--userid', action='store', dest='userid', required=False, default='cast',
                        help='Userid with authorization to run')
    parser.add_argument('-p', '--password', action='store', dest='password', required=False, default='cast',
                        help='password matching uid') 
    parser.add_argument('-c', '--connection', action='store', dest='connection', required=False, default='http://localhost:8080/CAST-AAD-823/rest/',
                        help='connection string e.g. http://localhost:8090/CAST-AAD/rest/')    						
    parser.add_argument('-r', '--rule', action='store', dest='rule', required=False, default="new_vs_old",
                        choices=['new_vs_old', 'TQI_change'],
                        help='Pre-defined rule number that will be evaluated for success')
    parser.add_argument('-l', '--logging', action='store', dest='ext_log', default='debug',
                        choices=['debug', 'info'],
                        help='Show log on the console when set to debug')
    parser.add_argument('-v','--version', action='version', version='%(prog)s 1.0')
    results = parser.parse_args()
    APP_NAME = results.aad_name
    setup_logging(APP_NAME, results.ext_log)
    start_logging()
    auth = (results.userid, results.password)
    _rule = results.rule
    connection = results.connection
    _result_code = check_rule(_rule, APP_NAME, auth, connection)
    logging.info('exit code is ' + str(_result_code))
    sys.exit(_result_code)

