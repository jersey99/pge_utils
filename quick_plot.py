'''
Takes csv files from PGE (Pacific Gas & Electric) billing and loads them into
a pandas dataframe and resamples them into a user selectable frequency
'''
import argparse
import matplotlib.ticker as ticker
import pandas as pd

from matplotlib import pyplot as plt


def load_electric(fname):
    return pd.read_csv(
        fname,
        skiprows=5,
        parse_dates=[[1, 3]],
        index_col=[0],
        converters={6: lambda s: float(s.strip('$'))})


def load_gas(fname):
    return pd.read_csv(
        fname,
        skiprows=5,
        parse_dates=[1],
        index_col=[1],
        converters={
            2: lambda s: float(s) * 29.003,  # Converting therms to kWH
            4: lambda s: float(s.strip('$'))
        })


def resample(electricity, gas, frequency):
    '''
    Resample the electricity and gas dataframes at the given frequency
    '''
    daily = pd.DataFrame()
    daily['electric_cost'] = electricity.COST.resample(frequency).sum()
    daily['gas_cost'] = gas.COST.resample(frequency).sum()
    daily['elec_usage_kwh'] = electricity.USAGE.resample(frequency).sum()
    daily['gas_usage_kwh'] = gas.USAGE.resample(frequency).sum()
    daily['total_cost'] = daily.electric_cost + daily.gas_cost
    daily['total_usage'] = daily.elec_usage_kwh + daily.gas_usage_kwh
    # daily['gas_dpkwh'] = daily.gas_cost / daily.gas_usage_kwh
    # daily['electric_dpkwh'] = daily.electric_cost / daily.elec_usage_kwh
    return daily


def plotting(daily, stacked=False):
    ticklabels = daily.index.strftime('%m-%d')
    ax = daily[['electric_cost', 'gas_cost']].plot.bar(stacked=stacked)
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    ax = daily[['elec_usage_kwh', 'gas_usage_kwh']].plot.bar(stacked=stacked)
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    # ax = daily[['electric_dpkwh', 'gas_dpkwh']].plot()
    # ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    ax = daily[['elec_usage_kwh']].plot.bar()
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))

    # ax = daily[['gas_dpkwh']].plot.bar()
    # ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    # plt.bar(gas.index, gas.COST)
    # plt.bar(daily.index, daily.electric_cost)
    plt.show()


def csv_dump(daily):
    print(daily.to_csv())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument(
        '-e',
        '--ebill',
        default=
        'data/pge_electric_interval_data_2616143909_2017-11-02_to_2018-09-27.csv',
        help='Electric bill usage/cost .csv file')
    parser.add_argument(
        '-g',
        '--gbill',
        default=
        'data/pge_gas_interval_data_2613214466_2017-11-02_to_2018-09-27.csv',
        help='Gas bill usage/cost .csv file')
    parser.add_argument(
        '-f',
        '--frequency',
        default='M',
        help='Group the data by M (Month), W (Weekly), D (Daily)')
    parser.add_argument(
        '-c',
        '--dump_csv',
        default='False',
        help='A summarized csv at the requested frequency')
    args = parser.parse_args()
    E_BILL = args.ebill
    G_BILL = args.gbill
    E = load_electric(E_BILL)
    G = load_gas(G_BILL)
    FREQ = args.frequency
    dump_csv = args.dump_csv

    daily = resample(E, G, FREQ)

    # Rescale the data frame if necessary
    # daily = daily['20180201':'20180901']

    plotting(daily)

    # daily['estimated_water_heating'] = [12.00] * len(daily.index)
    total_cost = daily.total_cost.sum()
    total_electric = daily.electric_cost.sum()
    total_gas = daily.gas_cost.sum()

    if dump_csv:
        csv_dump(daily)

    # total_estimated = (
    #    daily.electric_dpkwh * daily.gas_usage_kwh + daily.electric_cost).sum()

    # print('total_cost: {0:.2f}\ntotal_electric: {1:.2f}\ntotal_gas: {2:.2f}'.
    #       format(total_cost, total_electric, total_gas))
