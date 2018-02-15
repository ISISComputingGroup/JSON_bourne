from external_webpage.request_handler_utils import get_instrument_and_callback, \
    get_whether_ibex_is_running_on_all_instruments, get_detailed_state_of_specific_instrument
import json
import unittest


CALLBACK_STR = "?callback={}&"
INST_STR = "&Instrument={}&"

CALLBACK_AND_INST = CALLBACK_STR + INST_STR


class TestHandlerUtils(unittest.TestCase):

    #  Instrument and callback

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

    #  Ibex running

    def run_and_load_ibex_running(self, data):
        result = get_whether_ibex_is_running_on_all_instruments(data)
        return json.loads(result)

    def test_GIVEN_empty_dict_WHEN_get_ibex_running_called_THEN_empty_dict_json_returned(self):
        self.assertEqual(dict(), self.run_and_load_ibex_running(dict()))

    def test_GIVEN_dict_with_key_containing_data_WHEN_get_ibex_running_called_THEN_running_instrument_true(self):
        inst = "TEST"
        inp = {inst: "some_data"}
        self.assertEqual({inst: True}, self.run_and_load_ibex_running(inp))

    def test_GIVEN_dict_with_key_containing_no_data_WHEN_get_ibex_running_called_THEN_running_instrument_false(self):
        inst = "TEST"
        inp = {inst: ""}
        self.assertEqual({inst: False}, self.run_and_load_ibex_running(inp))

    def test_GIVEN_dict_with_data_and_no_data_WHEN_get_ibex_running_called_THEN_running_and_not_running_instruments_returned(self):
        running_inst, not_running_inst = "RUN", "NOT"
        inp = {not_running_inst: "", running_inst: "some_data"}
        self.assertEqual({not_running_inst: False, running_inst: True}, self.run_and_load_ibex_running(inp))

    #  Detailed instrument state

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

    def test_GIVEN_instrument_that_cannot_be_converted_to_json_WHEN_get_details_called_THEN_raises_error(self):
        inst = "TEST_INST"
        data = {inst: object}
        with self.assertRaises(ValueError):
            get_detailed_state_of_specific_instrument(inst, data)

    def test_GIVEN_instrument_with_data_WHEN_get_details_called_THEN_data_returned_as_json(self):
        inst = "TEST_INST"
        inst_data = ['test']
        data_dict = {inst: inst_data}
        out = get_detailed_state_of_specific_instrument(inst, data_dict)
        self.assertEqual(out, json.dumps(inst_data))
