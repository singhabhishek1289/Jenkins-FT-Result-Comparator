from tkinter import messagebox

import requests


class JenkinsTestResults:
    output_dict = {'Equal_Tests': [{}], 'Conflicting_Errors': [{}], 'Regression_Tests': [{}], 'Resolved_Tests': [{}],
                   'Ignored_Tests': [{}],
                   'Emerging_Test_Failures': [{}], 'Emerging_Resolved_Tests': [{}], 'New_Test_Failures': [{}],
                   'New_Testsuite_Failures': [{}]}

    # Clears all the empty dicts added to the output objevt.
    def clear_empty_fields(self):
        for key in self.output_dict.keys():
            self.output_dict[key].pop(0)

    def __init__(self, auth_info):
        self.auth_info = auth_info

    # Connects to jenkins server and gets the test results as json.
    def get_test_results(self, url):
        try:
            response = requests.get(url, auth=self.auth_info)
            if response.status_code == 200:
                print("Crumb details obtained successfully.")
                return response.json()
            else:
                raise ValueError(
                    f"Failed to obtain test Results. Status code: {response.status_code}")
                return None
        except ValueError as ve:
            messagebox.showerror("Value Error", ve)

    # Parses the response json and prepares a dictionary with suits name value as list with all cases.
    def parse_result(self, response):
        if response:
            tests_report = {}
            suites = response.get("suites")
            for suite in suites:
                tests_report[suite.get('name')] = suite.get('cases')
            return tests_report

    # Calls get_test_results and calls parse_result methods
    def get_result_and_parse(self, url):
        response = self.get_test_results(url)
        return self.parse_result(response)

    # This Method does the comparision.
    def compare_results(self, old_test_report, new_test_report):

        for key in new_test_report.keys():
            if key in old_test_report:
                self.compare_test_suits(old_test_report[key], new_test_report[key])
            else:
                self.add_new_suits(new_test_report[key])
        self.clear_empty_fields()
        return self.output_dict

    # Checks if passed test names are same or not and returns True/False
    def check_name(self, case1, case2):

        if case1["name"] == case2["name"]:
            return True
        else:
            return False

    # Checks if the status is passed/Failed and returns True/False
    def check_status(self, old_status, new_status):
        print(old_status + ":" + new_status)
        if old_status == "PASSED" and new_status == "FAILED":
            return False
        elif old_status == "FIXED" and new_status == "FAILED":
            return False
        else:
            print(True)
            return True

    #Checks if cases info is skipped and returns True/False.
    def check_skipped(self, old_skipped, new_skipped):

        if old_skipped == "false" and new_skipped == "true":
            return True
        else:
            return False

    # Verifies the testcase and added them to corresponding category from defined 9 categories.
    def check_test(self, testcase, testcase2):
        skip_status = cnf_error = add_test = False
        for key in testcase.keys():
            if testcase[key] != testcase2[key]:
                match key:
                    case "status":
                        if skip_status:
                            if self.check_status(testcase[key], testcase2[key]):
                                self.output_dict["Emerging_Resolved_Tests"].append(testcase2)
                            else:
                                self.output_dict["Emerging_Test_Failures"].append(testcase2)
                        else:
                            if self.check_status(testcase[key], testcase2[key]):
                                self.output_dict["Resolved_Tests"].append(testcase2)
                            else:
                                self.output_dict["Regression_Tests"].append(testcase2)
                        add_test = True
                        break
                    case "errorDetails":
                        if testcase[key] != "null" and testcase[key] is not None and testcase2[key] != "null" \
                                             and testcase2[key] is not None:
                            testcase2["old_errorDetails"] = testcase[key]
                            self.output_dict["Conflicting_Errors"].append(testcase2)
                            cnf_error = True
                            break

                    case "skipped":
                        if self.check_skipped(testcase[key], testcase2[key]):
                            self.output_dict["Ignored_Tests"].append(testcase2)
                            break
                        else:
                            skip_status = True
                            break
        if testcase2['status'] == 'FAILED' and not add_test and not cnf_error:
            self.output_dict["Equal_Tests"].append(testcase2)

    # Takes two test suites list and does the compare.
    def compare_test_suits(self, old_testcases, new_testcases):

        for testcase in new_testcases:
            is_new_case = True
            for testcase2 in old_testcases:
                if self.check_name(testcase2, testcase):
                    self.check_test(testcase2, testcase)
                    is_new_case = False
                else:
                    continue
            if is_new_case and testcase["status"] == "FAILED":
                self.output_dict["New_Test_Failures"].append(testcase)

    # Adds the new test suit failure to output.
    def add_new_suits(self, new_testcases):
        for new_case in new_testcases:
            if new_case["status"] == 'FAILED':
                self.output_dict["New_Testsuite_Failures"].append(new_case)
