# JealousyATP
Are you jealous? Do you suspect some couple of texting each other a bit too much? Are you nosy or a gossiper? Do you want to find out which friends of yours are texting each other? If you and they use Telegram, this is a tool made just for you!

## Setup
* Install Python
* Build the [Telegram Database library](https://tdlib.github.io/td/build.html?language=Python)
* Run the `whoiswho.py` script to load your contacts to the `names.txt` file
* Start the `ostrovid.py` script and keep it running, it log online statuses of your contacts to the `onlines.txt` file
* After some time, you can run the `anna_liza.py` script to analyse the collected data and find out which contacts of yours spent the most time online together

## ATP (Algorithm of T. and P.)
The `anna_liza.py` computes how much time each person spent online and how much time each couple spent online together (with T argument specifying the tolerance of what it means to be together). The quotient of those values is a portion of online time which is spent together. After sorting the couples by the quotient, the program takes those couples for whom each of the couple has the highest quotient in the relationship with the other of the couple. Those couples are marked as suspicious. After repeating these steps for different values of the T argument, the program prints the results.

The `inclusions` is the count of T values (from zero to maximal T) for which the couple has been marked as suspicious. The strictness of the filter is the minimal number of `inclusions` for which the couple is printed.
