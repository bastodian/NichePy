#!/bin/bash

### In its simplest form you can generate batches of Maxent models by pasting the commands to run into a file and make the file executable (e.g., chmod u+x myBatchFile.sh).
### Pending that the first line of the batch file conatains the line #!/bin/bash and you are using the bash shell (on a Mac the terminal is bash by default), the script can
### be executed by issuing ./myBatchFile.sh
###
### The example below works with Maxent 3.1.0. The important flags are -e that specifies the location of the environemntal ASCII grid files; projectionlayers is optional, but
### let's you specify the projection grid layers if different from training grids; -o specifies the output path; -z runs Maxent without starting the GUI; nowarnings, notooltips, 
### and autorun make Maxent run without interruptions such as errors due to some occurrence data that miss environmental information etc.
###
### Options for Maxent change frequently and the options in this example may not work in your version of Maxent. Start the Maxent GUI and click on the help button to learn more
### more about the flags supported by your version of Maxent.

java -jar /path/to/maxent.jar -e /path/to/environemntal/layers1/ projectionlayers=/path/to/projection/layers1/ samplesfile=/path/to/occurrences1.csv -o /path/to/output/directory1/ -z nowarnings notooltips autorun
java -jar /path/to/maxent.jar -e /path/to/environemntal/layers2/ projectionlayers=/path/to/projection/layers2/ samplesfile=/path/to/occurrences2.csv -o /path/to/output/directory2/ -z nowarnings notooltips autorun
