# ------------------------- IMPORT LIBRARIES --------------------
import datetime
import pandas_datareader.data as pdr
from pandas_datareader._utils import RemoteDataError
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


try:
    from html.parser import HTMLParser
except:
    from HTMLParser import HTMLParser

# ------------------------- GLOBAL PARAMETERS -------------------------

INDICES = ['GSPC', 'NSEI', 'N225', 'FTSE', 'HSI']
INDICES_NAME = ['S&P 500', 'Nifty 50', 'Nikkei 225', 'FTSE 100', 'Hang Seng']

# ------------------------------ CLASSES ---------------------------------


class ExternalDataRetrieval:
    """
    This class is dedicated to retrieve external finance data

    Args:
        symbol: stock quote.
    """

    def __init__(self, symbol):
        self._symbol = symbol

    def get_historical(self):
        """
        Download last ten year daily stock index data from Yahoo finance

        Returns:
            ten year daily stock index data

        """
        # Define data range
        start = datetime.datetime(2007, 11, 9)
        end = datetime.datetime(2017, 11, 9)

        # Get data from Yahoo Finance
        tenyear_historical = pdr.DataReader(
            self._symbol.strip('\n'), 'yahoo', start, end)

        return tenyear_historical

    def get_monthly_return(self, market_index):
        """
        Calculate index monthly return for the last ten years.

        Returns:
            A single index ten year monthly return
        """

        # Set flag to indicate success of data download
        flag = False

        # Set counter for download trial
        counter = 0
        # Yahoo Finance is unstable, there's chance of server not responding to request on first trial,
        # adding a while loop to get the program keep trying until it gets the data
        # Loop will stop after 10 trials, which indicate high chance of server down
        while not flag and counter < 11:
            try:
                # Concatenate '^' to complete index symbol
                j = '^' + market_index
                # Download index last ten years daily data from yahoo
                daily_price = ExternalDataRetrieval(j).get_historical()

                # Calculate monthly return
                monthly_ret = MathCalc().calc_monthly_return(daily_price)

                # Indicate success of download
                flag = True

            # When server doesn't response to request, set flag, increase counter and try again
            except RemoteDataError:

                # Indicate download failure
                flag = False

                # Add to counter to indicate number of trial
                counter += 1
                continue

        # After ten trials, raise exception and advise user to try again.
        if counter > 10:
            raise Exception(
                'Sorry, fail to download data. Yahoo Finance server may be down. Please try again later')

        return monthly_ret

    def get_stacked_monthly_return(self):
        """
        Calculate five indices monthly return for the last ten years.

        Returns:
            Five indices ten year monthly return vertically stacked together
        """

        # Set a blank array
        stacked_monthly_return = []

        # Do this for all indices
        for i in INDICES:

            # Set flag to indicate success of data download
            flag = False

            # Set counter for download trial
            counter = 0
            # Yahoo Finance is unstable, there's chance of server not responding to request on first trial,
            # adding a while loop to get the program keep trying until it gets the data
            # Loop will stop after 10 trials, which indicate high chance of server down
            while not flag and counter < 11:
                try:
                    # Concatenate '^' to complete index symbol
                    j = '^' + i
                    # Download index last ten years daily data from yahoo, save the name to represent the index name
                    vars()[
                        i + '_daily_price'] = ExternalDataRetrieval(j).get_historical()

                    k = vars()[i + '_daily_price']
                    # Calculate monthly return
                    vars()[i + '_monthly_ret'] = MathCalc().calc_monthly_return(k)

                    # Indicate success of download
                    flag = True

                # When server doesn't response to request, set flag, increase counter and try again
                except RemoteDataError:
                    flag = False
                    counter += 1
                    continue

            # If the index monthly return data is successfully constructed, add it to the stack
            if flag:
                # Construct the first array in stack
                if i == INDICES[0]:
                    stacked_monthly_return = vars()[i + '_monthly_ret']
                # Stack the rest of the arrays to the stack
                else:
                    stacked_monthly_return = np.vstack(
                        (stacked_monthly_return, vars()[i + '_monthly_ret']))

            # After ten trials, raise exception and advise user to try again.
            if counter > 10:
                raise Exception(
                    'Sorry, fail to download data. Yahoo Finance server may be down. Please try again later')

        return stacked_monthly_return


class UserInterfaceInput:
    """
    The class to contain user input function.

    Returns:
        symbol: stock symbol entered by user
    Raises:
        AttributeError: When the choice user entered is not among the five choices.
    """

    @staticmethod
    def get_symbol():
        """
        Get user to choose a stock exchange among the five choices,
        Once selected, inform user the market index that represents the market/stock exchange

        Returns:
            symbol: the market index that represents the market user selected.
        """

        # The flag to indicate whether user has entered a valid choice
        validity = False

        # Display welcome message and prompt user to make a choice
        print ("\n")
        print ("############# Welcome to EXCHANGE CORRELATIONS #############")
        print ("\n")
        print ("1. United States: New York Stock Exchange/NASDAQ")
        print ("2. India: Bombay Stock Exchange")
        print ("3. Japan: Tokyo Stock Exchange")
        print ("4. United Kingdom: London Stock Exchange")
        print ("5. Hong Kong: Hong Kong Stock Exchange")
        print ("\n")

        # Prompt user until a valid choice is made
        while validity is False:
            symbol = ""
            symbol_name = ""
            try:
                choice = raw_input(
                    "Please select a stock exchange from 1 to 5 > \b")
                if [int(s) for s in choice.split() if s.isdigit()] == [1]:
                    symbol = INDICES[0]
                    symbol_name = INDICES_NAME[0]
                    stock_exchange = "New York Stock Exchange/NASDAQ"
                elif [int(s) for s in choice.split() if s.isdigit()] == [2]:
                    symbol = INDICES[1]
                    symbol_name = INDICES_NAME[1]
                    stock_exchange = "Bombay Stock Exchange"
                elif [int(s) for s in choice.split() if s.isdigit()] == [3]:
                    symbol = INDICES[2]
                    symbol_name = INDICES_NAME[2]
                    stock_exchange = "Tokyo Stock Exchange"
                elif [int(s) for s in choice.split() if s.isdigit()] == [4]:
                    symbol = INDICES[3]
                    symbol_name = INDICES_NAME[3]
                    stock_exchange = "London Stock Exchange"
                elif [int(s) for s in choice.split() if s.isdigit()] == [5]:
                    symbol = INDICES[4]
                    symbol_name = INDICES_NAME[4]
                    stock_exchange = "Hong Kong Stock Exchange"
                else:
                    pass

                # If user input is not within the expected answers or user just hit enter without entering a value
                if symbol not in INDICES:

                    print('Entry is not a valid selection.')

                elif symbol in INDICES:

                    # Get user to confirm his/her input
                    user_confirm = raw_input(
                        "Stock exchange: %s is selected, enter y/n to confirm >" % stock_exchange)

                    # If user says No
                    if user_confirm in ['n', 'N', 'no', 'No', 'NO']:
                        pass

                    # If user says Yes
                    elif user_confirm in ['y', 'Y', 'yes', 'Yes', 'YES']:

                        print "Great, you have selected: ", stock_exchange
                        print "which is represented by market index: %s" % (symbol_name)
                        validity = True

                    # If user input is not within the expected answers, re-loop and prompt user input again
                    else:
                        pass

            # When user does not enter a correct selection
            except Exception:
                print('Entry is not a valid selection.')

        # Inform user what the program will be doing, as the wait can be a while depends on user's internet speed
        print("Please wait, downloading data ...")

        return symbol


class MathCalc:
    """
    The class to contain all mathematical computation functions.

    """

    def daily_to_monthly(self, daily_data):
        """
        Function to convert daily to monthly price data

        Args:
            daily_data: daily index price data
        return:
            monthly_data: monthly index price data

        """

        # Set frequency and convert
        monthly_data = daily_data['Adj Close'].asfreq('M').ffill()

        return monthly_data

    def calc_monthly_return(self, daily_data):
        """
        Function to compute monthly return from daily price data
        Args:
            daily_data: daily index price data

        Return:
             monthly_return: monthly index return
        """
        # Convert to monthly price data first
        monthly_data = MathCalc().daily_to_monthly(daily_data)

        # Compute monthly return
        monthly_return = monthly_data / monthly_data.shift(1) - 1

        return monthly_return

    def correlation_trend(self, monthly_ret_a, monthly_ret_b):
        """
        Function to compute an array of correlation coefficient of 2 indices' monthly return

        Args:
            monthly_ret_a: Monthly return data of index a
            monthly_ret_b: Monthly return data of index b

        Return:
            corr_array: An array correlation coefficient for the last ten years monthly return
            year_array: An array of years that covers the correlation.
        """
        # Set the the first year
        min_year = min(monthly_ret_a.index.year)

        # Set the last year
        max_year = max(monthly_ret_a.index.year)

        # Construct the year array
        year_array = list(range(min_year + 1, max_year + 1))

        # Iterate through the years and calculate the correlation coefficient of the year
        corr_array = []
        for i in range(min_year, max_year + 1):
            array_a = monthly_ret_a[monthly_ret_a.index.year == i]
            array_b = monthly_ret_b[monthly_ret_b.index.year == i]
            corr_array.append(np.corrcoef(array_a, array_b)[0][1])

        # Remove the first value which is a NaN
        corr_array.pop(0)

        return corr_array, year_array


class UserInterfaceDisplay:
    """
    The class to display output to users by plotting a graph

    Args:
        stacked_return: 10 years monthly return for five indices stacked vertically.
        selected_symbol: The selected market index to compare with other indices.

    """

    def __init__(self, stacked_return, selected_symbol):
        self._stacked_return = stacked_return
        self._symbol = selected_symbol

        # Get the index number of selected index from the indices list
        self._m = INDICES.index(self._symbol)

        # Get the full name of the index symbol through the index number obtained above
        self._selected_index = INDICES_NAME[self._m]

        # Construct a list of index symbol excluding the selected index
        self._compare_list = [
            element for element in INDICES if element not in self._symbol]

        # Construct a list of index name excluding the selected index
        self._compare_list_n = [
            element for element in INDICES_NAME if element not in self._selected_index]

    def plot_scatter(self):
        """
        Functions to plot scatter plots and histograms of the selected index with the other 4 indices
        To show correlations of the selected index with the other four indices

        """
        # Inform user what the program is doing, as computation may take a while depends on user's computation resource
        print("Please wait, plotting scatter plots and histograms ...")
        # extract monthly return of the selected symbol from stacked monthly return, multiply by 100 to get % value
        # Also the first value, which is a NaN value is removed
        vars()[self._symbol + '_x'] = self._stacked_return[self._m][np.logical_not(
            np.isnan(self._stacked_return[self._m]))] * 100

        # extract monthly return for the rest of the symbols in the indices list, multiply by 100 to get % value
        # Also the first value, which is a NaN value is removed
        for i in self._compare_list:
            n = INDICES.index(i)
            vars()[i + '_y'] = self._stacked_return[n][np.logical_not(
                np.isnan(self._stacked_return[n]))] * 100

        # Clear screen from previous plot
        plt.close('all')

        # Set plot canvas and its size
        fig1 = plt.figure(figsize=(10, 10))

        # Set the 2 x 2 grid in order to show 4 scatter plots subplots for side-by-side comparison
        outer = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.2)

        # Plot index by index
        for i, f in enumerate(self._compare_list):

            # Set the internal grid within each subplot, the selected index histogram on top
            # the compared index histogram on the right and the scatter plot enclosed by both histograms
            inner = gridspec.GridSpecFromSubplotSpec(2, 2,
                                                     width_ratios=[4, 1], height_ratios=[1, 4],
                                                     subplot_spec=outer[i], wspace=0.1, hspace=0.1)

            # Iterate through the subplot within subplot.
            for j in range(4):
                ax = plt.Subplot(fig1, inner[j])

                # last ten years monthly return for selected index
                x = vars()[self._symbol + '_x']

                # last ten years monthly return for compared index
                y = vars()[f + '_y']

                # An overall correlation coefficient of ten year monthly return
                cc = round(np.corrcoef(x, y)[0][1], 3)

                # Plot scatter plot of both indices at bottom left
                if j == 2:
                    ax.scatter(x, y, color='r', s=30, marker='s', alpha=.4)
                    if i > 1:
                        ax.set_xlabel('Monthly return for %s in percentage' % (
                            self._selected_index), fontsize=9)
                    ax.set_ylabel('Monthly return for %s in percentage' %
                                  (self._compare_list_n[i]), fontsize=9)

                # Plot compared index histogram at bottom right
                elif j == 3:
                    ax.hist(y, bins=30, orientation='horizontal')
                    plt.setp(ax.get_yticklabels(), visible=False)

                # Plot selected index histogram at top left
                elif j == 0:
                    ax.hist(x, bins=30)
                    ax.set_title('Correlation coef. of  %s with %s: %s ' % (
                        self._selected_index, self._compare_list_n[i], cc), size=10, color='g')
                    plt.setp(ax.get_xticklabels(), visible=False)

                # Void the top right subplot
                elif j == 1:
                    ax.axis('off')

                fig1.add_subplot(ax)

        # Display and save the graph
        plt.savefig('%s_scatter.pdf' % self._symbol)

        # Inform user graph is saved
        print(
            "Plot saved as %s_scatter.pdf. Please close this plot, Correlation trend will be plotted next. Thank You!" % self._symbol)
        plt.show()

    def plot_corr_trend(self):
        """
        Function to plot correlation trend of the selected index with other indices over the years

        """
        # Inform user what the program is doing, as computation may take a while depends on user's computation resource
        print("Please wait, plotting correlation trend ...")

        # Set plot canvas and its size
        fig2 = plt.figure(figsize=(10, 6))

        # Iterate the compared list to get correlation coefficient array for every compared index
        # Plot the correlation line on the plot canvas
        for i, f in enumerate(self._compare_list):

            monthly_return_selected = ExternalDataRetrieval(
                self._symbol).get_monthly_return(self._symbol)
            monthly_return_compare = ExternalDataRetrieval(
                self._symbol).get_monthly_return(f)
            correlation_array, year_array = MathCalc().correlation_trend(
                monthly_return_selected, monthly_return_compare)

            plt.plot(year_array, correlation_array, '-',
                     label="with %s" % (self._compare_list_n[i]))

        plt.legend()
        plt.xlabel('Year')
        plt.ylabel('Correlation coefficient')
        plt.title('Correlation trend for %s with other market indices ' %
                  (self._selected_index), fontsize=14)

        # Display and save the graph
        plt.savefig('%s_CorrTrend.pdf' % self._symbol)

        # Inform user graph is saved and the program is ending.
        print(
            "Plot saved as %s_CorrTrend.pdf. When done viewing, please close this plot to end program. Thank You!" % self._symbol)

        plt.show()


# ----------------------------- MAIN PROGRAM ---------------------------------


if __name__ == '__main__':

    # Get user to choose a market and symbol first
    selected_symbol = UserInterfaceInput.get_symbol()
    # Get monthly return for all five indices
    stacked_return = ExternalDataRetrieval(
        selected_symbol).get_stacked_monthly_return()
    # Display scatter plots and histograms
    UserInterfaceDisplay(stacked_return, selected_symbol).plot_scatter()
    # Display correlation trend
    UserInterfaceDisplay(stacked_return, selected_symbol).plot_corr_trend()

    # Officially end of program
    print ("\n")
    print (
        "#################### End of program, Thank you for using! ####################")
    print ("\n")
    # -------------------------------- END  ---------------------------------------
