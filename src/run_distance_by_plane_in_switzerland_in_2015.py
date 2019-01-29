from utils_mtmc.get_mtmc_files import *
import numpy as np
import pandas as pd
from scipy.stats import norm
import os


def run_distance_by_plane_in_switzerland_in_2015():
    df_zp = get_zp_renamed()
    # select only people who were asked questions about trips with overnights (module 1b, encoded 2)
    df_zp = df_zp[df_zp['module_attributed_to_the_respondent'] == 2]
    df_zp.drop(columns=['module_attributed_to_the_respondent'], inplace=True)
    # select only people who said the number of trips with overnights they made
    df_zp['with_trips'] = df_zp['nb_trips_with_overnights'] > 0
    df_zp = df_zp[~df_zp['nb_trips_with_overnights'] < 0]
    # sum of weights of the declared trips, including those without details, in particular distance
    weight_declared_trips = df_zp[df_zp['with_trips']]['WP'].sum()
    # select overnight trips whose distance is known
    df_overnight_trips = get_overnight_trips_in_2015_renamed()  # contains all trips with overnights
    df_overnight_trips = df_overnight_trips[df_overnight_trips['trip_distance'] >= 0]  # only trips with valid distance
    df_overnight_trips = add_aggregate_goal_to_overnight_trips(df_overnight_trips)  # add info about aggregated goals
    # get number of detailed trips (with distance) by person
    df_overnight_trips_count_nb = df_overnight_trips[['HHNR', 'trip_distance']].groupby('HHNR').count()
    df_overnight_trips_count_nb = df_overnight_trips_count_nb.rename(columns={'trip_distance': 'nb_detailed_trips'})
    df_zp = pd.merge(df_zp, df_overnight_trips_count_nb,
                     left_on='HHNR', right_index=True, how='left')
    # get total distance per person by plane
    df_overnight_trips['trip_distance_by_plane'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17)
    df_overnight_trips['trip_distance_by_plane_private'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17) \
        * (df_overnight_trips['trip_goal_agg'] == 1)
    df_overnight_trips['trip_distance_by_plane_business'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17) \
        * (df_overnight_trips['trip_goal_agg'] == 2)
    df_overnight_trips['trip_distance_by_plane_other'] = \
        df_overnight_trips['trip_distance'] * (df_overnight_trips['main_transport_mode'] == 17) \
        * (df_overnight_trips['trip_goal_agg'] == 3)
    df_overnight_trips_count_sum = df_overnight_trips[['HHNR', 'trip_distance_by_plane',
                                                       'trip_distance_by_plane_private',
                                                       'trip_distance_by_plane_business',
                                                       'trip_distance_by_plane_other']].groupby('HHNR').sum()
    df_overnight_trips_count_sum = \
        df_overnight_trips_count_sum.rename(columns={'trip_distance_by_plane': 'total_distance',
                                                     'trip_distance_by_plane_private': 'total_distance_private',
                                                     'trip_distance_by_plane_business': 'total_distance_business',
                                                     'trip_distance_by_plane_other': 'total_distance_other'})
    df_zp_with_trips_temp = pd.merge(df_zp[df_zp['with_trips']], df_overnight_trips_count_sum,
                                     left_on='HHNR', right_index=True, how='inner')
    df_zp = pd.concat([df_zp[~df_zp['with_trips']], df_zp_with_trips_temp])
    # extrapolation for all trips based on declared trips
    df_zp['total_distance_extrapolated'] = \
        df_zp['total_distance'] * df_zp['nb_trips_with_overnights'] / \
        df_zp['nb_detailed_trips']
    df_zp['total_distance_extrapolated_private'] = \
        df_zp['total_distance_private'] * df_zp['nb_trips_with_overnights'] / \
        df_zp['nb_detailed_trips']
    df_zp['total_distance_extrapolated_business'] = \
        df_zp['total_distance_business'] * df_zp['nb_trips_with_overnights'] / \
        df_zp['nb_detailed_trips']
    df_zp['total_distance_extrapolated_other'] = \
        df_zp['total_distance_other'] * df_zp['nb_trips_with_overnights'] / \
        df_zp['nb_detailed_trips']
    # Remove people who said they did a trip, but whose distance are not valid
    # For HHNR=333950, the distance is known, but not the country of destination.
    # For HHNR=488907, the destination is known but is the same as home.
    df_zp = df_zp[~df_zp['HHNR'].isin([333950, 488907])]
    nb_of_obs = len(df_zp)
    print('Basis total distance:', nb_of_obs,
          'persons who were asked about trips with overnights and with a valid information about the distance')
    # Result: 17054
    # Sum of weights of the detailed trips, without those missing details, in particular distance
    weight_detailed_trips = df_zp[df_zp['with_trips']]['WP'].sum()
    # Correction factor for people declaring they did trips, but without detailing them
    correction_factor_declared_detailed_trips = weight_declared_trips / weight_detailed_trips
    # Trips have been asked for 4 months on the phone in the MTMC and must be extrapolated for a year
    extrapolation_factor_4_months_to_1_year = 365.0 / 120
    df_zp['WP_corrected'] = np.where(df_zp['with_trips'],
                                     df_zp['WP'] * correction_factor_declared_detailed_trips,
                                     df_zp['WP'])
    df_zp['average_plane_dist'] = np.where(df_zp['with_trips'],
                                           df_zp['total_distance_extrapolated']
                                           * correction_factor_declared_detailed_trips
                                           * extrapolation_factor_4_months_to_1_year,
                                           0)
    df_zp['average_plane_dist_private'] = np.where(df_zp['with_trips'],
                                                   df_zp['total_distance_extrapolated_private']
                                                   * correction_factor_declared_detailed_trips
                                                   * extrapolation_factor_4_months_to_1_year,
                                                   0)
    df_zp['average_plane_dist_business'] = np.where(df_zp['with_trips'],
                                                    df_zp['total_distance_extrapolated_business']
                                                    * correction_factor_declared_detailed_trips
                                                    * extrapolation_factor_4_months_to_1_year,
                                                    0)
    df_zp['average_plane_dist_other'] = np.where(df_zp['with_trips'],
                                                 df_zp['total_distance_extrapolated_other']
                                                 * correction_factor_declared_detailed_trips
                                                 * extrapolation_factor_4_months_to_1_year,
                                                 0)
    weighted_avg, weighted_std = get_weighted_average_and_std(df_zp, 'average_plane_dist')
    print('Average distance made by plane per person in 2015, in km:',
          weighted_avg, ' (+/-', str(weighted_std) + ')')
    # Result: 5924.873511771452
    # Define age categories (including names for CSV-files)
    age_bins = pd.cut(df_zp['age'], [5, 17, 24, 44, 64, 79, 100],
                      labels=['6-17 years', '18-24 years', '25-44 years', '45-64 years', '65-79 years',
                              '80 years and over'])
    # Compute results by age
    output_by_age_as_series = df_zp.groupby(age_bins).apply(get_weighted_average_and_std, 'average_plane_dist')
    # Save results as CSV-file
    save_results_as_csv_file(output_by_age_as_series)
    # Generate a figure with the results
    print('--- Among which; ---')
    weighted_avg_private, weighted_std_private = get_weighted_average_and_std(df_zp, 'average_plane_dist_private')
    print('Only private trips:', weighted_avg_private, '(+/-', str(weighted_std_private) + ')')
    print(df_zp.groupby(age_bins).apply(get_weighted_average_and_std, 'average_plane_dist_private'))
    weighted_avg_business, weighted_std_business = get_weighted_average_and_std(df_zp, 'average_plane_dist_business')
    print('Only business trips:', weighted_avg_business, '(+/-', str(weighted_std_business) + ')')
    print(df_zp.groupby(age_bins).apply(get_weighted_average_and_std, 'average_plane_dist_business'))
    weighted_avg_other, weighted_std_other = get_weighted_average_and_std(df_zp, 'average_plane_dist_other')
    print('Only other trips:', weighted_avg_other, '(+/-', str(weighted_std_other) + ')')
    print(df_zp.groupby(age_bins).apply(get_weighted_average_and_std, 'average_plane_dist_other'))


def save_results_as_csv_file(output_by_age_as_series):
    output_by_age_as_df = pd.DataFrame(output_by_age_as_series.tolist(),
                                       columns=['Average distance made by plane per person in 2015, in km', '+/-'],
                                       index=output_by_age_as_series.index)
    output_by_age_as_df.index.names = ['Age category']
    output_by_age_as_df.to_csv(os.path.join('..', 'data', 'output', 'distance_by_plane_by_age.csv'))


def get_weighted_average_and_std(df_zp, name_variable):
    nb_of_obs = len(df_zp['HHNR'].unique())
    weighted_avg = (df_zp[name_variable] * df_zp['WP']).sum() / df_zp['WP_corrected'].sum()
    variance = np.average((df_zp[name_variable] - weighted_avg) ** 2, weights=df_zp['WP'])
    weighted_std = np.divide(norm.ppf(0.95) * 1.14 * np.sqrt(variance), np.sqrt(nb_of_obs))
    return weighted_avg, weighted_std


def get_zp_renamed():
    selected_columns = ['HHNR', 'WP', 'dmod', 'f70100', 'alter']
    df_zp = get_zp(year=2015, selected_columns=selected_columns)
    # Rename variables
    df_zp = df_zp.rename(columns={'dmod': 'module_attributed_to_the_respondent',
                                  'f70100': 'nb_trips_with_overnights',
                                  'alter': 'age'})
    return df_zp


def get_overnight_trips_in_2015_renamed():
    selected_columns = ['HHNR', 'WP', 'RENR', 'reisenr', 'f70801', 'f71300', 'f71400_01', 'f71600b',
                        'f70700_01', 'f71700b']
    df_overnight_trips = get_overnight_trips(year=2015, selected_columns=selected_columns)
    # Rename variables
    df_overnight_trips = df_overnight_trips.rename(columns={'f71600b': 'trip_distance',
                                                            'f71700b': 'trip_distance_in_CH',
                                                            'f70700_01': 'trip_goal',
                                                            'f70801': 'main_transport_mode'})
    return df_overnight_trips


def add_aggregate_goal_to_overnight_trips(df_overnight_trips):
    conditions_trip_goal = [df_overnight_trips['trip_goal'].isin([2,  # private: shopping
                                                                  3,  # Private: medical
                                                                  5,  # private: visit friends and family
                                                                  6,  # Private: gastronomie
                                                                  7,  # Private: active sport
                                                                  8,  # Private: hiking
                                                                  9,  # Private: bike tour
                                                                  10,  # Private: passive sport
                                                                  11,  # Private: outdoor activities (no sport)
                                                                  12,  # Private: Culture and leisure
                                                                  13,  # Private: Holidays, trips
                                                                  14,  # Private: Religion
                                                                  16,  # Private: Accompany for private trips
                                                                  17,  # Private: Round trip
                                                                  ]),
                            df_overnight_trips['trip_goal'].isin([4,  # Work: business trip
                                                                  15,  # Work: Accompany for work trips
                                                                  ])]
    choices_trip_goal = [1, 2]  # private (1), business (2), other (3, as default)
    df_overnight_trips['trip_goal_agg'] = np.select(conditions_trip_goal, choices_trip_goal, default=3)
    return df_overnight_trips


if __name__ == '__main__':
    run_distance_by_plane_in_switzerland_in_2015()
