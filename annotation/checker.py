# # -*- coding: utf-8 -*-
from identifier import get_IDs_from_path
import params

config = {}
config['N_COLUMNS'] = 4
config['sep'] = ','
config['header'] = 'labelname,start,stop,comment'

# err_range[0] is acceptable error
# err_range[1] is un-acceptable error
err_range = [123456, 123412345]
correct_path = 'sdfgyu.csv'


class Checker(object):
    def __init__(self, path):
        self.path = path
        prefix = path.split('/')[-1].split('.')[0]  # before the . of filename
        taskIDs = get_IDs_from_path(prefix.split('.')[0])  # before the .
        self.taskIDs = taskIDs
        self.contents = self._load_file(path)  # the list of string (each line)

        # Init the results variable
        self.results = Results(taskIDs)

        # Prepare correct data
        self.correct_data = self._load_correctly_labeled_data()

    def check(self):
        print("Start checking...")
        error_list = np.ones(len(self.correct_data), 3) * 1000
        for i, line in enumerate(self.contents):
            error_list = self._check_eachline(i, line, error_list)
        check_miss_labels(error_list)
        print("Done")

    def _load_file(self, path):
        return open(path).read().split('\n')

    def _check_eachline(self, i, line, error_list):
        self.line_format_check(i, line)
        error_list = self.compatible_validation_with_correct_labeles(i, line, error_list)
        return error_list

    def line_format_check(self, i, line):
        # do somevalidation (I think generator strategy would be work here)
        # e.g.
        # 1. the number of columns
        # 2. the format of time
        # 3. fin time - start time

        # Heare is example of 1. the number of columns
        # TODO: May by you need to separete each validation on other file
        # so that we can easily call it (and keep the source simple)
        nb_cols = len(line.split(','))
        if len(line.split(',')) != config["N_COLUMNS"]:
            message = "#column should be %d, detected %d" % (
                config["N_COLUMNS"], nb_cols)
            self.results.append((i, line, params.ERROR, message))
        # check e.g(2)
        line = line.split(',')
        if float(line[1]) >= float(line[2]):
            message = "start time is later stop time"
            self.results.append((i, line, params.ERROR, message))


    def compatible_validation_with_correct_labeles(self, i, line, error_list):
        #
        # 1. check missing an action
        # 2. check difference between test label's time and correct label's time
        #
        start_errors = []
        finish_errors = []
        check_start = False  # initialize start time's big error tag
        check_finish = False  # initialize finish time's big error tag

        for correct_i, correct_line in enumerate(self.correct_data):
            if line[0] == correct_line[0]:
                start_error = line[1] - correct_line[1]
                start_errors.append(start_error)
                finish_error = line[2] - correct_line[2]
                finish_errors.append(finish_error)
                if abs(error_list[correct_i][1]) > abs(start_error):
                    # update error_list to minimum value
                    error_list[correct_i][0] = i
                    error_list[correct_i][1] = start_error
                    error_list[correct_i][2] = line

        min_abs_time = min(abs(start_errors))
        if err_range[0] < min_abs_time < err_range[1]:
            message = "#start time may be later than %f second" % err_range[0]
        elif err_range[1] < min_abs_time:
            check_start = True

        min_abs_time = min(abs(finish_errors))
        if err_range[0] < min_abs_time < err_range[1]:
            message = "#finish time may be later than %f second" % err_range[0]
        elif (err_range[1] < min_abs_time):
            check_finish = True

        if check_start:
            if check_finish:
                message = "#this action is nothing"
                self.results.append((i, line, params.ERROR, message))
            else:
                message = "#start time is absolutely different"
                self.results.append((i, line, params.WARNING, message))
        elif check_finish:
            message = "#finish time is absolutely different"
            self.results.append((i, line, params.WARNING, message))
        return error_list

    def _load_correctly_labeled_data(self):
        return open(correct_path).read().split('\n')
        # raise Exception("The method is not implemented yet")
    def check_miss_labels(self, error_list):
        for error in error_list:
            if err_range[1] < abs(error[1]):
                if error[1] <= 0:
                    message = 'you missed a action before %0.3f second from this start time'%abs(error[1])
                    self.results.append((error[0], error[2], params.WARNING, message))
            else:
                message = 'you missed a action after %0.3f second from this start time'%abs(error[1])
                self.results.append((error[0], error[2], params.WARNING, message))




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
            status=line[2], message=line[3], i=line[0], content=line[1])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process task information.')
    parser.add_argument('path', metavar='path', help='file path for the data')

    args = parser.parse_args()

    document = Checker(args.path)
    document.check()
    print document.results.as_string()
