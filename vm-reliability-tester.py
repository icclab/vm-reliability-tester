# -*- coding: utf-8 -*-
"""
Created on Wed Mar 04 14:59:40 2015

@author: Konstantin
"""

import test_executor, test_setup, test_measurer, test_cleanup
import measurements_consolidator, data_processing
import model_fitter, model_validator

if __name__ == "__main__":
    test_cleanup.clean()
    test_setup.setup()
    for i in range(10):
        test_executor.run()
        test_measurer.data_collection()
        measurements_consolidator.set_data_point()
        test_cleanup.run()
    data_processing.add_diffs()
    model_fitter.fit_models()
    test_cleanup.clean()
    test_setup.setup()
    for i in range(10):
        test_executor.run()
        test_measurer.data_collection()
        measurements_consolidator.set_data_point()
        test_cleanup.run()
    data_processing.add_diffs()
    model_validator.fit_models()
    