from subprocess import call

test_scripts = [
    "gist.tests.test_utils",
    "gist.tests.test_sst",
]

if __name__ == "__main__":
    for test_case in test_scripts:
        call("python -m %s" % test_case)
