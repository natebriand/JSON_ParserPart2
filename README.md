README
Nate Briand


The instructions for running this code are quite simple. Provided are two folders, one input folder containing 10
intput.txt files containing token streams received from the Scanner in part 1 of the final project. The second folder
is an output folder containing 10 output.txt files to which the parse tree representation of the correlating input file
will be written to. All input folders already contain token streams, and Parser.py is programmed to write the
data to the output files, so a simple run of Parser.py will show functionality.

There are a few assumptions made:

1. Assume that the JSON being inputted is in proper format, meaning as there is a number of key-value pairs contained
inside opening and closing curly braces, where the key is a string, and the value can be a bool, number, string, list
or another object containing more key-value pairs.
2. Assuming that the token stream being inputted is in the format of what was obtained from my final project part 1.
An example of a token would be <STRING, sunny>. This also means that the last token in this input file is <EOF, -1>



