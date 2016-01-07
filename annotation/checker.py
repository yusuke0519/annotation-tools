# # -*- coding: utf-8 -*-
from identifier import get_IDs_from_path
import params

config = {}
config['N_COLUMNS'] = 4
config['sep'] = ','
config['header'] = 'labelname,start,stop,comment'


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
        # self.correct_data = self._load_correctly_labeled_data()

    def check(self):
        print("Start checking...")
        for i, line in enumerate(self.contents):
            self._check_eachline(i, line)
        print("Done")

    def _load_file(self, path):
        return open(path).read().split('\n')

    def _check_eachline(self, i, line):
        self.line_format_check(i, line)
        self.compatible_validation_with_correct_labeles(i, line)

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

    def compatible_validation_with_correct_labeles(self, i, line):
        # do something
        pass

    def _load_correctly_labeled_data(self):
        raise Exception("The method is not implemented yet")


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