# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
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

    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.set_qatrack_unit_names_to_ids()
     
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
        #self.log_info('available units: ' + str(self.qatrack_unit_names_to_ids))
        directory = self.get_config_value('PTW Quickcheck', 'directory')
        filename = self.get_config_value('PTW Quickcheck', 'filename')
        
        qcwfile = directory + "\\" + filename
        
        self.log_info('opening file ' + qcwfile)
        root = ET.parse(qcwfile).getroot()

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
        
        records = []
        for td in root.findall('./Content/TrendData'):
            if td.attrib['date'].split(' ')[0] in dates:
                # name used energy (photons or electrons)
                energy = td.find("Worklist/AdminData/AdminValues/Energy").text
                modality = td.find("Worklist/AdminData/AdminValues/Modality").text
            if modality == 'Photons':
                energy = energy + "x" #"MV Photon"
            if modality == 'Electrons':
                energy = energy + "e" #"MeV Electrons"   
                
            #construct dict with analyzed values
            values = {}
            for mv in td.findall('MeasData/AnalyzeValues/'):
                values["qc_" + mv.tag.lower() + "_" + energy] = {'value': float(mv.findtext('Value'))}
                #self.log_info(values["qc_" + mv.tag.lower() + "_" + energy])
                
            #unit_long_name = "Test: " + td.find("Worklist/AdminData/AdminValues/TreatmentUnit").text.split(' ')[0]
            record = {
                'unit': td.find("Worklist/AdminData/AdminValues/TreatmentUnit").text.split(' ')[0],
                'energy': energy,
                'date': td.attrib['date'], # .split(' ')[0],
                'values': values
            }
            records.append(record)
            #self.log_info(record['unit'] + " " + record['date'])
        return records
    
    def test_list_for_record(self, record):
        """Accept a record to process and return a test list name."""
        return "QC " + record['energy'] #  + " " + record['unit']

    def qatrack_unit_for_record(self, record):
        """Accept a record to process and return a QATrack+ Unit name."""
        #self.log_info('unit for record: ' + record['unit'])
        return record['unit']

    def id_for_record(self, record):
        rec_id = record['unit'] + "_" + record['date'] + "_" + record['energy']
        return rec_id

    def work_datetimes_for_record(self, record):
        rdt = datetime.datetime.strptime(record['date'], '%Y-%m-%d %H:%M:%S')
        return rdt, rdt + datetime.timedelta(seconds=1)

    def test_values_from_record(self, record):
        return record['values']
    
    def pump(self):
        self._unit_cache = {}
        #self._record_meta_cache = {}
        self.set_qatrack_unit_names_to_ids()
        return super().pump()
    
    def set_qatrack_unit_names_to_ids(self):
        """Fetch all available qatrack unit names.  We are overriding common.qatrack version
        of this because users are not selecting the unit names, instead we're getting
        directly from directory name"""
        self.qatrack_unit_names_to_ids = {}

        endpoint = self.construct_api_url("units/units")
        for unit in self.get_qatrack_choices(endpoint):
            self.qatrack_unit_names_to_ids[unit['name']] = unit['number']    