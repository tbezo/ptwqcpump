# ptwqcpump
PTW Quickcheck Pump for QATrack+ QCPump. PTW QC Pump is able to parse Quickcheck measurement files (\*.qcw) and extract the measurement values.

The main function is fetch_records() which returns a list of individual records. The individual record looks like this.

{'unit': 'Test_Linac', 'energy': '6e', 'date': '2021-10-18 11:18:38', 'values': {'qc_cax_6e': {'value': '1.0013E+02'}, 'qc_flatness_6e': {'value': '0.0000E+00'}, 'qc_symmetrygt_6e': {'value': '9.9904E+01'}, 'qc_symmetrylr_6e': {'value': '9.8105E+01'}, 'qc_bqf_6e': {'value': '9.9988E+01'}, 'qc_wedge_6e': {'value': '0.0000E+00'}}}
