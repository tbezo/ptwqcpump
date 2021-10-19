# ptwqcpump
PTW Quickcheck Pump for QATrack+ QCPump. PTW QC Pump is able to parse Quickcheck measurement files (\*.qcw) and extract the measurement values. The measured values are uploaded via the QATrack+ API as one testlist per energy.

The main function is fetch_records() which returns a list of individual records. The individual records looks like this (Reported are the \<AnalyzeValues\> in percent).

```python
{'unit': 'Test_Linac',
 'energy': '6e', 
 'date': '2021-10-18 11:18:38', 
 'values': {
      'qc_cax_6e': {'value': 100.13},
      'qc_flatness_6e': {'value': 0.0},
      'qc_symmetrygt_6e': {'value': 99.904},
      'qc_symmetrylr_6e': {'value': 98.105},
      'qc_bqf_6e': {'value': 99.988},
      'qc_wedge_6e': {'value': 0.0}
      }
}
```
  
Instructions for adding the Quick Check pump can be found here: [QCPump - Pump Type Development](http://qcpump.qatrackplus.com/en/stable/pumps/dev/developing.html)
To be able to Upload via the QATrack+ API you need to [generate an API token](https://docs.qatrackplus.com/en/stable/api/guide.html#using-the-qatrack-api).

At the moment the code uses only the first part (up to the first space) of the treatment unit name.
```python
  'unit': td.find("Worklist/AdminData/AdminValues/TreatmentUnit").text.split(' ')[0],
```
That needs to be adjusted for your institution.
