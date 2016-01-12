# # -*- coding: utf-8 -*-
from identifier import get_IDs_from_path
import params

import os
import re
import codecs

CONFIG = {}
# BASIC
CONFIG["EMAIL"] = "iwasawa@weblab.t.u-tokyo.ac.jp"
# VALIDATION RULES
CONFIG['ACCEPTABLE_DISCREPARENCY'] = 1
CONFIG['LIMIT_SAMPLE_LENGTH'] = 50
# FORMAT OF LINES
CONFIG["TIME_PATTERN"] = "\d{1,2}:[0-5]\d:[0-2]\d"
CONFIG["LINE_PATTERN"] = re.compile(
    "(?P<code>\D+),(?P<start>{}),(?P<stop>{}),(?P<comment>[^,]*)$".format(
        CONFIG["TIME_PATTERN"], CONFIG["TIME_PATTERN"])
)

# OTHER SORUCES
CONFIG["META_DIR"] = os.path.dirname(__file__) + "/meta-data"
CONFIG["LABEL_LIST_PATH"] = CONFIG["META_DIR"] + '/label_list.txt'


class Checker(object):
    def __init__(self, path):
        self.path = path
        prefix = path.split('/')[-1].split('.')[0].replace('_label', '')
        taskIDs = get_IDs_from_path(prefix.split('.')[0])  # before the .
        self.taskIDs = taskIDs
        self.test_lines = self._load_file(path)

        # Init the results variable
        self.results = Results(taskIDs)
        # Prepare label list
        self.label_list = open(CONFIG["LABEL_LIST_PATH"]).read().split('\n')

    def check(self):
        print("Start checking...")
        parsed_test_lines_with_fstatus = self.parse_lines(self.test_lines)

        # 1. Using only submitted file
        for i, p_line in enumerate(parsed_test_lines_with_fstatus):
            self._validate_eachline(i, p_line)

        # 2. Using prepared file
        self.compare_with_correct_data(parsed_test_lines_with_fstatus)
        print("Done")

    def parse_lines(self, lines):
        def parse_line(i, line, key='format_status'):
            match_obj = CONFIG["LINE_PATTERN"].search(line)
            if match_obj is None:
                return {key: params.ERROR, 'raw': line}
            line_dict = match_obj.groupdict()
            line_dict[key] = params.DONE
            line_dict['raw'] = line
            line_dict['start'] = convert_timeexpression(line_dict['start'])
            line_dict['stop'] = convert_timeexpression(line_dict['stop'])
            return line_dict
        return [parse_line(i, line) for i, line in enumerate(lines)]

    def compare_with_correct_data(self, p_data):
        """ Check two things

        1. Check if the time is correct or not
        2. Check if all label were included in submitted file
        """
        # 0. Init
        correct_data = self._load_correct_data()
        if correct_data is None:  # check if the correct data is exist
            return True
        p_correct_data = self.parse_lines(correct_data)
        # 1. Check if the time is correct or not
        for i, p_line in enumerate(p_data):
            self.validate_with_nearest_correct_line(i, p_line, p_correct_data)

        # 2. Check if all label were included in submitted file
        discreparencies = self.get_min_discreparencies(p_data, p_correct_data)
        print(discreparencies['stop'])

        for p_correct_line, start_disc, stop_disc in zip(
                p_correct_data, discreparencies['start'],
                discreparencies['stop']):
            if start_disc >= CONFIG['LIMIT_SAMPLE_LENGTH']:
                message = "You might missed {code} around ({start}, {stop})".format(
                    code=p_correct_line['code'],
                    start=int(p_correct_line['start']),
                    stop=int(p_correct_line['stop'])
                )
                self.results.append((-1, 'ALL lines', params.ERROR, message))

    def get_min_discreparencies(self, p_data, p_correct_data):
        # to store the current minimum discreparency of p_correct_data

        def minimum_discreparency(key):
            _min_disc = [
                CONFIG['LIMIT_SAMPLE_LENGTH']] * len(p_correct_data)
            for i, p_correct_line in enumerate(p_correct_data):
                for j, p_line in enumerate(p_data):
                    if p_line['format_status'] is params.DONE:
                        if p_line['code'] == p_correct_line['code']:
                            ij_discreparency = abs(
                                p_line[key] - p_correct_line[key])
                            _min_disc[i] = min(
                                _min_disc[i],
                                ij_discreparency
                            )
            return _min_disc

        return {
            'start': minimum_discreparency('start'),
            'stop': minimum_discreparency('stop'),
            }

    def _load_file(self, path):
        return codecs.open(path, 'r', 'shift-jis').read().split('\n')[:-1]

    def _load_correct_data(self):
        """ Load correct data correspond to the file

        Output:
            data: np.array or None
                return None if there is no corresponding file
        """
        # convert to correct path
        # exp1-sub1-label.csv(or.txt) <-> exp1-sub1-correct.csv
        correct_path = self.path.replace(
            "label", "correct").replace(".txt", ".csv")
        correct_path = correct_path.replace(
            os.path.dirname(correct_path), CONFIG["META_DIR"]
        )
        print(correct_path)
        if os.path.exists(correct_path):
            return open(correct_path).read().split('\n')[:-1]
        else:
            return None

    def _validate_eachline(self, i, p_line):
        """ Check if the line format is valid or not

        1. Check the format
        2. Check the diff between (start, stop)
        3. Check the code is in the list
        """
        # 1. Check the format
        if p_line['format_status'] == params.ERROR:
            message = "Invalid line syntax: "
            message += "Please be sure that the line looks like"
            message += " '{code},{start},{stop},{comment}'"
            self.results.append((i, p_line['raw'], params.ERROR, message))
            return False

        # 2. Check the diff between (start, stop)
        if p_line['start'] > p_line['stop']:
            message = "Start time must be ealier than stop time"
            self.results.append((i, p_line['raw'], params.ERROR, message))
            return False

        # 3. Check the code is in the list
        if p_line['code'] not in self.label_list:
            message = "Label name error:"
            message += "label name {} is not in the list".format(
                p_line['code'])
            self.results.append((i, p_line['raw'], params.ERROR, message))
            return False

        return True

    def validate_with_nearest_correct_line(self, i, line, p_correct_data):
        #
        # 1. check missing an action
        # 2. check difference between
        #      test label's time and correct label's time
        #
        start_errors = [CONFIG['LIMIT_SAMPLE_LENGTH']]
        stop_errors = [CONFIG['LIMIT_SAMPLE_LENGTH']]

        if line['format_status'] == params.ERROR:
            return None
        name = line['code']
        start = line['start']
        stop = line['stop']

        for correct_i, correct_line in enumerate(p_correct_data):
            correct_name = correct_line['code']
            correct_start = correct_line['start']
            correct_stop = correct_line['stop']
            if name == correct_name:
                start_error = start - correct_start
                start_errors.append(start_error)
                stop_error = stop - correct_stop
                stop_errors.append(stop_error)
            else:
                print(name, correct_name)

        min_abs_time = min(map(abs, start_errors))
        if CONFIG['ACCEPTABLE_DISCREPARENCY'] < min_abs_time:
            message = "Start time might be slightly different!"
            message += " Please check the line again."
            self.results.append((i, line['raw'], params.WARNING, message))
        min_abs_time = min(map(abs, stop_errors))
        if CONFIG['ACCEPTABLE_DISCREPARENCY'] < min_abs_time:
            message = "Start time might be slightly different!"
            message += " Please check the line again."
            self.results.append((i, line['raw'], params.WARNING, message))


def convert_timeexpression(time_string, frame_rate=30.0):
    # >>> time = '1:0:0'
    # >>> convert_timeexpression(time)
    # 60.0
    # >>> time = '0:0:30'
    # >>> convert_timeexpression(time)
    # 1.0
    m = int(time_string.split(':')[0])
    s = int(time_string.split(':')[1])
    f = int(time_string.split(':')[2])
    return m * 60 + s + f / float(frame_rate)


class Results(object):
    def __init__(self, taskIDs):
        self.taskIDs = taskIDs
        self.msg_lines = []  # the list of touple

    def append(self, msg_line):
        self.msg_lines.append(msg_line)

    def as_string(self, lfc='<br>'):
        if len(self.msg_lines) == 0:
            return """
Complete: There is no error/warning messages.
Please send a final version to iwasawa@weblab.t.u-tokyo.ac.jp.

            """
        else:
            return lfc.join([self._format_line(x) for x in self.msg_lines])

    def as_raw(self):
        return self.msg_lines()

    def _format_line(self, line):
        return "{status} (at line {i}, {content}): {message}".format(
            status=line[2], message=line[3], i=line[0], content=line[1].encode('utf-8')
        ).decode('utf-8')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process task information.')
    parser.add_argument('path', metavar='path', help='file path for the data')

    args = parser.parse_args()

    document = Checker(args.path)
    document.check()
    print document.results.as_string()
