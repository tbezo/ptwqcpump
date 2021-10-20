# -*- coding: utf-8 -*-
"""
ptw_quickcheck 0.1.0
Custom class for QCPump to upload PTW Quickcheck Data to QATrack+

"""
from pathlib import Path
import xml.etree.ElementTree as ET
import datetime

from qcpump.pumps.base import BasePump, STRING, DIRECTORY, UINT
from qcpump.pumps.common.qatrack import QATrackFetchAndPost #, slugify

class QuickcheckPump(QATrackFetchAndPost, BasePump):

    DISPLAY_NAME = "PTW Quickcheck"

    CONFIG = [
        {
            'name': 'PTW Quickcheck',
            'validation': 'validate_qc_file',
            'fields': [
                {
                    'name': 'directory',
                    'type': DIRECTORY,
                    'required': True,
                    'help': "Enter path for the *.qcw file",
                    'default': "",
                },
                {
                    'name': 'filename',
                    'type': STRING,
                    'required': True,
                    'help': "Enter the filename of the *.qcw file",
                    'default': "",
                },
                {
                    'name': 'Days of history',
                    'type': UINT,
                    'required': False,
                    'help': "enter the number of days to immport",
                    'default': 1,
                },
            ],
        },
        QATrackFetchAndPost.QATRACK_API_CONFIG,
    ]

    
    def validate_qc_file(self, values):
        filename = values['directory'] + "\\" + values['filename']
        self.log_info("QuickCheck filename: " + filename)
        
        if Path(filename).is_file():
            valid = True
            message = "file exists"
        else:
            valid = False
            message = "file does not exist!"
        
        return valid, message    
    
    def fetch_records(self):
        """
        Returns a list of records with the name of the treatment unit, energy, 
        date and the analyzed values from the xml file as a dict. One can
        choose how many days into the past the records are returned in the Pump
        setting Days of history.

        Returns
        -------
        records : LIST
            List oft dicts containing the individual records

        """
        # self.log_info('available units: ' + str(self.qatrack_unit_names_to_ids))
        directory = self.get_config_value('PTW Quickcheck', 'directory')
        filename = self.get_config_value('PTW Quickcheck', 'filename')
        
        qcwfile = directory + "\\" + filename

        # how many days including today should be imported (days of history)?
        # doh = 7
        doh = self.get_config_value('PTW Quickcheck', 'Days of history')
        dates = []
        for i in range(doh):
            dates.append((datetime.date.today() -
                          datetime.timedelta(days = i)).strftime('%Y-%m-%d'))   
        
        # for testing purpose 
        # searchdate = "2021-09-01"
        # dates.append(searchdate)
        
        # open/parse file with xml.etree.ElementTree and get the root
        # self.log_info('opening file ' + qcwfile)
        root = ET.parse(qcwfile).getroot()
        
        records = []
        for td in root.findall('./Content/TrendData'):
            if td.attrib['date'].split(' ')[0] in dates:
                # name used energy (photons or electrons)
                energy = td.find("Worklist/AdminData/AdminValues/Energy").text
                modality = td.find("Worklist/AdminData/AdminValues/Modality").text
            if modality == 'Photons':
                energy = energy + "x" # MV Photons
            if modality == 'Electrons':
                energy = energy + "e" # MeV Electrons
                
            # construct dict with analyzed values
            values = {}
            for mv in td.findall('MeasData/AnalyzeValues/'):
                values["qc_" + mv.tag.lower() + "_" + energy] = {'value': float(mv.findtext('Value'))}
                #self.log_info(values["qc_" + mv.tag.lower() + "_" + energy])
                
            record = {
                # comment out .split(' ')[0] in the line below to use the full treatment unit name
                'unit': td.find("Worklist/AdminData/AdminValues/TreatmentUnit").text.split(' ')[0],
                'energy': energy,
                'date': td.attrib['date'], # .split(' ')[0],
                'values': values
            }
            records.append(record)
            # self.log_info(record['unit'] + " " + record['date'])
        return records
    
    def test_list_for_record(self, record):
        """Accept a record to process and return a test list name."""
        return "QC " + record['energy'] #  + " " + record['unit']

    def qatrack_unit_for_record(self, record):
        """Accept a record to process and return a QATrack+ Unit name."""
        # self.log_info('unit for record: ' + record['unit'])
        return record['unit']

    def id_for_record(self, record):
        """
        Create an ID for the payload to prevent multiple uploads of the same 
        records.
        """
        rec_id = record['unit'] + "_" + record['date'] + "_" + record['energy']
        return rec_id

    def work_datetimes_for_record(self, record):
        """
        Returns work started and work completed times from a record. The date
        and time is taken from the Quick Check data (through fetch_records()) 
        and converted to a datetime object.
        """
        rdt = datetime.datetime.strptime(record['date'], '%Y-%m-%d %H:%M:%S')
        return rdt, rdt + datetime.timedelta(seconds=1)

    def test_values_from_record(self, record):
        """
        Returns the test values from a record for the API payload. Preparation
        and formatting is done in fetch_records().
        """
        return record['values']
    
    def pump(self):
        """Pump added to have a place to execute set_qatrack_unit_names_to_ids()"""
        self._unit_cache = {}
        #self._record_meta_cache = {}
        self.set_qatrack_unit_names_to_ids()
        return super().pump()
    
    def set_qatrack_unit_names_to_ids(self):
        """Fetch all available qatrack unit names.  We are overriding common.qatrack version
        of this because users are not selecting the unit names, instead we're getting
        directly from Quick Check measurement file"""
        self.qatrack_unit_names_to_ids = {}
        endpoint = self.construct_api_url("units/units")
        for unit in self.get_qatrack_choices(endpoint):
            self.qatrack_unit_names_to_ids[unit['name']] = unit['number']    