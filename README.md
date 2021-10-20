# ptwqcpump
A PTW Quickcheck Pump for [QATrack+ QCPump](https://github.com/qatrackplus/qcpump). PTW QC Pump is able to parse Quickcheck measurement files (\*.qcw) and extract the measurement values. The measured values are uploaded via the QATrack+ API as one testlist per energy.

The main function is fetch_records() which returns a list of individual records. The individual records looks like this (Reported are the \<AnalyzeValues\> in percent):

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

To be able to upload the data to QATrack+ you have to create the individual tests as a simple numerical type. The test macro name has to be the same as seen in the record above (a.e. qc_cax_6e, qc_flatness_18x, and so on). After you added the indivitual tests you need one test list for every energy. The test list name (not the slug) needs to be "QC {energy}" (a.e. QC 20e, QX 6x - please mind the case). 

- Instructions for adding the Quick Check pump can be found here: [QCPump - Pump Type Development](http://qcpump.qatrackplus.com/en/stable/pumps/dev/developing.html)
- To be able to Upload via the QATrack+ API you need to [generate an API token](https://docs.qatrackplus.com/en/stable/api/guide.html#using-the-qatrack-api).

At the moment the code uses only the first part (up to the first whitespace) of the treatment unit name.
```python
'unit': td.find("Worklist/AdminData/AdminValues/TreatmentUnit").text.split(' ')[0],
```
That needs to be adjusted for your institution if the treatment unit name in your Quick Check device is the same as in QATrack+.

FFF is currently only partially supported (only 10x with compensator - the FFF information in the measurement file is not being evaluated). 
