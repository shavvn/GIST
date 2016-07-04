import sys

if __name__ == "__main__":
    input_f_name = sys.argv[1]
    with open(input_f_name, "r") as fp:
        for line in fp:
            print "opened file %s" %input_f_name
            print line
