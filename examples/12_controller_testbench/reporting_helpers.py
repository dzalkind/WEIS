import os
import copy
import numpy as np
import pandas as pd
import ruamel.yaml as ry
import matplotlib.pyplot as plt
from openfast_io import FileTools


def create_summary_table(aep_info, char_loads, char_load_cases, char_load_channels, dd, ds, del_channels, labels):
    """
    Create a summary table DataFrame with AEP, characteristic loads, and DELs.
    Returns a DataFrame with percent change columns.
    """
    # Collect AEP information into a summary table dictionary
    summary_table_dict = {}
    summary_table_dict['AEP (GWh)'] = [aep_info[i]['AEP']/1e6 for i in range(len(aep_info))]

    # Collect characteristic loads for each DLC case and channel
    for cl in char_loads:
        for case in char_load_cases:
            for channel in char_load_channels:
                l = f'DLC {case} Char. {channel} Load'
                if l not in summary_table_dict:
                    summary_table_dict[l] = []
                summary_table_dict[l].append(cl[case][channel]['characteristic_load'])

    # Collect DELs for each channel, case
    cases = [index for index, element in enumerate(dd[0].index) if '1.1' in element]
    cases = dd[0].index[cases]
    for ds_i in ds:
        for channel in del_channels:
            l = f'{channel} DEL'
            if l not in summary_table_dict:
                summary_table_dict[l] = []
            summary_table_dict[l].append(ds_i[channel])

    # Set up dataframe for summary table
    summ_df = pd.DataFrame(summary_table_dict).T
    summ_df.columns = labels

    # Add percent change from baseline controller
    baseline_label = labels[0]
    for l in summ_df.columns[1:]:
        perc_change = 100 * (summ_df[l] / summ_df[baseline_label] - 1)
        change_label = f'{l} (percent change)'
        summ_df[change_label] = perc_change

    return summ_df

def plot_binned_data(dfs, channels=None, fig=None, labels = None):
    """
    Plots time series from defined channels within the dataframe (df, binned_*.p).
    """

    if not type(dfs) == list:
        dfs = [dfs]
    
    if channels is None:
        channels = ['RootMyb1','TwrBsMyt','LSSTipMya','YawBrMyp']

    if fig is None:
        fig, ax = plt.subplots(len(channels), 1, figsize=(10,3*len(channels)), tight_layout=True)
    else: 
        ax = fig.axes
    if len(ax) != len(channels):
        raise ValueError(f"Figure provided does not have the same number of axes as channels. Expected: {len(channels)}, actual: {len(ax)}.")

    if labels is None:
        labels = []
        for k in range(len(dfs)):
            labels.append('Controller '+str(k+1))

    for n, channel in enumerate(channels):
        for k, df in enumerate(dfs):
            ax[n].plot(
                np.sqrt(df['Wind1VelX']**2 + df['Wind1VelY']**2),
                abs(df[channel]),
                label=labels[k],
                marker='.',
                markersize=.75,
                alpha=0.75,
                linestyle='None'
            )
        # ax[n].axhline(y=np.max(abs(df[channel])), color='C'+str(k), linestyle='--', label='_')
        ax[n].set_xlabel('Wind speed')
        ax[n].set_ylabel(channel)
        ax[n].grid()
        ax[n].set_xlim([0, 30])
        if len(dfs) > 1:
            ax[0].legend()
    
    dt = df['Time'].iloc[1] - df['Time'].iloc[0]
    fig.set_size_inches(7,len(channels)*3)
    return fig, ax, dt

def plot_characteristic_loads(data, cases=None, channels=None, labels = None):
    """
    Plots characteristic loads from yaml file for defined channels and DLC cases.
    """

    if not type(data) == list:
        data = [data]

    if cases is None:
        cases = ['1.1','1.3']
    
    if channels is None:
        channels = ['RootMyb1','TwrBsMyt','LSSTipMya','YawBrMyp']

    if labels is None:
        labels = []
        for k in range(len(data)):
            labels.append('Controller '+str(k+1))

    for case in cases:
        fig, ax = plt.subplots(len(channels), 1, figsize=(7,2*len(channels)), tight_layout=True)

        ax[0].set_title(f"DLC {case}")
        for n, channel in enumerate(channels):
            for k, datum in enumerate(data):
                ax[n].scatter(datum[case][channel]['wind_speed'], datum[case][channel]['load_values'], label=labels[k])
                ax[n].axhline(y=datum[case][channel]['characteristic_load'], color='C'+str(k), linestyle='--',label='_')
            ax[n].set_xlabel('Wind speed')
            ax[n].set_ylabel(channel)
            ax[n].grid()
        if len(data) > 1:
            ax[0].legend()

    return fig, ax


# Function for reading case matrix
def read_cm(fname_case_matrix):
    cm_dict = FileTools.load_yaml(fname_case_matrix, package=1)
    cnames = []
    for c in list(cm_dict.keys()):
        if isinstance(c,ry.comments.CommentedKeySeq):
            cnames.append(tuple(c))
        else:
            cnames.append(c)

    cm = pd.DataFrame(cm_dict, columns=cnames)
    
    if ('DLC','Label') in cm:

        cm[('DLC','Label')].unique()

        dlc_inds = {}

        for dlc in cm[('DLC','Label')].unique():
            dlc_inds[dlc] = cm[('DLC','Label')] == dlc

        return cm, dlc_inds
    
    else:
        return cm, None

def plot_timeseries(summary_folders,cases_to_plot, channels=None,labels=None):
    if channels is None:
        channels = ["Wind1VelX_[m/s]", "GenTq_[kN-m]", "BldPitch1_[deg]", "RtSpeed_[rpm]"]
    
    if labels is None:
        labels = []
        for k in range(len(summary_folders)):
            labels.append('Controller '+str(k+1))
    
    for case in cases_to_plot:
        fig, axs = plt.subplots(len(channels), 1)
        if len(channels) == 1:
            axs = [axs]
        axs = axs.flatten()
        for summary_folder in summary_folders:
            dfdlc = pd.read_pickle(
                os.path.join(summary_folder,f"timeseries/{case}.p")
            )
            for i_chan, chan in enumerate(channels):

                if chan not in dfdlc.columns:
                    print(f"Channel {chan} not found in {case} timeseries data.")
                    continue
                axs[i_chan].plot(dfdlc["Time"], dfdlc[chan.split("_")[0]], label=case)
                axs[i_chan].set_ylabel(chan.replace("_", "\n"))
                axs[i_chan].grid(True)

        fig.set_figheight(2.5 * len(channels))
        fig.set_figwidth(7)
        fig.align_ylabels()
        axs[0].set_title(
            f"{case}"
        )
        axs[0].legend(labels)
        axs[-1].set_xlabel("Time")
    # return fig, axs
    

def stability_analysis(summary_folders, case_matrix, labels, case_index = 0):
    # NOTE: This code assumes that same dlcs has been run in all the cases.
    casematrix = case_matrix[case_index]
    
    allrampdlcs = []
    allstepdlcs = []
    allsteadystepdlcs = []
    allsteadydlcs = []

    for dlc, dlctype in casematrix["DLC"].items():
        match dlctype:
            case "Ramp":
                allrampdlcs.append(dlc)
            case "Step":
                allstepdlcs.append(dlc)
                if casematrix[('InflowWind', 'WindType')][dlc] == 2:
                    allsteadystepdlcs.append(dlc)
            case "Steady":
                allsteadydlcs.append(dlc)
    if allrampdlcs:
        plot_stability_timeseries(summary_folders, allrampdlcs, labels)
    if allstepdlcs:
        plot_stability_timeseries(summary_folders, allstepdlcs, labels)
    if allsteadydlcs:
        plot_stability_timeseries(summary_folders, allsteadydlcs, labels)
    if allsteadystepdlcs:  # TODO: disabled for now, use case_matrix to determine step time
        measure_stepresponse(summary_folders,casematrix,allsteadystepdlcs)



def plot_stability_timeseries(summary_folders, alldlcs, labels):
    channels = ["Wind1VelX_[m/s]", "GenTq_[kN-m]", "BldPitch1_[deg]", "RtSpeed_[rpm]"]
    for dlc in alldlcs:
        fig, axs = plt.subplots(len(channels), 1)
        if len(channels) == 1:
            axs = [axs]
        axs = axs.flatten()

        for case in summary_folders:
            dfdlc = pd.read_pickle(
                os.path.join(case, f"timeseries/{dlc}.p")
            )
            for i_chan, chan in enumerate(channels):
                axs[i_chan].plot(dfdlc["Time"], dfdlc[chan.split("_")[0]], label=case)
                axs[i_chan].set_ylabel(chan.replace("_", "\n"))
                axs[i_chan].grid(True)

        fig.set_figheight(2 * len(channels))
        fig.set_figwidth(7)
        axs[0].set_title(
            f"{dlc.split('_')[0][3:].lower()} inflow with {dlc}"
        )
        axs[0].legend(labels)
        axs[-1].set_xlabel("Time")
        # fig.savefig(f"{dlc}_StabilityAnalysis.png")

def measure_stepresponse(summary_folders,casematrix,alldlcs):
    for case in summary_folders:

        for dlc in alldlcs:

            # Read step wind information
            windfile_step = casematrix[('InflowWind', 'FileName_Uni')][dlc]


            with open(os.path.join(case,'wind',windfile_step),'r') as f:
                winddata = f.readlines()
            steptime = float(winddata[7].split()[0])

            dfdlc = pd.read_pickle(
                os.path.join(case, f"timeseries/{dlc}.p")
            )
            channels = ["GenTq_[kN-m]", "BldPitch1_[deg]", "RtSpeed_[rpm]"]
            time = dfdlc['Time']
            for chan in channels:
                y = dfdlc[chan.split("_")[0]]

                # Steady state value
                yss = np.mean(y[time>steptime])

                # Overshoot
                overshoot = (np.max(y) - yss) / yss * 100

                # Rise time
                y_10perc = 0.1 * yss
                y_90perc = 0.9 * yss
                rise_start = time[np.where(y >= y_10perc)[0][0]]
                rise_end = time[np.where(y >= y_90perc)[0][0]]
                rise_time = rise_end - rise_start

                # Settling time
                # within_tol_2percent = np.abs(y - yss) <= 0.02 * yss
                # settling_time_2percent = time[np.where(within_tol_2percent)[0][-1]] if np.all(within_tol_2percent) else time[-1]
                print(f"for chan = {chan}, overshoot is {overshoot}, risetime is {rise_time}")# , settline_time is {settling_time_2percent}")


def plot_dels_at_ws(dfs, sumfs, dss, channels = None, cases = None, fig = None, labels = None):
    """
    Plot DELs (from df DELs file) for different wind speeds (from sumf summary file).
    """

    if not type(dfs) == list:
        dfs = [dfs]    
    if not type(sumfs) == list:
        sumfs = [sumfs]  
    if not type(dss) == list:
        dss = [dss]

    if channels is None:
        channels = ['RootMyb1','TwrBsMyt','LSSTipMya','YawBrMyp']

    if fig is None:
        fig, ax = plt.subplots(len(channels), 1, figsize=(7,3*len(channels)), tight_layout=True)
    else: 
        ax = fig.axes
    if len(ax) != len(channels):
        raise ValueError(f"Figure provided does not have the same number of axes as channels. Expected: {len(channels)}, actual: {len(ax)}.")
    
    if labels is None:
        labels = []
        for k in range(len(dfs)):
            labels.append('Controller '+str(k+1))

    ws = []

    for sumf in sumfs:
        ws.append(np.sqrt( sumf.loc[cases]['Wind1VelX']['mean'].values**2 + sumf.loc[cases]['Wind1VelY']['mean'].values**2 ))
    for n, channel in enumerate(channels):
        for k, df in enumerate(dfs):
            ax[n].scatter(ws[k], abs(df.loc[cases][channel]), label=f'{labels[k]}: Sim. DEL')
            ax[n].axhline(y=dss[k][channel], color='C'+str(k), linestyle='-', label=f'{labels[k]}: Lifetime DEL')   # Lifeteime DELs
        
        ax[n].set_xlabel('Wind speed (m/s)')
        ax[n].set_ylabel(channel)
        ax[n].grid()

    # Plot distribution of wind speeds
    dist_prob = []
    dist_ws = []
    for ds in dss:
        _, unique_idx = np.unique(ds['wind_speeds'], return_index=True)
        dist_prob.append(np.array(ds['probability'])[unique_idx])
        dist_ws.append(np.array(ds['wind_speeds'])[unique_idx])

    
    for i_ax, a in enumerate(ax):   # for each axis
        ymax = np.max(a.get_ylim())  # Get y limits for the first axis
        
        for n, (prob, ws) in enumerate(zip(dist_prob, dist_ws)):  # for each controller
            ax[i_ax].plot(ws, 0.5 * prob * ymax / np.max(prob), label=f'{labels[k]}: Scaled dist.', color='C'+str(n), linestyle=':')


    ax[0].legend()

    return dist_prob, dist_ws


def parse_freq_string(freq_string):
    b = freq_string.replace('[','').replace(']','').split(',')
    return [float(bb) for bb in b]


def report_psd_ranking(psd_summ, labels, channels_to_analyze, n_largest=4, sort_index=0):
    """
    Reports the n_largest PSD values for each channel and frequency from the psd_summ DataFrame.
    psd_summ: List of DataFrames, each containing PSD values for different controllers/channels/frequencies.
    channels_to_analyze: List of channels to analyze.
    n_largest: Number of largest values to report.
    sort_index: Index of the column to sort by when reporting.
    """

    b = []  # List to store series for each controller/channel/frequency
    for i, psd_summ_i in enumerate(psd_summ):
        for chan in channels_to_analyze:
            for col in psd_summ_i[chan].columns:
                a = psd_summ_i[chan][col]  # Series of PSD values for this channel/frequency
                b.append(a)

                # When at the last controller, combine all into a DataFrame and print sorted results
                if i == len(psd_summ)-1:  # last case/controller
                    fdf = pd.DataFrame({l: s for l, s in zip(labels, b)})  # Combine all controllers into one DataFrame

                    print(f'{n_largest} highest cases for {chan} at f = {col}')
                    print(fdf.sort_values(by=labels[sort_index], ascending=False).head(n_largest))
                    print('')

def plot_psd_comparison(summary_folders, cases_to_plot, channels):
    """
    Plot PSD comparison for given cases and channels across multiple summary folders.
    """
    psd_folders = [os.path.join(folder, 'psds') for folder in summary_folders]

    for case_name in cases_to_plot:
        psd_df = []
        psd_summ = []
        for summary_folder, psd_folder in zip(summary_folders, psd_folders):
            psd_df.append(pd.read_pickle(os.path.join(psd_folder, f'{case_name}.p')))
            psd_summ.append(pd.read_pickle(os.path.join(summary_folder, 'psd_summary.p')))

        fig, axs = plt.subplots(len(channels), 1, sharex=True)
        fig.set_size_inches(7, 7)
        for ax, chan in zip(axs, channels):
            yl = None
            for i, (psd_df_i, psd_summ_i) in enumerate(zip(psd_df, psd_summ)):
                ax.loglog(psd_df_i[chan])
                sum_data = psd_summ_i.loc[case_name][chan]
                yl = ax.get_ylim()
                for item in sum_data.items():
                    freqs = parse_freq_string(item[0])
                    data = item[1]
                    if len(freqs) > 1:
                        ax.fill_betweenx(yl, freqs[0], freqs[1], alpha=0.1, color='k')
                        x = np.mean(np.array(freqs))
                    else:
                        ax.axvline(freqs[0], 0, 1)
                        x = freqs[0]
                    ax.plot(x, data, 'x', color='C'+str(i))
            ax.set_ylabel(chan)
            if yl is not None:
                ax.set_ylim(yl)
        axs[-1].set_xlabel('Freq. (Hz)')
        fig.suptitle(case_name)


def plot_aep(aep_info, summary_folders, ss, cm, labels):
    """
    Plot AEP power curves and probability distributions for each controller.
    summary_folders: List of folders containing summary data.
    ss: List of DataFrames containing summary statistics.
    cm: DataFrame containing case matrix information.
    labels: List of labels for each controller.
    """
    
    AEP_title = ''
    prob_dist = []
    for i, summary_folder in enumerate(summary_folders):

        # Reduce summary stats to AEP relevant cases
        ind_aep = np.array(cm[i]['DLC'] == 'AEP')
        ss_aep = ss[i].loc[ind_aep]

        # Unpack AEP information
        mean_power = ss_aep['GenPwr']['mean']
        ws_i = ss_aep['Wind1VelX']['mean']
        aep_ws = aep_info[i]['mean_wind_speeds']

        # Map each ws_i value to the nearest aep_ws value
        ws_i_mapped = ws_i.apply(lambda x: aep_ws[np.abs(np.array(aep_ws) - x).argmin()])
        ss_aep['AEP_WindSpeed'] = ws_i_mapped

        # Compute mean power for each wind speed in AEP power curve
        grouped = ss_aep.groupby('AEP_WindSpeed')
        mean_power_ws = []
        for ws, group in grouped:
            mean_power_ws.append(group['GenPwr']['mean'].mean())

        aep_info[i]['mean_power'] = mean_power_ws

        # Scale the probability distribution for plotting
        prob_dist.append(aep_info[i]['probability'])

        plt.scatter(ss_aep['Wind1VelX']['mean'], ss_aep['GenPwr']['mean'],
                    label=f'{labels[i]}: Sim. Mean Power', color='C'+str(i), marker='o', facecolors='none')
        plt.plot(np.unique(aep_info[i]['mean_wind_speeds']), aep_info[i]['mean_power'],
                 label=f'{labels[i]}: Power Curve', color='C'+str(i))

        AEP_title += f"{labels[i]}: AEP = {aep_info[i]['AEP']/1e6:.2f} GWh \n"

    max_power = np.max([np.max(info['mean_power']) for info in aep_info])
    prob_scaled = np.array(prob_dist) * max_power / np.max(aep_info[0]['probability']) / 2

    for i in range(len(aep_info)):
        plt.plot(aep_info[i]['mean_wind_speeds'], prob_scaled[i],
                 label=f'{labels[i]}: Prob. Dist. (scaled)', color='C'+str(i), linestyle='--')

    plt.legend(loc='upper center', bbox_to_anchor=(1.4, 1))
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Mean Power (kW)')
    plt.title(AEP_title)
    plt.grid()
