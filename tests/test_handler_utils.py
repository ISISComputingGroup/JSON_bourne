from hamcrest import *

from external_webpage.request_handler_utils import get_instrument_and_callback, \
    get_summary_details_of_all_instruments, get_detailed_state_of_specific_instrument
import json
import unittest


CALLBACK_STR = "?callback={}&"
INST_STR = "&Instrument={}&"

CALLBACK_AND_INST = CALLBACK_STR + INST_STR


class TestHandlerUtils_InstrumentandCallback(unittest.TestCase):

    def test_GIVEN_empty_path_WHEN_get_instrument_and_callback_called_THEN_raises_error(self):
        with self.assertRaises(ValueError):
            get_instrument_and_callback("")

    def test_GIVEN_path_with_callback_and_no_instrument_WHEN_get_instrument_and_callback_called_THEN_raises_error(self):
        with self.assertRaises(ValueError):
            get_instrument_and_callback(CALLBACK_STR.format("test"))

    def test_GIVEN_path_with_instrument_and_no_callback_WHEN_get_instrument_and_callback_called_THEN_raises_error(self):
        with self.assertRaises(ValueError):
            get_instrument_and_callback(INST_STR.format("test"))

    def test_GIVEN_path_with_callback_and_empty_instrument_WHEN_get_instrument_and_callback_called_THEN_raises_error(self):
        with self.assertRaises(ValueError):
            get_instrument_and_callback(CALLBACK_AND_INST.format("test", ""))

    def test_GIVEN_path_with_instrument_and_empty_callback_WHEN_get_instrument_and_callback_called_THEN_raises_error(self):
        with self.assertRaises(ValueError):
            get_instrument_and_callback(CALLBACK_AND_INST.format("", "test"))

    def test_GIVEN_path_with_multiple_callbacks_WHEN_get_instrument_and_callback_called_THEN_raises_error(self):
        with self.assertRaises(ValueError):
            get_instrument_and_callback(CALLBACK_STR.format("test") + CALLBACK_AND_INST.format("test", "test"))

    def test_GIVEN_path_with_multiple_instruments_WHEN_get_instrument_and_callback_called_THEN_raises_error(self):
        with self.assertRaises(ValueError):
            get_instrument_and_callback(CALLBACK_AND_INST.format("test", "test") + INST_STR.format("test"))

    def test_GIVEN_path_with_callback_WHEN_get_instrument_and_callback_called_THEN_expected_callback_returned(self):
        exp_callback = "callback"
        inst, callback = get_instrument_and_callback(CALLBACK_AND_INST.format(exp_callback, "test"))
        self.assertEqual(exp_callback, callback)

    def test_GIVEN_path_with_upper_instrument_WHEN_get_instrument_and_callback_called_THEN_expected_instrument_returned(self):
        exp_instrument = "INSTRUMENT"
        inst, callback = get_instrument_and_callback(CALLBACK_AND_INST.format("test", exp_instrument))
        self.assertEqual(exp_instrument, inst)

    def test_GIVEN_path_with_lower_instrument_WHEN_get_instrument_and_callback_called_THEN_upper_instrument_returned(self):
        exp_instrument = "instrument"
        inst, callback = get_instrument_and_callback(CALLBACK_AND_INST.format("test", exp_instrument))
        self.assertEqual(exp_instrument.upper(), inst)

    def test_GIVEN_path_with_instrument_containing_hyphen_WHEN_get_instrument_and_callback_called_THEN_upper_instrument_returned(self):
        exp_instrument = "EMMA-A"
        inst, callback = get_instrument_and_callback(CALLBACK_AND_INST.format("test", exp_instrument))
        self.assertEqual(exp_instrument, inst)


class TestHandlerUtils_IbexRunning(unittest.TestCase):

    def test_GIVEN_empty_dict_WHEN_get_ibex_running_called_THEN_empty_dict_json_returned(self):
        self.assertEqual(dict(), get_summary_details_of_all_instruments(dict()))

    def test_GIVEN_dict_with_key_containing_data_WHEN_get_ibex_running_called_THEN_running_instrument_true(self):
        inst = "TEST"
        inp = {inst: "some_data"}

        result = get_summary_details_of_all_instruments(inp)

        assert_that(result[inst], has_entry("is_up", True))

    def test_GIVEN_dict_with_key_containing_no_data_WHEN_get_ibex_running_called_THEN_running_instrument_false(self):
        inst = "TEST"
        inp = {inst: ""}

        result = get_summary_details_of_all_instruments(inp)

        assert_that(result[inst], has_entry("is_up", False))

    def test_GIVEN_dict_with_data_and_no_data_WHEN_get_ibex_running_called_THEN_running_and_not_running_instruments_returned(self):
        running_inst, not_running_inst = "RUN", "NOT"
        inp = {not_running_inst: "", running_inst: "some_data"}

        result = get_summary_details_of_all_instruments(inp)

        assert_that(result[running_inst], has_entry("is_up", True))
        assert_that(result[not_running_inst], has_entry("is_up", False))

    def test_GIVEN_dict_with_run_state_of_running_WHEN_get_summary_details_THEN_run_state_is_running(self):
        inst = "TEST"
        expected_state = "running"
        inp = {inst: {"inst_pvs": {"RUNSTATE": {"value": expected_state}}}}

        result = get_summary_details_of_all_instruments(inp)

        assert_that(result[inst], has_entry("run_state", expected_state))

    def test_GIVEN_dict_with_no_run_state_as_none_WHEN_get_summary_details_THEN_run_state_is_unknown(self):
        inst = "TEST"
        expected_state = "UNKNOWN"
        inp = {inst: {"inst_pvs": {"RUNSTATE": None}}}

        result = get_summary_details_of_all_instruments(inp)

        assert_that(result[inst], has_entry("run_state", expected_state))

    def test_GIVEN_dict_with_no_run_state_missing_value_key_WHEN_get_summary_details_THEN_run_state_is_unknown(self):
        inst = "TEST"
        expected_state = "UNKNOWN"
        inp = {inst: {"inst_pvs": {"RUNSTATE": {}}}}

        result = get_summary_details_of_all_instruments(inp)

        assert_that(result[inst], has_entry("run_state", expected_state))


    def test_GIVEN_dict_with_no_run_state_value_WHEN_get_summary_details_THEN_run_state_is_unknown(self):
        inst = "TEST"
        expected_state = "UNKNOWN"
        inp = {inst: {"inst_pvs": {}}}

        result = get_summary_details_of_all_instruments(inp)

        assert_that(result[inst], has_entry("run_state", expected_state))


class TestHandlerUtils_DetailedInstrumentState(unittest.TestCase):

    def test_GIVEN_instrument_not_in_data_WHEN_get_details_called_THEN_raises_error(self):
        inst = "TEST_INST"
        data = dict()
        with self.assertRaises(ValueError):
            get_detailed_state_of_specific_instrument(inst, data)

    def test_GIVEN_instrument_with_no_data_WHEN_get_details_called_THEN_raises_error(self):
        inst = "TEST_INST"
        data = {inst: ""}
        with self.assertRaises(ValueError):
            get_detailed_state_of_specific_instrument(inst, data)

    def test_GIVEN_instrument_with_data_WHEN_get_details_called_THEN_data_returned_for_that_instrument(self):
        inst = "TEST_INST"
        inst_data = ['test']
        data_dict = {inst: inst_data}

        out = get_detailed_state_of_specific_instrument(inst, data_dict)

        self.assertEqual(out, inst_data)
